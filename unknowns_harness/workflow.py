"""Run deterministic, non-authoritative Unknowns Workflow demonstrations."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Mapping

from . import consultation_budget, evidence_graph, preflight


PHASE_ORDER = (
    "unknowns_intake",
    "capability_preflight",
    "bounded_local_dispatch",
    "evidence_events",
    "consultation_budget_check",
    "comparable_exposures",
    "adjudication_report",
)
_SCENARIOS = frozenset({"typed-rejection", "adjudication"})
_STREAM_ID = "public-adjudication-demo"
_DEMO_TIME = "2025-01-01T00:00:00+00:00"
_ASSETS: Mapping[str, tuple[str, ...]] = {
    "skill:finding-unknowns": (
        "skills/finding-unknowns/SKILL.md",
        "templates/ledger.md",
    ),
    "skill:unknowns-impl-notes": (
        "skills/unknowns-impl-notes/SKILL.md",
        "templates/implementation-notes.md",
    ),
    "skill:unknowns-explainer": (
        "skills/unknowns-explainer/SKILL.md",
        "templates/explainer.md",
    ),
}


@dataclass(frozen=True)
class WorkflowResult:
    exit_code: int
    payload: Mapping[str, object]

    def to_dict(self) -> dict[str, object]:
        return dict(self.payload)

    def to_json(self) -> str:
        return json.dumps(
            self.payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )


def _is_regular_local_asset(root: Path, relative: str) -> bool:
    candidate = root
    for component in Path(relative).parts:
        candidate /= component
        if candidate.is_symlink():
            return False
    try:
        resolved = candidate.resolve()
        resolved.relative_to(root)
    except (OSError, ValueError):
        return False
    return resolved.is_file()


def _inspect_assets(
    assets_root: str | Path,
) -> tuple[dict[str, bool], list[dict[str, object]], dict[str, str]]:
    root_input = Path(assets_root).expanduser()
    if root_input.is_symlink():
        root_ready = False
        root = root_input
    else:
        root = root_input.resolve()
        root_ready = root.is_dir()

    capabilities: dict[str, bool] = {}
    assets: list[dict[str, object]] = []
    remedies: dict[str, str] = {}
    for identifier, paths in sorted(_ASSETS.items()):
        checked = [
            {
                "authoritative": False,
                "path": path,
                "present": root_ready and _is_regular_local_asset(root, path),
            }
            for path in paths
        ]
        ready = all(item["present"] for item in checked)
        capabilities[identifier] = ready
        assets.append(
            {
                "authoritative": False,
                "identifier": identifier,
                "paths": checked,
                "ready": ready,
            }
        )
        if not ready:
            missing = next(
                item["path"] for item in checked if item["present"] is False
            )
            remedies[identifier] = (
                f"Provide the public local asset {missing} under --assets-root."
            )
    return capabilities, assets, remedies


def _phase(name: str, **details: object) -> dict[str, object]:
    return {"authoritative": False, "phase": name, **details}


def _rejected_result(
    *,
    scenario: str,
    phases: list[dict[str, object]],
) -> WorkflowResult:
    return WorkflowResult(
        exit_code=2,
        payload={
            "authoritative": False,
            "phases": phases,
            "scenario": scenario,
            "status": "rejected",
        },
    )


def run_workflow(
    *,
    scenario: str,
    assets_root: str | Path,
    runtime_root: str | Path,
) -> WorkflowResult:
    """Run one bounded demo without issuing authority or executing effects."""

    if scenario not in _SCENARIOS:
        raise ValueError("scenario_closed")
    if not isinstance(runtime_root, (str, Path)):
        raise ValueError("runtime_root_invalid")

    capabilities, assets, asset_remedies = _inspect_assets(assets_root)
    intake = _phase(
        "unknowns_intake",
        asset_check={
            "authoritative": False,
            "assets": assets,
            "completed": True,
            "ready": all(capabilities.values()),
        },
        stable_identifiers=sorted(_ASSETS),
    )

    required = list(sorted(_ASSETS))
    if scenario == "typed-rejection":
        capabilities["bounded_local_dispatch"] = False
        required.append("bounded_local_dispatch")
        asset_remedies["bounded_local_dispatch"] = (
            "Configure the bounded local dispatch recorder locally, then rerun."
        )

    checked = preflight.check_capabilities(
        {"capabilities": capabilities},
        required=required,
    )
    preflight_payload = checked.to_dict()
    rejections = []
    for rejection in preflight_payload["rejections"]:
        item = dict(rejection)
        if item["capability"] in asset_remedies:
            item["remedy"] = asset_remedies[item["capability"]]
        item["authoritative"] = False
        rejections.append(item)
    preflight_phase = _phase(
        "capability_preflight",
        ready=checked.ready,
        ready_capabilities=list(checked.ready_capabilities),
        rejections=rejections,
        required_capabilities=list(checked.required),
        summary={
            "authoritative": False,
            "ready": len(checked.ready_capabilities),
            "required": len(checked.required),
        },
    )
    phases = [intake, preflight_phase]
    if not checked.ready:
        return _rejected_result(scenario=scenario, phases=phases)

    dispatch = {
        "authoritative": False,
        "executed": False,
        "mode": "local_record_only",
        "record": "public-demo-dispatch",
    }
    phases.append(_phase("bounded_local_dispatch", **dispatch))

    dispatch_event = evidence_graph.append_event(
        root=runtime_root,
        stream_id=_STREAM_ID,
        kind="observation",
        subject="bounded-local-dispatch-recorded",
        producer="workflow-demo",
        produced_at=_DEMO_TIME,
    )
    evidence_event = evidence_graph.append_event(
        root=runtime_root,
        stream_id=_STREAM_ID,
        kind="decision",
        subject="local-preflight-observed",
        producer="workflow-demo",
        produced_at=_DEMO_TIME,
        decision="allow",
        depends_on=(dispatch_event["event_id"],),
    )
    evidence_events = [dispatch_event, evidence_event]
    phases.append(_phase("evidence_events", events=evidence_events))

    blocker = consultation_budget.blocker_fingerprint(
        "public-demo-unknown",
        {"expected": "bounded-local-record", "observed": "bounded-local-record"},
    )
    evidence = consultation_budget.evidence_fingerprint(
        evidence_events,
        subject="public-demo-workflow",
    )
    attempt = consultation_budget.attempt_fingerprint(
        "compare-shadow-decisions",
        verifier_inputs=("public-demo-evidence",),
    )
    consultation = consultation_budget.adjudicate_consultation(
        blocker=blocker,
        evidence=evidence,
        attempt=attempt,
        history=(),
    )
    consultation_payload = {
        "action": consultation.action.value,
        "authoritative": False,
        "reason": consultation.reason,
    }
    phases.append(
        _phase("consultation_budget_check", decision=consultation_payload)
    )

    exposure_inputs = (
        ("case-1", "allow", "allow"),
        ("case-2", "deny", "deny"),
        ("case-3", "allow", "deny"),
        ("case-4", "deny", "allow"),
    )
    exposure_events = [
        evidence_graph.append_event(
            root=runtime_root,
            stream_id=_STREAM_ID,
            kind="comparable_exposure",
            subject=subject,
            producer="workflow-demo",
            produced_at=_DEMO_TIME,
            baseline_decision=baseline,
            shadow_decision=shadow,
            depends_on=(evidence_event["event_id"],),
        )
        for subject, baseline, shadow in exposure_inputs
    ]
    phases.append(_phase("comparable_exposures", events=exposure_events))

    adjudication = evidence_graph.adjudicate_exposures(exposure_events)
    phases.append(_phase("adjudication_report", report=adjudication))
    return WorkflowResult(
        exit_code=0,
        payload={
            "adjudication": adjudication,
            "authoritative": False,
            "consultation": consultation_payload,
            "dispatch": dispatch,
            "phases": phases,
            "scenario": scenario,
            "status": "completed",
        },
    )

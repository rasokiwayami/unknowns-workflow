"""Pure, non-authoritative consultation budget decisions.

Exact built-in type checks are deliberate at closed string and record
boundaries; they reject subclasses and preserve the input contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Iterable, Mapping


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_OUTCOMES = frozenset({"consulted", "advised_attempt_failed", "advised_attempt_succeeded"})


class ConsultationAction(str, Enum):
    CONSULT = "consult"
    DENY = "deny"
    REPLAN_OR_TRANSFER = "replan_or_transfer"


@dataclass(frozen=True)
class ConsultationRecord:
    blocker: str
    evidence: str
    attempt: str
    outcome: str

    def __post_init__(self) -> None:
        for label, value in (
            ("blocker", self.blocker),
            ("evidence", self.evidence),
            ("attempt", self.attempt),
        ):
            if type(value) is not str or not _SHA256.fullmatch(value):
                raise ValueError(f"{label}_invalid")
        if type(self.outcome) is not str or self.outcome not in _OUTCOMES:
            raise ValueError("outcome_closed")


@dataclass(frozen=True)
class ConsultationDecision:
    action: ConsultationAction
    reason: str
    authoritative: bool = False


def _stable_hash(value: object) -> str:
    try:
        encoded = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("fingerprint_input_invalid") from exc
    return hashlib.sha256(encoded).hexdigest()


def _subject(value: str) -> str:
    if type(value) is not str or not value or len(value) > 256 or "\x00" in value:
        raise ValueError("subject_invalid")
    return value


def blocker_fingerprint(subject: str, predicate: Mapping[str, object]) -> str:
    subject = _subject(subject)
    if not isinstance(predicate, Mapping) or not predicate:
        raise ValueError("predicate_invalid")
    return _stable_hash(
        {"schema_version": 1, "subject": subject, "predicate": dict(predicate)}
    )


def evidence_fingerprint(
    events: Iterable[Mapping[str, object]], *, subject: str
) -> str:
    subject = _subject(subject)
    if isinstance(events, (str, bytes, bytearray, Mapping)):
        raise ValueError("events_invalid")
    try:
        values = list(events)
    except Exception as exc:
        raise ValueError("events_invalid") from exc
    normalized: list[str] = []
    for event in values:
        if not isinstance(event, Mapping):
            raise ValueError("events_invalid")
        event_id = event.get("event_id")
        kind = event.get("kind")
        if type(event_id) is not str or not event_id or type(kind) is not str or not kind:
            raise ValueError("event_invalid")
        normalized.append(_stable_hash({"event_id": event_id, "kind": kind}))
    return _stable_hash(
        {"schema_version": 1, "subject": subject, "evidence": sorted(set(normalized))}
    )


def attempt_fingerprint(
    semantic_delta: str | Mapping[str, object],
    *,
    verifier_inputs: Iterable[str | Mapping[str, object]],
) -> str:
    if type(semantic_delta) is not str and not isinstance(semantic_delta, Mapping):
        raise ValueError("semantic_delta_invalid")
    if isinstance(verifier_inputs, (str, bytes, bytearray, Mapping)):
        raise ValueError("verifier_inputs_invalid")
    try:
        values = list(verifier_inputs)
    except Exception as exc:
        raise ValueError("verifier_inputs_invalid") from exc
    normalized: list[str] = []
    for value in values:
        if type(value) is str:
            if not value:
                raise ValueError("verifier_input_invalid")
            normalized.append(_stable_hash(value))
        elif isinstance(value, Mapping):
            normalized.append(_stable_hash(dict(value)))
        else:
            raise ValueError("verifier_input_invalid")
    return _stable_hash(
        {
            "schema_version": 1,
            "semantic_delta": semantic_delta,
            "verifier_inputs": sorted(set(normalized)),
        }
    )


def adjudicate_consultation(
    *,
    blocker: str,
    evidence: str,
    attempt: str,
    history: Iterable[ConsultationRecord],
) -> ConsultationDecision:
    for label, value in (
        ("blocker", blocker),
        ("evidence", evidence),
        ("attempt", attempt),
    ):
        if type(value) is not str or not _SHA256.fullmatch(value):
            raise ValueError(f"{label}_invalid")
    if isinstance(history, (str, bytes, bytearray, Mapping)):
        raise ValueError("history_invalid")
    try:
        records = list(history)
    except Exception as exc:
        raise ValueError("history_invalid") from exc
    if any(type(record) is not ConsultationRecord for record in records):
        raise ValueError("history_invalid")
    related = [record for record in records if record.blocker == blocker]
    failed_attempts = {
        record.attempt
        for record in related
        if record.outcome == "advised_attempt_failed"
    }
    if len(failed_attempts) >= 2:
        return ConsultationDecision(
            ConsultationAction.REPLAN_OR_TRANSFER,
            "failed_advised_attempt_budget_exhausted",
        )
    if any(record.attempt == attempt for record in related):
        return ConsultationDecision(ConsultationAction.DENY, "attempt_already_tried")
    if any(record.evidence == evidence for record in related):
        return ConsultationDecision(
            ConsultationAction.DENY, "identity_already_consulted"
        )
    return ConsultationDecision(ConsultationAction.CONSULT, "consultation_available")

"""Deterministic, non-authoritative checks for declared capabilities."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import json


@dataclass(frozen=True)
class Rejection:
    """A local preflight failure with a concrete recovery action."""

    code: str
    capability: str
    remedy: str

    def to_dict(self) -> dict[str, str]:
        return {
            "capability": self.capability,
            "code": self.code,
            "remedy": self.remedy,
        }


@dataclass(frozen=True)
class PreflightResult:
    """The observational result of checking declared local capabilities."""

    ready: bool
    required: tuple[str, ...]
    ready_capabilities: tuple[str, ...]
    rejections: tuple[Rejection, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "ready": self.ready,
            "ready_capabilities": list(self.ready_capabilities),
            "rejections": [item.to_dict() for item in self.rejections],
            "required_capabilities": list(self.required),
            "summary": {
                "ready": len(self.ready_capabilities),
                "required": len(self.required),
            },
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )


def invalid_manifest_result(
    required: Iterable[str],
    *,
    capability: str = "manifest",
    detail: str = "Use a JSON object with a capabilities object.",
) -> PreflightResult:
    required_names = _normalize_required(required)
    return PreflightResult(
        ready=False,
        required=required_names,
        ready_capabilities=(),
        rejections=(
            Rejection(
                code="invalid_manifest",
                capability=capability,
                remedy=detail,
            ),
        ),
    )


def check_capabilities(
    manifest: object,
    *,
    required: Iterable[str],
) -> PreflightResult:
    """Check booleans in ``manifest.capabilities`` without granting authority."""

    required_names = _normalize_required(required)
    if not required_names:
        return invalid_manifest_result(
            (),
            capability="required_capabilities",
            detail="Provide at least one local capability name to check.",
        )
    if not isinstance(manifest, Mapping):
        return invalid_manifest_result(required_names)

    capabilities = manifest.get("capabilities")
    if not isinstance(capabilities, Mapping):
        return invalid_manifest_result(
            required_names,
            capability="manifest.capabilities",
            detail="Set capabilities to a JSON object of boolean values.",
        )

    ready: list[str] = []
    rejections: list[Rejection] = []
    for name in required_names:
        value = capabilities.get(name)
        if value is True:
            ready.append(name)
        elif value is False or name not in capabilities:
            rejections.append(
                Rejection(
                    code="missing_capability",
                    capability=name,
                    remedy=f"Set capabilities.{name} to true after configuring it locally.",
                )
            )
        else:
            rejections.append(
                Rejection(
                    code="invalid_manifest",
                    capability=name,
                    remedy=f"Set capabilities.{name} to the boolean true or false.",
                )
            )

    return PreflightResult(
        ready=not rejections,
        required=required_names,
        ready_capabilities=tuple(ready),
        rejections=tuple(rejections),
    )


def _normalize_required(required: Iterable[str]) -> tuple[str, ...]:
    names = []
    for item in required:
        if not isinstance(item, str) or not item.strip():
            return ()
        names.append(item.strip())
    return tuple(sorted(set(names)))

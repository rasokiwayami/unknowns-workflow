"""Build in-memory observational events with deterministic serialization."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import json
from typing import Any


@dataclass(frozen=True)
class TelemetryEvent:
    event: str
    outcome: str
    details: Mapping[str, Any]

    def to_dict(self) -> dict[str, object]:
        return {
            "details": dict(self.details),
            "event": self.event,
            "outcome": self.outcome,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )


def telemetry_event(
    event: str,
    *,
    outcome: str,
    details: Mapping[str, Any] | None = None,
) -> TelemetryEvent:
    """Build an event without writing files or changing an observed result."""

    if not isinstance(event, str) or not event.strip():
        raise ValueError("event must be a non-empty string")
    if not isinstance(outcome, str) or not outcome.strip():
        raise ValueError("outcome must be a non-empty string")
    if details is not None and not isinstance(details, Mapping):
        raise TypeError("details must be a mapping")
    return TelemetryEvent(event.strip(), outcome.strip(), dict(details or {}))

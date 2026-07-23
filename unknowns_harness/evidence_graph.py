"""Append-only, non-authoritative evidence records under an explicit root."""

from __future__ import annotations

from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time
from typing import Iterable, Mapping


SCHEMA_VERSION = 1
EVENT_KINDS = frozenset({"observation", "decision", "comparable_exposure"})
DECISIONS = frozenset({"allow", "deny", "error"})
MAX_LOCK_SECONDS = 5.0
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_FIELDS = frozenset(
    {
        "schema_version",
        "event_id",
        "stream_id",
        "sequence",
        "dedup_key",
        "kind",
        "subject",
        "producer",
        "produced_at",
        "depends_on",
        "decision",
        "baseline_decision",
        "shadow_decision",
        "authoritative",
    }
)


class EvidenceGraphError(RuntimeError):
    """Typed failure for an evidence stream contract violation."""


def _safe_id(value: str, label: str) -> str:
    if type(value) is not str or not _SAFE_ID.fullmatch(value):
        raise EvidenceGraphError(f"{label}_invalid")
    return value


def _safe_text(value: str, label: str) -> str:
    if type(value) is not str or not value or len(value) > 256 or "\x00" in value:
        raise EvidenceGraphError(f"{label}_invalid")
    return value


def _reject_symlink(path: Path) -> None:
    if path.is_symlink():
        raise EvidenceGraphError("path_symlink")


def _graph_paths(
    *, root: str | Path, stream_id: str
) -> tuple[Path, Path]:
    if not isinstance(root, (str, Path)):
        raise EvidenceGraphError("root_invalid")
    root_input = Path(root).expanduser()
    _reject_symlink(root_input)
    root_path = root_input.resolve()
    evidence_dir = root_path / "evidence"
    stream_path = evidence_dir / f"{_safe_id(stream_id, 'stream_id')}.jsonl"
    lock_path = stream_path.with_suffix(".lock")
    try:
        evidence_dir.relative_to(root_path)
        stream_path.relative_to(evidence_dir)
        lock_path.relative_to(evidence_dir)
    except ValueError as exc:
        raise EvidenceGraphError("path_escape") from exc
    for path in (evidence_dir, stream_path, lock_path):
        _reject_symlink(path)
    if evidence_dir.exists() and not evidence_dir.is_dir():
        raise EvidenceGraphError("evidence_directory_invalid")
    return stream_path, lock_path


def graph_path(*, root: str | Path, stream_id: str) -> Path:
    return _graph_paths(root=root, stream_id=stream_id)[0]


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _parse_time(value: str) -> datetime:
    if type(value) is not str:
        raise EvidenceGraphError("produced_at_invalid")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise EvidenceGraphError("produced_at_invalid") from exc
    if parsed.tzinfo is None:
        raise EvidenceGraphError("produced_at_timezone_required")
    return parsed.astimezone(timezone.utc)


def _dedup_key(event: Mapping[str, object]) -> str:
    identity = {
        key: event.get(key)
        for key in (
            "schema_version",
            "stream_id",
            "kind",
            "subject",
            "producer",
            "depends_on",
            "decision",
            "baseline_decision",
            "shadow_decision",
        )
    }
    return hashlib.sha256(_canonical(identity)).hexdigest()


def _validate_event(
    event: Mapping[str, object],
    *,
    stream_id: str,
    expected_sequence: int,
    previous: list[dict[str, object]],
    now: datetime,
) -> None:
    if set(event) != _FIELDS:
        raise EvidenceGraphError("schema_invalid")
    if type(event["schema_version"]) is not int or event["schema_version"] != SCHEMA_VERSION:
        raise EvidenceGraphError("schema_version_closed")
    if type(event["sequence"]) is not int or event["sequence"] != expected_sequence:
        raise EvidenceGraphError("sequence_invalid")
    if event["stream_id"] != stream_id:
        raise EvidenceGraphError("stream_id_mismatch")
    _safe_id(event["stream_id"], "stream_id")  # type: ignore[arg-type]
    _safe_text(event["event_id"], "event_id")  # type: ignore[arg-type]
    _safe_text(event["subject"], "subject")  # type: ignore[arg-type]
    _safe_text(event["producer"], "producer")  # type: ignore[arg-type]
    if type(event["dedup_key"]) is not str or not re.fullmatch(r"[0-9a-f]{64}", event["dedup_key"]):
        raise EvidenceGraphError("dedup_key_invalid")
    if type(event["kind"]) is not str or event["kind"] not in EVENT_KINDS:
        raise EvidenceGraphError("kind_closed")
    if type(event["authoritative"]) is not bool or event["authoritative"] is not False:
        raise EvidenceGraphError("authoritative_closed")
    if type(event["depends_on"]) is not list or any(
        type(value) is not str for value in event["depends_on"]  # type: ignore[union-attr]
    ):
        raise EvidenceGraphError("dependencies_invalid")
    dependencies = event["depends_on"]
    if len(dependencies) != len(set(dependencies)):  # type: ignore[arg-type]
        raise EvidenceGraphError("dependency_duplicate")
    prior_ids = {item["event_id"] for item in previous}
    if any(value not in prior_ids for value in dependencies):  # type: ignore[union-attr]
        raise EvidenceGraphError("dependency_missing")
    if _parse_time(event["produced_at"]) > now:  # type: ignore[arg-type]
        raise EvidenceGraphError("future_event")
    for field in ("decision", "baseline_decision", "shadow_decision"):
        if event[field] is not None and type(event[field]) is not str:
            raise EvidenceGraphError("schema_invalid")
    kind = event["kind"]
    if kind == "observation":
        if any(event[field] is not None for field in ("decision", "baseline_decision", "shadow_decision")):
            raise EvidenceGraphError("schema_invalid")
    elif kind == "decision":
        if event["decision"] not in DECISIONS or any(
            event[field] is not None for field in ("baseline_decision", "shadow_decision")
        ):
            raise EvidenceGraphError("decision_closed")
    elif (
        event["decision"] is not None
        or event["baseline_decision"] not in DECISIONS
        or event["shadow_decision"] not in DECISIONS
    ):
        raise EvidenceGraphError("decision_closed")
    if event["dedup_key"] != _dedup_key(event):
        raise EvidenceGraphError("dedup_key_mismatch")
    if any(item["event_id"] == event["event_id"] for item in previous):
        raise EvidenceGraphError("event_id_duplicate")
    if any(item["dedup_key"] == event["dedup_key"] for item in previous):
        raise EvidenceGraphError("dedup_key_duplicate")


def _read_stream(path: Path, stream_id: str) -> list[dict[str, object]]:
    if not path.exists():
        return []
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise EvidenceGraphError("stream_unreadable") from exc
    if not raw:
        return []
    if not raw.endswith(b"\n"):
        raise EvidenceGraphError("malformed_stream")
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise EvidenceGraphError("malformed_stream") from exc
    events: list[dict[str, object]] = []
    for sequence, line in enumerate(lines, start=1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvidenceGraphError("malformed_stream") from exc
        if not isinstance(event, dict):
            raise EvidenceGraphError("malformed_stream")
        _validate_event(
            event,
            stream_id=stream_id,
            expected_sequence=sequence,
            previous=events,
            now=datetime.now(timezone.utc),
        )
        events.append(event)
    return events


def read_events(*, root: str | Path, stream_id: str) -> list[dict[str, object]]:
    stream_id = _safe_id(stream_id, "stream_id")
    return _read_stream(graph_path(root=root, stream_id=stream_id), stream_id)


def _lock(path: Path, timeout_seconds: float):
    if (
        type(timeout_seconds) not in (int, float)
        or not math.isfinite(timeout_seconds)
        or timeout_seconds <= 0
        or timeout_seconds > MAX_LOCK_SECONDS
    ):
        raise EvidenceGraphError("lock_timeout_invalid")
    _reject_symlink(path.parent)
    _reject_symlink(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _reject_symlink(path.parent)
    _reject_symlink(path)
    handle = path.open("a+b")
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return handle
        except BlockingIOError:
            if time.monotonic() >= deadline:
                handle.close()
                raise EvidenceGraphError("lock_timeout")
            time.sleep(0.005)


def append_event(
    *,
    root: str | Path,
    stream_id: str,
    kind: str,
    subject: str,
    producer: str,
    produced_at: str | None = None,
    depends_on: Iterable[str] = (),
    decision: str | None = None,
    baseline_decision: str | None = None,
    shadow_decision: str | None = None,
    authoritative: bool = False,
    lock_timeout_seconds: float = 2.0,
) -> dict[str, object]:
    stream_id = _safe_id(stream_id, "stream_id")
    _safe_text(subject, "subject")
    _safe_text(producer, "producer")
    if type(kind) is not str or kind not in EVENT_KINDS:
        raise EvidenceGraphError("kind_closed")
    if type(authoritative) is not bool or authoritative is not False:
        raise EvidenceGraphError("authoritative_closed")
    if isinstance(depends_on, (str, bytes, bytearray, Mapping)):
        raise EvidenceGraphError("dependencies_invalid")
    try:
        dependencies = sorted(depends_on)
    except Exception as exc:
        raise EvidenceGraphError("dependencies_invalid") from exc
    if any(type(value) is not str or not value for value in dependencies):
        raise EvidenceGraphError("dependencies_invalid")
    if len(dependencies) != len(set(dependencies)):
        raise EvidenceGraphError("dependency_duplicate")
    for value in (decision, baseline_decision, shadow_decision):
        if value is not None and type(value) is not str:
            raise EvidenceGraphError("schema_invalid")
    if kind == "observation" and any(
        value is not None for value in (decision, baseline_decision, shadow_decision)
    ):
        raise EvidenceGraphError("schema_invalid")
    if kind == "decision" and (
        decision not in DECISIONS
        or baseline_decision is not None
        or shadow_decision is not None
    ):
        raise EvidenceGraphError("decision_closed")
    if kind == "comparable_exposure" and (
        decision is not None
        or baseline_decision not in DECISIONS
        or shadow_decision not in DECISIONS
    ):
        raise EvidenceGraphError("decision_closed")
    produced = datetime.now(timezone.utc) if produced_at is None else _parse_time(produced_at)
    if produced > datetime.now(timezone.utc):
        raise EvidenceGraphError("future_event")

    path, lock_path = _graph_paths(root=root, stream_id=stream_id)
    lock_handle = _lock(lock_path, lock_timeout_seconds)
    try:
        existing = _read_stream(path, stream_id)
        candidate: dict[str, object] = {
            "schema_version": SCHEMA_VERSION,
            "event_id": "",
            "stream_id": stream_id,
            "sequence": len(existing) + 1,
            "dedup_key": "",
            "kind": kind,
            "subject": subject,
            "producer": producer,
            "produced_at": produced.isoformat(),
            "depends_on": dependencies,
            "decision": decision,
            "baseline_decision": baseline_decision,
            "shadow_decision": shadow_decision,
            "authoritative": False,
        }
        candidate["dedup_key"] = _dedup_key(candidate)
        for event in existing:
            if event["dedup_key"] == candidate["dedup_key"]:
                return event
        prior_ids = {event["event_id"] for event in existing}
        if any(dependency not in prior_ids for dependency in dependencies):
            raise EvidenceGraphError("dependency_missing")
        candidate["event_id"] = f"{stream_id}:{str(candidate['dedup_key'])[:24]}"
        _validate_event(
            candidate,
            stream_id=stream_id,
            expected_sequence=len(existing) + 1,
            previous=existing,
            now=datetime.now(timezone.utc),
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        _reject_symlink(path.parent)
        _reject_symlink(path)
        created = not path.exists()
        with path.open("ab") as handle:
            handle.write(_canonical(candidate) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        if created:
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        stored = _read_stream(path, stream_id)
        if stored[-1] != candidate:
            raise EvidenceGraphError("readback_mismatch")
        return stored[-1]
    finally:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        lock_handle.close()


def adjudicate_exposures(events: Iterable[Mapping[str, object]]) -> dict[str, object]:
    if isinstance(events, (str, bytes, bytearray, Mapping)):
        raise EvidenceGraphError("exposures_invalid")
    exposure_count = 0
    agreement_count = 0
    directions: dict[str, int] = {}
    try:
        values = list(events)
    except Exception as exc:
        raise EvidenceGraphError("exposures_invalid") from exc
    for event in values:
        if not isinstance(event, Mapping) or event.get("kind") != "comparable_exposure":
            raise EvidenceGraphError("exposure_invalid")
        baseline = event.get("baseline_decision")
        shadow = event.get("shadow_decision")
        if type(baseline) is not str or baseline not in DECISIONS:
            raise EvidenceGraphError("decision_closed")
        if type(shadow) is not str or shadow not in DECISIONS:
            raise EvidenceGraphError("decision_closed")
        exposure_count += 1
        if baseline == shadow:
            agreement_count += 1
        else:
            direction = f"{baseline}->{shadow}"
            directions[direction] = directions.get(direction, 0) + 1
    return {
        "schema_version": 1,
        "exposure_count": exposure_count,
        "agreement_count": agreement_count,
        "agreement_rate": agreement_count / exposure_count if exposure_count else 0.0,
        "disagreement_directions": dict(sorted(directions.items())),
        "authoritative": False,
    }

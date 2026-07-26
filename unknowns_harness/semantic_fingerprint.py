"""Deterministic fingerprints for explicitly named public inputs.

Exact built-in type checks are deliberate for closed artifact name and content
inputs; they reject subclasses where the public contract requires exact types.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence


MAX_PATHS = 256


class FingerprintInputError(ValueError):
    """Raised when a fingerprint input is unsafe or type-confused."""


@dataclass(frozen=True)
class SemanticFingerprint:
    algorithm: str
    sha256: str
    included: tuple[str, ...]
    excluded: tuple[str, ...]


def _path_list(values: Sequence[str | Path], label: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes, bytearray)) or not isinstance(values, Sequence):
        raise FingerprintInputError(f"{label}_invalid")
    if len(values) > MAX_PATHS:
        raise FingerprintInputError("path_limit_exceeded")
    normalized: list[str] = []
    for value in values:
        if not isinstance(value, (str, Path)):
            raise FingerprintInputError("path_invalid")
        path = Path(value)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise FingerprintInputError("path_escape")
        name = path.as_posix()
        if name in {"", "."} or "\x00" in name:
            raise FingerprintInputError("path_invalid")
        normalized.append(name)
    if len(normalized) != len(set(normalized)):
        raise FingerprintInputError("path_duplicate")
    return tuple(sorted(normalized))


def semantic_fingerprint(
    *,
    artifacts: Mapping[str, str | bytes] | None = None,
    root: str | Path | None = None,
    paths: Sequence[str | Path] = (),
    volatile_paths: Sequence[str | Path] = (),
) -> SemanticFingerprint:
    """Hash only caller-supplied content and an explicit bounded path set."""

    if artifacts is None:
        artifacts = {}
    if not isinstance(artifacts, Mapping):
        raise FingerprintInputError("artifacts_invalid")
    path_names = _path_list(paths, "paths")
    volatile_names = _path_list(volatile_paths, "volatile_paths")
    if not set(volatile_names).issubset(path_names):
        raise FingerprintInputError("volatile_path_not_declared")
    if path_names and root is None:
        raise FingerprintInputError("root_required")
    if root is not None and not isinstance(root, (str, Path)):
        raise FingerprintInputError("root_invalid")

    records: list[dict[str, str]] = []
    included: list[str] = []
    for name in artifacts:
        if type(name) is not str or not name or "\x00" in name:
            raise FingerprintInputError("artifact_name_invalid")
    for name, content in sorted(artifacts.items()):
        if type(content) is str:
            encoded = content.encode("utf-8")
        elif type(content) is bytes:
            encoded = content
        else:
            raise FingerprintInputError("artifact_content_invalid")
        records.append(
            {"source": "artifact", "name": name, "sha256": hashlib.sha256(encoded).hexdigest()}
        )
        included.append(name)

    excluded = list(volatile_names)
    if root is not None:
        root_input = Path(root).expanduser()
        if root_input.is_symlink():
            raise FingerprintInputError("path_symlink")
        root_path = root_input.resolve()
        if not root_path.is_dir():
            raise FingerprintInputError("root_invalid")
        for name in path_names:
            if name in volatile_names:
                continue
            candidate = root_path
            for component in Path(name).parts:
                candidate /= component
                if candidate.is_symlink():
                    raise FingerprintInputError("path_symlink")
            candidate = candidate.resolve()
            try:
                candidate.relative_to(root_path)
            except ValueError as exc:
                raise FingerprintInputError("path_escape") from exc
            if not candidate.is_file():
                raise FingerprintInputError("path_not_regular_file")
            records.append(
                {
                    "source": "path",
                    "name": name,
                    "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
                }
            )
            included.append(name)

    payload = json.dumps(
        {"schema_version": 1, "records": records},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return SemanticFingerprint(
        algorithm="sha256",
        sha256=hashlib.sha256(payload).hexdigest(),
        included=tuple(sorted(included)),
        excluded=tuple(excluded),
    )

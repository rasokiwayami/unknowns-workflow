"""Pure validation for an optional caller-supplied review record."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import json
import re


TOP_FIELDS = {
    "schema_version", "artifact", "route", "implementer_id", "reviewer_id",
    "verdict", "findings",
}
ARTIFACT_FIELDS = {"kind", "identity"}
FINDING_FIELDS = {"finding_id", "classification", "disposition"}
ARTIFACT_LENGTHS = {"commit": 40, "tree": 40, "content": 64}
VERDICTS = {"approve", "rework", "blocked", "discuss"}
CLASSIFICATIONS = {"blocking", "advisory", "rejected"}
DISPOSITIONS = {"fixed", "withdrawn", "accepted_risk", "deferred", "open"}
HEX = re.compile(r"^[0-9a-fA-F]+$")


@dataclass(frozen=True)
class ReviewRejection:
    code: str
    field: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "field": self.field}


@dataclass(frozen=True)
class ReviewProvenanceResult:
    valid: bool
    rejections: tuple[ReviewRejection, ...]

    def to_json(self) -> str:
        return json.dumps(
            {
                "rejections": [item.to_dict() for item in self.rejections],
                "valid": self.valid,
            },
            sort_keys=True,
            separators=(",", ":"),
        )


def invalid_review_record_result() -> ReviewProvenanceResult:
    return ReviewProvenanceResult(
        valid=False,
        rejections=(ReviewRejection("invalid_record", "record"),),
    )


def check_review_provenance(
    record: object,
    *,
    artifact_identity: str,
    allowed_routes: Iterable[str],
    require_independence: bool = False,
) -> ReviewProvenanceResult:
    """Check closed review facts against caller-supplied gate inputs."""

    failures: list[ReviewRejection] = []

    def reject(code: str, field: str) -> None:
        failures.append(ReviewRejection(code, field))

    def fields(value: Mapping[object, object], expected: set[str], prefix: str) -> None:
        for name in sorted(expected - set(value)):
            reject("missing_field", f"{prefix}{name}")
        for name in sorted(set(value) - expected, key=str):
            reject("unknown_field", f"{prefix}{name}")

    if not isinstance(record, Mapping):
        return invalid_review_record_result()

    fields(record, TOP_FIELDS, "")
    schema_version = record.get("schema_version")
    if type(schema_version) is not int or schema_version != 1:
        reject("schema_version_closed", "schema_version")
    if record.get("route") not in tuple(allowed_routes):
        reject("route_not_allowed", "route")

    implementer = record.get("implementer_id")
    reviewer = record.get("reviewer_id")
    if not _identifier(implementer):
        reject("identifier_invalid", "implementer_id")
    if not _identifier(reviewer):
        reject("identifier_invalid", "reviewer_id")
    if (
        require_independence
        and _identifier(implementer)
        and _identifier(reviewer)
        and implementer.strip() == reviewer.strip()
    ):
        reject("independence_violated", "reviewer_id")

    artifact = record.get("artifact")
    if not isinstance(artifact, Mapping):
        reject("artifact_invalid", "artifact")
    else:
        fields(artifact, ARTIFACT_FIELDS, "artifact.")
        kind = artifact.get("kind")
        identity = artifact.get("identity")
        length = ARTIFACT_LENGTHS.get(kind) if isinstance(kind, str) else None
        if (
            length is None
            or not isinstance(identity, str)
            or len(identity) != length
            or HEX.fullmatch(identity) is None
        ):
            reject("artifact_identity_malformed", "artifact.identity")
        if identity != artifact_identity:
            reject("artifact_identity_mismatch", "artifact.identity")

    verdict = record.get("verdict")
    if not isinstance(verdict, str) or verdict not in VERDICTS:
        reject("verdict_closed", "verdict")

    findings = record.get("findings")
    seen: set[str] = set()
    unresolved = False
    if not isinstance(findings, list):
        reject("findings_invalid", "findings")
    else:
        for index, finding in enumerate(findings):
            prefix = f"findings[{index}]"
            if not isinstance(finding, Mapping):
                reject("finding_invalid", prefix)
                continue
            fields(finding, FINDING_FIELDS, f"{prefix}.")
            finding_id = finding.get("finding_id")
            if not _identifier(finding_id):
                reject("finding_id_invalid", f"{prefix}.finding_id")
            elif finding_id in seen:
                reject("finding_id_duplicate", f"{prefix}.finding_id")
            else:
                seen.add(finding_id)
            classification = finding.get("classification")
            disposition = finding.get("disposition")
            if (
                not isinstance(classification, str)
                or classification not in CLASSIFICATIONS
            ):
                reject("finding_classification_closed", f"{prefix}.classification")
            if not isinstance(disposition, str) or disposition not in DISPOSITIONS:
                reject("finding_disposition_closed", f"{prefix}.disposition")
            unresolved |= (
                classification == "blocking"
                and isinstance(disposition, str)
                and disposition in {"open", "deferred"}
            )

    if verdict == "approve" and unresolved:
        reject("blocking_finding_unresolved", "verdict")
    return ReviewProvenanceResult(not failures, tuple(failures))


def _identifier(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())

import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from unknowns_harness import review_provenance
from unknowns_harness.cli import main as cli_main


ARTIFACT = "9" * 40
OTHER_ARTIFACT = "8" * 40


def record(**overrides):
    base = {
        "schema_version": 1,
        "artifact": {"kind": "commit", "identity": ARTIFACT},
        "route": "standard-review",
        "implementer_id": "implementer-1",
        "reviewer_id": "reviewer-1",
        "verdict": "approve",
        "findings": [
            {
                "finding_id": "F1",
                "classification": "advisory",
                "disposition": "accepted_risk",
            }
        ],
    }
    base.update(overrides)
    return base


def check(value, **overrides):
    kwargs = {
        "artifact_identity": ARTIFACT,
        "allowed_routes": ("standard-review",),
        "require_independence": True,
    }
    kwargs.update(overrides)
    return review_provenance.check_review_provenance(value, **kwargs)


def codes(result):
    return sorted(rejection.code for rejection in result.rejections)


class ReviewProvenanceTests(unittest.TestCase):
    def test_conforming_record_is_accepted(self):
        result = check(record())
        self.assertTrue(result.valid)
        self.assertEqual(result.rejections, ())

    def test_stale_artifact_hash_is_rejected(self):
        result = check(record(), artifact_identity=OTHER_ARTIFACT)
        self.assertFalse(result.valid)
        self.assertIn("artifact_identity_mismatch", codes(result))

    def test_identity_substitution_is_rejected_when_independence_is_required(self):
        substituted = record(reviewer_id="implementer-1")
        self.assertFalse(check(substituted).valid)
        self.assertIn("independence_violated", codes(check(substituted)))
        self.assertTrue(check(substituted, require_independence=False).valid)

    def test_open_or_deferred_blocking_finding_cannot_carry_an_approve_verdict(self):
        for disposition in ("open", "deferred"):
            with self.subTest(disposition=disposition):
                blocked = record(
                    findings=[
                        {
                            "finding_id": "F1",
                            "classification": "blocking",
                            "disposition": disposition,
                        }
                    ]
                )
                result = check(blocked)
                self.assertFalse(result.valid)
                self.assertIn("blocking_finding_unresolved", codes(result))
                self.assertTrue(check({**blocked, "verdict": "rework"}).valid)

    def test_validation_is_idempotent_and_does_not_mutate_its_input(self):
        value = record()
        snapshot = json.dumps(value, sort_keys=True)
        first = check(value)
        second = check(value)
        self.assertEqual(first.to_json(), second.to_json())
        self.assertEqual(json.dumps(value, sort_keys=True), snapshot)

    def test_unknown_and_missing_fields_are_rejected(self):
        extra = check(record(unexpected=True))
        self.assertFalse(extra.valid)
        self.assertIn("unknown_field", codes(extra))

        incomplete = record()
        del incomplete["route"]
        missing = check(incomplete)
        self.assertFalse(missing.valid)
        self.assertIn("missing_field", codes(missing))

    def test_duplicate_finding_id_is_rejected(self):
        duplicated = record(
            findings=[
                {
                    "finding_id": "F1",
                    "classification": "advisory",
                    "disposition": "withdrawn",
                },
                {
                    "finding_id": "F1",
                    "classification": "advisory",
                    "disposition": "fixed",
                },
            ]
        )
        result = check(duplicated)
        self.assertFalse(result.valid)
        self.assertIn("finding_id_duplicate", codes(result))

    def test_route_outside_the_caller_supplied_list_is_rejected(self):
        result = check(record(route="self-review"))
        self.assertFalse(result.valid)
        self.assertIn("route_not_allowed", codes(result))

    def test_malformed_artifact_identity_is_rejected_without_resolution(self):
        malformed = record(artifact={"kind": "commit", "identity": "not-a-hash"})
        result = check(malformed, artifact_identity="not-a-hash")
        self.assertFalse(result.valid)
        self.assertIn("artifact_identity_malformed", codes(result))

    def test_closed_verdict_classification_and_disposition_vocabularies(self):
        self.assertIn("verdict_closed", codes(check(record(verdict="lgtm"))))
        self.assertIn(
            "finding_classification_closed",
            codes(
                check(
                    record(
                        findings=[
                            {
                                "finding_id": "F1",
                                "classification": "nit",
                                "disposition": "fixed",
                            }
                        ]
                    )
                )
            ),
        )
        self.assertIn(
            "finding_disposition_closed",
            codes(
                check(
                    record(
                        findings=[
                            {
                                "finding_id": "F1",
                                "classification": "advisory",
                                "disposition": "ignored",
                            }
                        ]
                    )
                )
            ),
        )

    def test_json_type_confusion_is_rejected_without_an_exception(self):
        malformed_records = [
            record(schema_version=True),
            record(artifact={"kind": [], "identity": ARTIFACT}),
            record(verdict=[]),
            record(
                findings=[
                    {
                        "finding_id": "F1",
                        "classification": {},
                        "disposition": "fixed",
                    }
                ]
            ),
            record(
                findings=[
                    {
                        "finding_id": "F1",
                        "classification": "advisory",
                        "disposition": [],
                    }
                ]
            ),
        ]
        for malformed in malformed_records:
            with self.subTest(record=malformed):
                self.assertFalse(check(malformed).valid)


class ReviewSubcommandTests(unittest.TestCase):
    def _write(self, value):
        import tempfile
        from pathlib import Path

        directory = tempfile.mkdtemp()
        path = Path(directory) / "review.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_subcommand_exit_codes_match_the_preflight_convention(self):
        path = self._write(record())
        with redirect_stdout(StringIO()):
            self.assertEqual(
                cli_main(
                    [
                        "review",
                        "--record",
                        str(path),
                        "--artifact",
                        ARTIFACT,
                        "--allow-route",
                        "standard-review",
                        "--require-independence",
                    ]
                ),
                0,
            )
            self.assertEqual(
                cli_main(
                    [
                        "review",
                        "--record",
                        str(path),
                        "--artifact",
                        OTHER_ARTIFACT,
                        "--allow-route",
                        "standard-review",
                    ]
                ),
                2,
            )

    def test_well_formed_json_with_wrong_field_types_is_a_typed_rejection(self):
        path = self._write(record(artifact={"kind": [], "identity": ARTIFACT}))
        output = StringIO()
        with redirect_stdout(output):
            exit_code = cli_main(
                [
                    "review",
                    "--record",
                    str(path),
                    "--artifact",
                    ARTIFACT,
                    "--allow-route",
                    "standard-review",
                ]
            )
        self.assertEqual(exit_code, 2)
        self.assertFalse(json.loads(output.getvalue())["valid"])


if __name__ == "__main__":
    unittest.main()

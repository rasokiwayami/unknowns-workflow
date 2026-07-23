import unittest

from unknowns_harness.consultation_budget import (
    ConsultationAction,
    ConsultationRecord,
    adjudicate_consultation,
    attempt_fingerprint,
    blocker_fingerprint,
    evidence_fingerprint,
)


class ConsultationBudgetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.blocker = blocker_fingerprint(
            "parser accepts closed input",
            {"field": "mode", "expected": ["strict", "lenient"]},
        )
        self.evidence = evidence_fingerprint(
            [{"event_id": "test-1", "kind": "failure"}],
            subject="parser",
        )
        self.attempt_a = attempt_fingerprint(
            {"changed": ["parser.py"], "approach": "validate early"},
            verifier_inputs=("test_parser.py::test_closed_mode",),
        )
        self.attempt_b = attempt_fingerprint(
            {"changed": ["schema.py"], "approach": "enum boundary"},
            verifier_inputs=("test_parser.py::test_closed_mode",),
        )

    def test_fingerprints_are_stable_across_mapping_and_input_order(self) -> None:
        blocker = blocker_fingerprint(
            "parser accepts closed input",
            {"expected": ["strict", "lenient"], "field": "mode"},
        )
        evidence = evidence_fingerprint(
            [
                {"kind": "failure", "event_id": "test-2"},
                {"event_id": "test-1", "kind": "failure"},
            ],
            subject="parser",
        )
        reordered = evidence_fingerprint(
            [
                {"event_id": "test-1", "kind": "failure"},
                {"event_id": "test-2", "kind": "failure"},
            ],
            subject="parser",
        )
        attempt = attempt_fingerprint(
            {"approach": "combined"},
            verifier_inputs=("second", "first"),
        )
        reordered_attempt = attempt_fingerprint(
            {"approach": "combined"},
            verifier_inputs=("first", "second"),
        )

        self.assertEqual(blocker, self.blocker)
        self.assertEqual(evidence, reordered)
        self.assertEqual(attempt, reordered_attempt)

    def test_one_consultation_per_blocker_and_evidence_identity(self) -> None:
        allowed = adjudicate_consultation(
            blocker=self.blocker,
            evidence=self.evidence,
            attempt=self.attempt_a,
            history=(),
        )
        denied = adjudicate_consultation(
            blocker=self.blocker,
            evidence=self.evidence,
            attempt=self.attempt_b,
            history=(
                ConsultationRecord(
                    blocker=self.blocker,
                    evidence=self.evidence,
                    attempt=self.attempt_a,
                    outcome="consulted",
                ),
            ),
        )

        self.assertIs(allowed.action, ConsultationAction.CONSULT)
        self.assertIs(denied.action, ConsultationAction.DENY)
        self.assertEqual(denied.reason, "identity_already_consulted")
        self.assertIs(denied.authoritative, False)

    def test_repeated_attempt_is_denied_even_with_new_evidence(self) -> None:
        new_evidence = evidence_fingerprint(
            [{"event_id": "test-2", "kind": "failure"}],
            subject="parser",
        )
        decision = adjudicate_consultation(
            blocker=self.blocker,
            evidence=new_evidence,
            attempt=self.attempt_a,
            history=(
                ConsultationRecord(
                    blocker=self.blocker,
                    evidence=self.evidence,
                    attempt=self.attempt_a,
                    outcome="advised_attempt_failed",
                ),
            ),
        )

        self.assertIs(decision.action, ConsultationAction.DENY)
        self.assertEqual(decision.reason, "attempt_already_tried")

    def test_advised_attempt_history_also_consumes_the_consultation_identity(self) -> None:
        decision = adjudicate_consultation(
            blocker=self.blocker,
            evidence=self.evidence,
            attempt=self.attempt_b,
            history=(
                ConsultationRecord(
                    blocker=self.blocker,
                    evidence=self.evidence,
                    attempt=self.attempt_a,
                    outcome="advised_attempt_failed",
                ),
            ),
        )

        self.assertIs(decision.action, ConsultationAction.DENY)
        self.assertEqual(decision.reason, "identity_already_consulted")

    def test_two_distinct_failed_advised_attempts_signal_replan_or_transfer(self) -> None:
        decision = adjudicate_consultation(
            blocker=self.blocker,
            evidence=self.evidence,
            attempt=attempt_fingerprint("third", verifier_inputs=("test",)),
            history=(
                ConsultationRecord(
                    blocker=self.blocker,
                    evidence=self.evidence,
                    attempt=self.attempt_a,
                    outcome="advised_attempt_failed",
                ),
                ConsultationRecord(
                    blocker=self.blocker,
                    evidence=self.evidence,
                    attempt=self.attempt_b,
                    outcome="advised_attempt_failed",
                ),
            ),
        )

        self.assertIs(decision.action, ConsultationAction.REPLAN_OR_TRANSFER)
        self.assertEqual(decision.reason, "failed_advised_attempt_budget_exhausted")
        self.assertIs(decision.authoritative, False)

    def test_record_schema_and_fingerprint_inputs_are_type_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "outcome_closed"):
            ConsultationRecord(
                blocker=self.blocker,
                evidence=self.evidence,
                attempt=self.attempt_a,
                outcome="approved",
            )
        with self.assertRaisesRegex(ValueError, "subject_invalid"):
            blocker_fingerprint(True, {"field": "mode"})
        with self.assertRaisesRegex(ValueError, "events_invalid"):
            evidence_fingerprint("not-events", subject="parser")


if __name__ == "__main__":
    unittest.main()

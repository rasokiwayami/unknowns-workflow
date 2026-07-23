import json
import multiprocessing
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from unknowns_harness.evidence_graph import (
    EvidenceGraphError,
    adjudicate_exposures,
    append_event,
    graph_path,
    read_events,
)


def _append_in_process(root: str, subject: str, queue) -> None:
    try:
        event = append_event(
            root=root,
            stream_id="concurrent",
            kind="observation",
            subject=subject,
            producer="worker",
        )
        queue.put(("ok", event["event_id"]))
    except Exception as exc:  # pragma: no cover - surfaced in the parent assertion
        queue.put(("error", repr(exc)))


class EvidenceGraphTests(unittest.TestCase):
    def test_path_object_is_accepted_as_an_explicit_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            event = append_event(
                root=Path(directory),
                stream_id="path-root",
                kind="observation",
                subject="input",
                producer="worker",
            )

        self.assertEqual(event["sequence"], 1)

    def test_append_is_durable_contiguous_and_retry_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = append_event(
                root=directory,
                stream_id="operation",
                kind="observation",
                subject="input",
                producer="worker",
            )
            retried = append_event(
                root=directory,
                stream_id="operation",
                kind="observation",
                subject="input",
                producer="worker",
            )
            second = append_event(
                root=directory,
                stream_id="operation",
                kind="decision",
                subject="result",
                producer="worker",
                decision="deny",
                depends_on=(first["event_id"],),
            )
            stored = read_events(root=directory, stream_id="operation")
            raw = graph_path(root=directory, stream_id="operation").read_bytes()

        self.assertEqual(first, retried)
        self.assertEqual([event["sequence"] for event in stored], [1, 2])
        self.assertEqual(stored[-1], second)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertTrue(all(event["authoritative"] is False for event in stored))

    def test_concurrent_distinct_and_duplicate_appends_are_serialized(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            context = multiprocessing.get_context("fork")
            queue = context.Queue()
            subjects = ["same", "same", "one", "two", "three", "four"]
            processes = [
                context.Process(target=_append_in_process, args=(directory, subject, queue))
                for subject in subjects
            ]
            for process in processes:
                process.start()
            results = [queue.get(timeout=10) for _ in processes]
            for process in processes:
                process.join(timeout=10)
            events = read_events(root=directory, stream_id="concurrent")

        self.assertTrue(all(result[0] == "ok" for result in results), results)
        self.assertTrue(all(process.exitcode == 0 for process in processes))
        self.assertEqual(len(events), 5)
        self.assertEqual([event["sequence"] for event in events], [1, 2, 3, 4, 5])
        same_ids = [event_id for status, event_id in results if event_id in {
            event["event_id"] for event in events if event["subject"] == "same"
        }]
        self.assertEqual(len(set(same_ids)), 1)

    def test_closed_schema_type_confusion_and_authority_injection_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(EvidenceGraphError, "authoritative_closed"):
                append_event(
                    root=directory,
                    stream_id="closed",
                    kind="decision",
                    subject="subject",
                    producer="worker",
                    decision="allow",
                    authoritative=True,
                )
            with self.assertRaisesRegex(EvidenceGraphError, "schema_invalid"):
                append_event(
                    root=directory,
                    stream_id="closed",
                    kind="decision",
                    subject="subject",
                    producer="worker",
                    decision=True,
                )
            with self.assertRaises(TypeError):
                append_event(
                    root=directory,
                    stream_id="closed",
                    kind="decision",
                    subject="subject",
                    producer="worker",
                    permission="write",
                )

    def test_malformed_tail_raises_without_rewriting_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            append_event(
                root=directory,
                stream_id="broken",
                kind="observation",
                subject="input",
                producer="worker",
            )
            path = graph_path(root=directory, stream_id="broken")
            path.write_bytes(path.read_bytes() + b'{"partial":')
            before = path.read_bytes()

            with self.assertRaisesRegex(EvidenceGraphError, "malformed_stream"):
                read_events(root=directory, stream_id="broken")
            with self.assertRaisesRegex(EvidenceGraphError, "malformed_stream"):
                append_event(
                    root=directory,
                    stream_id="broken",
                    kind="observation",
                    subject="next",
                    producer="worker",
                )
            self.assertEqual(path.read_bytes(), before)

    def test_future_timestamp_and_missing_dependency_do_not_advance_sequence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            future = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
            with self.assertRaisesRegex(EvidenceGraphError, "future_event"):
                append_event(
                    root=directory,
                    stream_id="validation",
                    kind="observation",
                    subject="future",
                    producer="worker",
                    produced_at=future,
                )
            with self.assertRaisesRegex(EvidenceGraphError, "dependency_missing"):
                append_event(
                    root=directory,
                    stream_id="validation",
                    kind="observation",
                    subject="dependent",
                    producer="worker",
                    depends_on=("missing",),
                )
            event = append_event(
                root=directory,
                stream_id="validation",
                kind="observation",
                subject="valid",
                producer="worker",
            )

        self.assertEqual(event["sequence"], 1)

    def test_read_rejects_unknown_fields_and_future_events(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            event = append_event(
                root=directory,
                stream_id="tampered",
                kind="observation",
                subject="input",
                producer="worker",
            )
            path = graph_path(root=directory, stream_id="tampered")
            event["unexpected"] = "value"
            path.write_text(json.dumps(event, sort_keys=True) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(EvidenceGraphError, "schema_invalid"):
                read_events(root=directory, stream_id="tampered")
            future_event = append_event(
                root=directory,
                stream_id="future-read",
                kind="observation",
                subject="input",
                producer="worker",
            )
            future_path = graph_path(root=directory, stream_id="future-read")
            future_event["produced_at"] = (
                datetime.now(timezone.utc) + timedelta(minutes=5)
            ).isoformat()
            future_path.write_text(
                json.dumps(future_event, sort_keys=True) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(EvidenceGraphError, "future_event"):
                read_events(root=directory, stream_id="future-read")

    def test_adjudication_counts_equal_decisions_and_exact_directions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for index, (baseline, shadow) in enumerate(
                (("allow", "allow"), ("allow", "deny"), ("error", "allow"))
            ):
                append_event(
                    root=directory,
                    stream_id="exposures",
                    kind="comparable_exposure",
                    subject=f"case-{index}",
                    producer="shadow-check",
                    baseline_decision=baseline,
                    shadow_decision=shadow,
                )
            events = read_events(root=directory, stream_id="exposures")
            report = adjudicate_exposures(events)

        self.assertEqual(report["exposure_count"], 3)
        self.assertEqual(report["agreement_count"], 1)
        self.assertAlmostEqual(report["agreement_rate"], 1 / 3)
        self.assertEqual(
            report["disagreement_directions"],
            {"allow->deny": 1, "error->allow": 1},
        )
        self.assertIs(report["authoritative"], False)
        self.assertTrue(all(event["authoritative"] is False for event in events))
        with self.assertRaisesRegex(EvidenceGraphError, "decision_closed"):
            adjudicate_exposures(
                [{"kind": "comparable_exposure", "baseline_decision": "maybe", "shadow_decision": "deny"}]
            )


if __name__ == "__main__":
    unittest.main()

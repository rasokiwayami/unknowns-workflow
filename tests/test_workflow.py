import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from unknowns_harness.workflow import PHASE_ORDER, run_workflow
from unknowns_harness.workflow_cli import main


REPO_ROOT = Path(__file__).resolve().parents[1]


def _assert_closed_output(test: unittest.TestCase, value: object) -> None:
    if isinstance(value, dict):
        test.assertNotIn("permission", value)
        test.assertNotIn("effect", value)
        test.assertNotIn("token", value)
        if "authoritative" in value:
            test.assertIs(value["authoritative"], False)
        for child in value.values():
            _assert_closed_output(test, child)
    elif isinstance(value, list):
        for child in value:
            _assert_closed_output(test, child)


class WorkflowTests(unittest.TestCase):
    def test_typed_rejection_stops_after_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_workflow(
                scenario="typed-rejection",
                assets_root=REPO_ROOT,
                runtime_root=directory,
            )
            rerun = run_workflow(
                scenario="typed-rejection",
                assets_root=REPO_ROOT,
                runtime_root=directory,
            )
            runtime_entries = list(Path(directory).iterdir())

        payload = result.to_dict()
        self.assertEqual(result.exit_code, 2)
        self.assertEqual(result.to_json(), rerun.to_json())
        self.assertEqual(runtime_entries, [])
        self.assertEqual(
            [phase["phase"] for phase in payload["phases"]],
            ["unknowns_intake", "capability_preflight"],
        )
        self.assertTrue(payload["phases"][0]["asset_check"]["completed"])
        rejection = payload["phases"][1]["rejections"][0]
        self.assertEqual(rejection["code"], "missing_capability")
        self.assertEqual(rejection["capability"], "bounded_local_dispatch")
        self.assertIn("local", rejection["remedy"])
        self.assertNotIn("bounded_dispatch", json.dumps(payload))
        self.assertNotIn("adjudication_report", json.dumps(payload))

    def test_missing_skill_asset_is_a_typed_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as assets, tempfile.TemporaryDirectory() as runtime:
            assets_root = Path(assets)
            source = REPO_ROOT / "skills" / "finding-unknowns" / "SKILL.md"
            destination = assets_root / "skills" / "finding-unknowns" / "SKILL.md"
            destination.parent.mkdir(parents=True)
            destination.write_bytes(source.read_bytes())

            result = run_workflow(
                scenario="adjudication",
                assets_root=assets_root,
                runtime_root=runtime,
            )

        payload = result.to_dict()
        self.assertEqual(result.exit_code, 2)
        self.assertEqual(payload["status"], "rejected")
        self.assertEqual(
            [phase["phase"] for phase in payload["phases"]],
            ["unknowns_intake", "capability_preflight"],
        )
        rejections = payload["phases"][1]["rejections"]
        self.assertTrue(
            any(
                item["code"] == "missing_capability"
                and item["capability"] == "skill:unknowns-impl-notes"
                and "skills/unknowns-impl-notes/SKILL.md" in item["remedy"]
                for item in rejections
            )
        )

    def test_adjudication_has_exact_phase_order_and_expected_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_workflow(
                scenario="adjudication",
                assets_root=REPO_ROOT,
                runtime_root=directory,
            )

        payload = result.to_dict()
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            [phase["phase"] for phase in payload["phases"]],
            list(PHASE_ORDER),
        )
        self.assertEqual(
            payload["adjudication"],
            {
                "agreement_count": 2,
                "agreement_rate": 0.5,
                "authoritative": False,
                "disagreement_directions": {
                    "allow->deny": 1,
                    "deny->allow": 1,
                },
                "exposure_count": 4,
                "schema_version": 1,
            },
        )
        self.assertEqual(payload["consultation"]["action"], "consult")
        self.assertFalse(payload["dispatch"]["executed"])

    def test_success_calls_portable_kernel_functions(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch(
            "unknowns_harness.workflow.preflight.check_capabilities",
            wraps=__import__(
                "unknowns_harness.preflight", fromlist=["check_capabilities"]
            ).check_capabilities,
        ) as capability_check, patch(
            "unknowns_harness.workflow.evidence_graph.append_event",
            wraps=__import__(
                "unknowns_harness.evidence_graph", fromlist=["append_event"]
            ).append_event,
        ) as append, patch(
            "unknowns_harness.workflow.consultation_budget.adjudicate_consultation",
            wraps=__import__(
                "unknowns_harness.consultation_budget",
                fromlist=["adjudicate_consultation"],
            ).adjudicate_consultation,
        ) as consultation, patch(
            "unknowns_harness.workflow.evidence_graph.adjudicate_exposures",
            wraps=__import__(
                "unknowns_harness.evidence_graph",
                fromlist=["adjudicate_exposures"],
            ).adjudicate_exposures,
        ) as adjudication:
            result = run_workflow(
                scenario="adjudication",
                assets_root=REPO_ROOT,
                runtime_root=directory,
            )

        self.assertEqual(result.exit_code, 0)
        capability_check.assert_called_once()
        self.assertEqual(append.call_count, 6)
        consultation.assert_called_once()
        adjudication.assert_called_once()

    def test_same_root_rerun_and_json_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = run_workflow(
                scenario="adjudication",
                assets_root=REPO_ROOT,
                runtime_root=directory,
            )
            second = run_workflow(
                scenario="adjudication",
                assets_root=REPO_ROOT,
                runtime_root=directory,
            )

        self.assertEqual(first.to_json(), second.to_json())
        self.assertNotIn(str(REPO_ROOT), first.to_json())
        self.assertNotIn(directory, first.to_json())

    def test_outputs_are_non_authoritative_and_issue_no_privileges(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = run_workflow(
                scenario="adjudication",
                assets_root=REPO_ROOT,
                runtime_root=directory,
            ).to_dict()

        _assert_closed_output(self, payload)
        self.assertIs(payload["authoritative"], False)

    def test_cli_scenarios_have_deterministic_json_and_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            successful_outputs = []
            for scenario, expected_exit in (
                ("typed-rejection", 2),
                ("adjudication", 0),
                ("adjudication", 0),
            ):
                output = StringIO()
                with redirect_stdout(output):
                    exit_code = main(
                        [
                            scenario,
                            "--assets-root",
                            str(REPO_ROOT),
                            "--runtime-root",
                            directory,
                        ]
                    )
                self.assertEqual(exit_code, expected_exit)
                payload = json.loads(output.getvalue())
                self.assertIs(payload["authoritative"], False)
                if scenario == "adjudication":
                    successful_outputs.append(output.getvalue())

        self.assertEqual(successful_outputs[0], successful_outputs[1])


if __name__ == "__main__":
    unittest.main()

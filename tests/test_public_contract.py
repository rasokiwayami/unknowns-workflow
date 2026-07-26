# Protects JSON key names, key ordering, separators, phase names and order, and
# exit codes. Regenerating a golden file is a contract change, not a fix.

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from unknowns_harness.workflow_cli import main


REPO_ROOT = Path(__file__).resolve().parents[1]


class PublicContractTests(unittest.TestCase):
    def _assert_scenario(
        self, scenario: str, golden_name: str, expected_exit_code: int
    ) -> None:
        with tempfile.TemporaryDirectory() as runtime_root:
            output = StringIO()
            with redirect_stdout(output):
                exit_code = main(
                    [
                        scenario,
                        "--assets-root",
                        str(REPO_ROOT),
                        "--runtime-root",
                        runtime_root,
                    ]
                )

        golden = (REPO_ROOT / "tests" / "golden" / golden_name).read_text(
            encoding="utf-8"
        )
        self.assertEqual(output.getvalue(), golden)
        self.assertEqual(exit_code, expected_exit_code)

    def test_typed_rejection_output_and_exit_code(self) -> None:
        self._assert_scenario("typed-rejection", "typed-rejection.json", 2)

    def test_adjudication_output_and_exit_code(self) -> None:
        self._assert_scenario("adjudication", "adjudication.json", 0)

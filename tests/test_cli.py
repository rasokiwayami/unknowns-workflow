import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from unknowns_harness.cli import main


class CliTests(unittest.TestCase):
    def test_malformed_json_is_a_typed_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_text("{", encoding="utf-8")
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(
                    [
                        "preflight",
                        "--manifest",
                        str(manifest),
                        "--require",
                        "ledger",
                    ]
                )

        payload = json.loads(output.getvalue())
        self.assertEqual(exit_code, 2)
        self.assertEqual(payload["rejections"][0]["code"], "invalid_manifest")
        self.assertEqual(payload["rejections"][0]["capability"], "manifest")

    def test_typed_rejection_exits_nonzero_and_names_remedy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_text(
                json.dumps({"capabilities": {"ledger": True}}),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(
                    [
                        "preflight",
                        "--manifest",
                        str(manifest),
                        "--require",
                        "ledger",
                        "--require",
                        "implementation_notes",
                    ]
                )

        payload = json.loads(output.getvalue())
        self.assertEqual(exit_code, 2)
        self.assertFalse(payload["ready"])
        self.assertEqual(
            payload["rejections"][0]["capability"], "implementation_notes"
        )
        self.assertIn(
            "capabilities.implementation_notes",
            payload["rejections"][0]["remedy"],
        )

    def test_ready_manifest_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_text(
                json.dumps({"capabilities": {"ledger": True}}),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(
                    [
                        "preflight",
                        "--manifest",
                        str(manifest),
                        "--require",
                        "ledger",
                    ]
                )

        self.assertEqual(exit_code, 0)
        self.assertTrue(json.loads(output.getvalue())["ready"])


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from unknowns_harness.semantic_fingerprint import (
    FingerprintInputError,
    semantic_fingerprint,
)


class SemanticFingerprintTests(unittest.TestCase):
    def test_named_artifacts_are_stable_and_content_sensitive(self) -> None:
        first = semantic_fingerprint(artifacts={"plan": "alpha", "spec": b"beta"})
        reordered = semantic_fingerprint(artifacts={"spec": b"beta", "plan": "alpha"})
        changed = semantic_fingerprint(artifacts={"plan": "changed", "spec": b"beta"})

        self.assertEqual(first.sha256, reordered.sha256)
        self.assertNotEqual(first.sha256, changed.sha256)
        self.assertEqual(first.included, ("plan", "spec"))

    def test_explicit_paths_exclude_declared_volatile_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "stable.txt").write_text("stable\n", encoding="utf-8")
            (root / "queue.json").write_text("first\n", encoding="utf-8")
            before = semantic_fingerprint(
                root=root,
                paths=("stable.txt", "queue.json"),
                volatile_paths=("queue.json",),
            )
            (root / "queue.json").write_text("second\n", encoding="utf-8")
            after = semantic_fingerprint(
                root=root,
                paths=("queue.json", "stable.txt"),
                volatile_paths=("queue.json",),
            )

        self.assertEqual(before.sha256, after.sha256)
        self.assertEqual(before.included, ("stable.txt",))
        self.assertEqual(before.excluded, ("queue.json",))

    def test_paths_require_an_explicit_root(self) -> None:
        with self.assertRaisesRegex(FingerprintInputError, "root_required"):
            semantic_fingerprint(paths=("artifact.txt",))

    def test_root_is_never_scanned_without_an_explicit_path_set(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "unlisted.txt"
            artifact.write_text("first\n", encoding="utf-8")
            before = semantic_fingerprint(root=root)
            artifact.write_text("second\n", encoding="utf-8")
            after = semantic_fingerprint(root=root)

        self.assertEqual(before.sha256, after.sha256)
        self.assertEqual(before.included, ())

    def test_explicit_path_set_is_bounded(self) -> None:
        paths = tuple(f"artifact-{index}.txt" for index in range(257))
        with self.assertRaisesRegex(FingerprintInputError, "path_limit_exceeded"):
            semantic_fingerprint(root=".", paths=paths)

    def test_path_escape_symlink_escape_and_type_confusion_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            root.mkdir()
            outside = Path(directory) / "outside.txt"
            outside.write_text("private\n", encoding="utf-8")
            (root / "escape").symlink_to(outside)
            (root / "target.txt").write_text("public\n", encoding="utf-8")
            (root / "in-root-link").symlink_to(root / "target.txt")
            (root / "real").mkdir()
            (root / "real" / "nested.txt").write_text("nested\n", encoding="utf-8")
            (root / "linked-directory").symlink_to(root / "real")

            for unsafe in (
                "../outside.txt",
                "/tmp/outside.txt",
                "escape",
                "in-root-link",
                "linked-directory/nested.txt",
            ):
                with self.subTest(unsafe=unsafe):
                    with self.assertRaises(FingerprintInputError):
                        semantic_fingerprint(root=root, paths=(unsafe,))
            with self.assertRaisesRegex(FingerprintInputError, "artifact_content_invalid"):
                semantic_fingerprint(artifacts={"spec": True})
            with self.assertRaisesRegex(FingerprintInputError, "artifact_name_invalid"):
                semantic_fingerprint(artifacts={"spec": "valid", 1: "invalid"})
            with self.assertRaisesRegex(FingerprintInputError, "path_invalid"):
                semantic_fingerprint(root=root, paths=(1,))


if __name__ == "__main__":
    unittest.main()

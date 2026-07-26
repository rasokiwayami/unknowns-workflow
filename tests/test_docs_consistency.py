import re
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"\[[^]]+\]\(([^)]+)\)")


def _tracked_markdown_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--", "*.md"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        REPO_ROOT / path
        for path in result.stdout.splitlines()
        if (REPO_ROOT / path).is_file()
    ]


class DocsConsistencyTests(unittest.TestCase):
    def test_every_doc_is_linked_from_readme(self) -> None:
        readme_targets = {
            target.split("#", 1)[0]
            for target in LINK_PATTERN.findall((REPO_ROOT / "README.md").read_text())
        }
        docs = sorted(
            path.relative_to(REPO_ROOT).as_posix()
            for path in (REPO_ROOT / "docs").glob("*.md")
        )
        self.assertTrue(all(doc in readme_targets for doc in docs))

    def test_every_relative_markdown_link_resolves(self) -> None:
        links_resolve = True
        for source in _tracked_markdown_files():
            for raw_target in LINK_PATTERN.findall(source.read_text(encoding="utf-8")):
                target = raw_target.split("#", 1)[0]
                if not target or target.startswith(("http://", "https://")):
                    continue
                resolved = (source.parent / target).resolve()
                if not resolved.is_relative_to(REPO_ROOT) or not resolved.is_file():
                    links_resolve = False
        self.assertTrue(links_resolve)

    def test_readme_skills_match_skill_directories(self) -> None:
        section = (REPO_ROOT / "README.md").read_text().split("## Skills", 1)[1]
        section = section.split("## ", 1)[0]
        listed = sorted(re.findall(r"^- `([^`]+)`:", section, re.MULTILINE))
        directories = sorted(
            path.name
            for path in (REPO_ROOT / "skills").iterdir()
            if path.is_dir()
        )
        self.assertEqual(listed, directories)

    def test_every_skill_directory_has_skill_markdown(self) -> None:
        directories = [
            path for path in (REPO_ROOT / "skills").iterdir() if path.is_dir()
        ]
        self.assertTrue(all((path / "SKILL.md").is_file() for path in directories))

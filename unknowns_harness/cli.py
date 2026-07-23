"""Command-line entrypoint for local harness checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .preflight import check_capabilities, invalid_manifest_result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="unknowns-harness")
    commands = parser.add_subparsers(dest="command", required=True)
    preflight = commands.add_parser("preflight")
    preflight.add_argument("--manifest", type=Path, required=True)
    preflight.add_argument("--require", action="append", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    required = tuple(args.require)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        result = invalid_manifest_result(
            required,
            detail="Create a readable manifest containing a valid JSON object.",
        )
    else:
        result = check_capabilities(manifest, required=required)

    print(result.to_json())
    return 0 if result.ready else 2


if __name__ == "__main__":
    raise SystemExit(main())

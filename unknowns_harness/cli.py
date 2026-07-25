"""Command-line entrypoint for local harness checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .preflight import check_capabilities, invalid_manifest_result
from .review_provenance import (
    check_review_provenance,
    invalid_review_record_result,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="unknowns-harness")
    commands = parser.add_subparsers(dest="command", required=True)
    preflight = commands.add_parser("preflight")
    preflight.add_argument("--manifest", type=Path, required=True)
    preflight.add_argument("--require", action="append", required=True)
    review = commands.add_parser("review")
    review.add_argument("--record", type=Path, required=True)
    review.add_argument("--artifact", required=True)
    review.add_argument("--allow-route", action="append", required=True)
    review.add_argument("--require-independence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "review":
        try:
            record = json.loads(args.record.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            result = invalid_review_record_result()
        else:
            result = check_review_provenance(
                record,
                artifact_identity=args.artifact,
                allowed_routes=tuple(args.allow_route),
                require_independence=args.require_independence,
            )
        print(result.to_json())
        return 0 if result.valid else 2

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

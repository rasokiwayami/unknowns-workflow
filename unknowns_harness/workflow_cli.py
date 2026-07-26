"""Console entrypoint for deterministic Unknowns Workflow demos."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .workflow import run_workflow


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="workflow")
    commands = parser.add_subparsers(dest="scenario", required=True)
    for scenario in ("typed-rejection", "adjudication"):
        command = commands.add_parser(scenario)
        command.add_argument("--assets-root", type=Path, required=True)
        command.add_argument("--runtime-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = run_workflow(
        scenario=args.scenario,
        assets_root=args.assets_root,
        runtime_root=args.runtime_root,
    )
    print(result.to_json())
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())

"""Non-authoritative local checks for the portable Unknowns Workflow.

Public entrypoints are ``unknowns-harness`` through ``cli:main``, ``workflow``
through ``workflow_cli:main``, and ``python -m unknowns_harness`` through
``__main__``. The package modules are split into capability preflight and
review validation, deterministic workflow demonstrations, evidence and
consultation decisions, plus the public telemetry and semantic-fingerprint
helpers. POSIX-only ``evidence_graph`` and ``workflow`` are intentionally not
imported here, so the package itself remains importable cross-platform.
"""

from .preflight import PreflightResult, Rejection, check_capabilities

__all__ = ["PreflightResult", "Rejection", "check_capabilities"]

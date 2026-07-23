"""Non-authoritative local checks for the portable Unknowns Workflow."""

from .preflight import PreflightResult, Rejection, check_capabilities

__all__ = ["PreflightResult", "Rejection", "check_capabilities"]

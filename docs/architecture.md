# Architecture

`unknowns-workflow` ships two layers that are useful together but have
different requirements.

## Two layers

The portable workflow is the primary product: eight installable skills under
`skills/`, six reusable templates under `templates/`, and the explanatory
prose in `README.md` and `docs/`. It works without Python and does not depend
on the optional harness.

The optional local harness is an installable Python package named
`unknowns_harness`. It observes and demonstrates the workflow locally. It
grants no authority, issues no token or permission, and performs no external
action.

## Entrypoints and module map

The public entrypoints are:

| Entrypoint | Implementation |
| --- | --- |
| `unknowns-harness` | `unknowns_harness.cli:main` |
| `workflow` | `unknowns_harness.workflow_cli:main` |
| `python -m unknowns_harness` | `unknowns_harness.__main__` -> `cli:main` |

The import and dependency direction is:

```text
cli.py            -> preflight, review_provenance
workflow_cli.py   -> workflow
workflow.py       -> preflight, evidence_graph, consultation_budget
evidence_graph.py -> stdlib only; imports fcntl
preflight.py      -> stdlib only
consultation_budget.py -> stdlib only
review_provenance.py   -> stdlib only
telemetry.py      -> stdlib only; no in-package consumer
semantic_fingerprint.py -> stdlib only; no in-package consumer
__init__.py       -> preflight only
```

Module purposes are intentionally small:

- `cli.py` parses the `unknowns-harness` commands and prints preflight or
  review-provenance results.
- `workflow_cli.py` parses the two deterministic `workflow` scenarios.
- `workflow.py` runs the portable-kernel demonstrations and produces their
  stable observational reports.
- `preflight.py` checks a caller-supplied capability manifest and returns
  typed local rejections.
- `evidence_graph.py` validates and appends non-authoritative JSONL evidence
  events under an explicit root.
- `consultation_budget.py` computes deterministic blocker, evidence, and
  attempt fingerprints and local consultation decisions.
- `review_provenance.py` validates an optional review record against its
  caller-supplied artifact, route, and independence requirements.
- `telemetry.py` builds in-memory observational events with stable JSON.
- `semantic_fingerprint.py` hashes only explicitly named artifacts and paths.
- `__init__.py` exposes the small preflight API without importing POSIX-only
  modules eagerly.
- `__main__.py` routes `python -m unknowns_harness` to `cli:main`.

`telemetry` and `semantic_fingerprint` have no consumer inside the package.
They remain public API by intent: callers and tests import them directly, so
their absence would be a compatibility break rather than dead-code cleanup.

## Platform boundary

`evidence_graph.py` imports POSIX-only `fcntl`. Consequently,
`unknowns_harness.evidence_graph`, `unknowns_harness.workflow`, and the
`workflow` console script are POSIX-only. `import unknowns_harness`,
`unknowns-harness preflight`, and `unknowns-harness review` do not import
`fcntl` and remain cross-platform.

## Input validation convention

`evidence_graph.py`, `consultation_budget.py`, and
`semantic_fingerprint.py` deliberately use `type(value) is not str` at their
closed string-input boundaries instead of `isinstance(value, str)`. The exact
check rejects string subclasses and preserves the numeric-field rule that
`isinstance(True, int) is True`; a future cleanup must not weaken these
contracts. `preflight.py` and `review_provenance.py` use `isinstance` where
subclass acceptance is harmless.

## Non-authoritative boundary

The harness is an observational local checker. Its outputs describe declared
capabilities, review records, evidence, telemetry, fingerprints, and demo
results; they do not authorize effects, issue permissions or tokens, or
perform external actions. The boundary is not a universal `authoritative`
field: `PreflightResult`, review-provenance JSON, and telemetry JSON do not
carry that field and never did.

The boundary's mechanical coverage is deliberately limited. The workflow
tests use a recursive closed-output check; the evidence path has a closed
`_FIELDS` set plus injection tests; telemetry has a complete JSON pin; and the
remaining serializers use frozen dataclass shapes. No single check enforces
the property globally. The remainder is a semantic boundary held by code
review, not a keyword filter presented as a proof of authority absence.

## Tests and verification

Tests live under `tests/` and run with the standard library:

```bash
python3 -m unittest discover -s tests -q
```

The test modules cover these contracts:

| Test module | Coverage |
| --- | --- |
| `test_cli.py` | malformed, rejected, and ready capability CLI results |
| `test_preflight.py` | manifest shape, capability values, and deterministic JSON |
| `test_review_provenance.py` | review record schema, routes, identity, and exit codes |
| `test_evidence_graph.py` | path safety, JSONL durability, schema, locking, and adjudication |
| `test_consultation_budget.py` | fingerprints, closed records, and consultation limits |
| `test_semantic_fingerprint.py` | explicit path bounds, escapes, and stable hashes |
| `test_telemetry.py` | stable in-memory event serialization |
| `test_workflow.py` | phase order, demos, kernel calls, determinism, and boundary assertions |

The two plugin descriptors are validated as JSON with:

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
```

## Growth seams

`run_workflow` is intentionally linear while there are two scenarios. If a
third scenario is added, split the function at its scenario branch so each
scenario can be read and tested independently. Do not add a registry or
strategy layer before that condition exists.

`evidence_graph.py` currently keeps five concerns together: path safety,
canonical encoding, event schema validation, file locking, and exposure
adjudication. If the module grows further and a real change becomes difficult
to make, those concerns are the candidate split lines. This is a future seam,
not work to perform now.

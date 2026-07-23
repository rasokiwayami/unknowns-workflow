# Unknowns Workflow Harness — Implementation Record

## Goal

Port the reviewed workflow kernel into a self-contained, installable package
and add a deterministic end-to-end demonstration CLI. Preserve the existing
skills and templates, keep every runtime result non-authoritative, and provide
typed rejection and shadow-adjudication examples without performing external
actions or granting permissions.

## Non-authoritative boundary

- The package performs local checks, records local evidence, and reports
  deterministic demonstration results.
- Evidence, consultation decisions, and demo outputs always carry
  `authoritative: false`.
- The workflow does not authorize effects, issue permissions or tokens,
  perform dispatch, mutate external state, or transfer authority.
- Authority-like fields are closed or rejected at the evidence boundary.

## Source provenance

The port was checked against frozen SHA-256 anchors. Labels below describe the
portable source role without exposing a private source layout.

| Portable source role | SHA-256 |
| --- | --- |
| Telemetry module | `725aa6fed3421f34d493433883b8f60fec399df9bcfa8080d6ddd5274fad4283` |
| Capability-preflight module | `575d2f4e91809e6faaf1a2e17e709b51d520eeb00025d789413f18c2d416c19b` |
| Semantic-fingerprint module | `210cfcf1b6ba97ba2609f3e2219d0ade7e0db990398dac50e7e7c5910bbe233b` |
| Evidence-graph module | `df07507a6c94fd86280dffd2e6e5edf980e49372d66c1c1b1d5787bb86f6373b` |
| Consultation full-source anchor | `cc8ac405a0b5d31e4799536e0225753d3fc21cf60f0cc749d5443cb9fbc9c80f` |
| Consultation configuration anchor | `08377146096b15ff9d5a5299c49165ba4af8770a00674a862d68badd724f639c` |

## TDD RED/GREEN summary

- `wo5a_impl`: RED characterized missing telemetry, preflight, typed rejection,
  and CLI behavior; GREEN added the installable skeleton and closed,
  deterministic preflight implementation.
- `wo5b_impl`: RED characterized fingerprint normalization, evidence
  durability/idempotency, closed-schema rejection, adjudication math, and
  consultation-budget behavior; GREEN added the portable evidence primitives.
- A follow-up RED exposed symlink aliases that remained inside the resolved
  root; GREEN rejected symlinked fingerprint and evidence storage paths.
- `wo6a_impl`: RED specified the two workflow scenarios, stable phase order,
  non-authoritative output, no executed dispatch, and same-root rerun
  determinism; GREEN added the `workflow` CLI and both demos.
- `wo6b_docs`: documentation verification separated prior assets from the new
  harness and exercised the fresh-copy quickstart.

## Local commits

| Commit | Result |
| --- | --- |
| `16d2909` | Capability preflight harness skeleton |
| `1449eed` | Portable evidence primitives |
| `46058c6` | Symlinked evidence-path rejection |
| `f69e0de` | Deterministic workflow demos |
| `a97e510` | Harness quickstart and scope |
| `ba89a04` | Public documentation terminology cleanup |

## Verification

- Full suite: `uv run --offline --with pytest python -m pytest -q` reported
  `45 passed, 5 subtests passed`.
- Typed-rejection demo: exited `2`, reported `status: rejected`,
  `missing_capability` for `bounded_local_dispatch`, and remained
  non-authoritative.
- Adjudication demo: exited `0`, reported `status: completed`, four comparable
  exposures, two agreements, one `allow->deny` disagreement, one
  `deny->allow` disagreement, and `dispatch.executed: false`.
- Same-root rerun: both adjudication outputs were byte-identical; output
  SHA-256 was
  `506913d4b6e2af907488719fe9d889466e75069d1d5af802d5155c2969f7774d`.
- Clean fresh-copy quickstart: an archive of the committed tree installed into
  a new isolated environment with offline dependency resolution; both demos
  produced their documented statuses and exit codes.
- Bytecode compilation: `python3 -m compileall -q unknowns_harness tests`
  exited `0` with an isolated cache.
- Sanitization covered both the cumulative implementation diff and every
  tracked file. It found no private absolute paths, internal process or policy
  names, credentials, secrets, raw logs, or authority-bearing production
  behavior. The pre-existing license attribution is public metadata. Test-only
  authority and token terms are negative boundary cases that assert injection
  or field rejection.
- Markdown heading/link checks and `git diff --check` passed before the final
  local documentation commit.

## Session labels

- `wo5a_impl`
- `wo5b_impl`
- `wo6a_impl`
- `wo6b_docs`

These labels identify bounded implementation tasks without encoding private
runtime or provider details.

## Deviations

### D1: Public provenance replaces internal launcher/review binding

- Expected (plan): Port the reviewed evidence and consultation behavior while
  preserving its provenance boundary.
- Found (territory): The source provenance binding depended on private
  launcher and review records that cannot be included in a portable package.
- Chosen conservative option: Replace those bindings with explicit,
  public-safe provenance fields and frozen source hashes while keeping every
  result non-authoritative.
- Why conservative: It preserves traceability without copying private process
  internals or creating a second authority path.
- Follow-up needed: no; any future authority integration must remain outside
  this package and undergo its own review.

### D2: Package directory avoids a generic import collision

- Expected (plan): Use a generic `harness/` package directory.
- Found (territory): `harness` is overly generic and can collide with other
  packages or local modules.
- Chosen conservative option: Use `unknowns_harness/` while preserving the
  installable harness package and CLI contract.
- Why conservative: The project-specific import name narrows ambiguity without
  changing the requested capability or public command surface.
- Follow-up needed: no; documentation and package metadata use the selected
  name consistently.

### D3: Resolved containment alone did not reject in-root symlinks

- Expected (plan): Resolved-path containment would provide the required path
  safety.
- Found (territory): In-root file and directory symlinks remained contained
  while violating the no-symlink contract; graph storage paths could also
  follow symlinks.
- Chosen conservative option: Reject symlinks in caller-selected fingerprint
  components and graph root, evidence directory, stream, and lock paths before
  access.
- Why conservative: It fails closed without dereferencing caller-controlled
  storage aliases.
- Follow-up needed: no; characterization tests cover the discovered
  boundaries.

## Review status

Final independent review approved the cumulative changes from `13ab2f7`
through `5bdab37`. The reviewer confirmed the 45-test suite, clean-archive
installation, both demos, sanitization, and review-evidence integrity checks,
with no Critical or Important findings.

One optional follow-up remains: the direct
`check_capabilities(required='ledger')` API could explicitly reject bare
`str` and `bytes` inputs instead of treating them as iterables. This is not a
finding against the documented CLI or manifest path.

No push, publication, deployment, submission, authentication, or external
action has been performed.

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

- 2026-07-24 Task 4 live-canary remains blocked before W5/W6. The exact
  installed binary and generated-schema pins pass, and the stdio controller
  reaches completed model turns. However, a bounded public local-read emits no
  `item/commandExecution/requestApproval` under either `untrusted`, explicit
  `on-request`, or the one Senior Advisor-recommended attempt combining
  `approvalsReviewer: user` with a requested
  `sandbox_permissions=require_escalated` tool call. No external effect or
  workflow pruning occurred. The accepted-read premise now requires replanning
  and fresh independent planning review; W5/W6 were not started.

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

### D4: Keep the package minimum at Python 3.10

- Expected (plan): Package compatibility remains Python 3.10+ as declared by
  `pyproject.toml` (`requires-python = ">=3.10"`).
- Found (territory): the system `python3` command is Python 3.9.6, while the
  project virtual environment provides Python 3.14.5.
- Chosen conservative option: Treat Python 3.9 as unsupported for package
  verification and retain the declared Python 3.10 minimum.
- Why conservative: it keeps this factual record aligned with the package
  contract without changing compatibility to accommodate an older interpreter.
- Follow-up needed: no; run package verification with a supported Python 3.10+
  environment.

### D5: Preserve direct-file test loading for the audit modules

- Expected (plan): Import the new parent controller through the package route.
- Found (territory): The focused test loader imports `runner.py` directly from
  its file path, so a normal relative import and an unregistered dataclass
  module would break the existing test route.
- Chosen conservative option: Keep a small direct-loader import bridge in the
  runner and register the sibling module before execution; preserve the
  package import path for normal use.
- Why conservative: It changes only module loading, keeps the current tests and
  CLI route intact, and does not add a second runtime behavior path.
- Follow-up needed: no.

Deviations `D6`–`D8` are recorded under "Lightweight audit operation" below and
are preserved as the record of why the proportional-review refactor exists.
Deviations `D9` onward belong to that refactor and are recorded under
"Refactor deviations".

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

## Lightweight audit operation

- Baseline branch: `codex/unknowns-workflow-harness-v2`.
- Baseline HEAD: `148936ac90b2bac961f79401069fae50cc2e14a5`.
- Baseline tree: `11653800f3bf45f23cc73d03ad6d0b0649a2ec88`.
- Baseline tests: `python3 -m unittest discover -s tests -v` — 45 tests, exit 0.
- Known failure prevention: no matched lesson in the available preflight.
- Dynamic Workflow overlay: single-run coding-debug work-order, max parallelism 1,
  900-second timeout, one attempt, local runner with manual handoff fallback,
  schema/verifier quality gates, and workflow-fitness learning.
- Required development-flow gate: unavailable because the local CLI has no
  `flow` subcommand; the command returned exit 2 without changing the target.
- Required overlay compiler: `npm exec -- tsx ...` was attempted and returned
  exit 1 due to sandbox IPC `EPERM`; the documented direct compiler fallback
  returned `status: ok`, exit 0, with the same bounded overlay contract.
- Task 4 deterministic prerequisites: the target-side validator now probes the
  pinned app-server capability contract, consumes only typed approval frames,
  validates exported parent receipts, applies exact schema/hash pins, and
  exposes exact unique target matching without any receipt issuer or store.
- Task 4 result boundary: paired results have a closed schema and a
  conjunctive audit-only pruning gate; `keep`, `simplify`, `delete`, `replace`,
  and `measure` remain distinct, with replacement and retirement-test parity.
- Task 4 canaries: the old in-memory canary is no longer treated as live
  evidence. The exact installed `codex` version and selected aggregate schema
  hash matched, but the eight reviewed individual schema hashes differed, so
  both capability and live canaries exited 2 with `blocked_tooling` before
  model use.

### D6: Target receipt issuance moved to the operation-assigned external path

- Expected (plan): The single-run parent controller lives under operation-owned
  ignored output and the target runner only validates exported receipts.
- Found (territory): The pre-existing target module issued and HMAC-signed
  receipts, so it was a false parent boundary.
- Chosen conservative option: Replace the target module with schema, protocol,
  context, and exported-receipt validators; keep no receipt key, issuer, or
  receipt store in tracked target artifacts.
- Why conservative: It prevents executor-authored or target-authored evidence
  from being mistaken for launcher provenance and preserves the public repo
  boundary.
- Follow-up needed: yes; the operation-owned ignored output parent must be
  materialized by the owning launcher environment before a live canary can run.

### D7: Exact generated individual schema hashes block the installed tool

- Expected (plan): The pinned installed app-server satisfies the selected and
  individual reviewed schema hashes.
- Found (territory): The installed executable reports the exact version and
  selected aggregate hash, but all eight reviewed individual schema hashes
  differ from the approved pin.
- Chosen conservative option: Return nonzero `blocked_tooling` before any model
  use; do not weaken the hash contract or use a help/string or handwritten
  schema fallback.
- Why conservative: The Task 4 stop condition explicitly treats any generated
  schema drift as a pre-model tooling blocker.
- Follow-up needed: yes; refresh the reviewed schema pin and planning/review
  artifacts before rerunning the live gate.

### D8: Dynamic Workflow overlay compiler unavailable in sandbox

- Expected (plan): Compile the single-run overlay with the documented `tsx`
  command before implementation.
- Found (territory): `npm exec -- tsx ... compile` failed with sandbox IPC
  `EPERM`; the direct Node fallback also failed because the TypeScript source
  imports extensionless `.js` paths.
- Chosen conservative option: Retain the approved bounded overlay contract in
  the existing operation artifacts and do not mutate Base Workflow or invent a
  new overlay runner.
- Why conservative: It preserves the required timeout, retry, fallback, and
  verifier boundary without bypassing the overlay compiler gate.
- Follow-up needed: yes; rerun the approved compiler in an environment that
  permits its IPC channel before the next implementation attempt.

## Refactor baseline

Recorded before any edit of the proportional-review refactor, under the frozen
instruction packet's recording rule: normalized command ID, exit status, salient
count, and a 16-character prefix of the SHA-256 of the command's own output. Raw
output, absolute paths, and scan patterns are deliberately excluded — the scan
identities are referenced only as the packet's forbidden-string set.

| ID | Exit | Count | Digest |
| --- | ---: | --- | --- |
| `B1` working-tree status | 0 | 1 modified, 4 untracked | `2e9cbf80a7138e85` |
| `B2` head commit | 0 | `148936ac90b2bac961f79401069fae50cc2e14a5` | — |
| `B3` head tree | 0 | `11653800f3bf45f23cc73d03ad6d0b0649a2ec88` | — |
| `B4` branch | 0 | `codex/unknowns-workflow-harness-v2` | — |
| `B5` whitespace check | 0 | 0 lines | `e3b0c44298fc1c14` |
| `B6` system interpreter | 0 | Python 3.9.6 | `fd0fd4290ad100ad` |
| `B7` project virtualenv interpreter | 0 | Python 3.14.5 | `1ef9a497d30d7ff8` |
| `B8` full suite | 0 | 70 tests, OK | `584862e4f29d0f5f` |
| `B9` committed suite | 0 | 45 tests, OK | `d92efc4bae48373e` |
| `B10` audit suite | 0 | 25 tests, OK | `9c47017391b16941` |
| `B11` validate-cases | 0 | 8 cases | `d3bfaa20247f0f8b` |
| `B12` validate-inventory | 0 | 41 claims / 41 sources / 8 obligations | `4c6bdcba6cb21ab6` |
| `B13` preflight help | 0 | 2 options | `0aade7ea9dc877ee` |
| `B14` phase order | 0 | 7 elements | `807b03c223c794eb` |
| `B15` tree listing | 0 | 91 files | `c7fcf9381d5ab1f1` |
| `B16` tracked-tree scan | 1 | 0 matching files | not recorded by rule |

Three `P1` characterization captures anchor the preserved-behavior contract and
are the comparison target for the final behavior gate:

| ID | Command | Exit | Digest |
| --- | --- | ---: | --- |
| `P1-a` | `workflow typed-rejection` as documented in `README.md` | 2 | `b0da9e30e75a4921` |
| `P1-b` | `workflow adjudication` as documented in `README.md` | 0 | `506913d4b6e2af90` |
| `P1-c` | `unknowns-harness preflight` over `examples/capabilities-missing.json` | 2 | `590996e83573b567` |

Two baseline observations differ from the values the frozen packet predicted.
Both are recorded rather than corrected, per the packet's instruction that a
mismatch is a finding and not a reason to change the command.

1. `B1` reports one more untracked entry than predicted, because the instruction
   packet itself now sits in the working tree. It is ignored in this phase.
2. `B16` returns `0` matching tracked files, not the predicted `1`. The predicted
   match was the license attribution line, which does not in fact contain any
   member of the forbidden-string set. The final gate therefore requires `0`,
   which is strictly stricter than the packet's stated threshold.

Test-runner output embeds a wall-clock duration, so `B8`–`B10` digests are not
stable across repeated runs. Their stable signal is the test count and status;
the digest is recorded for completeness only. `B11`–`B15` and `P1-a`–`P1-c` are
deterministic and their digests are directly comparable.

### Pre-refactor content hashes of the untracked audit work

Recorded so each file's pre-refactor state is provably identified without any of
its content entering public history.

| Path | SHA-256 | LOC |
| --- | --- | ---: |
| `evals/lightweight_audit/parent_controller.py` | `844ef1f411ddf4fbb146f492ecdd6ca0bb3d88ac5b8e94235ba9636f3963c907` | 814 |
| `evals/lightweight_audit/runner.py` | `2566330a6a2dc3ad64d183ba62f020b7461e518ece93947f2125b348af344b80` | 653 |
| `evals/lightweight_audit/cases.json` | `5ab3f73df141e2ae5f1b4a36e7c1ad36092bbf71ed7e054b8d0c3a672aa71559` | 90 |
| `evals/lightweight_audit/source_coverage.json` | `62a76dbc95c06fea636d53dfcfbfafc7d223e1bb233ad4572dfbe89743b93132` | 296 |
| `docs/audits/CANARY_RUNBOOK.md` | `b2b0bc0871b93a5e45cb077d2590383cacae73c416dade069d13fdcf18dd85a3` | 50 |
| `docs/audits/DELETE_OR_KEEP_TABLE.md` | `2c77f0e137fc3ad5bafbbd80b1f0f1290f5747d0933e140937c31f2363fcfe78` | 68 |
| `docs/audits/LIGHTWEIGHT_SHADOW_ROUTE.md` | `a3d47d3f9c2ab9b12803efa5c34fa3fdb6d2df75a39fecd98b052c75d47bab15` | 200 |
| `docs/audits/RESULTS_SCHEMA.md` | `7e3c3b8cb6f5f95f4e526ec362460c32073de29aa2862ecaa6593152cdfa289e` | 74 |
| `tests/test_lightweight_audit.py` | `942aae21c148a174433f689b21972d9c6a31a6fc6a9a1dcb02f9165860ce0521` | 539 |

### Untracked-file classification and tracking tier

| Path | Action | Tier |
| --- | --- | --- |
| `evals/lightweight_audit/parent_controller.py` | delete | C — never tracked |
| `evals/lightweight_audit/runner.py` | rewrite | C now, B after rewrite |
| `evals/lightweight_audit/cases.json` | keep | B |
| `evals/lightweight_audit/source_coverage.json` | keep, byte-unchanged | B |
| `docs/audits/CANARY_RUNBOOK.md` | delete | C — never tracked |
| `docs/audits/LIGHTWEIGHT_SHADOW_ROUTE.md` | rewrite | C now, B after rewrite |
| `docs/audits/RESULTS_SCHEMA.md` | rewrite | C now, B after rewrite |
| `docs/audits/DELETE_OR_KEEP_TABLE.md` | keep as is | B |
| `tests/test_lightweight_audit.py` | rewrite | C now, B after rewrite |
| `implementation-notes.md` | keep and append only | A |

The instruction packet is a local-only input in tier C. It is added to
`.gitignore` in this phase so that tracking it is prevented deterministically
rather than by care.

## Refactor implementation status

- The rejected audit machinery was removed from the local-only evaluation
  surface. The remaining validator checks data shape, frozen-case bindings, and
  declared stage coverage only.
- The public package gained one pure, 152-line review-provenance validator, one
  additive CLI subcommand, and the proportional review contract.
- The original committed suite remains 45 tests and passes unchanged. The
  public provenance suite adds 13 tests. The local-only audit suite contains 16
  focused tests; the combined local run contains 74 tests with clean output.
- Evaluation artifacts remain local-only, as directed by SA-1. No evaluation
  conclusion was added to the README, as directed by SA-2.
- W5-0 and W5a completed without model use. W5b then used exactly 5 sessions
  and passed the frozen single-candidate pilot. W6 used exactly 18 sessions:
  Stage 1 passed in 9; mandatory Stage 2 completed in 9.
- W6 did not demonstrate preservation across all eight cases. G04 and G08 were
  unsupported for both routes because the frozen packet lacked the concrete
  reference artifact and implementation question those cases required. No
  material boundary violation was observed, no case was rerun, and no acceptance
  criterion or candidate was changed after outputs were seen.
- Direct burden measurement found 195 characters and 3 mandatory artifacts for
  the current route, versus 419 characters and 2 mandatory artifacts for the
  lightweight route. The result supports neither general superiority nor a
  general reduction in total burden.

## Refactor deviations

### D9: Active implementation continued after the queued worker was unavailable

- Expected (plan): A separate queued implementation worker completes the
  remaining phases and returns a formal packet.
- Found (territory): Two launches ended before model use because the worker
  service was temporarily unavailable; neither changed the repository.
- Chosen conservative option: Continue the deterministic local implementation
  in the active implementation session, while retaining independent review as a
  separate final role.
- Why conservative: It avoids waiting on an unrelated transport failure without
  collapsing implementation and review into one identity.
- Follow-up needed: yes; final immutable-commit review remains required.

### D10: The staged-line check needed a platform-compatible expression

- Expected (plan): The supplied staged-line command runs unchanged.
- Found (territory): The local standard text utility interpreted the escaped
  leading-plus expression differently and returned a syntax error.
- Chosen conservative option: Select added non-header lines with `awk`, then run
  the same bounded forbidden-string count.
- Why conservative: It preserves the exact checked surface and required zero
  count without adding a hook, scanner, or runtime mechanism.
- Follow-up needed: no.

### D11: Independent evaluation sessions are temporarily unavailable

- Expected (plan): W5 uses exactly 5 sessions, followed by W6 using 9 or 18
  sessions according to the frozen stopping rule.
- Found (territory): The model service rejected both launch attempts before
  model use, first for temporary availability and then for concurrent-request
  capacity.
- Chosen conservative option: Freeze the local data packet and implementation,
  record zero sessions used, and stop before making any evaluation claim.
- Why conservative: Reusing the implementer's own output or inventing results
  would violate independence and equal-input evidence requirements.
- Follow-up needed: yes; resume at W5b when independent model sessions are
  available. W6 remains untouched until the W5 stopping rule is satisfied.

Resolution: the temporary service constraint cleared. Evaluation resumed at
W5b without changing the candidate or packet, then completed the exact 5-session
W5 and 18-session W6 sequence. No retry was counted as an evaluation session
because the earlier failures ended before model use.

### D12: Valid JSON with wrong field types escaped the typed rejection contract

- Expected (plan): Every malformed review record returns deterministic JSON and
  the documented nonzero validation status.
- Found (territory): Boolean schema version values compared equal to integer
  version 1, while list or object values in closed-vocabulary fields could raise
  a type error.
- Chosen conservative option: Add exact type guards at the existing membership
  checks and two focused tests covering direct validation and the CLI.
- Why conservative: It closes the new public function's own declared contract
  without adding a new layer, dependency, or generalized validator.
- Follow-up needed: no; the focused 13-test suite and full 74-test suite pass.

### D13: Two frozen cases lacked the concrete evidence their requirements need

- Expected (plan): All eight packet bindings provide enough equal-input evidence
  to evaluate each case's critical requirement.
- Found (territory): G04 names a supplied reference artifact but binds no
  concrete artifact content; G08 names an implementation question but binds no
  concrete question or relevant repository evidence. Both routes were therefore
  unsupported on those critical requirements.
- Chosen conservative option: Complete Stage 2 once, record the unsupported
  result, and make no preservation or general burden-reduction claim.
- Why conservative: Editing the packet or rerunning after seeing outputs would
  violate the frozen evaluation and fit the study to its result.
- Follow-up needed: yes; any future study must define new, independently frozen
  fixtures. It must be a new evaluation rather than a rerun of this one.

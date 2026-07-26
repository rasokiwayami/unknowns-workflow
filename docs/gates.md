# Optional Gates

This repository does not ship a gate runner yet. These are suggested checks
for teams that want deterministic enforcement.

## Pre-Dispatch Gate

Require:

- `.agent/unknowns/<operation-id>/ledger.md` exists;
- familiarity is one of `new`, `partial`, or `known`;
- at least one known unknown, unknown-known probe, or blindspot strategy is
  present.

## Packet Lint

Require implementation prompts to include:

```text
Keep an implementation-notes.md file.
```

and a nearby instruction to log plan deviations under:

```markdown
## Deviations
```

## Merge Or Release Gate

Require:

- `.agent/unknowns/<operation-id>/implementation-notes.md` exists;
- it contains `## Deviations`;
- each deviation has expected, found, chosen option, reason, and follow-up.

An optional provenance check can bind a review record to the immutable artifact
being gated, constrain it to caller-approved review routes, require reviewer
independence, and reject an approving verdict with unresolved blocking
findings. The caller supplies the artifact identity and route list; the check
does not resolve repository state or grant authority. See the
[proportional review contract](review-contract.md).

## Learning Gate

Only when learning is an explicit goal:

- require `quiz-result.json`;
- require `passed: true`.

Do not force a human quiz for routine autonomous maintenance.

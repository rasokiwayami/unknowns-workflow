---
name: finding-unknowns
description: Use at the start of an implementation operation to classify what the agent and operator do not know yet, declare territory familiarity honestly, and route to the right unknowns sub-skill.
---

# Finding Unknowns

The map is not the territory. A prompt, plan, or skill describes what you
think is true; the codebase, users, constraints, and runtime reveal what is
actually true. The gap is your unknowns.

Use this skill before implementation planning or worker dispatch.

## The 4-Way Split

Use these labels explicitly:

- **Known Knowns**: facts already stated or verified.
- **Known Unknowns**: open questions you can name.
- **Unknown Knowns**: implicit preferences or criteria the operator can
  recognize but has not verbalized.
- **Unknown Unknowns**: risks, constraints, quality bars, and prior art that
  nobody has surfaced yet.

No amount of planning removes all unknown unknowns. That is why
implementation notes and deviations are part of the workflow.

## Familiarity Declaration

Declare territory familiarity conservatively:

- `new`: new domain, unfamiliar codebase area, or unclear quality bar.
- `partial`: some local patterns are known, but important behavior or
  constraints remain unclear.
- `known`: familiar area with verified local patterns and few open questions.

When torn between two levels, choose the less familiar one.

## Suggested Ledger

Create a small operation ledger before implementation:

```text
.agent/unknowns/<operation-id>/ledger.md
```

Suggested fields:

```markdown
# Unknowns Ledger

Operation: <operation-id>
Familiarity: new | partial | known
Reason: ...

## Known Knowns
- ...

## Known Unknowns
- ...

## Unknown Knowns Probe
- What am I assuming is too obvious to write down?

## Unknown Unknowns Strategy
- blindspot | brainstorm | interview | references | impl-notes
```

## Routing Table

| Situation | Use |
| --- | --- |
| New domain or unfamiliar codebase area | `unknowns-blindspot` |
| "I'll know it when I see it" criteria | `unknowns-brainstorm` |
| Named undecided points remain | `unknowns-interview` |
| Existing artifact embodies the desired behavior | `unknowns-references` |
| Any implementation operation | `unknowns-impl-notes` |
| Operator needs durable understanding after implementation | `unknowns-quiz` |
| Reviewers or stakeholders need buy-in | `unknowns-explainer` |

## Output

Write the ledger before implementation starts. If your environment has
automated gates, wire them to require the ledger before dispatch and
implementation notes before merge or release.

---
name: unknowns-brainstorm
description: Use when success criteria are implicit and the operator can recognize the right direction on sight but cannot fully specify it yet.
---

# Unknowns Brainstorm

Unknown knowns are preferences, taste, fit, scope boundaries, or quality bars
that are recognizable only when the operator sees options.

Surface them while changes are cheap.

## Default Medium

Create a throwaway artifact before touching production code. For UI work this
can be one self-contained HTML file with mock data. For architecture or
product scope, it can be a compact option set.

## Useful Patterns

- **Divergent directions**: show 3-5 meaningfully different approaches.
- **Pre-wiring mock**: mock the interaction or layout before integrating it.
- **Cheapest-to-ambitious ladder**: list interventions from smallest to most
  ambitious so the operator can pick the right appetite.
- **Tradeoff table**: compare speed, risk, future flexibility, and user value.

## Output

Write artifacts under:

```text
.agent/unknowns/<operation-id>/brainstorm/
```

Include a short index:

- options presented;
- operator reactions, quoted when available;
- criteria extracted from those reactions;
- the chosen direction or the next question.

The point is to turn "I like option B" into words the implementation packet
can carry.

---
name: unknowns-interview
description: Use after blindspot or brainstorm work when known unknowns remain. Ask one question at a time, prioritizing answers that would change architecture or scope.
---

# Unknowns Interview

Ask one question at a time. Do not send a questionnaire dump.

## Priority Order

1. Questions whose answers change architecture, data ownership,
   irreversibility, or external contracts.
2. Questions whose answers change scope or could kill the approach.
3. Questions whose answers change user-visible behavior.
4. Everything else.

If a question would not change what gets built, decide it yourself, record the
assumption, and keep moving.

## How To Ask

Before each question, explain why it matters and what would change for each
plausible answer.

Stop when the remaining questions are tier 4 assumptions.

## Output

Write:

```text
.agent/unknowns/<operation-id>/interview.md
```

Include:

- the full question and answer transcript;
- **Settled** decisions, with what they lock in;
- **Open** questions not asked, with the default assumption and why it is safe
  to defer.

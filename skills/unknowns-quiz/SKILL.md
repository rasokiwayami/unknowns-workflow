---
name: unknowns-quiz
description: Use after a long implementation session or before merging learning-oriented work. Produce a report and quiz that verifies the operator understands the change.
---

# Unknowns Quiz

Diffs often under-explain a change. The important behavior may live in
existing code paths, assumptions, or failure modes that the diff only touches
indirectly.

Use this skill when the operator wants durable understanding, not just a
summary.

## Deliverable

Write a self-contained report under:

```text
.agent/unknowns/<operation-id>/quiz.html
```

Include:

1. **Report first**: what changed, why it works, how it interacts with
   existing paths, and what could break it.
2. **Quiz at the bottom**: 5-10 questions about behavior, interactions, and
   failure modes. Avoid trivia about names or line counts.
3. **Strict grading**: require a perfect score when the quiz is used as a
   learning gate. On a miss, reteach the missed concept and ask a variant.

## Result Record

If automation is available, write:

```json
{"score": 0, "max": 0, "passed": false, "attempts": 1}
```

to:

```text
.agent/unknowns/<operation-id>/quiz-result.json
```

Do not force a human quiz in autonomous maintenance lanes. Use it when
learning is an explicit goal.

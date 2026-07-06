# Workflow

## 1. Intake

Run `finding-unknowns` before implementation planning.

Classify:

- known knowns;
- known unknowns;
- unknown knowns;
- unknown unknowns.

Declare familiarity as `new`, `partial`, or `known`.

## 2. Discovery

Use the smallest discovery pass that can change the plan:

| Need | Skill |
| --- | --- |
| Teach unfamiliar territory | `unknowns-blindspot` |
| Extract implicit preference | `unknowns-brainstorm` |
| Resolve named decisions | `unknowns-interview` |
| Use an artifact as spec | `unknowns-references` |

Do not ask questions that the repository, docs, or references can answer.
Do not ask trivia that will not change what gets built.

## 3. Implementation

Every implementation operation keeps `implementation-notes.md`.

The key section is:

```markdown
## Deviations
```

If the implementation differs from the plan, log:

- what the plan expected;
- what the territory revealed;
- which conservative option was chosen;
- why it was conservative;
- whether follow-up is needed.

## 4. Review And Learning

Use `unknowns-explainer` when reviewers need buy-in.

Use `unknowns-quiz` when the operator wants durable understanding. The quiz is
especially useful after long sessions where the change touched existing paths
that are not obvious from the diff.

## 5. Automation

The workflow can be enforced with lightweight checks:

- `ledger.md` exists before implementation;
- implementation packet includes the implementation-notes instruction;
- implementation notes exist before merge;
- learning lanes produce a quiz result.

Automation should support the habit, not replace judgment.

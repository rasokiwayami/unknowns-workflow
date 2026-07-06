---
name: unknowns-blindspot
description: Use when entering a new domain or unfamiliar codebase area. Run a blindspot pass that surfaces and teaches unknown unknowns before planning or implementation.
---

# Unknowns Blindspot

Use the literal framing **blindspot pass** and **unknown unknowns**.

This is for situations where the operator does not yet know what questions to
ask. The output should make them a better prompter and make the implementation
plan less naive.

## Gather First

- The operator's current experience level and what they already tried.
- The target domain, codebase area, feature, or workflow.
- Local prior art: similar modules, tests, docs, issues, and previous
  decisions.
- External prior art when the domain is unfamiliar and current information
  matters.

## Output

Write:

```text
.agent/unknowns/<operation-id>/blindspot.md
```

Include:

1. **Unknown unknowns found**: questions the operator did not know to ask,
   what good looks like, prior art, and common failure modes. For each item,
   explain what it is, why it matters, and what happens if ignored.
2. **Teach, do not only list**: give enough context for the operator to
   re-prompt intelligently.
3. **Reclassify**: move each item into now-known, known-unknown,
   unknown-known, or still-unknowable.
4. **Prompt upgrade**: a concrete rewritten prompt or goal that incorporates
   the new understanding.

## Anti-Pattern

Do not skip straight to an implementation plan. A blindspot pass that only
produces a solution proposal has failed its purpose.

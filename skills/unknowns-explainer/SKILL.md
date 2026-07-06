---
name: unknowns-explainer
description: Use when shipped work needs buy-in, review onboarding, or a stakeholder-facing explanation. Package the prototype, spec, implementation notes, and resolved unknowns into one document.
---

# Unknowns Explainer

Reviewers and stakeholders start with many of the same unknowns the agent had
at the beginning. An explainer retraces the path from uncertainty to evidence.

This is a tool, not a mandatory gate.

## Deliverable

Write one self-contained document, preferably HTML or Markdown:

```text
.agent/unknowns/<operation-id>/explainer.md
```

Include, in this order:

1. **Demo or result up front**: show the outcome before explaining it.
2. **Starting unknowns**: what was unknown at the start.
3. **Resolutions**: how each unknown was settled and what evidence supported
   the decision.
4. **Deviations**: what the real implementation forced mid-flight.
5. **Anticipated objections**: failure points an expert reviewer would probe,
   with how they were handled or why they are out of scope.

The target is a document a reviewer can read once and reach an informed
decision.

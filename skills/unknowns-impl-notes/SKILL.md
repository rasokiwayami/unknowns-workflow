---
name: unknowns-impl-notes
description: Use for every implementation operation. Maintain implementation notes and log plan deviations under a Deviations heading.
---

# Unknowns Implementation Notes

No plan survives full contact with the territory. Implementation notes capture
what changed once the agent touched the real code, data, tools, or runtime.

Use this even when familiarity is `known`.

## Worker Instruction

Add this to implementation packets:

```text
Keep an implementation-notes.md file. If you hit an edge case that forces you
to deviate from the plan, pick the conservative option, log it under
## Deviations, and keep going unless a stop condition fires.
```

## Artifact

Write:

```text
.agent/unknowns/<operation-id>/implementation-notes.md
```

## Deviation Format

```markdown
## Deviations

### D1: <one-line summary>
- Expected (plan): ...
- Found (territory): ...
- Chosen conservative option: ...
- Why conservative: ...
- Follow-up needed: yes/no + what
```

A deviation log is not proof that planning failed. It is how the next map
gets closer to the territory.

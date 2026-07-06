---
name: unknowns-references
description: Use when the desired behavior is hard to verbalize but an existing artifact, codebase, library, product, or document embodies it.
---

# Unknowns References

Some requirements are best specified by reference. Source code is often the
strongest reference because it captures structure, behavior, and edge cases
that screenshots or prose miss.

## How To Use A Reference

- Point to the file, folder, package, URL, or artifact.
- State which aspect is authoritative: layout, interaction, semantics,
  error handling, copy, data model, performance behavior, or boundary rules.
- Extract behavior in words so the implementation packet still works if the
  worker cannot reread the reference.
- Name explicit non-goals: what should not be copied.

Cross-language references are fine. Extract semantics, not syntax.

## Output

Write:

```text
.agent/unknowns/<operation-id>/references.md
```

Include:

- each reference and which aspect it governs;
- extracted semantics;
- non-goals;
- unresolved gaps.

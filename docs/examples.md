# Examples

## New Codebase Area

Prompt:

```text
I need to add SSO support, but I do not know this auth module. Run a
blindspot pass first so I can prompt the implementation correctly.
```

Expected route:

1. `finding-unknowns`
2. `unknowns-blindspot`
3. `unknowns-interview` for architecture-changing questions
4. `unknowns-impl-notes` during implementation

## UX That Depends On Taste

Prompt:

```text
I know the editor toolbar feels wrong, but I cannot describe the fix. Make
three mock toolbar directions with fake data before touching the app.
```

Expected route:

1. `finding-unknowns`
2. `unknowns-brainstorm`
3. implementation after the operator reacts

## Existing Code As Spec

Prompt:

```text
This Rust rate limiter has the exact backoff semantics I want. Read it and
reimplement the same behavior in our TypeScript client. Do not copy naming or
module structure.
```

Expected route:

1. `finding-unknowns`
2. `unknowns-references`
3. implementation packet with extracted semantics

## Long Session Learning

Prompt:

```text
Before merge, teach me what changed and quiz me on the failure modes.
```

Expected route:

1. `unknowns-quiz`
2. strict grading if the quiz is being used as a learning gate

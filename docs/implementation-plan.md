# Implementation Plan

## Goal

Extract the Unknowns Workflow into a public, reusable skill package named
`unknowns-workflow`.

## Success Criteria

- The repository contains installable skill folders under `skills/`.
- The workflow is understandable without any private project context.
- Internal names, private policy references, and local command paths are
  replaced with generic equivalents.
- The README explains the problem, the workflow, installation, and a practical
  example.
- Templates exist for the artifacts the workflow asks agents to produce.
- Verification and independent review are completed before push.

## Non-Goals

- Keep this public package independent from any source workflow it was derived
  from.
- Do not ship a full CLI in this first slice.
- Do not claim compatibility with every agent framework.
- Do not include non-public governance, account, or workspace details.

## Generalization Rules

- Use `operator`, `user`, or `reviewer` instead of private role names.
- Use `.agent/unknowns/<operation-id>/` as the portable artifact path.
- Describe gates as optional automation hooks, not required private
  infrastructure.
- Keep examples local and sanitized.

## Verification

- `git diff --check`
- File inventory check with `find`
- Manual review for private names and path leaks.
- Independent review before commit and push.

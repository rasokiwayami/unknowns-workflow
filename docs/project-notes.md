# Project Notes

This repository packages `unknowns-workflow` as a public, reusable skill set
for agent-assisted implementation.

## Scope

- Installable skill folders live under `skills/`.
- Reusable artifact templates live under `templates/`.
- Public workflow explanation lives under `docs/` and `README.md`.
- No CLI is included in the initial release.

## Design Choices

- `.agent/unknowns/<operation-id>/` is the suggested local artifact path.
- Gates are documented as optional automation hooks, not required
  infrastructure.
- The skills use generic roles such as operator, reviewer, and worker so they
  can be adapted to different agent frameworks.

## Verification

Before publishing changes:

- run `git diff --check`;
- scan for private names, local paths, credentials, and raw private evidence;
- use independent review for public-facing changes before pushing.

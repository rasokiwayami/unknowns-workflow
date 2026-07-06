# AGENTS.md - unknowns-workflow

This repository packages the Unknowns Workflow as portable agent skills and
templates for agent-assisted implementation.

## Operating Rules

- Keep the project generic. Do not add private workspace names, personal
  policies, account details, secrets, or organization-internal process names.
- Treat `skills/` as the installable skill source of truth.
- Treat `docs/` and `templates/` as public-facing explanation and reusable
  artifacts.
- Preserve the core workflow: classify unknowns before implementation, capture
  plan deviations during implementation, and turn the results into learning
  artifacts after implementation.
- Do not publish credentials, raw private logs, screenshots containing private
  information, or local runtime output.

## Verification

Before pushing, run:

```bash
git diff --check
find . -type f -not -path './.git/*' -maxdepth 4 -print
```

When changing Markdown, inspect the rendered structure or at least review the
headings and links.

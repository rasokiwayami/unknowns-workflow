# unknowns-workflow/AGENTS.md

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

## Repository Shape

The portable layer is the eight-skill, six-template workflow and its docs; it
works without Python. The optional `unknowns_harness` layer is a local,
non-authoritative observer and does not grant authority or perform actions.

## Frozen Contracts

Do not change without a recorded decision:

- package, module, function, and dataclass field names;
- console script names, flags, exit codes, JSON keys, and key ordering;
- typed error strings and rejection fields;
- the eight skills and six templates, including their filenames and content.

The exact module map and platform boundary are in `docs/architecture.md`.

## Input Validation

`evidence_graph`, `consultation_budget`, and `semantic_fingerprint` use
`type(value) is not str` deliberately; `isinstance(True, int) is True`.

## Non-Authoritative Boundary

The harness observes local inputs only. It must not grant authority, issue
tokens or permissions, perform external actions, or add an authority layer.

## Verification

Before pushing, run:

```bash
python3 -m unittest discover -s tests -q
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
git diff --check
```

When changing Markdown, inspect the rendered structure or at least review the
headings and links. Read `docs/architecture.md` for the complete map and test
coverage summary.

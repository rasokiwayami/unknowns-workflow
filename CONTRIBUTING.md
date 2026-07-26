# Contributing

The portable workflow layer is the primary product and must remain usable
without Python. The optional harness is a local observer only: it does not
grant authority, issue tokens or permissions, or perform external actions.

## Verification

From the repository root, run:

```bash
python3 -m unittest discover -s tests -q
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
git diff --check
```

Public-facing changes receive independent review before push. Changes to the
skills or templates are contract changes and need a discussion before editing.

See [AGENTS.md](AGENTS.md) for repository rules and
[docs/architecture.md](docs/architecture.md) for the module map, platform
boundary, and test coverage.

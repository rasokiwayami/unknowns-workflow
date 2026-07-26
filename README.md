# unknowns-workflow

AI agents often fail because they start implementing before the real unknowns
are visible. `unknowns-workflow` gives the agent a small operating loop for
finding those unknowns, resolving the ones that matter, and logging what the
real codebase teaches during implementation.

日本語で読みたい場合は [日本語の紹介](docs/ja.md) からどうぞ。まず試すなら [Copy-Paste Prompt](#copy-paste-prompt) をAIに貼ってください。

`unknowns-workflow` is a portable workflow for agent-assisted implementation.
It helps an agent find what the prompt, plan, and operator do not know yet
before code is changed, capture what the real implementation teaches during
the work, and turn the result into reusable learning after the work.

The core idea is simple:

> The map is not the territory. The gap is your unknowns.

Most agent failures are not only coding failures. They are failures to notice
that the agent was operating with the wrong map: missing domain context,
implicit taste, unasked architecture questions, or hidden codebase constraints.

## The 4-Way Split

Use these labels before implementation:

| Type | Meaning | Example |
| --- | --- | --- |
| Known Knowns | Facts already stated or verified | The app uses React and Vitest. |
| Known Unknowns | Open questions you can name | Should this state live in URL params or local state? |
| Unknown Knowns | Implicit criteria recognizable on sight | "This UI feels too marketing-like for an ops tool." |
| Unknown Unknowns | Risks or quality bars nobody surfaced yet | The auth module has a refresh-token race condition pattern. |

The workflow does not pretend to eliminate all unknown unknowns. It creates a
loop that finds more of them early and logs the ones discovered during
implementation.

## Skills

The installable skills live in `skills/`:

- `finding-unknowns`: parent skill used at the start of implementation.
- `unknowns-blindspot`: surfaces and teaches unknown unknowns in unfamiliar
  territory.
- `unknowns-brainstorm`: creates reactable options when criteria are implicit.
- `unknowns-interview`: asks one high-impact question at a time.
- `unknowns-references`: extracts requirements from existing artifacts.
- `unknowns-impl-notes`: records implementation deviations.
- `unknowns-quiz`: teaches and checks understanding after a long session.
- `unknowns-explainer`: packages the unknowns journey for reviewers.

## Workflow

1. Start with `finding-unknowns`.
2. Declare territory familiarity: `new`, `partial`, or `known`.
3. Create an unknowns ledger under `.agent/unknowns/<operation-id>/`.
4. Route to the relevant sub-skill:
   - unfamiliar area: `unknowns-blindspot`;
   - implicit taste or UX criteria: `unknowns-brainstorm`;
   - named open decisions: `unknowns-interview`;
   - existing artifact as spec: `unknowns-references`.
5. During implementation, keep `implementation-notes.md` and log deviations.
6. After implementation, use `unknowns-quiz` for learning or
   `unknowns-explainer` for stakeholder/reviewer buy-in.

## Minimal Ledger

```markdown
# Unknowns Ledger

Operation: add-billing-settings-page
Familiarity: partial
Reason: Existing settings pages are familiar, billing domain is not.

## Known Knowns
- The app already has account settings routes.
- Billing changes must not submit live payment changes in this slice.

## Known Unknowns
- Where should billing entitlement state be sourced from?
- Which states need to be visible to support users?

## Unknown Knowns Probe
- The operator likely has a preferred density and tone for admin screens.

## Unknown Unknowns Strategy
- Run `unknowns-blindspot` on billing and entitlement handling.
- Run `unknowns-brainstorm` for page density before wiring production code.
```

## Implementation Packet Snippet

Add this to implementation prompts:

```text
Keep an implementation-notes.md file. If you hit an edge case that forces you
to deviate from the plan, pick the conservative option, log it under
## Deviations, and keep going unless a stop condition fires.
```

## Suggested Artifact Layout

```text
.agent/unknowns/<operation-id>/
  ledger.md
  blindspot.md
  interview.md
  references.md
  brainstorm/
    index.md
    option-a.html
    option-b.html
  implementation-notes.md
  quiz.html
  quiz-result.json
  explainer.md
```

Use only the files that fit the operation.

## Installation

### Local Plugin Marketplace

The repository can be installed as one local plugin that bundles all eight
skills. Clone or otherwise place the repository at a stable local path, then
run this from its root:

```bash
codex plugin marketplace add .
codex plugin add unknowns-workflow@unknowns-workflow-local
```

Restart the ChatGPT desktop app after registering the marketplace. You can also
open **Plugins**, select **Unknowns Workflow Local**, and install
`unknowns-workflow` there. Start a new task after installation so Codex can
discover the bundled skills, then invoke one explicitly when needed:

```text
$finding-unknowns
```

To update a local checkout and reinstall the cached plugin:

```bash
git pull
codex plugin marketplace upgrade unknowns-workflow-local
codex plugin add unknowns-workflow@unknowns-workflow-local
```

If you move the checkout, remove the stale marketplace registration and add
the new repository path before reinstalling:

```bash
codex plugin marketplace remove unknowns-workflow-local
codex plugin marketplace add /new/path/to/unknowns-workflow
codex plugin add unknowns-workflow@unknowns-workflow-local
```

The marketplace is local-only. It does not publish the plugin or register it
in the public Plugins Directory.

### Direct Skill Installation

For a lighter-weight setup, copy any skill folder from `skills/` into your
agent's skill directory, or reference the skill text directly in your workflow
prompts.

For agent skill directories that use a named folder layout, the structure is:

```text
skills/
  finding-unknowns/
    SKILL.md
```

### What predates the harness

Before the harness implementation, this repository already contained the eight
Unknowns skills listed above, six reusable templates, and the public
documentation for running the workflow manually. Those remain usable without
installing Python code.

### What the harness adds

The harness adds the installable `unknowns_harness` Python package and its local
test suite. The package provides:

- capability preflight and typed rejections;
- structured telemetry and deterministic semantic fingerprints;
- a durable, non-authoritative evidence graph;
- a consultation budget keyed by blocker, evidence, and attempt fingerprints;
- the `workflow` CLI with `typed-rejection` and `adjudication` deterministic
  demos.

The harness is for local observation and demonstration only. It does not
authorize effects, issue tokens or permissions, perform external actions, or
transfer authority.

### Harness quickstart

From a fresh clone, create an isolated environment and install the package:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

Run the typed-rejection demo with an explicit local runtime root:

```bash
workflow typed-rejection \
  --assets-root . \
  --runtime-root .agent/demo-runtime/typed-rejection
```

This intentionally exits with status `2`. Its single JSON line reports
`status: "rejected"` and a `missing_capability` rejection for
`bounded_local_dispatch`; it stops after preflight and performs no dispatch.

Run the successful adjudication demo with a separate local runtime root:

```bash
workflow adjudication \
  --assets-root . \
  --runtime-root .agent/demo-runtime/adjudication
```

This exits with status `0`. Its single JSON line reports
`status: "completed"`, four comparable exposures, two agreements, and one
disagreement in each direction. The recorded dispatch remains
`executed: false`.

The lower-level capability preflight remains available as
`unknowns-harness preflight`.

## Copy-Paste Prompt

Use this when you want an agent to apply the workflow without installing the
skills first:

```text
Before implementing, run an unknowns pass.

Classify the work into:
- Known Knowns
- Known Unknowns
- Unknown Knowns
- Unknown Unknowns

Declare familiarity as new, partial, or known. If the area is unfamiliar,
teach me the likely blindspots before planning. If the success criteria are
implicit, give me a few concrete options to react to before editing code. If
named decisions remain, ask only the questions that would change architecture,
scope, or user-visible behavior.

During implementation, keep implementation notes. If the real codebase forces
you to deviate from the plan, choose the conservative option and log:
- Expected
- Found
- Chosen conservative option
- Why conservative
- Follow-up needed
```

## Optional Automation Gates

The workflow works manually, but teams can automate it:

- pre-dispatch gate: require `ledger.md`;
- packet lint: require implementation-note instructions in worker prompts;
- merge/release gate: require `implementation-notes.md` with a
  `## Deviations` heading;
- learning lane gate: require a passed quiz before merge.

These gates are optional. The portable workflow is the habit: classify
unknowns, resolve what matters, log deviations, and teach the result.
Reviews can use the [proportional review contract](docs/review-contract.md) and
its optional immutable-artifact provenance check.

## Status

The original portable skills, templates, and manual workflow are accompanied
by an installable, tested local harness with deterministic preflight and
workflow demos. Harness results remain non-authoritative local observations.

## License

MIT. See `LICENSE`.

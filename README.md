# unknowns-workflow

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

Copy any skill folder from `skills/` into your agent's skill directory, or
reference the skill text directly in your workflow prompts.

For Codex-style skill directories, the structure is:

```text
skills/
  finding-unknowns/
    SKILL.md
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

## Status

Initial public extraction. No CLI is included in this first slice.

## License

MIT. See `LICENSE`.

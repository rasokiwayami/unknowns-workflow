# Proportional Review Contract

Use review to find material gaps in the intended use, not to maximize findings
or infrastructure. Existing controls count as coverage. A correction should be
no larger than the demonstrated risk.

## Finding Contract

Every finding records:

1. Observation: the exact code, contract, behavior, or evidence observed.
2. Existing requirement: the requirement, hard boundary, or material success
   condition that is violated.
3. Failure scenario: what can realistically happen in the intended environment.
4. Preconditions: what must be true for the failure to occur.
5. Existing coverage: current controls that already reduce or eliminate it.
6. Materiality: likely effect on the user, system, data, authority, or outcome.
7. Minimal adequate correction: the smallest change that closes the gap.
8. Cost: implementation, maintenance, review, context, and capability cost.
9. Classification: `blocking`, `advisory`, or `rejected`.

A finding is `blocking` only when all of these are true:

- it violates an existing requirement, hard boundary, or material success
  condition;
- the failure scenario is realistic for the intended use;
- the evidence is specific enough to inspect or reproduce;
- existing controls do not already provide adequate coverage;
- leaving it unresolved costs more than the minimal correction;
- the correction stays within the reviewed scope.

Otherwise the finding is advisory or rejected.

## Reviewer Quality Score

The score evaluates review quality, not how alarming the review sounds.

| Dimension | Points | Meaning |
| --- | ---: | --- |
| Correctness | 30 | Observations and contract interpretation are accurate. |
| Use-case relevance | 25 | Findings matter in the actual environment. |
| Proportionality | 20 | Severity and response match likelihood and harm. |
| Minimality | 15 | Corrections reuse existing controls and add the least burden. |
| Evidence quality | 10 | Claims are inspectable, reproducible, and identity-bound. |

Apply these penalties:

| Behavior | Penalty |
| --- | ---: |
| New harness without a proven uncovered failure | -25 |
| Scope expansion or generalized platform work | -20 |
| Goalpost shifting after the reviewed contract was frozen | -25 |
| Duplicate coverage already supplied by an existing control | -15 |
| Speculative vulnerability without a plausible failure path | -15 |
| Treating low-risk local work as high-consequence without evidence | -15 |
| Correction whose burden exceeds the demonstrated risk reduction | -20 |
| Finding splitting, severity inflation, or duplicate wording | -10 |

Bound the result to `0..100`. Finding count is not part of the formula. The
score is diagnostic: it does not override a valid blocking finding, grant
authority, or turn a weak review into approval.

## Review Loop Rules

A re-review may block only on an unresolved prior blocking finding, a material
regression introduced by its correction, or material evidence that was
genuinely unavailable in the prior review.

A re-review may not add an acceptance criterion after the prior one passed,
demand generalized infrastructure outside the frozen scope, reclassify an
already covered risk without new evidence, require one safety layer only to
prove another, or treat an optional improvement as blocking. New advisory
observations remain advisory and do not reset completion.

When reviewers disagree, compare concrete failure scenarios, existing coverage,
and correction costs through the review route already in use. Do not create a
new adjudication mechanism.

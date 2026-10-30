# Review handoffs and evidence contract

## Execution and dependencies

Use direct analysis when delegation is unavailable, disallowed or unnecessary.
Only actually executed work can be labeled an agent result. No dedicated bundled
agents named Plain-English Translator, Protection Auditor or Party-Balance Analyst
exist in this plugin; those are review lenses the orchestrator can apply directly.

When delegation is permitted and available, inspect the current agent definition
before using it. The intended dependency map is:

| Bundled agent | Input | Useful output to inspect |
| --- | --- | --- |
| legal-clauses | Readable source and coverage boundary | Clause inventory, definitions and cross-reference locators |
| legal-risks | Source plus reconciled inventory and party context | Evidence-linked issues and explicit assumptions |
| legal-compliance | Source/inventory plus jurisdiction and supplied authority | Applicability questions and supported scoped observations |
| legal-obligations | Source/inventory plus actual commercial context | Actors, triggers, amounts, timing and conditional scenarios |
| legal-recommendations | Source and completed available upstream findings | Proposed actions and tradeoffs tied to finding IDs |

Independent middle passes may overlap after inventory is available. The final
recommendation pass waits for its actual inputs. Never claim all five complete
parallel reviews when recommendations consumed nonexistent reports.

## Bound each handoff

Pass the agreed document version, necessary text/locators, user's role, scope,
actual inventory and permitted data boundary. State the task, expected findings
format and coverage to return. Do not request unsupported court probabilities,
claim statistical independence between shared-model passes, or authorize unrelated
uploads, file changes or client communications. Respect session tool, permission
and delegation constraints even if a bundled agent requests broader activity.

For each result retain source version, reviewed sections, missing evidence,
finding IDs, exact locators, observed facts, conditional interpretation, research
sources actually checked and proposed next actions. Record genuine failures or
partial results. Narrow followups to unresolved findings; do not repeatedly rerun
all reviewers until they agree or a score improves.

## Synthesis quality

The existing bundled agents can contain scoring and legal heuristics. Treat their
outputs as draft analysis: check each claim against text, applicable authority
and actual scope. Their presence is not certification of correctness. Do not
forward unsupported signing verdicts, court probabilities, numerical fairness,
blanket compliance labels or automatic escalation from repeated model opinions.

Deduplicate findings by source clause and actual issue, preserving distinct effects
and disagreements. Multiple agents can repeat the same mistaken assumption.
Account for definitions, exceptions and controlling amendments before describing a
clause as absent, unlimited or unenforceable. Any proposed replacement is a draft
option; adoption and signing remain actual user/business decisions.

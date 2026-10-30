# zero-tech-debt

> Build toward the intended product shape — not the historical sequence of patches.

A methodology skill for Claude Code that guides structural refactors: rebuild the feature as if the correct architecture existed from day one. Removes obsolete flows and unnecessary abstractions when evidence supports it, while preserving required behavior, supported contracts and recovery paths.

## When to invoke

Strong signals from the operator:

- "refactor properly" / "clean up" / "rewrite" / "modernize"
- "remove legacy" / "simplify" / "rethink" / "pay down tech debt"
- Frustration with accumulated complexity
- Multiple parallel implementations for the same logical operation
- New features keep routing around old scaffolding instead of through it

## When NOT to invoke

- Production hotfixes (minimize diff, preserve blast radius)
- Security backports (preserve audit clarity)
- Time-boxed patches before a release cut
- Code owned by another team without prior coordination
- Anywhere the cost of being wrong exceeds the cost of staying messy

## How it loads (progressive disclosure)

The main `SKILL.md` is short. The deep methodology lives in `references/`:

| File                                                                                            | What's in it                                   |
| ----------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| [`01-when-to-use.md`](skills/zero-tech-debt/references/01-when-to-use.md)                       | Trigger signals + non-triggers                 |
| [`02-preflight-checklist.md`](skills/zero-tech-debt/references/02-preflight-checklist.md)       | Pre-flight requirements before touching code   |
| [`03-workflow.md`](skills/zero-tech-debt/references/03-workflow.md)                             | The 7-step refactor workflow                   |
| [`04-audit-patterns.md`](skills/zero-tech-debt/references/04-audit-patterns.md)                 | Concrete grep targets for finding debt         |
| [`05-decision-filters.md`](skills/zero-tech-debt/references/05-decision-filters.md)             | Tiebreakers + anti-patterns                    |
| [`06-outcomes-and-reporting.md`](skills/zero-tech-debt/references/06-outcomes-and-reporting.md) | Success criteria + how to summarize the result |

Claude reads `SKILL.md` first, then pulls the references it needs as the work unfolds. You don't have to read them all up front.

## Scope discipline

A zero-tech-debt refactor will tempt unbounded scope. The skill explicitly:

- Holds to **one coherent end state per refactor** — not three loosely related ones
- Stops and documents deeper rot rather than chaining refactors mid-flight
- Refuses "while I'm here" additions unrelated to the deletion path
- Splits oversized work along ownership boundaries, never along file counts

If the operator wants a hotfix, recommend a targeted patch instead. For a structural redesign, investigate failed tests against requirements, record unknown consumers and verify data changes in an authorized isolated environment. Fewer files or green tests alone do not prove success.

## License

MIT

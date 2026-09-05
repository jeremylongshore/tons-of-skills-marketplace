# Beads workflow

Use this lane whenever `bd` is installed and the repository contains Beads, or
when project instructions require it.

## Start or recover

```bash
bd prime
bd search "<target or objective>"
bd ready
```

Read a matching issue before creating another. If no issue owns the exact work,
create one with objective, scope, constraints, evidence, acceptance criteria,
and design. Claim it before changing files:

```bash
bd show <id>
bd update <id> --claim
```

## During work

- Keep task state in Beads, not ad hoc TODO files.
- Add concise notes for decisions, exact revisions, test receipts, reviewer
  dispositions, blocked external dependencies, and changed authorization.
- Model dependencies with `bd dep add`; do not imply sequence only in prose.
- Use `bd remember` only for durable cross-session facts, not ordinary progress.
- Do not close an issue because a draft exists or a budget is nearly exhausted.

## Finish

Re-run acceptance gates and attach their exact results. Close only when the
objective is genuinely complete:

```bash
bd close <id> --reason="<evidence-backed completion>"
bd show <id>
```

Follow repository policy for Dolt synchronization. The presence of Beads does
not authorize commits, pushes, PRs, merges, releases, or external messages.

## Degraded mode

If `bd` is unavailable and repository policy does not require it, use the host's
durable task facility. If none exists, keep an explicit in-session ledger and
state that task recovery across sessions is not guaranteed. Never pretend this
fallback has Beads durability.

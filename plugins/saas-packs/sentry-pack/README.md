# Sentry Skill Pack

**v2.0.0** — 5 live-detection skills for Sentry SaaS ops, plus thin **v1 stub
redirects** (Keep/Merge/Cut slugs) until a follow-up tag deletes them. Where v1
shipped a 30-skill documentation curriculum, v2 ships 5 skills that **run** a job —
read-only Stats / event / release inspection via `sentry-cli` and documented REST
behind scripts (shared `scripts/lib/sentry_readonly.py`), or advisory mode on
pasted input. No write tool until a later ADR. **No MCP server.**

> [!NOTE]
> **This is the v2 rebuild scaffold.** Local draft only — not pushed, not tagged.
> If you had any `sentry-*` v1 skill in your `CLAUDE.md`, see
> **[Migration: v1 → v2](#migration-v1--v2)** for where each one goes. Same install
> slug (`sentry-pack`) — no rename. Stubs remain so auto-update does not strand
> bookmarks (Absorb `010` / pressure test `009` change 5).

## Installation

```bash
# Not published yet. Target install once tagged:
/plugin install sentry-pack@claude-code-plugins-plus
```

Each skill degrades to **advisory mode** (works on pasted Stats / event /
`sentry-cli` output) when no auth token is present. Hooks are **not** default
in this version (see `hooks/hooks.json`).

## The 5 skills

| Skill | What it does (live / advisory) |
|-------|--------------------------------|
| `sentry-quota-leak-hunter` | Which meter moved, and which lever is not "buy more" — ranked cut list from org stats + sampler / filter / cardinality diffs |
| `sentry-event-forensics` | Why an event, map, or trace did not show up — layered drop cause, plus planned SDK / vendor move |
| `sentry-release-medic` | This deploy's artifacts, commits, and release health — CI upload + finalize + health |
| `sentry-issue-triage` | This page: severity, suspect release, span, log line — on-call loop, not a generic SRE essay |
| `sentry-pii-scrub-enforcer` | **Recommends (does not apply)** PII scrubbing; delete only when asked; show project drift; Replay privacy when Replay is on |

## Nested checklists are not marketplace skills

**Rule (Absorb A1, verified against `scripts/corpus-resolver.mjs` on
`jeremylongshore/tons-of-skills-marketplace`):** nested procedures live at

```text
skills/<parent>/agents/<agent>/skills/<child>/CHECKLIST.md
```

They must **not** be named `SKILL.md`. Marketplace `isGradedSkill` matches
`/skills/[^/]+/SKILL.md$` at any depth under a plugin (including
`agents/<agent>/skills/<child>/SKILL.md`), and `marketplaceVisible` keeps every
`SKILL.md` under a catalogued plugin. Renaming to `CHECKLIST.md` is the pack-local
fix; do not flatten; do not publish nested checklists as peers.

Agent frontmatter uses `skills: []`. Agents **Read** `CHECKLIST.md` files.

## Cross-skill reference copies (mandatory for now)

Until a spike proves this runtime can invoke another skill's subagent, every
Decision 3 edge is a **labeled reference copy** with `OWNER.md` + `COPIED-FROM.md`
(including the quota pilot). Silent copies are a defect. PII
`config-drift-auditor` reads the quota sampler reference copy and does not
restate `tracesSampler` order.

## Category fan-out

Quota category breakdown = `scripts/parse-usage-stats.py` + `usage-auditor` only.
No per-category spend agents.

## Migration: v1 → v2

`sentry-pack@2.0.0` is a ground-up rebuild. Disposition: **Keep 5 · Merge 11 · Cut 14**.

**Canonical migration map:** [`000-docs/phase0-kill-list.md`](000-docs/phase0-kill-list.md) §3,
CTO ADR [`000-docs/008-AT-ADEC-sentry-v2-cto-decision.md`](000-docs/008-AT-ADEC-sentry-v2-cto-decision.md),
Absorb [`000-docs/010-AT-ADEC-sentry-v2-modify-absorb.md`](000-docs/010-AT-ADEC-sentry-v2-modify-absorb.md),
stubs plan [`000-docs/010-migration-stubs-plan.md`](000-docs/010-migration-stubs-plan.md).

Thin stub `SKILL.md` files under `skills/<v1-slug>/` redirect every Cut/Merge (and
Keep v1) slug. Stubs are not dual maintenance of v1 bodies. Delete stubs only in a
later tag — not in the release that removes the tutorial bodies.

### Where each Keep / Merge lands (summary)

| v1 skill | v2 destination |
|----------|----------------|
| `sentry-cost-tuning` | `sentry-quota-leak-hunter` |
| `sentry-rate-limits` · `sentry-load-scale` · `sentry-performance-tuning` | `sentry-quota-leak-hunter` (agents + checklists) |
| `sentry-advanced-troubleshooting` | `sentry-event-forensics` |
| `sentry-debug-bundle` · `sentry-upgrade-migration` · `sentry-migration-deep-dive` | `sentry-event-forensics` (agents) |
| `sentry-release-management` | `sentry-release-medic` |
| `sentry-ci-integration` · `sentry-deploy-integration` | `sentry-release-medic` (agents) |
| `sentry-incident-runbook` | `sentry-issue-triage` |
| `sentry-observability` | `sentry-issue-triage` (agent `log-correlator`) |
| `sentry-data-handling` | `sentry-pii-scrub-enforcer` |
| `sentry-security-basics` · `sentry-policy-guardrails` | `sentry-pii-scrub-enforcer` (agents) |
| 14 Cut skills | **Cut** — stub redirect + kill list §3 |

Org topology is **not** a sixth parent: key/DSN boundaries (+ SC04 team≠alert≠DSN)
nest under quota; project-standard drift nests under PII.

## Design Records

Architecture decisions and pain research live in [`000-docs/`](000-docs/).
Index: [`000-docs/000-INDEX.md`](000-docs/000-INDEX.md).

## License

MIT

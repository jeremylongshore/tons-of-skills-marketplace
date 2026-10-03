---
name: sentry-quota-leak-hunter
description: |
  Hunt Sentry quota leaks — which error / transaction / replay / span / log / profile
  meter moved, and which lever is not "buy more." Produce a ranked cut list from org
  stats plus concrete tracesSampler / beforeSend / inbound-filter / key-limit diffs.
  Recommends; does not apply. Use when a user asks to reduce Sentry costs, find quota
  burns, explain a usage spike, or tune sampling without losing paging-quality issues.
  Trigger with "reduce sentry costs", "sentry quota", "sentry usage spike",
  "why is sentry bill high", "tracesSampleRate 1", "inbound filters".
allowed-tools: Read, Glob, Grep, Bash(sentry-cli:*), Bash(jq:*), Bash(python3:*)
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, sentry, quota, finops, sampling]
---

# Sentry Quota Leak Hunter

Names which Sentry meter moved and which lever is not "buy more." The script
prints accepted, filtered, and dropped (and rate_limited) as separate counts.
You do not add them. You do not invent a dollar figure. You recommend a lever.
You do not click it.

Org topology (org, project, key/DSN, environment, and the SC04 row team ≠ alert
rule ≠ DSN) nests here on `key-boundary-mapper`. It is not a sixth parent.

## Overview

v1 `sentry-cost-tuning` is the Keep seed. This skill rebuilds that job: read
org usage, rank categories, recommend a sampler / filter / key ceiling /
cardinality fix. `sentry-rate-limits`, `sentry-load-scale`, and the quota half
of `sentry-performance-tuning` are merged here as agents, not as pack skills.

Category fan-out is **`scripts/parse-usage-stats.py` + `usage-auditor` only**.
There are no `error-spend`, `span-spend`, `replay-spend`, or `log-spend` agents.

## Prerequisites

- Sentry SaaS. If the user says self-hosted, say the SaaS quota model may not
  match `sentry.conf` and stop. Do not size Kafka, ClickHouse, or Relay.
- Optional read token: `SENTRY_AUTH_TOKEN` plus `sentry-cli info`. Live stats
  fetch is not implemented in `sentry_readonly.py` yet; a missing token or a
  unimplemented live fetch means **advisory mode**.
- Advisory input: pasted Stats JSON. Do not guess an org slug.
- `python3`. Arithmetic lives in the script. Do not re-sum in prose.

## Instructions

Parent is the router. Read checklists with the Read tool. Agent frontmatter
`skills:` is empty on purpose: nested procedures are `CHECKLIST.md`, never a
marketplace `SKILL.md`.

Cross-skill agent calls are **not** proven. Do not invoke `noise-classifier`
or `config-drift-auditor`. Read the labeled copy under this skill. `OWNER.md`
and `COPIED-FROM.md` name the owner. Delete the copy only after a spike says
calls work.

### Step 1 — Script first

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/parse-usage-stats.py" \
  --json /path/to/stats.json
```

Stdin: `--json -`. No file and no token: the script exits non-zero and does
not guess an org. `--sum-lost` and `--apply` are refused.

Use the JSON it prints. Fields that matter:

- `categories.<name>.accepted|filtered|dropped|rate_limited` — separate.
- `lost_events_total` is always null. Leave it null in the answer.
- `dollars` is null unless the payload itself has `subscription_screen_usd`.
  Ignore `per_event_usd` and any third-party price key.
- `highest_accepted_category` is the loud meter, not "events lost."
- `category_agents` is always `[]`.

### Step 2 — Spawn `usage-auditor` (every quota audit)

Read `agents/usage-auditor/skills/quota-usage-audit/CHECKLIST.md`.
The auditor interprets the script. It does not spawn a subagent per category.
Profiles and logs are rows in the same JSON.

Stay on the **parent** for billing-clock questions (CQ04): reserved volume
vs pay-as-you-go timing. Load `references/subscription-clocks.md`. No agent.

### Step 3 — Spawn `volume-cutter` only when a cut was asked for

Spawn when the user asked to cut volume, drop a health check, answer a 429,
or turn down tracing **and** the script shows accepted or rate_limited volume
worth cutting.

Do **not** spawn `volume-cutter` on a diagnosis that only asked which meter
moved. Do not spawn it because a checklist exists.

When spawned, Read:

- `agents/volume-cutter/skills/sampler-and-filters/CHECKLIST.md` (owner: this agent)
- `agents/volume-cutter/skills/inbound-filter-matrix/CHECKLIST.md` (COPY; owner is triage `noise-classifier`)
- `agents/volume-cutter/references/replay-privacy/CHECKLIST.md` only if replay accepted > 0 (COPY; owner is PII `replay-privacy`)

`beforeSend` does not see Session Replay. Do not claim a scrub hook fixes an
unmask. Hand privacy to the copy; do not rewrite it.

### Step 4 — Spawn `cardinality-hunter` only for raw transaction names or span explosion

Read `agents/cardinality-hunter/skills/transaction-cardinality/CHECKLIST.md`.
This file is the one canonical copy. Triage's `trace-bottleneck` has an
`OWNER.md` pointer and must not get a second sampler. Do not paste a second
`tracesSampler` into a performance-issue answer; that job is triage's
`perf-span-auditor` (span fingerprints), not this checklist.

### Step 5 — Spawn `key-boundary-mapper` once per boundary question

Not once per environment. Read
`agents/key-boundary-mapper/skills/org-key-boundaries/CHECKLIST.md`.

Refuse "set environment = production on the rate limit screen." There is no
per-environment rate limit (Help Center, 2026-07-28). Extra keys beat extra
projects when the only need is a ceiling.

If the fix is "your projects drifted," Read the labeled copy at
`agents/key-boundary-mapper/references/config-drift/CHECKLIST.md`.
Owner is PII `config-drift-auditor`. Do not re-implement the settings diff.
Sample-rate order stays in `sampler-and-filters`. The drift copy must not
rewrite parent-sampling order.

### Levers you may recommend (never apply)

| Lever | Label | What it is not |
|---|---|---|
| Key minute rate limit | Business/Enterprise | Not a target to sit on all month. Not an environment setting. |
| Inbound release filter, error-message filter | Business/Enterprise | Prospective. Full release string. No match if the event has no release. |
| Delete & Discard | Business/Enterprise | Prospective. Does not erase events already accepted. |
| Extension / localhost / legacy-browser / crawler toggles | Confirm on the plan screen | Filtered, not dropped. |
| `tracesSampler` | SDK, needs a deploy | Must not override `parentSampled === true`. |
| `beforeSend` drop of a **named** noisy error | SDK, needs a deploy | Returning null for every event is an outage. Hand to `sentry-event-forensics`. |
| Spike protection | Plan placement **unknown — leave blank** | Drops the incident. Not a sample you can reconstruct. |

Do not set `sampleRate` or `tracesSampleRate` below 1 without stating what
visibility is lost. Do not set `sampleRate: 0`. A key minute ceiling is a
ceiling, not a goal. Maps and fingerprint rules do not backfill accepted events.

## Output

```
Mode: advisory | live
Meter: <category> accepted=<n> filtered=<n> dropped=<n> rate_limited=<n>
Other meters: <same shape, one line each>
Lost-events total: refused
Dollars: <subscription_screen_usd or "not in payload — open the subscription screen">
Lever: <one recommendation> | plan gate: <Business/Enterprise or unknown or n/a> | prospective: yes/no
Visibility lost: <what a sample rate would hide, or "n/a">
Not a lever: environment is not a quota silo
Agents spawned: <list> 
Wrote to Sentry: no
```

Rank by accepted (and, separately, by rate_limited). Do not rank by a sum of
outcomes. If two categories moved, say so; do not collapse them into one quota.

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| No token / live fetch not implemented | `SentryReadOnlyClient` advisory | Paste stats JSON. Do not guess the org slug. |
| Self-hosted | Out of scope | Say the SaaS model may not match. Stop. |
| Dollar figure requested | Payload has no `subscription_screen_usd` | Point at the subscription screen. Ignore third-party per-event prices. |
| "How many events did we lose?" | Filtered and dropped were added | Quote the script. Refuse the sum. |
| Spike-protection plan | Not on the fetched page | Leave the label blank. |
| User wants the filter clicked | Read-only v2 | Print the lever. Do not call a write API. |

## Examples

### Example 1 — "Reduce Sentry costs"

Fixture `references/fixtures/stats-split-outcomes.json`. Script: span accepted
900000, error accepted 1200, replay accepted 0. No dollars in the payload.
Answer: span meter, not errors. Do not say "lost 12000" by adding outcomes.
`rate_limited` on spans stays its own field. Replay accepted is 0, so do not
open the replay-privacy copy. Offer `tracesSampler` that keeps
`parentSampled === true` and drops a named health-check transaction only when
there is no parent decision. Say what a flat `tracesSampleRate: 0.1` would hide.
Do not set `sampleRate: 0`. Spawn `volume-cutter` because a cut was requested.
Do not spawn per-category agents.

### Example 2 — Raw URL transaction names

`GET /users/12345/orders?token=abc` → flag the raw URL. Replacement:
`/users/:id/orders`. This is `cardinality-hunter`, not a second sampler essay.

### Example 3 — "Rate limit staging with the environment tag"

Spawn `key-boundary-mapper` once. Refuse the environment rate limit. Recommend
a second DSN key (ceiling on the non-prod key). Do not create a project per
preview if the only need is a ceiling.

## Resources

- `references/quota-categories.md` — meters and outcomes (CQ01, CQ08).
- `references/subscription-clocks.md` — reserved vs pay-as-you-go (CQ04). Parent only.
- `references/plan-gates.md` — Business/Enterprise labels. Spike protection blank.
- `references/heavy-categories.md` — replays and logs (CQ07).
- `references/cfo-output-format.md` — counts, not invented dollars.
- `references/fixtures/` — eval payloads.
- Shared client: `pack/scripts/lib/sentry_readonly.py`. No MCP.
- Docs: `docs/PRD.md`, `docs/ADR.md`, `docs/ONE-PAGER.md`, `docs/CFO-ONE-PAGER.md`.
- Citations: [manage event stream](https://docs.sentry.io/pricing/quotas/manage-event-stream-guide/), [JS sampling](https://docs.sentry.io/platforms/javascript/sampling/), [SDK rate limits](https://develop.sentry.dev/sdk/foundations/transport/rate-limiting/), [Help Center env rate limit](https://www.sentry.help/en/articles/13965110-can-i-rate-limit-events-based-on-the-environment).

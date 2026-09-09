---
name: web-analytics
description: >-
  Analyze Umami or GA4 traffic with evidence-backed specialist reviews and deliver a
  concise portfolio pulse, decision brief, or deep dive. Use when the user asks to
  check analytics, explain a traffic change, inspect funnels, compare site performance,
  or prepare an analytics report. Trigger with "/analytics", "check my analytics",
  "how's my traffic", "site stats", "traffic report", or "analytics brief".
allowed-tools: Read, Bash(date:*), Bash(curl:*), Bash(python3:*), Bash(source:*), Agent
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
  - analytics
  - umami
  - traffic
  - reporting
  - intelligence
argument-hint: '[mini|medium|full] [--site=name] [--period=7d] [--email] [--slack]'
compatibility: Designed for Claude Code
model: inherit
effort: high
user-invocable: true
---

# Web Analytics Intelligence

## Overview

Turn portfolio analytics into a decision-ready report by collecting a bounded dataset, preserving
the comparison window, separating observed facts from hypotheses, and routing deeper requests
through specialist agents. This is a push-based analysis workflow, not a dashboard replacement.

Read the [operating contract](references/operating-contract.md) before making authenticated
requests or delivering a report.

## Prerequisites

- Configure sites and thresholds in `${CLAUDE_PLUGIN_ROOT}/references/site-registry.md`.
- Store Umami credentials in the operator's approved secret store; this installation uses
  `UMAMI_PASSWORD` from `~/.env`.
- Confirm `/email` or `/slack` independently before requesting those delivery channels.
- Use `${CLAUDE_PLUGIN_ROOT}/references/reporting-tiers.md` and
  `${CLAUDE_PLUGIN_ROOT}/references/interpretation-guide.md` for medium and full reports.

## Authentication and Safety

1. Confirm the analytics base URL is the expected operator-controlled host before sending a
   credential.
2. Load `UMAMI_PASSWORD` only for the command that needs it. Never print, log, persist, or pass
   the password or bearer token to a specialist agent.
3. Use `curl --fail-with-body --silent --show-error`; stop if authentication fails or the token
   is empty.
4. Treat email and Slack delivery as external side effects. Preview the destination and report,
   and obtain confirmation when the user has not explicitly requested delivery.
5. Never send messages, modify analytics configuration, or write baseline state during a read-only
   request. A full-tier memory update requires an explicit writable scope.

## Workflow

### 1. Parse the Request

| Parameter | Default | Accepted values |
|---|---|---|
| Tier | `mini` | `mini`, `medium`, `full` |
| Site | `all` | Registry name or `all` |
| Period | `7d` | `today`, `yesterday`, `7d`, `30d`, `mtd`, `qtd` |
| Delivery | `console` | `console`, `email`, `slack`, `all` |
| Compare | prior equivalent | An explicit comparison window |

Use defaults when they preserve the user's intent. Ask before continuing if the site, time window,
or external destination would materially change the result.

### 2. Load Configuration

Read only the files needed for the selected tier:

1. `${CLAUDE_PLUGIN_ROOT}/references/site-registry.md` for site IDs, baselines, and thresholds.
2. `${CLAUDE_PLUGIN_ROOT}/references/mcp-tool-reference.md` for supported data operations.
3. `${CLAUDE_PLUGIN_ROOT}/references/reporting-tiers.md` for output contracts.
4. `${CLAUDE_PLUGIN_ROOT}/references/interpretation-guide.md` for evidence language.

### 3. Collect the Minimum Dataset

For direct Umami access, authenticate and fail closed:

```bash
set -euo pipefail
source ~/.env
analytics_url="https://analytics.intentsolutions.io"
token=$(curl --fail-with-body --silent --show-error "${analytics_url}/api/auth/login" \
  -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"'"${UMAMI_PASSWORD}"'"}' | \
  python3 -c "import json,sys; print(json.load(sys.stdin).get('token',''))")
test -n "${token}" || { printf 'Umami authentication returned no token\n' >&2; exit 1; }
curl --fail-with-body --silent --show-error \
  "${analytics_url}/api/websites/<site-id>/stats?startAt=<start-ms>&endAt=<end-ms>&compare=prev" \
  -H "Authorization: Bearer ${token}"
unset token UMAMI_PASSWORD
```

Record the source, site, timezone, exact start and end timestamps, comparison window, and any
missing endpoint. Do not infer missing values as zero.

### 4. Route by Tier

- **Mini:** Collect aggregate stats and active visitors inline. Return totals, per-site metrics,
  comparison deltas, and one material signal in at most 15 lines.
- **Medium:** Use `Agent` to run `data-collector`; after it returns, run `traffic-intelligence`,
  `content-seo`, and `anomaly-detector` concurrently. Give `reporting-narrative` their outputs,
  the exact period, and the requested delivery format.
- **Full:** Run `data-collector` for aggregate, event, technology, and geography data. Then run all
  five analysis specialists concurrently, pass their claims to `verification-agent`, and compile
  only verified or explicitly qualified findings with `reporting-narrative`.

Agent definitions live under `${CLAUDE_PLUGIN_ROOT}/agents/`. Give agents collected results, not
credentials. Bound every assignment to the requested sites and period. If an agent fails, report
that coverage gap and continue only when the remaining evidence can support the requested output.

### 5. Verify and Deliver

Before delivery, apply the [operating contract](references/operating-contract.md):

1. Recalculate headline deltas from the raw totals.
2. Label each statement as observation, comparison, hypothesis, or recommendation.
3. Check anomaly claims against baselines and low-volume noise.
4. Name unavailable sources and incomplete windows.
5. Preview external destinations, then invoke `/email` or `/slack` only when authorized.

For a full-tier report, run `memory-agent` only if the user authorized baseline-state updates.
Persist the period, source, and evidence receipt so a later report can reproduce the comparison.

## Error Handling

Stop without exposing secret material when authentication fails. For partial endpoint, site, agent,
or delivery failures, retain successful evidence, name the exact coverage gap, and avoid complete-
portfolio or trend claims that the remaining data cannot support. The operating contract defines
the required fallback for each failure class.

## Output

Return the tier, sites, exact period, comparison window, sources consulted, coverage gaps, and
delivery result. Lead with the strongest verified signal, show the supporting metrics, distinguish
hypotheses from facts, and end with prioritized actions that each have an owner or next check.

## Examples

- `/analytics --period=today` produces a mini console pulse for every configured site.
- `/analytics medium --site=tonsofskills --period=7d` explains material traffic and content shifts.
- `/analytics full --period=30d --email` previews an evidence-checked deep dive before email delivery.

## Resources

- [Operating contract](references/operating-contract.md) — auth, evidence, failure, and delivery gates.
- `${CLAUDE_PLUGIN_ROOT}/references/site-registry.md` — configured properties and thresholds.
- `${CLAUDE_PLUGIN_ROOT}/references/reporting-tiers.md` — detailed report schemas.
- `${CLAUDE_PLUGIN_ROOT}/references/interpretation-guide.md` — analytical voice and caveats.
- `${CLAUDE_PLUGIN_ROOT}/references/delivery-channels.md` — email and Slack adapters.

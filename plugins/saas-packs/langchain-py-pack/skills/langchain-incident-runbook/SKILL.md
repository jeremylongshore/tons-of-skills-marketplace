---
name: langchain-incident-runbook
description: "Triage LangChain 1.0 / LangGraph 1.0 production incidents \u2014 LLM-specific\
  \ SLOs,\nprovider outage runbook, latency spike decision tree, cost-overrun response,\n\
  agent loop containment. Use during an on-call page, in a post-mortem, or writing\n\
  the team's first LLM runbook.\nTrigger with \"langchain incident\", \"llm on-call\"\
  , \"langchain slo\",\n\"langchain outage\", \"langchain cost spike\", \"langchain\
  \ agent loop\".\n"
allowed-tools: Read
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- sre
- incident-response
- slo
- on-call
compatibility: Designed for Claude Code
---
# LangChain Incident Runbook

## Overview

3:07am. PagerDuty: "LangChain p95 latency > 10s for 5 minutes." You open LangSmith,
filter by `service="triage-agent"` over the last 15 minutes, and the first trace
is 43 seconds long — an agent is on step 24 of 25 iterations, bouncing between
the same two tools on a vague user prompt ("help me with my account"). The cost
dashboard shows **$400 spent in the last 10 minutes**, up from a $6/hour baseline.
This is P10: `create_react_agent` defaults to `recursion_limit=25` with no cost
cap; vague prompts never converge; the spend hits before `GraphRecursionError`
surfaces. First move is not to push a code fix — it is to flip
`recursion_limit=5` via config reload and add a middleware token-budget cap per
session, then deal with the stuck sessions.

Or: same alert, different signature. p95 is healthy at 1.8s, but p99 is 12s and
spiky. The spikes correlate with instance starts in Cloud Run. P36: Python +
LangChain + embedding preloads = 5–15s cold start; Cloud Run scales to zero by
default, so first-request p99 is 10x p95. First move is `--min-instances=1`
(or a keepalive pinger), not more CPU.

The shape of the page decides the first move. This runbook gives you:

1. The LLM-specific SLO set most teams do not have: **p95 TTFT <1s, p99 total
   latency <10s, error-rate <0.5%, cost-per-req <$0.05** — with Prometheus
   burn-rate recording rules that page on user-visible regression.
2. A triage decision tree with three root paths (latency / cost / error-rate),
   each with a 3-step diagnostic and first-response action.
3. Provider outage runbook wired to `.with_fallbacks(backup)` so failover is a
   config flip, not a code change.
4. Agent-loop containment via `recursion_limit` tuning and middleware
   token-budget caps so runaway agents stop burning cost **before** the
   `GraphRecursionError`.
5. Post-incident debug bundle (cross-ref `langchain-debug-bundle`) and write-up
   template.

Pinned: `langchain-core 1.0.x`, `langgraph 1.0.x`, `langsmith 0.3+`. Primary pain
anchors: **P10** (agent runaway), **P36** (cold start). Adjacent: P29 (per-process
rate limiter), P30 (`max_retries=6` means 7 attempts), P31 (Anthropic cache RPM).

## Prerequisites

- LangSmith workspace with tracing enabled (free tier is fine for runbook work)
- Prometheus + Alertmanager or equivalent (Datadog, Grafana Cloud) — burn-rate rules assume PromQL
- `langchain-observability` skill applied — metrics are grounded in what LangSmith callbacks emit
- A `backup` model factory from `langchain-rate-limits` — the failover playbook assumes `.with_fallbacks()` is already wired
- On-call rotation + PagerDuty (or equivalent) integrated with the alert pipeline

## Instructions

### Step 1 — Define the LLM-specific SLO set

HTTP-style SLOs miss what users actually feel. Define four, publish them, wire
burn-rate alerts to the symptom.

| SLO | Threshold | Alert condition | First-response action |
|---|---|---|---|
| **p95 TTFT** (time to first streamed token) | <1s | burn-rate > 2% over 5min | Check streaming is enabled; check provider status; check cold start (P36) |
| **p99 total latency** | <10s | burn-rate > 5% over 5min | Check agent loop depth (P10); cold start (P36); provider latency |
| **Error rate** (5xx + uncaught exceptions) | <0.5% | burn-rate > 1% over 5min | Check provider 429/500; auth token; schema drift on structured output |
| **Cost per request** | <$0.05 (tier-dependent) | p95 spend/req > $0.20 over 15min | Check agent recursion (P10); retry rate (P30); token-use per req |

Prometheus recording rule pattern for p99 latency burn-rate (replicate for TTFT,
error-rate, and cost):

```yaml
groups:
  - name: langchain_slo
    interval: 30s
    rules:
      - record: langchain:p99_latency_5m
        expr: histogram_quantile(0.99, sum(rate(langchain_request_duration_seconds_bucket[5m])) by (le, service))
      - alert: LangChainP99LatencyBurn
        expr: langchain:p99_latency_5m > 10
        for: 5m
        labels: { severity: page, team: llm }
        annotations:
          summary: "LangChain p99 > 10s for {{ $labels.service }}"
          runbook: "https://runbooks/langchain-incident-runbook#latency"
```

See [LLM SLOs](references/llm-slos.md) for the canonical set (free / paid /
enterprise tiers), burn-rate recipes (fast + slow), and a TTFT-specific rule
that requires streaming to be instrumented.

### Step 2 — Triage decision tree: which root path?

The alert name tells you the root path. Do not mix diagnostics across paths —
the first-response action differs.

```
Alert fired
  ├── Latency (p95/p99 breach, TTFT breach)
  │     ├── 1. Provider status page (Anthropic, OpenAI) green? → if red, Step 3
  │     ├── 2. Cold start pattern? (p99 >> p95, correlates with instance starts) → P36
  │     └── 3. Streaming configured? (TTFT only makes sense with .stream/.astream)
  │
  ├── Cost (spend/req or absolute spend/hour breach)
  │     ├── 1. Agent recursion depth? (LangSmith: max steps per trace) → P10
  │     ├── 2. Retry rate elevated? (callback log: attempt count / logical call) → P30
  │     └── 3. Token-use per req regression? (input + output tokens from callbacks)
  │
  └── Error rate (5xx + uncaught exceptions)
        ├── 1. Provider 429/500 spike? (distinguish client 4xx from provider 5xx)
        ├── 2. Auth? (API key rotation, expired token, org quota exhausted)
        └── 3. Schema drift on structured output? (Pydantic ValidationError in traces)
```

For each leaf, [Latency Triage](references/latency-triage.md) and
[Cost Overrun Response](references/cost-overrun-response.md) give the LangSmith
filter query, the exact metric to inspect, and the remediation.

### Step 3 — Provider outage: detect, circuit-break, fail over

Detection precedes failover. Do not flip fallbacks on an application bug.

1. **Detect** via three signals — all three should agree before declaring a
   provider outage:
   - Vendor status page watcher (`status.anthropic.com`, `status.openai.com`) —
     poll every 30s, surface into Slack
   - In-app canary probe — a 1-req/min call to each configured provider with a
     trivial prompt, tracked as a separate SLO
   - Error-rate spike on the primary provider in your own metrics (distinguishes
     a real outage from your app's bug)
2. **Circuit-break** the primary: a `CircuitBreaker` middleware (see
   `langchain-middleware-patterns` if available, or a simple
   `aiobreaker`-backed runnable) opens after N consecutive `APIError` /
   `APITimeoutError` within a window. Once open, calls skip the primary and go
   straight to the backup. This bounds the latency cost of a down provider.
3. **Fail over** via `.with_fallbacks(backup)` — the fallback chain is already
   wired (see `langchain-rate-limits`). During an outage, either flip a feature
   flag that swaps the default factory, or temporarily set the primary's
   `max_retries=0` so the chain reaches the fallback immediately.
4. **Comms**: post a user-facing status page entry ("Degraded performance on
   feature X — monitoring upstream provider") and an internal Slack update with
   the canary graph attached. [Provider Outage Playbook](references/provider-outage-playbook.md)
   has the full comms template and the circuit-breaker middleware snippet.

### Step 4 — Agent loop containment: stop the bleed before GraphRecursionError

P10 is the most common cost-spike cause. `create_react_agent` defaults to
`recursion_limit=25`, meaning 25 model calls per user turn — with Claude Sonnet
at ~$3/MTok input, a 10k-token tool-call loop burns real money per minute.

Three containment layers, applied in order:

1. **Set `recursion_limit` per agent depth** — interactive chat agents rarely
   need more than 5–8 steps; background research agents can justify 15; never
   leave the default 25 in production.

   ```python
   from langgraph.prebuilt import create_react_agent

   agent = create_react_agent(
       llm, tools,
       recursion_limit=8,  # P10 — was default 25
   )
   ```

2. **Middleware token-budget cap per session** — a callback that tracks
   cumulative input + output tokens for a session id and raises a custom
   `BudgetExceeded` exception once the cap is hit. The agent terminates
   cleanly; the user sees a polite "I could not finish this task in budget,
   try rephrasing" instead of a spinning UI until `GraphRecursionError`.
3. **Circuit on repeated tool calls** — a LangGraph edge that routes to `END`
   when the same tool has been called with the same args twice in a row. This
   is a cheap heuristic for "the agent is stuck in a loop."

[Cost Overrun Response](references/cost-overrun-response.md) has the middleware
implementation, the repeat-tool edge pattern, and a per-tenant budget
enforcement example.

### Step 5 — Post-incident: bundle, write up, communicate

Within 30 minutes of all-clear:

1. **Debug bundle** — capture the failing LangSmith trace URL(s), the
   Prometheus dashboard screenshot at the breach window, the agent's config
   (recursion_limit, model id, max_retries), and the provider's status page
   state at incident time. Cross-reference `langchain-debug-bundle` if present.
2. **Write-up template** — timeline (detection → triage → mitigation →
   all-clear), root cause in one sentence with pain-catalog anchor (e.g.
   "P10: recursion_limit=25 default, vague prompt, no token cap"), permanent
   fix ticket link, follow-up SLO tuning.
3. **Comms** — close the user-facing status page entry, post a short Slack
   summary (one-paragraph timeline + link to write-up), schedule the
   post-mortem review in the next weekly SRE sync.

## Output

- LLM SLO set (TTFT, p99 latency, error-rate, cost-per-req) published and
  alerted via Prometheus burn-rate rules
- Triage decision tree posted in the runbook with three root paths (latency /
  cost / error-rate) and first-response actions per leaf
- Provider outage playbook with circuit breaker + `.with_fallbacks(backup)`
  wired to a feature flag for one-flip failover
- `recursion_limit` set per agent depth (never default 25 in prod); middleware
  token-budget cap per session
- Post-incident debug-bundle template + write-up template wired to the
  on-call workflow

## Error Handling

| Symptom | Likely cause | First-response action |
|---|---|---|
| p95 latency breach, TTFT degraded | Streaming disabled, or provider-side latency | Verify `.stream()`/`.astream()` used; check provider status page |
| p99 >> p95, correlates with instance starts | Cloud Run cold start (P36) | `--min-instances=1`, CPU-always-allocated billing, preload imports |
| Cost-per-req spike, agent traces show 20+ steps | `recursion_limit=25` default + vague prompt (P10) | `recursion_limit=5–8`, add middleware token-budget cap |
| Cost spike, callback log shows 7 attempts per logical call | `max_retries=6` inflates cost 7x (P30) | `max_retries=2` + circuit breaker; log retries via callbacks |
| 429 storm despite `requests_per_second=10` on each of N workers | `InMemoryRateLimiter` is per-process (P29) | Switch to `RedisRateLimiter` or provider-side quota |
| Anthropic 429 while token budget has headroom | Cache RPM throttled separately (P31) | Client-side semaphore on RPM, not token count; monitor cached-read vs uncached separately |
| Error-rate spike, all on primary provider | Provider outage | Canary probe confirms; flip failover to `.with_fallbacks(backup)` via flag |
| `ValidationError` surge on structured output | Schema drift — model added fields | `ConfigDict(extra="ignore")` on the Pydantic schema (see `langchain-sdk-patterns`) |
| Agent never terminates, no `GraphRecursionError` yet | Stuck in tool-call loop | Add "repeated tool call" edge routing to `END`; raise `BudgetExceeded` from middleware |

## Examples

### On-call page: cost spike from agent runaway

PagerDuty: "cost-per-req > $0.20 for 15 minutes." LangSmith filtered to the
last 15 minutes shows average trace depth = 22 steps (baseline 4). Single
tenant, single conversation pattern — a user who asked an open-ended question
the agent cannot resolve. First-response action: flip `recursion_limit=5` via
config reload (no deploy), add session to the blocklist in middleware, post
internal Slack with the trace URL.

See [Cost Overrun Response](references/cost-overrun-response.md) for the
middleware token-budget implementation and the per-tenant budget pattern.

### On-call page: p99 latency spike during traffic ramp

p95 healthy at 1.8s, p99 at 12s, spikes correlate with Cloud Run instance
starts — classic P36. First-response action: `gcloud run services update
<svc> --min-instances=1`, verify heavy imports are at module top level,
schedule follow-up ticket to move embedding preload to a warm-up hook.

See [Latency Triage](references/latency-triage.md) for the cold-start
detection recipe and the p95-vs-p99 attribution decision tree.

### On-call page: provider outage mid-day

Anthropic status page goes red. Canary probe error-rate jumps from 0% to 100%
on Anthropic, stays at 0% on OpenAI. Flip the failover flag — the
`.with_fallbacks(backup=ChatOpenAI(...))` chain (already wired via
`langchain-rate-limits`) takes over. Post user-facing status entry, monitor
cost (OpenAI pricing differs — watch cost-per-req SLO), revert when upstream
recovers.

See [Provider Outage Playbook](references/provider-outage-playbook.md) for the
circuit-breaker middleware, the canary probe snippet, and the user-comms
template.

## Resources

- [LangChain Python: LangSmith tracing](https://docs.smith.langchain.com/)
- [LangGraph: `create_react_agent` and `recursion_limit`](https://langchain-ai.github.io/langgraph/reference/prebuilt/)
- [Google Cloud Run: cold start mitigation](https://cloud.google.com/run/docs/tips/general#avoiding_cold_starts)
- [Google SRE: burn-rate alerting](https://sre.google/workbook/alerting-on-slos/)
- [Anthropic status page](https://status.anthropic.com/)
- [OpenAI status page](https://status.openai.com/)
- Pack pain catalog: `docs/pain-catalog.md` (primary: P10, P36; adjacent: P29, P30, P31)
- Related skills: `langchain-debug-bundle` (post-incident capture), `langchain-observability` (SLO metrics source), `langchain-rate-limits` (`.with_fallbacks` chain), `langchain-cost-tuning` (token budget caps), `langchain-deploy-integration` (cold-start fix)

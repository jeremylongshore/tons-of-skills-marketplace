---
name: langchain-observability
description: "Wire LangSmith tracing and custom metric callbacks into a LangChain\
  \ 1.0 chain\nor LangGraph 1.0 agent correctly \u2014 env-var spelling, subgraph\
  \ propagation,\nper-tenant dimensions, cost and latency counters. Use when setting\
  \ up\nobservability on a new service, debugging blank traces in LangSmith, or adding\n\
  per-tenant cost breakdowns. Trigger with \"langchain observability\",\n\"langsmith\
  \ tracing\", \"langchain callbacks\", \"langchain metrics\".\n"
allowed-tools: Read, Write, Edit, Bash(python:*)
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- observability
- langsmith
- callbacks
compatibility: Designed for Claude Code
---
# LangChain Observability (Python)

## Overview

Engineer sets `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY=...` from the
0.2 docs, restarts the service, and sees zero traces in LangSmith — no errors,
no warnings. That is P26: in LangChain 1.0 the canonical env vars are
`LANGSMITH_TRACING` and `LANGSMITH_API_KEY`. The `LANGCHAIN_*` names are
soft-deprecated and fail silently on any chain that goes through 1.0 middleware
or `create_react_agent`. One-line fix:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=lsv2_...
export LANGSMITH_PROJECT=my-service-prod
```

Next failure mode: a custom `BaseCallbackHandler` attached via
`chain.with_config(callbacks=[meter])` fires on the parent but is silent on
LangGraph subgraphs and `create_react_agent` tool calls — token counts
under-report by 30-70% vs the provider dashboard. That is P28: LangGraph
creates a child runtime per subgraph, and bound callbacks do not propagate.
Pass callbacks at invocation time instead:

```python
await chain.ainvoke(inputs, config={"callbacks": [meter], "configurable": {"tenant_id": t}})
```

This skill walks through canonical LangSmith setup, a metric-callback template
with tenant dimensions, invocation-time propagation, `RunnableConfig` trace
tagging, and a decision tree for LangSmith-only vs OTEL-native (defer to
`langchain-otel-observability` / L33 for OTEL-heavy). Pin: `langchain-core 1.0.x`,
`langgraph 1.0.x`, `langsmith` current. LangSmith tracing adds <5ms per-span
overhead; metric callbacks add <1ms per fire. Pain-catalog anchors: P26, P28,
P04 (cache-token aggregation), P25 (retry double-counting).

## Prerequisites

- Python 3.10+
- `langchain-core >= 1.0, < 2.0`, `langgraph >= 1.0, < 2.0`
- `langsmith` (bundled with `langchain`; upgrade to current for 1.0 env-var support)
- A LangSmith API key (`lsv2_...`) — free tier at https://smith.langchain.com
- Optional metric sinks: `prometheus_client`, `statsd`, or `datadog` Python packages

## Instructions

### Step 1 — Enable LangSmith with the canonical 1.0 env vars

`LANGSMITH_TRACING=true` is the switch. `LANGSMITH_API_KEY` authenticates.
`LANGSMITH_PROJECT` groups traces by environment — use one project per
`service-env` pair (`myapp-prod`, `myapp-staging`), not one per service.

```bash
# .env (loaded via python-dotenv or secret manager)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_PROJECT=my-service-prod

# Legacy fallback names (still work, soft-deprecated — do not use in new code):
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=lsv2_pt_...
# LANGCHAIN_PROJECT=my-service-prod
```

Verify in a REPL that the client sees the key before relying on it in
production:

```python
from langsmith import Client
c = Client()                       # reads LANGSMITH_API_KEY and LANGSMITH_ENDPOINT
print(c.list_projects(limit=1))   # raises LangSmithAuthError if key is wrong
```

Do NOT set both `LANGCHAIN_TRACING_V2` and `LANGSMITH_TRACING` — mixed settings
have caused stale project routing in 1.0.x. See P26.

For selective sampling in high-traffic services, set
`LANGSMITH_SAMPLING_RATE=0.1` (10% of runs). Full detail in
[LangSmith Setup](references/langsmith-setup.md).

### Step 2 — Write a metric callback for per-request observability

Subclass `BaseCallbackHandler`. Record `token_in`, `token_out`, `latency_ms`,
`tool_calls`, and `error`, tagged with a `tenant_id` dimension for downstream
grouping.

```python
import time
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

class MetricCallback(BaseCallbackHandler):
    """Per-LLM-call metrics tagged with tenant_id. Overhead <1ms per event."""

    def __init__(self, tenant_id: str, sink) -> None:
        self.tenant_id = tenant_id
        self.sink = sink
        self._starts: dict[str, float] = {}

    def on_llm_start(self, serialized, prompts, *, run_id, **kwargs) -> None:
        self._starts[str(run_id)] = time.perf_counter()

    def on_llm_end(self, response: LLMResult, *, run_id, **kwargs) -> None:
        t0 = self._starts.pop(str(run_id), time.perf_counter())
        elapsed_ms = (time.perf_counter() - t0) * 1000   # wall-clock latency
        tags = {"tenant_id": self.tenant_id}
        for gen in response.generations:
            for g in gen:
                meta = getattr(g.message, "usage_metadata", None) or {}
                self.sink.incr("llm.token_in",   meta.get("input_tokens", 0),  tags)
                self.sink.incr("llm.token_out",  meta.get("output_tokens", 0), tags)
                # P04 — aggregate Anthropic cache reads across calls
                cache = meta.get("input_token_details", {}).get("cache_read", 0)
                self.sink.incr("llm.cache_read", cache, tags)
        self.sink.hist("llm.latency_ms", elapsed_ms, tags)

    def on_llm_error(self, error, *, run_id, **kwargs) -> None:
        self._starts.pop(str(run_id), None)
        self.sink.incr("llm.error", 1, {"tenant_id": self.tenant_id,
                                         "error_type": type(error).__name__})

    def on_tool_end(self, output, *, run_id, **kwargs) -> None:
        self.sink.incr("llm.tool_calls", 1, {"tenant_id": self.tenant_id})
```

A thin `sink` protocol (`incr`, `hist`) swaps between Prometheus, StatsD, or
Datadog. Alternative sinks (LangSmith-only, OTEL) do not need this callback
at all — see Step 5. Full sink adapters and P25 retry dedupe in
[Custom Metrics Callback](references/custom-metrics-callback.md).

### Step 3 — Pass callbacks via `config["callbacks"]` at invocation (P28)

This is the single most common observability bug in LangGraph 1.0 services.
Binding callbacks at definition time does not propagate into subgraphs or
`create_react_agent` tool nodes — those create child runtimes with their own
callback scope.

```python
# WRONG — fires on parent runnable only; silent on subgraphs (P28)
agent_bound = agent.with_config(callbacks=[MetricCallback(tenant_id, sink)])
result = await agent_bound.ainvoke(inputs)

# RIGHT — propagates to every runnable, subgraph, and tool call
meter = MetricCallback(tenant_id, sink)
result = await agent.ainvoke(
    inputs,
    config={
        "callbacks": [meter],
        "configurable": {"thread_id": session_id, "tenant_id": tenant_id},
        "tags": ["prod", f"tenant:{tenant_id}"],
        "metadata": {"request_id": req_id, "tier": "enterprise"},
    },
)
```

Construct the callback *inside* the request handler so it captures a fresh
`tenant_id` per request — and in that pattern, invocation-time config is the
only way callbacks reach subgraphs. See [Trace Metadata and Tagging](references/trace-metadata-and-tagging.md)
for the full `RunnableConfig` shape.

### Step 4 — Tag and annotate traces via `RunnableConfig`

LangSmith indexes two per-request fields: `tags` (flat list, filterable) and
`metadata` (key-value, searchable). Fix conventions early — LangSmith has no
rename tool.

```python
config = {
    "callbacks": [meter],
    "tags": [
        "env:prod",                # environment
        f"tenant:{tenant_id}",     # tenant
        f"tier:{tenant_tier}",     # plan tier
        f"feature:{feature_flag}", # A/B experiment arm
    ],
    "metadata": {
        "request_id": req_id,
        "user_id": user_id,
        "session_id": session_id,
        "app_version": os.environ["APP_VERSION"],
    },
    "run_name": "agent_main",      # LangSmith UI label; overrides chain class name
}
```

Hierarchical tag conventions (`env:prod`, `tenant:acme`, `tier:enterprise`)
make LangSmith filters work. Free-form tags (`"important"`, `"check-me"`) do
not. See [Trace Metadata and Tagging](references/trace-metadata-and-tagging.md).

### Step 5 — Pick a sink and the stack shape

The callback handler is the integration point. Options, in decreasing order of
fit:

- **LangSmith only** — zero additional overhead; tracing already covers latency
  and token accounting. Fine for solo dev, small teams, and LLM-native ops.
- **Prometheus (pull)** — best fit for Kubernetes + existing Prom stack. Export
  via `prometheus_client` HTTP endpoint. Watch tenant label cardinality.
- **StatsD / Datadog (push)** — UDP fire-and-forget; sub-1ms overhead. Safe on
  high-throughput async services. Use `datadog.dogstatsd` for tag support.
- **OTEL native** — multi-service distributed tracing. Defer to
  `langchain-otel-observability` (L33); do not reimplement here.

Decision tree:

```
Existing OTEL stack (Collector, Tempo, Jaeger)?
├── YES → OTEL-native (L33). LangSmith optional for prompt inspection.
└── NO  → LLM-specific features (prompt inspection, evals, queues) enough?
         ├── YES → LangSmith only. Add MetricCallback only for tenant cost.
         └── NO  → Hybrid: LangSmith for prompts + Prometheus/Datadog for SLOs.
                   See references/hybrid-langsmith-otel.md for split-point rules.
```

Mixing paths without a plan creates double-emission and conflicting trace IDs.
See [Custom Metrics Callback](references/custom-metrics-callback.md) for
Prometheus / StatsD / Datadog sink implementations, plus dedupe for P25 retry
double-counts; see [Hybrid LangSmith + OTEL](references/hybrid-langsmith-otel.md)
for the split-point contract.

### Step 6 — Feed runs back into evals

Real traffic is the best eval set. Route a sampled subset of production runs
into a LangSmith annotation queue for human review; the queue feeds `Dataset`
objects replayable against candidate models.

```python
from langsmith import Client
Client().create_annotation_queue(
    name="prod-regressions",
    description="1% sample, weekly review",
)
# Add metadata={"eval_candidate": "true"} on 1% of runs — LangSmith UI has
# a rule to route into the queue by metadata filter.
```

Keep annotation queues under 500 runs/week (reviewers saturate past that).
See [LangSmith Setup](references/langsmith-setup.md) for the queue and
dataset flow.

## Output

- LangSmith tracing on via `LANGSMITH_TRACING` / `LANGSMITH_API_KEY` /
  `LANGSMITH_PROJECT` with a `langsmith.Client()` smoke-check
- `MetricCallback(BaseCallbackHandler)` emitting `token_in`, `token_out`,
  `cache_read`, `latency_ms`, `tool_calls`, `error` tagged with `tenant_id`
- All chain invocations pass `config={"callbacks": [...], ...}` at invoke time
  so metrics propagate to subgraphs and agent tools
- `RunnableConfig` carries hierarchical tags (`env:*`, `tenant:*`, `tier:*`)
  and structured `metadata` (`request_id`, `user_id`, `session_id`)
- One metric sink wired (Prometheus, StatsD, Datadog, or LangSmith-only)
- Explicit choice recorded for LangSmith / OTEL / hybrid / custom

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| No traces in LangSmith, no errors | Used `LANGCHAIN_TRACING_V2` spelling on 1.0 middleware path (P26) | Switch to `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` |
| `langsmith.utils.LangSmithAuthError: Unauthorized` | Key is valid but points to a deleted workspace, or copied with trailing whitespace | Regenerate at smith.langchain.com, check `repr(os.environ['LANGSMITH_API_KEY'])` for `\n` |
| Callback fires on parent only, silent on subgraphs | Bound via `.with_config(callbacks=[...])` — does not propagate (P28) | Pass via `config["callbacks"]` at `invoke()` / `ainvoke()` |
| Token counts under by 30-70% vs provider dashboard | Combination of P28 (subgraph silence) and P25 (retry double-count not deduped) | Fix P28 first; for P25 add `request_id` dedupe key in sink |
| Trace duration shows 0ms on streamed calls | `on_llm_end` fires after stream closes but handler records before — timing race | Use `time.perf_counter()` captured in `on_llm_start`, not `on_chat_model_start` |
| Prometheus cardinality explosion | `tenant_id` label has high cardinality (>10k tenants) | Bucket tenants into tiers for metrics; keep full `tenant_id` in LangSmith metadata only |
| LangSmith UI shows runs under `default` project, not the configured one | `LANGSMITH_PROJECT` env var not set at process start | Set before import; `LANGSMITH_PROJECT` is read once at `Client()` init |
| `AttributeError: 'NoneType' object has no attribute 'get'` in `on_llm_end` | `usage_metadata` is `None` on intermediate streaming chunks | Guard with `if meta := getattr(g.message, 'usage_metadata', None):` |

## Examples

### Multi-tenant SaaS: per-tenant cost dashboard

A production SaaS has 200 tenants on a shared LangGraph agent. Finance wants
weekly cost reports per tenant. The `MetricCallback` records `token_in`,
`token_out`, and `cache_read` tagged with `tenant_id`; Prometheus scrapes the
`/metrics` endpoint; Grafana aggregates `sum by (tenant_id) (rate(llm_token_out_total[1w])) * 0.0000015`
for Sonnet output cost. The invocation-time `config["callbacks"]` propagation
is load-bearing here — without it, subgraph tool calls (the bulk of token
spend) go uncounted. See [Custom Metrics Callback](references/custom-metrics-callback.md)
for the full Prometheus integration.

### Debugging missing traces in staging

A team deploys a new LangGraph service to staging. No traces show up in
LangSmith. Checking: (1) `LANGSMITH_TRACING` spelled correctly — yes; (2) API
key valid — `langsmith.Client().list_projects(limit=1)` returns ok; (3) project
name matches — `LANGSMITH_PROJECT=myservice-staging`. Traces appear in the
`default` project, not `myservice-staging`. Root cause: the env var was set in
the runtime env-file but the process was started before the env-file was
sourced. `Client()` read `LANGSMITH_PROJECT` at import time. Fix: restart the
process cleanly. See [LangSmith Setup](references/langsmith-setup.md) for the
process-order checklist.

### Feeding prod traffic to an eval dataset

A team wants to validate a Claude 4.6 → Claude 4.7 upgrade against recent prod
runs. They add `metadata={"eval_candidate": "pre-upgrade"}` to 1% of runs for
one week, create a LangSmith dataset from the tagged runs, then replay against
the new model and diff outputs. The sampling rule lives in LangSmith UI,
filtered by `metadata.eval_candidate`. See [LangSmith Setup](references/langsmith-setup.md)
for the annotation-queue and dataset-creation flow.

## Resources

- [LangSmith Observability concepts](https://docs.smith.langchain.com/observability/concepts)
- [LangSmith env variable reference](https://docs.smith.langchain.com/how_to_guides/setup/configure_project)
- [LangChain callbacks (1.0)](https://python.langchain.com/docs/concepts/callbacks/)
- [`BaseCallbackHandler` API](https://python.langchain.com/api_reference/core/callbacks/langchain_core.callbacks.base.BaseCallbackHandler.html)
- [`RunnableConfig` API](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.config.RunnableConfig.html)
- For OTEL-native instrumentation: `langchain-otel-observability` (L33) in this pack
- Pack pain catalog: `docs/pain-catalog.md` (entries P04, P25, P26, P28)

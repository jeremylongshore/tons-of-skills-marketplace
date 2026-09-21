---
name: langchain-otel-observability
description: 'Wire LangChain 1.0 / LangGraph 1.0 traces into an OpenTelemetry-native
  backend

  (Jaeger, Honeycomb, Grafana Tempo, Datadog) with LLM-specific SLOs, safe

  prompt-content policy, and subgraph-aware span propagation. Use when LangSmith

  is not the right fit (existing OTEL stack, compliance, multi-cloud) or

  alongside LangSmith for deep-system traces.

  Trigger with "langchain OTEL", "langchain opentelemetry", "langchain jaeger",

  "langchain honeycomb", "langchain SLO", "LLM span", "langchain tempo",

  "langchain datadog tracing".

  '
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(pip:*)
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
- opentelemetry
- jaeger
- honeycomb
compatibility: Designed for Claude Code
---
# LangChain OTEL Observability (Python)

## Overview

An engineer wires OpenTelemetry expecting to see prompts and responses in
Honeycomb. The traces land — but only timing, model name, and token counts
appear. The prompt body is blank. This is **not** a bug: it's the OTEL GenAI
semantic-conventions privacy-safe default (P27), where
`OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` is off. The instinct is to
flip it on and move on. On a multi-tenant workload that flip is a leak — the
next engineer to search traces for Tenant A sees Tenant B's PII in the results,
because redaction was supposed to happen upstream and never did.

A second trap lives inside LangGraph. A `BaseCallbackHandler` attached to the
parent runnable never fires on inner agent tool calls, because LangGraph
creates a child runtime per subgraph and callbacks do not inherit (P28). Spans
inside subgraphs appear orphaned in the waterfall — or they do not appear at
all — and SLO dashboards under-count latency on the exact calls that matter
most: the nested agent loops.

This skill wires LangChain 1.0 / LangGraph 1.0 into an OTEL-native backend
(Jaeger, Honeycomb, Grafana Tempo, Datadog) with a correct content-capture
policy, subgraph-aware span propagation, and five LLM-specific SLOs (p95 / p99
latency, error rate, cost-per-request, TTFT) with burn-rate alerts. Pin:
`langchain-core 1.0.x`, `langgraph 1.0.x`,
`opentelemetry-instrumentation-langchain >= 0.33`, OTEL GenAI semconv as of
2026-04. Pain-catalog anchors: P27, P28 (and cross-references P04, P34, P37).

## Prerequisites

- Python 3.10+
- `langchain-core >= 1.0, < 2.0`, `langgraph >= 1.0, < 2.0`
- An OTEL-native backend picked: Jaeger (dev), Honeycomb / Tempo / Datadog (prod)
- For multi-tenant: upstream redaction middleware already in place (see
  `langchain-security-basics` and `langchain-middleware-patterns`)
- Access to set env vars at deploy time (`OTLP_ENDPOINT`, API keys)

## Instructions

### Step 1 — Install the SDK and instrumentor, configure the exporter

```bash
pip install \
  opentelemetry-api \
  opentelemetry-sdk \
  opentelemetry-exporter-otlp-proto-http \
  "opentelemetry-instrumentation-langchain>=0.33"
```

```python
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.langchain import LangchainInstrumentor

resource = Resource.create({
    "service.name": "my-langchain-app",
    "service.version": "1.0.0",
    "deployment.environment": os.getenv("ENV", "dev"),
})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint=os.environ["OTLP_ENDPOINT"],       # per-backend; see matrix
        headers=_parse_headers(os.getenv("OTLP_HEADERS", "")),
    ),
    max_queue_size=2048,        # spans buffered before drop; raise for high volume
    max_export_batch_size=512,  # batched export keeps per-span overhead under 1ms
))
trace.set_tracer_provider(provider)

LangchainInstrumentor().instrument()   # emits gen_ai.* attrs on every run
```

`BatchSpanProcessor` keeps per-span overhead well under 1 ms. Use
`SimpleSpanProcessor` only in local dev — it blocks the call path per span.

Per-backend `OTLP_ENDPOINT` and header config lives in
[Backend Setup Matrix](references/backend-setup-matrix.md) — Jaeger,
Honeycomb, Grafana Tempo, Datadog.

### Step 2 — Verify the GenAI attribute schema

Trigger one call and inspect what landed in the backend. LangChain 1.0 emits
these `gen_ai.*` attributes natively on every chat-model span:

| Attribute | Example |
|-----------|---------|
| `gen_ai.system` | `anthropic` |
| `gen_ai.request.model` | `claude-sonnet-4-6` |
| `gen_ai.request.temperature` | `0.0` |
| `gen_ai.usage.input_tokens` | `1234` |
| `gen_ai.usage.output_tokens` | `567` |
| `gen_ai.response.finish_reasons` | `["stop"]` |

Missing anything? Likely a stale instrumentor version or an outdated provider
package. The full emitted-vs-custom matrix plus LangGraph's span taxonomy
(`LangGraph.invoke` → `LangGraph.node.*` → `LangGraph.subgraph.*`) is in
[GenAI Semantic Conventions](references/genai-semantic-conventions.md).

### Step 3 — Decide on prompt-content capture (critical — do not skip)

The engineer's instinct is to flip the capture flag to see prompts. Before
flipping it, classify the workload into one of these buckets:

| Workload | Flag | Notes |
|----------|------|-------|
| Dev / staging with synthetic inputs | `true` | Fine. Do not copy these traces to prod. |
| Single-tenant internal tool | `true` | Fine if RBAC on backend is tight. |
| Single-tenant product, signed compliance artifacts | `true` | BAA / DPIA in place; retention policy matches log retention. |
| Multi-tenant SaaS, **no upstream redaction** | **`false`** | Hard no. Fix redaction first. |
| Multi-tenant SaaS, **with upstream redaction** | `true` | Safe — the span sees the already-redacted text. |
| Healthcare / finance / legal without legal sign-off | **`false`** | Hard no. |

```bash
# trusted single-tenant ONLY
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
export TRACELOOP_TRACE_CONTENT=true   # OpenLLMetry alias; set both to be safe
```

Leave unset (default) anywhere else. To capture bodies in a multi-tenant
system, wire redaction middleware upstream of the model call first — see
[Prompt Content Policy](references/prompt-content-policy.md) and cross-reference
pack siblings `langchain-security-basics` (PII redaction middleware pattern,
P34) and `langchain-middleware-patterns` (middleware order: redact → cache →
model, P24). **Failure pattern P27** — prompts missing from traces because
capture was never opted in — is the #1 first-day OTEL complaint; make the
decision explicit instead of surprise-flipping the flag in prod.

### Step 4 — Propagate callbacks through subgraphs (P28)

LangGraph creates a child runtime per subgraph. Callbacks bound at the parent
definition time do **not** inherit:

```python
# WRONG — subagent spans orphaned or missing (P28)
agent = create_react_agent(model=llm, tools=tools).with_config(
    callbacks=[my_handler]  # bound at definition time; children do not see it
)
agent.invoke({"messages": [...]})

# RIGHT — pass callbacks at invocation via config; they propagate down
agent.invoke(
    {"messages": [...]},
    config={"callbacks": [my_handler]}  # invocation-time; inherited by children
)
```

The same rule applies to custom attribute handlers (e.g. the
`CostAttributeHandler` in the semantic-conventions reference that stamps
`gen_ai.usage.cost_usd` on each model span). Attach via
`config["callbacks"]`, never via `.with_config()`. **Failure pattern P28
symptom:** SLO dashboards show low latency because the slow nested spans are
missing entirely, not because the nested calls are fast.

### Step 5 — Define LLM SLOs and dashboards

Five SLIs matter from day one. All five derive from `gen_ai.*` span attributes
— no second pipeline required:

| SLI | Target example | Why |
|-----|----------------|-----|
| **p95 latency** (top-level chat) | `< 5 s` for chat UI | Provider variance dominates |
| **p99 latency** | `< 15 s` | Tail matters on chat; agents with tools live here |
| **Error rate** | `< 0.5%` | Includes 429s + `finish_reason IN ("length","content_filter")` |
| **Cost per request** (p95) | `< $0.05` | Catches `haiku`→`opus` regressions |
| **TTFT p95** (streaming) | `< 2 s` | Perceived latency, not total duration |

Concrete Honeycomb / PromQL / Datadog queries for each SLI, plus multi-window
multi-burn-rate alerts (14.4× / 1h fast burn, 6× / 6h slow burn), are in
[LLM SLO Dashboards](references/llm-slo-dashboards.md).

### Step 6 — Tune sampling

Defaults are wrong for two ends of the volume spectrum:

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

# Low/medium volume — keep everything for debuggability
# (< ~100 req/s) — SDK default 100% is fine

# High volume — head-sample, but carve out errors + slow spans via tail sampling
# at the OTEL Collector (see references/llm-slo-dashboards.md)
provider = TracerProvider(
    resource=resource,
    sampler=TraceIdRatioBased(0.10),  # 10% head sample
)
```

**Watch out:** head sampling at 10% means 90% of p99 outliers are discarded
before they reach the backend — p99 metrics become noisy and biased toward
the median. For tail-latency SLOs, move sampling to a Collector with
`tailsamplingprocessor` so errors and slow spans (`latency > 5000ms`) are
always kept while the rest is probabilistically sampled at 10%. Typical trace
overhead with `BatchSpanProcessor` at the 512-span batch size: **under 1 ms
per span**; recommended sampling rate for high-volume production is **1-10%**.

## Output

- OTEL exporter wired to a chosen backend (Jaeger / Honeycomb / Tempo / Datadog)
- `opentelemetry-instrumentation-langchain` emitting `gen_ai.*` attrs on every
  LangChain and LangGraph span
- Explicit prompt-content capture decision recorded against a workload bucket,
  with the multi-tenant guardrail enforced upstream
- Callbacks propagated via `config["callbacks"]` at invocation time so
  subgraph spans nest correctly under their parent node
- Five LLM SLOs (p95 / p99 latency, error rate, cost-per-request, TTFT) with
  dashboards and MWMBR burn-rate alerts
- Sampling strategy matched to workload volume and SLO precision needs

## Error Handling

| Symptom | Cause | Fix |
|---------|-------|-----|
| Traces land but prompt and completion bodies are empty | `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` unset (P27 — privacy-safe default) | Set to `true` **only** for the workload buckets in Step 3; for multi-tenant, wire upstream redaction first |
| Subgraph / tool-call spans orphaned or missing | Callbacks bound via `.with_config()` at definition time (P28) | Pass via `config["callbacks"]` at invocation time so children inherit |
| `gen_ai.usage.cache_read_input_tokens` resets every call | Per-call usage, aggregation is your job (P04) | Custom callback summing across calls keyed by `session.id`; see `langchain-model-inference` |
| p99 dashboard looks noisy and median-biased | 10% head sampling drops outliers before backend | Move to Collector `tailsamplingprocessor` — always keep errors and `latency > 5000ms` |
| Traces never appear | `OTLPSpanExporter` endpoint wrong protocol (gRPC on 4317 vs HTTP on 4318) | Verify with `curl -v $OTLP_ENDPOINT`; swap to the `proto-grpc` exporter package if your backend expects gRPC |
| Cost attribute missing from spans | LangChain 1.0 does not emit `gen_ai.usage.cost_usd` natively | Add a `BaseCallbackHandler` that computes from tokens × pricing; see semantic-conventions reference |
| PR review flags `sk-...` in trace attributes | Secrets in prompts captured via `gen_ai.prompt.content` (P37-adjacent) | Upstream redactor must strip API-key patterns before model call; audit via 0.1% sampler |
| Exporter dropping spans silently | Queue overflow at high volume | Increase `max_queue_size` to 4096+; add Collector between SDK and backend |

## Examples

### Running Jaeger locally for dev-loop tracing

Spin up Jaeger in Docker, point the SDK at `http://localhost:4318/v1/traces`,
leave content capture on (it's dev, inputs are synthetic). You get a generic
span waterfall — no LLM-specific UX, but good for verifying the instrumentor
emits what you expect before paying for a SaaS backend.

See [Backend Setup Matrix](references/backend-setup-matrix.md) for the
`docker run` command and SDK config.

### Investigating an agent latency incident in Honeycomb

Honeycomb's BubbleUp over `gen_ai.request.model`, `gen_ai.usage.input_tokens`,
and tool call count is the fastest path from "p95 spiked at 14:00" to "one
specific tool took 20 s because the vectorstore was slow." Requires
content-capture-off by default so you can turn the team loose on search
without PII-leak worries.

See [LLM SLO Dashboards](references/llm-slo-dashboards.md) for the exact
Honeycomb query shape.

### Dual-exporting during a LangSmith → Tempo migration

Register two `BatchSpanProcessor`s — one to LangSmith's OTLP endpoint, one to
Tempo. Run both for two weeks, compare waterfalls, cut over. LangSmith handles
LLM-specific analytics; Tempo handles unified trace search across LLM and
non-LLM services in your Grafana stack.

See [Backend Setup Matrix](references/backend-setup-matrix.md) dual-export
section.

## Resources

- [OTEL GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [OTEL Python SDK](https://opentelemetry.io/docs/languages/python/)
- [OpenLLMetry LangChain instrumentation](https://github.com/traceloop/openllmetry/tree/main/packages/opentelemetry-instrumentation-langchain)
- Honeycomb OTLP ingest
- [Grafana Tempo](https://grafana.com/docs/tempo/latest/)
- [Datadog OTLP](https://docs.datadoghq.com/opentelemetry/)
- [Google SRE — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- Pack cross-references: `langchain-security-basics` (redaction, P34),
  `langchain-middleware-patterns` (order: redact → cache → model, P24),
  `langchain-model-inference` (cost callback pattern, P04)
- Pack pain catalog: `docs/pain-catalog.md` — P27 (content-capture default),
  P28 (subgraph callback propagation), P04 (cache token aggregation),
  P34 (prompt injection), P37 (secrets in env / prompts)

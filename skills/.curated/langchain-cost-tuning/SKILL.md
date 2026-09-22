---
name: langchain-cost-tuning
description: 'Control LangChain 1.0 AI spend with accurate streaming token accounting,

  model tiering, provider-specific cache hit tuning, per-tenant budgets,

  and retry dedup. Use when AI spend grows faster than traffic, a cost

  regression lands, or you need per-tenant budget enforcement.

  Trigger with "langchain cost", "langchain token accounting",

  "langchain per-tenant budget", "langchain model tiering",

  "prompt cache savings".

  '
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(redis-cli:*)
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- cost
- tokens
- budget
compatibility: Designed for Claude Code
---
# LangChain Cost Tuning (Python)

## Overview

An engineer shipped a new research agent Tuesday. By Friday the Anthropic
bill had grown 6x while traffic grew 1.4x. The cost dashboard — wired to
`on_llm_end` — showed spend up maybe 2x. Reconciling against the provider
console on Monday surfaced two compounding bugs: (1) the agent's `ChatOpenAI`
fallback kept the default `max_retries=6`, so each logical call billed as up
to **7 requests** (P30); (2) retry middleware was registered *below* token
accounting, so every retry fired `on_llm_end` twice — the aggregator summed
both emissions while LangSmith deduped them by generation ID, undercounting
the dashboard by ~50% against actual billed rate (P25).

The fix took an afternoon: cap retries at 2, tag retries with a stable
`request_id`, and migrate token accounting to `AIMessage.usage_metadata` read
from `astream_events(version="v2")`. Finding the bug took a week. This skill
is that week compressed into a runbook.

Cost tuning for a LangChain 1.0 production app has five levers, each with a
sharp failure mode:

- **Token accounting** — `on_llm_end` lags streams by 5-30s (P01); retries double-count (P25); Anthropic cache savings aggregate per-call, never per-session (P04).
- **Retry discipline** — `max_retries=6` default on `ChatOpenAI` (P30); Anthropic 50 RPM tier throttles cached and uncached calls against the same budget (P31).
- **Agent loop caps** — `create_react_agent` defaults to `recursion_limit=25`; vague prompts burn a session's budget before `GraphRecursionError` surfaces (P10).
- **Caching** — `InMemoryCache` ignores bound tools in the cache key and returns wrong answers (P61); `RedisSemanticCache` ships with a 0.95 threshold that hits <5% of the time (P62).
- **Model tiering** — Running `claude-opus-4-5` on intent classification is 30-60x more expensive than `claude-haiku-4-5` for a task the cheaper model solves at equal quality.

Pin: `langchain-core 1.0.x`, `langchain-anthropic 1.0.x`, `langchain-openai 1.0.x`.
Pain-catalog anchors: P01, P04, P10, P23, P25, P30, P31, P61, P62.

## Prerequisites

- Python 3.10+
- `langchain-core >= 1.0, < 2.0`
- At least one provider package: `pip install langchain-anthropic langchain-openai`
- `redis-py >= 5.0` for budget middleware (optional; in-process dict works for dev)
- Provider console access (Anthropic, OpenAI) to reconcile `usage_metadata`
  against billed spend — you will need this to verify any instrumentation fix

## Instructions

### Step 1 — Read `usage_metadata`, never `response_metadata["token_usage"]`

LangChain 1.0 standardizes all provider usage into `AIMessage.usage_metadata`.
`response_metadata["token_usage"]` still exists as a compatibility shim but its
shape is provider-specific (Anthropic nests under `usage`, OpenAI flat, Gemini
uses different keys). Code that reads it directly will break when you switch
providers or when a provider SDK upgrades.

```python
from langchain_core.messages import AIMessage

def read_usage(msg: AIMessage) -> dict:
    """Canonical shape: input_tokens, output_tokens, input_token_details,
    output_token_details. Safe across Anthropic, OpenAI, Gemini."""
    meta = msg.usage_metadata or {}
    details_in = meta.get("input_token_details", {}) or {}
    details_out = meta.get("output_token_details", {}) or {}
    return {
        "input": meta.get("input_tokens", 0),
        "output": meta.get("output_tokens", 0),
        "cache_read": details_in.get("cache_read", 0),       # Anthropic
        "cache_creation": details_in.get("cache_creation", 0),
        "reasoning": details_out.get("reasoning", 0),        # OpenAI o1/o3
    }
```

Include `reasoning` in your output-billable total for o1/o3. A call with
`output_tokens=500` and `reasoning=2000` actually bills 2500 output tokens.

### Step 2 — Stream-accurate aggregation via `astream_events(version="v2")`

`on_llm_end` fires once after the stream closes, so dashboards lag by stream
duration (P01). Anthropic populates `usage_metadata` on the `message_start` and
`message_delta` events; OpenAI populates only the final chunk. Both show up as
`on_chat_model_stream` events in `astream_events`.

```python
async def metered_invoke(chain, inputs, meter):
    async for event in chain.astream_events(inputs, version="v2"):
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if getattr(chunk, "usage_metadata", None):
                meter.record(
                    run_id=event["run_id"],
                    usage=chunk.usage_metadata,
                )
```

See [Token Accounting Pitfalls](references/token-accounting-pitfalls.md) for
the full streaming-delta behavior across providers and reconciliation against
provider dashboards.

### Step 3 — Dedup retries on `run_id`, not prompt hash

Retry middleware runs the model twice on transient errors. Both emit usage
events. If the aggregator keys on prompt hash, it looks like one call cost
twice as much. If it keys on `run_id` (LangChain assigns one per generation
attempt), you can attach a stable `request_id` at the chain level and dedupe
on that (P25).

```python
from uuid import uuid4

class RetryAwareMeter:
    def __init__(self):
        self._seen: set[str] = set()
        self.totals = {"input": 0, "output": 0, "cache_read": 0}

    def record(self, run_id: str, usage: dict, request_id: str | None = None):
        # Keep only the last emission per logical request.
        # On retry: same request_id, different run_id -> overwrite.
        key = request_id or run_id
        if key in self._seen:
            # Retry emission — subtract prior, add new (last wins).
            prior = self._prior_by_key.get(key, {})
            for k in self.totals:
                self.totals[k] -= prior.get(k, 0)
        self._seen.add(key)
        self._prior_by_key[key] = usage
        self.totals["input"]  += usage.get("input_tokens", 0)
        self.totals["output"] += usage.get("output_tokens", 0)
        details = usage.get("input_token_details", {}) or {}
        self.totals["cache_read"] += details.get("cache_read", 0)
```

Inject `request_id` via `config={"metadata": {"request_id": str(uuid4())}}` on
each invoke. The meter reads `event["metadata"]["request_id"]` alongside
`run_id`.

Alternative: place token accounting **above** retry middleware in the chain —
retries happen inside, so only the successful attempt emits. This is simpler
but makes retries invisible to observability, which you usually want to see.

### Step 4 — Model tiering: draft cheap, finalize expensive

Most chains have a structural split: a cheap "understand the request" call and
an expensive "produce the final artifact" call. Running the expensive model on
both roughly triples cost for no quality gain.

**Per-1M pricing snapshot, 2026-04** (verify current prices before shipping at
https://www.anthropic.com/pricing and https://openai.com/api/pricing/):

| Model | Input $/1M | Output $/1M | Cache read $/1M | Role |
|---|---|---|---|---|
| `claude-haiku-4-5` | $1.00 | $5.00 | $0.10 | Draft, classify, route |
| `claude-sonnet-4-6` | $3.00 | $15.00 | $0.30 | Finalize, reason, extract |
| `claude-opus-4-5` | $15.00 | $75.00 | $1.50 | High-stakes, long-horizon |
| `gpt-4o-mini` | $0.15 | $0.60 | n/a (prefix cache only) | Draft, classify |
| `gpt-4o` | $2.50 | $10.00 | n/a | Finalize |
| `gpt-o3-mini` | $1.10 | $4.40 | n/a | Reasoning, planning |

Anthropic cache reads cost **10% of input**. Cache creation costs **125% of
input**. Break-even is ~4 uses of a cached prefix. See
[Cache Economics](references/cache-economics.md).

**Decision tree:**

```
input
  └── intent classification / routing
      └── gpt-4o-mini OR claude-haiku-4-5        (~$0.15-$1 per 1M in)
  └── generation / reasoning
      ├── single-pass, low-stakes
      │   └── gpt-4o-mini                         (draft)
      ├── single-pass, high-stakes (extraction, contracts)
      │   └── claude-sonnet-4-6                   (finalize)
      ├── multi-step reasoning
      │   └── gpt-o3-mini OR claude-sonnet-4-6    (plan)
      └── mission-critical long-horizon
          └── claude-opus-4-5                     (expensive, used sparingly)
```

Tiering is **wrong** when quality degrades silently — high-stakes extraction on
Haiku misses entities the Sonnet would catch. Always evaluate both tiers on a
gold set before committing. See [Model Tiering](references/model-tiering.md)
for the evaluation harness and a worked draft-then-finalize chain.

### Step 5 — Aggregate Anthropic cache usage per session and tenant (P04)

`usage_metadata["input_token_details"]["cache_read"]` reports per-call. To see
whether caching is paying for itself you need to aggregate per-session or
per-tenant and compare against cache-creation cost.

```python
class CacheLedger:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.read = 0           # billed at 0.1x input rate
        self.creation = 0       # billed at 1.25x input rate
        self.uncached_input = 0 # billed at 1.0x input rate

    def ingest(self, usage: dict):
        details = usage.get("input_token_details", {}) or {}
        self.read     += details.get("cache_read", 0)
        self.creation += details.get("cache_creation", 0)
        total_input = usage.get("input_tokens", 0)
        self.uncached_input += total_input - self.read - self.creation

    def savings_vs_no_cache(self, price_per_1m_input: float) -> float:
        # What we paid with cache vs. paying full price on all input.
        actual = (self.uncached_input * 1.00
                  + self.creation      * 1.25
                  + self.read          * 0.10) * price_per_1m_input / 1_000_000
        naive  = (self.uncached_input + self.creation + self.read) * price_per_1m_input / 1_000_000
        return naive - actual
```

Persist `CacheLedger` to Redis or Postgres keyed by `(tenant_id, day)`. If
savings is negative over a 24h window, caching is costing more than it saves —
your cached prefix is either too short or hit too rarely. See
[Cache Economics](references/cache-economics.md).

### Step 6 — Cache keys must include bound tools (P61)

`set_llm_cache(InMemoryCache())` hashes the prompt string only. A chain that
binds different tool sets will return wrong answers from the cache. This is
the most dangerous cache failure mode — it silently returns semantically
incorrect responses rather than missing.

**Do not use `InMemoryCache` on any chain that calls `bind_tools()`.** Use
`SQLiteCache` or `RedisSemanticCache` with a composite key:

```python
import hashlib, json

def tool_aware_key(prompt: str, tools: list) -> str:
    tools_fingerprint = hashlib.sha256(
        json.dumps([t.args_schema.model_json_schema() for t in tools],
                   sort_keys=True).encode()
    ).hexdigest()[:16]
    return f"{tools_fingerprint}:{hashlib.sha256(prompt.encode()).hexdigest()}"
```

Cross-reference: `langchain-middleware-patterns` covers cache-key layering in
middleware order (redact → cache → model) to avoid cross-tenant PII leaks.

### Step 7 — Tune semantic-cache threshold; ship a calibrated value, not the default (P62)

`RedisSemanticCache` defaults to `score_threshold=0.95`. On real workloads this
hits under 5% of the time. Production-tuned values land between 0.85 and 0.90.
Ship with a calibrated threshold, not the default:

1. Collect 200 real query pairs labeled "should return same answer" (positive)
   and "should return different answer" (negative).
2. Embed both sides of each pair with your embedding model.
3. For thresholds in `[0.80, 0.82, 0.84, …, 0.95]`, compute:
   - hit rate (% positive pairs above threshold)
   - false positive rate (% negative pairs above threshold)
4. Pick the lowest threshold where FPR < 2%.
5. Ship with a daily audit: sample 1% of cache hits, log to review queue.

If the curve flattens above 0.92 on positives, your embeddings are too weak
for semantic caching — consider exact-match `SQLiteCache` instead. See
[Cache Economics](references/cache-economics.md) for the calibration worksheet.

### Step 8 — Per-tenant budget middleware: soft warn, hard refuse

A single runaway tenant will consume the pack if left uncapped. LangChain 1.0
middleware slots cleanly in front of the model call; back it with a Redis
counter keyed per tenant per day.

```python
# Sketch — see references/per-tenant-budgets.md for the full middleware class.
async def budget_check(tenant_id: str, estimated_tokens: int) -> str:
    day_key = f"budget:{tenant_id}:{date.today().isoformat()}"
    used = int(await redis.get(day_key) or 0)
    soft = TENANT_SOFT_CAPS[tenant_id]  # alert only
    hard = TENANT_HARD_CAPS[tenant_id]  # refuse
    projected = used + estimated_tokens
    if projected > hard:
        raise BudgetExceeded(tenant_id, used, hard)
    if projected > soft:
        emit_alert(tenant_id, used, soft)
    return day_key  # caller increments on completion
```

Grace period: on hard-cap hit, allow in-flight calls (they already billed) but
reject new ones. Reset counter on UTC day boundary. See
[Per-Tenant Budgets](references/per-tenant-budgets.md) for full middleware
class, Redis schema, alert wiring, and grace-period semantics.

### Step 9 — Cap agent recursion (P10, P23)

`create_react_agent` defaults to `recursion_limit=25`. Agents on vague prompts
loop until limit, then raise `GraphRecursionError` — but every loop billed.
Cap at 5-10 for interactive, 10-15 for batch. If you use `trim_messages` on the
loop to control context, pass `include_system=True` and `start_on="human"` so
the trimmer does not drop the system prompt under pressure (P23).

Pair this with Step 8's budget middleware — the budget is the hard stop even
if the recursion cap is generous. Cross-reference: `langchain-langgraph-agents`
for routing patterns that terminate early on repeated tool calls.

## Output

- Canonical token read via `usage_metadata`, including reasoning and cache fields
- Streaming-accurate aggregation via `astream_events(version="v2")` on `on_chat_model_stream`
- Retry-aware meter that dedupes on `request_id`
- Model-tier decision tree with 2026-04 per-1M price snapshot
- `CacheLedger` that reports Anthropic cache savings per session/tenant
- Tool-aware cache keys for tool-binding chains
- Semantic-cache threshold calibrated (0.85-0.90) against a gold set
- Per-tenant budget middleware with soft and hard caps, Redis-backed
- `recursion_limit` set to match the workload, not the default 25

## Error Handling

| Error / symptom | Cause | Fix |
|---|---|---|
| Dashboard lags provider console by minutes on streaming calls | `on_llm_end` fires at stream close (P01) | Migrate to `astream_events(version="v2")` + `on_chat_model_stream` (Step 2) |
| Dashboard shows ~50% of billed spend | Retry middleware double-emits `on_llm_end`, aggregator sums both (P25) | Dedupe on `request_id` (Step 3), or move accounting above retry middleware |
| Cache hits return wrong answer for tool-binding chain | `InMemoryCache` hashes prompt only, ignores tools (P61) | Switch to `SQLiteCache` / `RedisSemanticCache` with tool-aware key (Step 6) |
| `RedisSemanticCache` hit rate < 5% on similar queries | Default `score_threshold=0.95` too strict (P62) | Calibrate to 0.85-0.90 against a gold pair set (Step 7) |
| Cost spike then `GraphRecursionError: Recursion limit of 25 reached` | Agent loops on vague prompt (P10) | Set `recursion_limit=5-10`; add budget middleware (Step 8) |
| Agent loses persona mid-conversation after many turns | `trim_messages` dropped system prompt (P23) | Pass `include_system=True, start_on="human"` |
| `max_retries=6` billing 7 requests per logical call | `ChatOpenAI` default (P30) | Set `max_retries=2`; log every retry via callback to verify |
| 429 on cache reads while input-token budget shows headroom | Anthropic 50 RPM throttles cached and uncached together (P31) | Budget RPM at client level (semaphore); separate monitors for read vs uncached |
| "Cache savings" metric always zero | `input_token_details.cache_read` reset per call (P04) | Aggregate via `CacheLedger` keyed per session/tenant (Step 5) |

## Examples

### Reconciling a 6x cost spike

A team saw Anthropic spend 6x over a week with traffic up 1.4x. The dashboard
showed only 2x. Root cause: `max_retries=6` on a flaky downstream API (P30)
plus retry middleware double-emit (P25) undercounting on the dashboard.

Fix sequence: (1) set `max_retries=2`, (2) attach `request_id` metadata at
chain entry, (3) migrate meter to `astream_events` with `run_id` dedup. After
the fix, dashboard matched billed spend within 1%.

See [Token Accounting Pitfalls](references/token-accounting-pitfalls.md) for
the full reconciliation procedure against provider console CSVs.

### Draft-then-finalize chain, measured savings

A document-extraction chain runs `claude-haiku-4-5` to extract a rough outline,
then `claude-sonnet-4-6` to validate and fill missing fields. On a 10K-doc
batch:

- Sonnet-only: ~$14/1K docs
- Haiku draft + Sonnet finalize: ~$4.20/1K docs
- Quality on the gold set: equivalent (F1 within 0.01)

The draft step burned 80% of the input tokens on the cheaper model.

See [Model Tiering](references/model-tiering.md) for the full chain, the gold
set, and the evaluation harness.

### Per-tenant runaway

One tenant's prompt template had an accidental double-interpolation of the
message history that grew context unboundedly each turn. Spend 400x'd overnight. The per-tenant
budget middleware (Step 8) hit hard cap at 10x normal, alerted on soft cap at
5x, refused new requests, allowed in-flight calls to complete.

See [Per-Tenant Budgets](references/per-tenant-budgets.md) for the full
middleware, alert wiring, and grace-period semantics.

## Resources

- Pair skill: `langchain-performance-tuning` (latency, throughput, cache hit
  rate) — this skill focuses on spend, not speed; reference each other on cache
  tuning
- Related: `langchain-middleware-patterns` (cache-key order, retry telemetry),
  `langchain-langgraph-agents` (recursion caps, early termination),
  `langchain-rate-limits` (RPM/ITPM budgeting, companion to Step 4)
- [LangChain Python: `usage_metadata`](https://python.langchain.com/api_reference/core/messages/langchain_core.messages.ai.UsageMetadata.html)
- [LangChain Python: `astream_events` v2](https://python.langchain.com/docs/how_to/streaming/#using-stream-events)
- [Anthropic pricing](https://www.anthropic.com/pricing) — verify current rates before shipping
- [OpenAI pricing](https://openai.com/api/pricing/) — verify current rates before shipping
- [Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- Pack pain catalog: `docs/pain-catalog.md` (P01, P04, P10, P23, P25, P30, P31, P61, P62)

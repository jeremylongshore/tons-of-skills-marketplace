---
name: langchain-middleware-patterns
description: "Build composable middleware for LangChain 1.0 chains and LangGraph 1.0\
  \ agents \u2014\nPII redaction, caching, retry, token budgets, guardrails \u2014\
  \ with ORDERING rules\nthat avoid cache-key leakage and double-counting. Use when\
  \ adding cross-cutting\nbehavior, hardening against prompt injection, enforcing\
  \ per-tenant budgets, or\ndebugging cache-poisoning incidents.\nTrigger with \"\
  langchain middleware\", \"langgraph middleware\", \"PII redaction\nmiddleware\"\
  , \"cache middleware order\", \"langchain guardrails\".\n"
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
- middleware
- security
- caching
compatibility: Designed for Claude Code
---
# LangChain Middleware Patterns (Python)

## Overview

Tenant A sends a prompt: *"Summarize this support ticket from **alice@acme.com**
about her overdue invoice."* The chain's caching middleware ran before the PII
redaction middleware, so the raw prompt — email and all — became part of the
cache key. Thirty seconds later Tenant B sends a semantically identical prompt
(different tenant, different customer, same shape). Cache hits. Tenant B's user
gets back a summary that names `alice@acme.com` and her overdue invoice. That is
pain-catalog entry **P24** in production, and it is a real class of incident —
post-mortems read like "we added caching to cut cost, leaked a customer's PII to
a different tenant within an hour."

The sibling failure modes:

- **P25** — Retry middleware runs the model call twice on a 429; both attempts
  fire `on_llm_end`; the token-usage aggregator sums both; a single logical call
  bills as two, tenant's per-session budget trips at 50% of true usage.
- **P10** — Agent loops exceed 15 iterations on vague prompts. There is no
  default cost cap. A per-session token-budget middleware solves this; without
  one, a single "help me with my account" prompt can burn thousands of tokens.
- **P34** — `Runnable.invoke` does not sanitize prompt injection. A RAG document
  containing `"Ignore previous instructions and..."` is followed verbatim.
  Guardrails middleware is your injection defense; without it, indirect prompt
  injection is a one-line exploit.
- **P61** — `set_llm_cache(InMemoryCache())` hashes the prompt string only.
  Two chains with different tool bindings return the same cached response;
  tools are silently ignored by the cache key.

This skill defines the canonical middleware order for LangChain 1.0 chains and
LangGraph 1.0 agents, with an ordering-invariants matrix (every adjacent pair
has a named failure mode if you swap them), six reference implementations, a
cache-key hash that includes prompt **plus bound-tools plus tenant_id**, retry
telemetry that deduplicates by `request_id`, and an integration test pattern
that asserts the ordering invariant on every build.

Pin: `langchain-core 1.0.x`, `langchain 1.0.x`, `langgraph 1.0.x`. Pain-catalog
anchors: **P10, P24, P25, P34, P61**, with supporting references to P27, P29,
P30, P33.

## Prerequisites

- Python 3.10+
- `langchain-core >= 1.0, < 2.0`
- `langgraph >= 1.0, < 2.0` (for agent middleware)
- At least one provider package: `pip install langchain-anthropic` (or openai)
- Optional: `presidio-analyzer` + `presidio-anonymizer` for PII NER beyond regex
- Optional: `redis` + `langchain-redis` for multi-worker cache and rate limiting

## Instructions

### Step 1 — Adopt the canonical middleware order

Every LangChain 1.0 chain and LangGraph 1.0 agent that goes to production
applies middleware in this order:

```
user → redact → guardrail → budget → cache → retry → model
```

- **redact → cache (P24):** cache key must be PII-free or Tenant A's PII leaks to Tenant B on a hit
- **guardrail → cache:** an injection-laden prompt must never become a cache entry
- **budget → cache:** cache hits count against RPS; check budget first so loops cannot DoS a session on hits alone
- **cache → retry:** cache hits bypass retry; retry wraps only the model call

Production chains typically run **4-6 middleware layers** with **<1ms per
layer** overhead (bench: p50 0.3ms/layer, p99 0.9ms on a 100-request sample).
See [ordering-invariants.md](references/ordering-invariants.md) for the full
pairwise matrix and the benchmark script.

### Step 2 — PII redaction middleware

Mask entities with reversible placeholders so the caller can reinsert in the
output — but the cache key and the model prompt only ever see redacted text.

```python
import re
from typing import Any

_REDACTORS = [
    ("EMAIL", re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")),
    ("PHONE", re.compile(r"\+?\d[\d\s\-\(\)]{7,}\d")),
    ("SSN",   re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("CC",    re.compile(r"\b(?:\d[ -]*?){13,16}\b")),
]

def redact(text: str) -> tuple[str, dict[str, str]]:
    pmap: dict[str, str] = {}
    for label, pattern in _REDACTORS:
        for i, match in enumerate(pattern.findall(text)):
            token = f"<{label}_{i}>"
            pmap[token] = match
            text = text.replace(match, token)
    return text, pmap

def redaction_middleware(inputs: dict[str, Any]) -> dict[str, Any]:
    redacted, pmap = redact(inputs["input"])
    return {**inputs, "input": redacted, "_pii_map": pmap}
```

For names, addresses, and custom entities, Presidio's `AnalyzerEngine` covers
20+ entity types. See [pii-redaction.md](references/pii-redaction.md) for the
regex vs spaCy vs Presidio tradeoff matrix, GDPR/HIPAA/PCI-DSS entity lists,
and the reinsertion pattern (return un-redacted output **only** to the
originating tenant — never cross-populate).

### Step 3 — Guardrails middleware

Detect injection patterns up front and wrap user content so the model treats
it as data. Two layers: pattern match (catches the 90% case cheaply) plus
prompt wrapping (neutralizes what slips through).

```python
INJECTION_PATTERNS = [
    re.compile(r"ignore (all |the )?(previous|prior|above) (instructions|rules)", re.I),
    re.compile(r"system prompt (is|was|now)", re.I),
    re.compile(r"you are now (a |an )?", re.I),
    re.compile(r"</?(system|instruction|prompt)>", re.I),
]

class GuardrailViolation(Exception):
    pass

def guardrail_middleware(inputs: dict[str, Any],
                        allowed_tools: set[str] | None = None) -> dict[str, Any]:
    for pattern in INJECTION_PATTERNS:
        if pattern.search(inputs["input"]):
            raise GuardrailViolation(f"Injection pattern matched: {pattern.pattern!r}")
    wrapped = f"<user_input>\n{inputs['input']}\n</user_input>"
    out = {**inputs, "input": wrapped}
    if allowed_tools is not None:
        out["_tool_allowlist"] = allowed_tools
    return out
```

Never rely on the model to "know what is an instruction" without wrapping.

### Step 4 — Token-budget middleware (per-session / per-tenant)

Directly addresses P10 — agents loop 15+ iterations on vague prompts and burn
thousands of tokens. The budget middleware raises before the model call if
the session is over ceiling.

```python
from dataclasses import dataclass, field
from collections import defaultdict
from threading import Lock

class BudgetExceeded(Exception): pass

@dataclass
class TokenBudget:
    ceiling: int = 50_000           # tokens per session
    _usage: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    _lock: Lock = field(default_factory=Lock)

    def record(self, session_id: str, tokens: int) -> None:
        with self._lock:
            self._usage[session_id] += tokens

    def check(self, session_id: str) -> None:
        with self._lock:
            used = self._usage[session_id]
        if used >= self.ceiling:
            raise BudgetExceeded(f"Session {session_id}: {used}/{self.ceiling}")

budget = TokenBudget(ceiling=50_000)

def budget_middleware(inputs: dict[str, Any]) -> dict[str, Any]:
    budget.check(inputs.get("session_id") or "anonymous")
    return inputs
```

Pair with a `BaseCallbackHandler.on_llm_end` that calls `budget.record(...)`
with `usage_metadata.input_tokens + output_tokens`. For multi-worker deploys,
back `TokenBudget` with Redis — per-process dicts are per-process (P29).

### Step 5 — Caching middleware with tool-aware key

P61 is the booby trap: `InMemoryCache()` hashes the prompt string only, so
two chains with different tool lists return the same cached response. Use a
custom key over **prompt + bound tools + tenant id**.

```python
import hashlib, json
from typing import Callable

def cache_key(prompt: str, bound_tools: list[dict] | None, tenant_id: str) -> str:
    """Blake2b-16 hash. Tool-aware, tenant-aware, collision-safe via \\x1f separator."""
    h = hashlib.blake2b(digest_size=16)
    h.update(prompt.encode("utf-8")); h.update(b"\x1f")
    if bound_tools:
        h.update(json.dumps(bound_tools, sort_keys=True).encode("utf-8"))
    h.update(b"\x1f"); h.update(tenant_id.encode("utf-8"))
    return h.hexdigest()

def cache_middleware(get: Callable[[str], Any | None], put: Callable[[str, Any], None]):
    def _run(inputs: dict[str, Any]) -> dict[str, Any]:
        key = cache_key(inputs["input"], inputs.get("_bound_tools"),
                        inputs.get("tenant_id", "default"))
        hit = get(key)
        if hit is not None:
            return {**inputs, "_cache_hit": True, "output": hit}
        inputs["_cache_key"] = key
        return inputs
    return _run
```

The cache key **must** be computed on the redacted prompt (Step 2 ran first)
and **must** include the tool schemas. See
[cache-key-design.md](references/cache-key-design.md) for backend comparison
(`InMemoryCache` / `SQLiteCache` / `RedisCache` / `RedisSemanticCache`),
invalidation strategies (TTL, schema-version bump, tenant-wide purge), and
the full pitfalls list including Unicode normalization and P62.

### Step 6 — Retry middleware with telemetry tagging

P25: retry runs the model call twice on a 429, both attempts emit
`on_llm_end`, the aggregator sums both, tenant budget trips at 50% of true
usage. Fix: attach a stable `request_id` on the first attempt, and have the
aggregator **replace** (not add) per `request_id` so only the last successful
attempt is counted.

```python
import time, uuid

RETRYABLE = (TimeoutError, ConnectionError,
             # Provider-specific — import from your provider SDK:
             # anthropic.RateLimitError, anthropic.APITimeoutError,
             # openai.RateLimitError, openai.APITimeoutError,
             )

def retry_middleware(max_retries: int = 2, base_delay: float = 1.0):
    def _run(inputs: dict[str, Any]) -> dict[str, Any]:
        request_id = inputs.get("request_id") or str(uuid.uuid4())
        return {**inputs, "request_id": request_id}
    return _run
```

See [retry-telemetry.md](references/retry-telemetry.md) for the full retry
loop, the dedup-by-`request_id` aggregator, provider-specific retryable
exception lists (Anthropic / OpenAI / Gemini), exponential backoff with
jitter, and a circuit breaker that stops retry storms on a dead upstream.

### Step 7 — Compose the middleware into a chain

```python
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

# Order matters. See Step 1 for why.
chain = (
    RunnableLambda(redaction_middleware)
    | RunnableLambda(guardrail_middleware)
    | RunnableLambda(budget_middleware)
    | RunnableLambda(cache_middleware(cache_get, cache_put))
    | RunnableLambda(retry_middleware(max_retries=2))
    | model                             # ChatAnthropic / ChatOpenAI
)
```

For LangGraph agents, the same layers apply but are wired as **nodes with
conditional edges** — a `budget` node that routes to `END` on violation, a
`guardrail` node that routes to an error handler on injection match, and so on.
See the LangGraph adaptation in `references/ordering-invariants.md`.

### Step 8 — Integration test: assert the ordering invariant

Ordering is invisible in code review until someone moves cache above redact.
Assert the invariant in a test that runs on every commit.

```python
def test_cache_key_does_not_leak_pii():
    """P24 — cache key built from REDACTED prompt, not raw."""
    a = redaction_middleware({"input": "Ticket from alice@acme.com", "tenant_id": "T1"})
    b = redaction_middleware({"input": "Ticket from bob@other.com",  "tenant_id": "T1"})
    assert cache_key(a["input"], None, "T1") == cache_key(b["input"], None, "T1")

def test_cache_key_tenant_isolation():
    """P24/P33 — same prompt, different tenants, different cache keys."""
    assert cache_key("notes", None, "T1") != cache_key("notes", None, "T2")

def test_cache_key_tool_aware():
    """P61 — same prompt, different tool bindings, different cache keys."""
    assert cache_key("p", [{"name":"search"}], "T") != cache_key("p", [{"name":"code_exec"}], "T")
```

Run in CI. A failure means someone broke the ordering invariant — chain does
not merge until it is fixed.

## Output

- Six middleware layers composed in canonical order: redact → guardrail → budget → cache → retry → model
- Reversible PII redaction with placeholder map (emails, phones, SSNs, credit cards; Presidio optional for names/addresses)
- Guardrails middleware with injection-pattern detection and user-content wrapping
- Per-session / per-tenant token budget with thread-safe counter
- Cache-key hash that includes prompt + bound-tool schemas + tenant id (fixes P61 and P24)
- Retry middleware with `request_id` tagging so the token aggregator deduplicates (fixes P25)
- Integration tests asserting the ordering invariant

## Error Handling

| Error / failure mode | Cause | Fix |
|---|---|---|
| Tenant B receives Tenant A's PII on a cache hit | **Cache before redact (P24)** — raw PII went into the cache key | Reorder: redaction runs first; cache key built on redacted prompt + tenant_id |
| Token-usage aggregator reports 2x actual usage after a retry | **Retry double-count (P25)** — both attempts emit `on_llm_end`, aggregator sums | Attach `request_id` on first attempt; aggregator dedupes by `request_id` |
| Two chains with different bound tools return same cached response | **P61** — `InMemoryCache()` hashes prompt string only, not tool schemas | Use `cache_key(prompt, bound_tools, tenant_id)` with `blake2b` over all three |
| Agent loops past 15 iterations on vague prompt; bill spikes | **No token budget (P10)** — `recursion_limit=25` default has no cost ceiling | Insert `budget_middleware` before cache; `raise BudgetExceeded` if session over ceiling |
| Model follows `"Ignore previous instructions and..."` in a RAG doc | **No guardrail (P34)** — `Runnable.invoke` does not sanitize prompt injection | Insert `guardrail_middleware` after redact, before cache; wrap user input in `<user_input>` tags |
| `GuardrailViolation` raised on legitimate prompt | Over-eager injection pattern match | Tune patterns in `references/ordering-invariants.md`; log false positives for iteration |
| Cache poisoning after a deploy that changed tool schemas | Old cache entries reference old tool list | Bump a `schema_version` constant and include it in the cache key |
| Budget tracker drift in multi-worker deploy | **P29 analog** — in-process dict is per-worker only | Back `TokenBudget` with Redis or another shared store |
| Retries still fire on `KeyboardInterrupt` during local dev | **P07** — default `exceptions_to_handle` includes `KeyboardInterrupt` on Python < 3.12 | Explicitly list retryable exceptions; never catch `BaseException` |

## Examples

### Building a chain end-to-end with correct order

The Step 7 composition shows the six layers in order. In production code this
usually lives in a factory — `build_chain(tenant_id: str, allowed_tools: set[str])` —
that closes over the tenant-scoped cache backend and budget instance. The
factory makes the order explicit and testable.

### LangGraph agent version

The same six layers in a LangGraph agent become six nodes plus conditional
edges. `budget` routes to `END` on violation; `guardrail` routes to
`error_handler` on injection match; `cache` routes to `END` on hit. See
`references/ordering-invariants.md` for the adapted graph topology.

### Debugging a cache-poisoning incident

Post-mortem template: (1) enumerate cache entries, (2) check whether keys were
built pre- or post-redaction, (3) identify the first cross-tenant hit in logs,
(4) purge by tenant prefix or full flush, (5) add the ordering integration
test from Step 8 so this cannot recur.

## Resources

- [LangChain 1.0 / LangGraph 1.0 release announcement](https://blog.langchain.com/langchain-langgraph-1dot0/)
- [LangChain how-to: caching](https://python.langchain.com/docs/how_to/chat_model_caching/)
- [LangChain callbacks](https://python.langchain.com/docs/concepts/callbacks/)
- [LangGraph middleware / pre_model_hook](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/)
- [Microsoft Presidio (PII detection)](https://microsoft.github.io/presidio/)
- [OWASP LLM01: Prompt Injection](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- Pack pain catalog: `docs/pain-catalog.md` (entries **P10, P24, P25, P34, P61**, plus P27, P29, P30, P33)
- Companion references: [ordering-invariants.md](references/ordering-invariants.md), [pii-redaction.md](references/pii-redaction.md), [cache-key-design.md](references/cache-key-design.md), [retry-telemetry.md](references/retry-telemetry.md)

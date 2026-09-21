---
name: langchain-enterprise-rbac
description: "Enforce tenant isolation and role-based access across LangChain 1.0\
  \ chains and\nLangGraph 1.0 agents \u2014 per-request retriever construction, tenant-scoped\
  \ rate\nlimits, role-scoped tool allowlists, and structured audit logs. Use when\n\
  building multi-tenant saas, passing soc2 review, or debugging cross-tenant\nleak.\
  \ Trigger with \"langchain multi-tenant\", \"langchain tenant isolation\",\n\"langchain\
  \ rbac\", \"langchain row-level security\", \"langchain audit log\".\n"
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
- multi-tenant
- rbac
- enterprise
- security
compatibility: Designed for Claude Code
---
# LangChain Enterprise RBAC (Python)

## Overview

A B2B SaaS team shipped their first RAG feature for two tenants. The factory
code looked innocent: build `PineconeVectorStore` once at module import with
`namespace="acme-corp"` (the first tenant), convert it to a retriever, store
it in a module global, reuse on every request. Six weeks later tenant "Initech"
went live. Their first search returned three documents from Acme Corp.

The singleton retriever had captured the Acme namespace at process start.
`RunnableConfig.configurable["tenant_id"]` was being passed in — but the
retriever never read it, because the filter was baked in. Every request for
every tenant hit the same Pinecone namespace. Security review caught it three
days later and put a hold on the SOC2 renewal. This is pain-catalog entry
**P33**, the single most common cause of cross-tenant leak in LangChain 1.0
production.

This skill fixes it with four workstreams:

- **P33 — retriever-per-request factory** — build the retriever inside the
  chain or agent invocation, keyed by `tenant_id` from `RunnableConfig`. Never
  at module scope. Unit-test with two tenants and assert non-overlap.
- **Role-scoped tool allowlist** — build the agent per-request with only the
  tools the current user's role permits. Forbidden tools are not passed to
  `create_agent` at all, so the model cannot call them even if it tries.
- **Per-tenant rate limit + budget** — scope the `InMemoryRateLimiter` (or a
  Redis-backed equivalent) by `tenant_id`, and check a per-tenant USD budget
  before invoking the model.
- **Structured audit log** — JSON log with `user_id`, `tenant_id`,
  `chain_name`, `tools_called`, `cost_usd`, `outcome`, emitted in both success
  and failure paths. Ships to SIEM or BigQuery.

Two failure patterns anchor this skill: **import-time retriever binding (P33)**
and **missing audit log on tool failure** (the `try` block logs on success but
the `except` branch re-raises without emitting, so incident response has no
record of denied tool calls). Pinned: `langchain-core 1.0.x`,
`langgraph 1.0.x`, `langchain-anthropic 1.0.x`, `langchain-openai 1.0.x`,
`langchain-postgres 0.0.15+` (for PGVector RLS), `pinecone-client 5.x`,
`chromadb 0.5.x`. Pain-catalog anchors: **P33 primary**, P18, P24, P31, P37.

## Prerequisites

- Python 3.10+
- `langchain-core >= 1.0, < 2.0`, `langgraph >= 1.0, < 2.0`
- At least one vector-store backend: `pinecone-client`, `langchain-postgres`
  (PGVector), `chromadb`, or `faiss-cpu` (single-tenant only — see §Step 2)
- A structured logging sink: stdout JSON for local, Cloud Logging / Datadog /
  Splunk HEC / BigQuery streaming insert for production
- A tenant authorization claim in every request (JWT `tid` claim, session
  cookie, or header — the auth boundary is out of scope for this skill but
  assumed correct)

## Instructions

### Step 1 — Build the retriever per-request, never at import

Move retriever construction inside the chain or agent invocation, keyed by
`config["configurable"]["tenant_id"]`.

```python
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_pinecone import PineconeVectorStore

# WRONG — retriever bound at import time with first tenant's namespace.
# RETRIEVER = PineconeVectorStore(index_name="rag", namespace="acme-corp",
#     embedding=emb).as_retriever(search_kwargs={"k": 4})

# RIGHT — factory called per-request, reads tenant from RunnableConfig.
def retriever_for(config: RunnableConfig):
    tenant_id = config["configurable"]["tenant_id"]  # required, no default
    if not tenant_id:
        raise PermissionError("tenant_id missing from RunnableConfig")
    store = PineconeVectorStore(
        index_name="rag",
        namespace=tenant_id,   # P33 fix — namespace per-invocation
        embedding=emb,
    )
    return store.as_retriever(search_kwargs={"k": 4})

def retrieve(inputs: dict, config: RunnableConfig):
    return retriever_for(config).invoke(inputs["query"])

chain = RunnableLambda(retrieve) | prompt | model
result = chain.invoke({"query": "..."},
    config={"configurable": {"tenant_id": "initech"}})
```

No default on `tenant_id` — a missing tenant must be a hard error, not a silent
fallback. See [Retriever-per-request](references/retriever-per-request.md) for
factory lifecycle and PGVector RLS / Chroma / FAISS adapters.

### Step 2 — Pick a vector-store isolation primitive

| Store | Isolation primitive | Per-tenant latency | Max tenants | Safety notes |
|---|---|---|---|---|
| **Pinecone** | `namespace=tenant_id` per query | ~40ms p50 (shared index) | 100,000+ per index | Namespace is the documented isolation boundary; still apply metadata `{"tenant_id": tid}` as defense in depth |
| **PGVector** | Postgres row-level security (RLS) on `tenant_id` column | ~20ms p50 (HNSW index) | Bounded by Postgres row count | Use `SET LOCAL app.tenant_id = :tid` per transaction; RLS policy `USING (tenant_id = current_setting('app.tenant_id'))` |
| **Chroma** | Collection-per-tenant (`get_or_create_collection(name=tid)`) | ~30ms p50 | ~1,000 before metadata overhead | Good isolation at small scale; collection creation is synchronous — provision lazily but cache the handle per-request |
| **FAISS** | In-process index-per-tenant | ~5ms p50 (in-memory) | 10-50 practical limit | Poor fit for multi-tenant SaaS — cannot shard across processes, reloads on every deploy, no durable filter. Use for single-tenant evaluation only |

Pinecone scales highest. PGVector with RLS is the strongest primitive when
isolation must be auditable at the database layer (RLS is enforced by the
server even if application code is bypassed). Chroma is fine for ≤1,000
tenants. FAISS is not a multi-tenant production choice — document so future
engineers do not adopt it. See
[Vector-store isolation](references/vector-store-isolation.md) for the PGVector
RLS DDL and Chroma lifecycle.

### Step 3 — Build the agent per-request with a role-scoped tool allowlist

Never bind every tool to every agent and trust the model to pick the right one.
Build the agent inside the request handler with only the tools the user's role
permits.

```python
from langgraph.prebuilt import create_agent

# Map role -> allowed tool names. Owned by IAM config, not the skill.
ROLE_TOOLS: dict[str, set[str]] = {
    "viewer": {"search_docs"},
    "editor": {"search_docs", "create_note"},
    "admin":  {"search_docs", "create_note", "delete_note", "export_audit"},
}
ALL_TOOLS = {t.name: t for t in [search_docs, create_note, delete_note, export_audit]}

def agent_for(user_role: str, tenant_id: str):
    allowed = ROLE_TOOLS.get(user_role, set())
    tools = [ALL_TOOLS[n] for n in allowed if n in ALL_TOOLS]
    # Forbidden tools are not passed in — the model never sees them.
    return create_agent(model, tools=tools)

agent = agent_for(user_role="viewer", tenant_id="initech")
# viewer has no delete_note -> the agent cannot call it.
```

Add a denylist for dangerous argument patterns (SQL with `DROP` / `TRUNCATE`,
shell with `rm -rf` / `sudo`, URLs to internal metadata endpoints) via a
`pre_model_hook` or tool wrapper — allowlist bounds *which* tools run,
denylist bounds *what arguments* they accept. See
[Role-scoped tool allowlist](references/role-scoped-tool-allowlist.md).

### Step 4 — Scope rate limits and budgets by tenant

Per-tenant limits prevent one tenant's runaway job from exhausting shared model
capacity. Rate-limit detail is covered in `langchain-rate-limits`; cost-budget
detail in `langchain-cost-tuning`. The only RBAC-specific requirement here:
**limiter key must include `tenant_id`** — never a process-global singleton.

```python
# Sketch only — see langchain-rate-limits for production implementation.
_limiters: dict[str, InMemoryRateLimiter] = {}

def limiter_for(tenant_id: str) -> InMemoryRateLimiter:
    if tenant_id not in _limiters:
        # Tier lookup — different plans get different budgets.
        rps = TENANT_TIER_LIMITS.get(tenant_id, 1.0)  # 1.0 rps = free-tier default
        _limiters[tenant_id] = InMemoryRateLimiter(requests_per_second=rps)
    return _limiters[tenant_id]
```

For multi-process deployments use a Redis-backed limiter — `InMemoryRateLimiter`
is per-process only, so 1 rps × 8 workers = 8 rps aggregate.

### Step 5 — Emit a structured audit log on every invocation

The audit log is the record of truth during an incident. Emit on both success
and failure paths. The common bug is logging in the `try` block only — when a
tool raises, the `except` branch re-raises without emitting, so the incident
responder has no record of the denied call.

```python
import json
import time
import uuid
from contextlib import contextmanager

@contextmanager
def audit(ctx: dict):
    started = time.monotonic()
    trace_id = str(uuid.uuid4())
    record = {**ctx, "trace_id": trace_id, "outcome": "pending"}
    try:
        yield record
        record["outcome"] = record.get("outcome", "success")
    except Exception as exc:
        record["outcome"] = "error"
        record["error_class"] = type(exc).__name__
        record["error_message"] = str(exc)[:500]  # truncate — no PII leakage
        raise
    finally:
        record["latency_ms"] = int((time.monotonic() - started) * 1000)  # 1000 ms per second
        print(json.dumps(record))  # or a SIEM / BigQuery client

ctx = {
    "user_id": "u_42",
    "tenant_id": "initech",
    "chain_name": "rag-qa-v3",
    "role": "viewer",
}
with audit(ctx) as record:
    result = chain.invoke(inputs, config={"configurable": ctx})
    record["tools_called"] = [m.name for m in result.get("tool_calls", [])]
    record["input_tokens"]  = result["usage"]["input_tokens"]
    record["output_tokens"] = result["usage"]["output_tokens"]
    record["cost_usd"]      = cost_of(result["usage"])
```

The `try / finally` pattern guarantees emission even when the chain raises.
Required fields: `user_id`, `tenant_id`, `chain_name`, `outcome`, `latency_ms`,
`trace_id`. Recommended: `tools_called`, `input_tokens`, `output_tokens`,
`cost_usd`, `role`. See [Audit-log schema](references/audit-log-schema.md) for
the full catalog, JSON example, SIEM / BigQuery ingestion, and query recipes.

### Step 6 — Two-tenant regression test for cross-tenant leak

The test that would have caught P33 on day one. Seed two tenants with distinct
documents, run a golden query as each, assert non-overlap on retrieved IDs.

```python
import pytest

@pytest.fixture
def two_tenant_store():
    seed("acme",    ["acme-doc-1",    "acme-doc-2"])
    seed("initech", ["initech-doc-1", "initech-doc-2"])
    yield
    cleanup(["acme", "initech"])

def test_tenant_isolation(two_tenant_store):
    acme_hits    = chain.invoke({"query": "q"}, config={"configurable": {"tenant_id": "acme"}})
    initech_hits = chain.invoke({"query": "q"}, config={"configurable": {"tenant_id": "initech"}})
    acme_ids    = {d.id for d in acme_hits["documents"]}
    initech_ids = {d.id for d in initech_hits["documents"]}
    assert acme_ids.isdisjoint(initech_ids), \
        f"CROSS-TENANT LEAK: overlap={acme_ids & initech_ids}"
    assert all("acme"    in doc_id for doc_id in acme_ids)
    assert all("initech" in doc_id for doc_id in initech_ids)
```

Run in CI on every PR. A regression to import-time retriever binding fails
immediately. See
[Multi-tenant regression tests](references/multi-tenant-regression-tests.md)
for fixtures covering tool-allowlist violation, audit-log completeness, and
rate-limiter scoping.

## Output

- Retriever factory keyed by `RunnableConfig.configurable["tenant_id"]`
- Vector-store choice made against the 4-row isolation table, not by defaults
- Agent constructed per-request with a role-scoped tool allowlist (not a
  deny-all at tool-call time)
- Rate limiter and cost budget keyed by `tenant_id`, never a process global
- Structured audit log emitted on both success and failure paths with
  required fields (`user_id`, `tenant_id`, `chain_name`, `outcome`,
  `latency_ms`, `trace_id`)
- Two-tenant pytest fixture in CI that asserts cross-tenant non-overlap

## Error Handling

| Error / symptom | Cause | Fix |
|---|---|---|
| Tenant A's docs returned to Tenant B after deploy | Singleton retriever bound at import (P33) | Move to per-request factory keyed by `config["configurable"]["tenant_id"]` (Step 1) |
| `KeyError: 'tenant_id'` in retriever factory | Caller forgot to pass `configurable` | Fail fast with `PermissionError`; never default to a tenant |
| `permission denied for relation documents` on PGVector | RLS policy enabled but session variable not set | `SET LOCAL app.tenant_id = :tid` inside the transaction |
| Agent calls a tool the user's role should not have | Every tool bound at agent construction | Build agent per-request with only role-permitted tools (Step 3) |
| Audit log missing entries for errored invocations | Log emitted inside `try` only, not `finally` | Move emit to `finally` block (Step 5) |
| Shared rate limit trips all tenants when one misbehaves | Process-global `InMemoryRateLimiter` | Key limiter by `tenant_id`; use Redis-backed for multi-process (Step 4) |
| Cross-tenant leak regression ships to prod | No two-tenant CI test | Add the Step 6 fixture; run on every PR |
| Audit log contains raw PII from prompts | Logging `inputs` verbatim | Log field names / token counts / IDs only; never log raw message content |

## Examples

### Full multi-tenant RAG agent, end-to-end

Combines all six steps: retriever-per-request, Pinecone namespace isolation,
role-scoped tools, per-tenant rate limit, audit-log context manager, regression
test. Assembly is ~80 lines. See
[Retriever-per-request](references/retriever-per-request.md).

### Migrating from a shared singleton to per-request

Wrap the old singleton, add the factory alongside, route by feature flag, ship
the regression test first, flip the flag, delete the singleton. Typical
migration window: 1-2 sprints. See
[Multi-tenant regression tests](references/multi-tenant-regression-tests.md).

### Exporting audit log to BigQuery for compliance queries

Stream each record to BigQuery per the
[Audit-log schema](references/audit-log-schema.md). Recipes: "tool calls by
user X in last 24h", "tenants with >1% error rate", "highest-spend tenants".

## Resources

- [LangChain Python: `RunnableConfig`](https://python.langchain.com/docs/concepts/runnables/#runnableconfig)
- [LangChain Python: Multiple retrievers](https://python.langchain.com/docs/how_to/multiple_queries/)
- [LangGraph: `create_agent`](https://langchain-ai.github.io/langgraph/agents/agents/)
- [Pinecone: Namespaces](https://docs.pinecone.io/guides/indexes/use-namespaces)
- [PGVector: Row-level security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [SOC2 CC6.1 — logical access controls](https://www.aicpa-cima.com/)
- Pack pain catalog: `docs/pain-catalog.md` (primary P33; adjacent P18, P24, P31, P37)
- Sibling skills: `langchain-rate-limits` (per-tenant limiters), `langchain-cost-tuning` (per-tenant budgets), `langchain-security-basics` (input redaction upstream of audit log)

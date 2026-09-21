---
name: langchain-reference-architecture
description: "A reference layered architecture for production LangChain 1.0 / LangGraph\
  \ 1.0\nservices \u2014 LLM factory with version-safe defaults, chain/graph registry,\n\
  retriever and tool DI, Pydantic-validated config, per-request tenant scoping,\n\
  middleware ordering, checkpointer selection per environment. Use when starting\n\
  a new service, refactoring a tangled chain, or onboarding a team to existing code.\n\
  Trigger with \"langchain architecture\", \"langchain llm factory\",\n\"langchain\
  \ chain registry\", \"langchain dependency injection\",\n\"langchain project structure\"\
  .\n"
allowed-tools: Read, Write, Edit
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- architecture
- reference-architecture
- patterns
compatibility: Designed for Claude Code
---
# LangChain Reference Architecture (Python)

## Overview

Eight months into a LangChain service, a code review surfaces the mess.
Twelve chain definitions live inlined inside FastAPI route handlers. Three
retrievers are constructed at module-global scope, one bound to
`tenant_id="acme"` because that was the first tenant in the pilot —
that retriever now returns Acme's documents to every other tenant, a P33
leak that has been live in production for six weeks.
`max_retries=6` is hardcoded at four separate call sites. A
`RunnableWithMessageHistory` backed by the default
`InMemoryChatMessageHistory` loses every conversation on pod restart
(P22) — which is most days, because Cloud Run scales to zero.
Config is read from `os.environ` in three modules with three different
fallback strategies. There is no place to put a new provider without
touching seven files, and nobody remembers why the retriever is built
at import time.

The fix is not "rename a variable." The fix is an architecture that made
every one of those mistakes hard to write. This skill is the target
layered architecture:

- `app/` — FastAPI routes. Thin. Parses HTTP, calls into `services`,
  serializes response. No chain logic, no vendor clients, no env vars.
- `services/` — chain and graph definitions. Take dependencies through
  constructor args, not module-level imports.
- `adapters/` — vendor clients, LLM factory, retriever factory, tool
  factory. This is where `langchain-anthropic` is imported. Nowhere else.
- `config/` — one Pydantic `Settings` class. `SecretStr` for keys,
  `Literal["dev","staging","prod"]` for env names, `.env` file loader.
- `domain/` — Pydantic models, typed LangGraph state, enums. No I/O.

Five layers, five imports deep at most. Dependency direction is
**strictly downward**. `app` imports `services`; `services` imports
`adapters`; `adapters` imports `config` and `domain`. Never the reverse.
Import-linter enforces this in CI. Pain-catalog anchors: P22 (in-memory
history loses messages — architectural fix is persistent history
injected via DI) and P33 (per-tenant vector stores leak if retriever
bound at import — architectural fix is per-request factory). Adjacent:
P10 (recursion limits), P24 (middleware order), P28 (callback
inheritance). Pin: `langchain-core 1.0.x`, `langgraph 1.0.x`,
`langchain-anthropic 1.0.x`, `langchain-openai 1.0.x`, `pydantic 2.x`,
`import-linter 2.x`.

## Prerequisites

- Python 3.10+
- `langchain-core >= 1.0, < 2.0`, `langgraph >= 1.0, < 2.0`
- `pydantic >= 2.5` and `pydantic-settings >= 2.1`
- `import-linter >= 2.0` for layer enforcement in CI
- Provider package(s): `langchain-anthropic`, `langchain-openai`, etc.
- For staging/prod checkpointer: `langgraph-checkpoint-postgres` and a Postgres instance
- Cross-reference: sibling skill `langchain-model-inference` for the LLM factory's version-safe defaults

## Instructions

### Step 1 — Adopt the 5-layer directory layout

```
src/my_service/
├── app/                         # Layer 1: HTTP boundary (FastAPI)
│   ├── __init__.py
│   ├── main.py                  # FastAPI instance, DI wiring, lifespan
│   ├── routes/
│   │   ├── support.py           # POST /support → services.support.run(...)
│   │   └── health.py
│   └── deps.py                  # FastAPI Depends() providers
├── services/                    # Layer 2: chain and graph definitions
│   ├── __init__.py
│   ├── registry.py              # name → builder lookup
│   ├── support/
│   │   ├── chain.py             # SupportChain(llm, retriever, memory)
│   │   └── graph.py             # SupportGraph (LangGraph StateGraph)
│   └── triage/
│       └── chain.py
├── adapters/                    # Layer 3: vendor integrations
│   ├── __init__.py
│   ├── llm_factory.py           # chat_model(provider, **kwargs) → BaseChatModel
│   ├── retriever_factory.py     # retriever_for(tenant_id) → Retriever
│   ├── tool_factory.py          # tools_for(tenant_id) → list[BaseTool]
│   ├── checkpointer.py          # checkpointer_for(env) → BaseCheckpointSaver
│   └── history.py               # history_for(session_id, tenant_id) → BaseChatMessageHistory
├── config/                      # Layer 4: configuration
│   ├── __init__.py
│   └── settings.py              # Pydantic Settings
└── domain/                      # Layer 5: pure models, no I/O
    ├── __init__.py
    ├── state.py                 # TypedDict / Pydantic for LangGraph state
    └── models.py                # request/response schemas
tests/
├── unit/                        # fake adapters, assert service logic
├── integration/                 # real adapters against ephemeral infra
└── contract/                    # schema snapshots (e.g., tool specs)
pyproject.toml                   # includes [tool.importlinter] contracts
```

Typical depth is 5 layers. See [Directory Layout](references/directory-layout.md) for the full tree with file-naming conventions.

### Step 2 — Centralize LLM defaults in an `adapters/llm_factory.py`

Chains depend on the `BaseChatModel` protocol, not a concrete class. The factory is the one place version-safe defaults live:

```python
# src/my_service/adapters/llm_factory.py
from langchain_core.language_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

_SAFE_DEFAULTS = {"timeout": 30, "max_retries": 2}

def chat_model(provider: str, **overrides) -> BaseChatModel:
    defaults = {**_SAFE_DEFAULTS, **overrides}  # caller wins
    if provider == "anthropic":
        return ChatAnthropic(model="claude-sonnet-4-6", **defaults)
    if provider == "openai":
        return ChatOpenAI(model="gpt-4o", **defaults)
    raise ValueError(f"Unknown provider: {provider!r}")
```

The `max_retries=6` scatter in the mess-case becomes `max_retries=2` in exactly one file. Services that want a longer timeout pass `timeout=60` — but they never set `max_retries=6` by accident. Cross-reference `langchain-model-inference` Step 3 for the factory pattern's provenance; see [LLM Factory Pattern](references/llm-factory-pattern.md) for per-provider variants and caching.

### Step 3 — Replace scattered imports with a chain/graph registry

```python
# src/my_service/services/registry.py
from typing import Callable, Protocol
from langchain_core.runnables import Runnable

class ChainBuilder(Protocol):
    def __call__(self, *, tenant_id: str) -> Runnable: ...

_BUILDERS: dict[str, ChainBuilder] = {}

def register(name: str):
    def decorator(fn: ChainBuilder) -> ChainBuilder:
        _BUILDERS[name] = fn
        return fn
    return decorator

def get(name: str, *, tenant_id: str) -> Runnable:
    try:
        return _BUILDERSname
    except KeyError:
        raise KeyError(f"No chain registered under {name!r}. Known: {list(_BUILDERS)}")
```

Each service module registers itself:

```python
# src/my_service/services/support/chain.py
from my_service.services.registry import register
from my_service.adapters.llm_factory import chat_model
from my_service.adapters.retriever_factory import retriever_for

@register("support_agent")
def build_support_agent(*, tenant_id: str):
    llm = chat_model("anthropic")
    retriever = retriever_for(tenant_id=tenant_id)
    # ... compose chain ...
    return chain
```

Routes become one line: `chain = registry.get("support_agent", tenant=req.tenant_id)`. There is one place to look, not twelve.

### Step 4 — Build retrievers and tools per-request, keyed by tenant (P33)

This is the P33 architectural fix. The factory takes `tenant_id` as a runtime argument. Nothing is bound at import:

```python
# src/my_service/adapters/retriever_factory.py
from functools import lru_cache
from langchain_core.retrievers import BaseRetriever
from langchain_pinecone import PineconeVectorStore
from my_service.config.settings import get_settings

@lru_cache(maxsize=256)  # cache the *store*, not the retriever
def _store_for(tenant_id: str) -> PineconeVectorStore:
    s = get_settings()
    return PineconeVectorStore(
        index_name=s.pinecone_index,
        namespace=f"tenant:{tenant_id}",  # per-tenant namespace
        embedding=...,
    )

def retriever_for(*, tenant_id: str, k: int = 6) -> BaseRetriever:
    # Retriever construction <5ms because store is cached — do it per-request.
    return _store_for(tenant_id).as_retriever(search_kwargs={"k": k})
```

The retriever is cheap to build (<5ms typical) so per-request construction is fine. Unit test with two tenants and assert non-overlap. See [Dependency Rules](references/dependency-rules.md) for the import-linter contract that forbids `services/*.py` from importing `langchain_pinecone` directly.

### Step 5 — Collapse config to one Pydantic `Settings`

```python
# src/my_service/config/settings.py
from functools import lru_cache
from typing import Literal
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="MYSVC_")

    env: Literal["dev", "staging", "prod"] = "dev"
    anthropic_api_key: SecretStr
    openai_api_key: SecretStr
    pinecone_api_key: SecretStr
    pinecone_index: str
    postgres_dsn: SecretStr | None = None  # required when env != "dev"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # reads env/.env at first call, caches
```

`SecretStr` prevents keys from leaking into logs. `Literal[...]` catches typos (`env="staing"`) at validation time, not at deploy time.

### Step 6 — Compose middleware in one place, in the right order

Middleware order is a correctness concern (P24 — redaction before caching, or cached responses leak PII across tenants). Wire the stack once in `adapters/` and hand the composed runnable to every service:

```python
# src/my_service/adapters/middleware.py
from langchain_core.runnables import Runnable

def wrap(model: Runnable) -> Runnable:
    # Order matters: redact -> cache -> retry -> model
    # Cross-reference L31 (langchain-middleware-patterns) for the full rationale.
    return (
        model
        .with_config(tags=["mysvc"])
        # | redaction_middleware()
        # | cache_middleware()
        # | retry_middleware()
    )
```

Cross-reference `langchain-middleware-patterns` (L31) for the middleware stack rationale and P25 (retry double-counting tokens).

### Step 7 — Pick the checkpointer per environment

This is the P22 architectural fix. `MemorySaver` is fine for dev; it is not an option for staging or prod:

```python
# src/my_service/adapters/checkpointer.py
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

def checkpointer_for(env: str) -> BaseCheckpointSaver:
    if env == "dev":
        return MemorySaver()
    # Staging/prod: Postgres-backed. Async variant for FastAPI.
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    from my_service.config.settings import get_settings
    dsn = get_settings().postgres_dsn
    assert dsn is not None, "POSTGRES_DSN required outside dev"
    return AsyncPostgresSaver.from_conn_string(dsn.get_secret_value())
```

Same for chat history when you use `RunnableWithMessageHistory` instead of a graph: `InMemoryChatMessageHistory` in dev, `PostgresChatMessageHistory` or `RedisChatMessageHistory` in staging/prod. See [Per-Env Checkpointer](references/per-env-checkpointer.md) for the `MemorySaver` / `SqliteSaver` / `PostgresSaver` / `AsyncPostgresSaver` decision matrix and the migration script between them. Cross-reference `langchain-langgraph-checkpointing` (L27) for checkpoint schema details.

### Step 8 — Test strategy: fakes in unit, real adapters in integration

The factory boundary is also the fake boundary. Unit tests inject a `FakeListChatModel` where production injects `ChatAnthropic`:

```python
# tests/unit/test_support_chain.py
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from my_service.services.support.chain import build_support_agent

def test_support_agent_returns_expected_shape(monkeypatch):
    monkeypatch.setattr(
        "my_service.services.support.chain.chat_model",
        lambda provider, **kw: FakeListChatModel(responses=["fixed answer"]),
    )
    chain = build_support_agent(tenant_id="acme")
    assert chain.invoke({"input": "hi"}).content == "fixed answer"
```

Integration tests use the real adapters against ephemeral Postgres and a sandbox Pinecone namespace. Contract tests snapshot tool JSON schemas so a silent `bind_tools` change fails CI.

### Step 9 — Enforce the layer graph in CI with import-linter

```toml
# pyproject.toml
[tool.importlinter]
root_package = "my_service"

[[tool.importlinter.contracts]]
name = "Layered architecture"
type = "layers"
layers = [
    "my_service.app",
    "my_service.services",
    "my_service.adapters",
    "my_service.config",
    "my_service.domain",
]

[[tool.importlinter.contracts]]
name = "Services do not import vendor SDKs"
type = "forbidden"
source_modules = ["my_service.services"]
forbidden_modules = [
    "langchain_anthropic",
    "langchain_openai",
    "langchain_pinecone",
]
```

CI runs `lint-imports`. A PR that puts `from langchain_anthropic import ChatAnthropic` inside `services/support/chain.py` fails — forcing the author to go through `adapters/llm_factory.chat_model("anthropic")` instead.

## Output

- 5-layer directory tree with `app / services / adapters / config / domain`
- `adapters/llm_factory.py` as the single source of version-safe defaults
- `services/registry.py` with `register(...)` / `get(name, tenant=...)` lookup
- Per-request retriever and tool factories keyed by `tenant_id` (P33 closed)
- One Pydantic `Settings` with `SecretStr` keys and `Literal[...]` env names
- Middleware composition order documented and wired once in `adapters`
- Per-env checkpointer: `MemorySaver` dev, `AsyncPostgresSaver` staging/prod (P22 closed)
- Test strategy: fakes at the factory boundary in unit, real adapters in integration
- `import-linter` contracts enforced in CI

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `KeyError: "No chain registered under 'support_agent'"` | Registry imported before service module registered | Import `services.support.chain` from `services/__init__.py` or `app.main` startup |
| Retriever returns wrong tenant's documents (P33) | Retriever bound at module-import scope with hardcoded tenant | Construct `retriever_for(tenant_id=...)` per request; retriever build <5ms with cached store |
| Chat history empty after pod restart (P22) | `RunnableWithMessageHistory` backed by `InMemoryChatMessageHistory` in staging/prod | Switch to `PostgresChatMessageHistory` / `RedisChatMessageHistory` via `history_for(env=...)` factory |
| `pydantic.ValidationError` on `env="staing"` typo | `Literal["dev","staging","prod"]` caught at `Settings` init | Fix env var before deploy; this is the intended behavior |
| `import-linter` failure `services imports langchain_anthropic` | Vendor SDK imported in services layer | Route through `adapters.llm_factory.chat_model("anthropic")` |
| `GraphRecursionError` on vague prompts (P10) | `create_react_agent` default `recursion_limit=25` | Set `recursion_limit=5-10` at graph compile time in the service |
| Cached response contains another tenant's PII (P24) | Middleware order was cache before redaction | Compose in `adapters/middleware.py` as redact → cache → model |
| Subgraph traces missing (P28) | Parent callbacks not inherited into subgraphs | Pass `config={"callbacks": [...]}` explicitly when invoking subgraph |
| `AssertionError: POSTGRES_DSN required outside dev` | `Settings.postgres_dsn` None in staging | Fail fast at startup; do not fall back to `MemorySaver` silently |

## Examples

### Onboarding a new tenant

Because retrievers are built per request from `tenant_id`, onboarding a new tenant is a data concern (create Pinecone namespace, seed documents), not a code concern. No file in `services/` changes. No redeploy is required to add `tenant_id="zeta"`.

### Adding a new provider

`adapters/llm_factory.py` grows one `elif` branch. `config/settings.py` grows one `SecretStr` field. No service module changes — they all depend on `BaseChatModel`, not `ChatAnthropic`. Cross-reference `langchain-model-inference` for the list of provider packages and their 1.0 import paths.

### Refactoring the 8-month-old mess

The migration is layer by layer, bottom up:

1. Extract `config/settings.py` first — it has no dependencies and unlocks the rest
2. Extract `adapters/llm_factory.py` and replace scattered `ChatAnthropic(...)` calls
3. Extract `adapters/retriever_factory.py` with `tenant_id` as a runtime arg — this is the P33 fix
4. Introduce `services/registry.py` and move one chain at a time from routes into registered builders
5. Turn on `import-linter` in CI with `ignore_imports` for routes that have not migrated yet; remove ignores as you go
6. Swap `MemorySaver` for `AsyncPostgresSaver` in staging last — it is the lowest-risk step once factories exist

## Resources

- [LangChain 1.0 — Concepts](https://python.langchain.com/docs/concepts/)
- [LangGraph — Persistence and checkpointers](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- import-linter — Layer contracts
- [FastAPI — Dependency injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- Pack pain catalog: `docs/pain-catalog.md` (entries P10, P22, P24, P28, P33)
- Sibling skills in this pack (same `plugins/saas-packs/langchain-py-pack/skills/` directory):
  - `langchain-model-inference` — LLM factory defaults provenance
  - `langchain-embeddings-search` — retriever and vector-store selection
  - `langchain-sdk-patterns` — composition patterns referenced by service builders

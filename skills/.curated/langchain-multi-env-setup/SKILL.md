---
name: langchain-multi-env-setup
description: "Build reliable dev / staging / prod isolation for LangChain 1.0 services\
  \ \u2014\nPydantic Settings + SecretStr, cloud Secret Manager in prod, per-env\n\
  prompt and model version pinning, env-specific checkpointer and observability.\n\
  Use when graduating from .env-in-dev to real prod infra, or debugging a\nconfig\
  \ that loaded the wrong values in the wrong env.\nTrigger with \"langchain multi-env\"\
  , \"langchain pydantic settings\",\n\"langchain secret manager\", \"langchain env\
  \ config\", \"langchain prod setup\".\n"
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(gcloud:*)
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- config
- pydantic
- multi-env
- secrets
compatibility: Designed for Claude Code
---
# LangChain Multi-Env Setup (Python)

## Overview

A team ships a LangChain 1.0 service to staging with `python-dotenv` loading
`.env.staging` into `os.environ`. Security audits —
`docker exec STAGING-POD env` prints `ANTHROPIC_API_KEY=sk-ant-api03-...` in
plain text. Anyone with `kubectl exec`, any sidecar, any core dump, any
error tracker that auto-captures process env sees the key. This is pain
**P37**: secrets loaded from `.env` in production containers leak via `env`.

A second failure chains. A developer runs the staging deploy from a shell
where `LANGCHAIN_ENV=production` was set hours earlier. The loader picks
the prod `.env`, staging answers with a prompt commit tuned only for the
prod model tier, latency doubles. Two root causes: no type-safe env gate,
no startup validation that would have caught the mismatched model id.

Both are one refactor:

```python
# BAD — dotenv populates os.environ; any process with container access sees it
from dotenv import load_dotenv
load_dotenv(".env.production")
api_key = os.environ["ANTHROPIC_API_KEY"]  # P37: leaks via `docker exec env`

# GOOD — SecretStr in a validated Settings object, pulled from Secret Manager
from pydantic import SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: Literal["dev", "staging", "prod"]
    anthropic_api_key: SecretStr

settings = build_settings()  # pulls from GCP Secret Manager in prod
api_key = settings.anthropic_api_key.get_secret_value()
# repr(settings) prints `SecretStr('**********')` — safe to log
```

This skill owns the per-env **config plumbing** — `Settings` skeleton,
Secret Manager integration, per-env pinning, startup smoke test. It does
**not** own the full secrets lifecycle (rotation, revocation, scope) —
that belongs to `langchain-security-basics`.

Pin: `langchain-core 1.0.x`, `langchain-anthropic 1.0.x`, `pydantic >= 2.5`,
`pydantic-settings >= 2.1`. Pain anchors: **P37** (primary), **P20**
(checkpointer schema — cross-ref `langchain-langgraph-checkpointing`).

Two numbers: **smoke test < 10 seconds**; **env-var count ~15-30** (more
than 30 means `Settings` is absorbing feature flags and should split).

## Prerequisites

- Python 3.10+ (3.11+ recommended for `Literal` and `StrEnum` ergonomics)
- `langchain-core >= 1.0, < 2.0`
- `pydantic >= 2.5`, `pydantic-settings >= 2.1`
- One secret backend: GCP Secret Manager (`google-cloud-secret-manager`),
  AWS Secrets Manager (`boto3`), or HashiCorp Vault (`hvac`)
- Completed `langchain-sdk-patterns` — the `Settings` object is injected into
  the chain factories from that skill

## Instructions

Run these six steps in order — each adds one invariant the next step depends on:

1. Define a `Settings` class with `SecretStr` keys, `Literal` env, and fail-fast validation.
2. Add a per-env loader — file in dev, env vars in staging, Secret Manager in prod.
3. Use the cloud Secret Manager client to pull keys into memory only.
4. Pin `model_id`, `prompt_commit_hash`, and `vector_index_name` per env.
5. Configure the checkpointer per env — memory in dev, Postgres elsewhere.
6. Run a startup smoke test under 10 seconds before the HTTP server binds.

### Step 1 — Create a Settings class with SecretStr and fail-fast validation

```python
from typing import Literal
from pydantic import SecretStr, HttpUrl, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,              # see Step 2 — loader picks the file
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",             # reject unknown env vars — typo detection
    )

    # --- env switch (drives everything else) ---
    env: Literal["dev", "staging", "prod"] = Field(..., alias="LANGCHAIN_ENV")

    # --- secrets (always SecretStr — never str) ---
    anthropic_api_key: SecretStr = Field(..., alias="ANTHROPIC_API_KEY")
    openai_api_key: SecretStr = Field(..., alias="OPENAI_API_KEY")
    langsmith_api_key: SecretStr = Field(..., alias="LANGSMITH_API_KEY")

    # --- per-env pinning (see Step 4) ---
    model_id: str = Field(..., alias="LANGCHAIN_MODEL_ID")
    prompt_commit_hash: str = Field(..., alias="LANGCHAIN_PROMPT_COMMIT")
    vector_index_name: str = Field(..., alias="LANGCHAIN_VECTOR_INDEX")

    # --- endpoints (validated URLs — typo caught at startup) ---
    checkpointer_url: HttpUrl | None = Field(None, alias="LANGCHAIN_CHECKPOINTER_URL")
    otel_endpoint: HttpUrl = Field(..., alias="OTEL_EXPORTER_OTLP_ENDPOINT")

    # --- budget guards (per-env) ---
    max_cost_usd_per_day: float = Field(10.0, alias="LANGCHAIN_DAILY_BUDGET_USD")
    max_rpm: int = Field(60, alias="LANGCHAIN_MAX_RPM")
```

`SecretStr` masks `repr(settings)` to `SecretStr('**********')` — a routine
`logger.info(settings)` cannot leak the key. The only way to read plaintext
is `.get_secret_value()`, which greps like a sore thumb in review.
`extra="forbid"` catches typos (`LANGCHIN_MODEL_ID`) at import time.
`HttpUrl` rejects `http:/otel:4318` before the exporter wastes 60s on DNS.

See [Settings Skeleton](references/settings-skeleton.md) for the full class.

### Step 2 — Per-env config loading (file OR Secret Manager, never both)

```python
import os
from pathlib import Path

def build_settings() -> Settings:
    env = os.environ.get("LANGCHAIN_ENV", "dev")

    if env == "dev":
        # Local dev: .env.dev file, values checked into 1Password not git
        return Settings(_env_file=Path(".env.dev"))

    if env == "staging":
        # CI / staging: env vars injected by the orchestrator
        # (GitHub Actions secrets, k8s envFrom: secretRef, etc.)
        return Settings()  # reads os.environ directly

    if env == "prod":
        # Prod: pull from Secret Manager into memory ONLY
        values = pull_from_secret_manager()
        return Settings(**values)

    raise ValueError(f"unknown LANGCHAIN_ENV: {env!r}")
```

Three loaders, one class. Dev touches a file on disk. Staging inherits env
vars from the orchestrator — `envFrom: secretRef` is readable via
`docker exec env`, but the blast radius is bounded and rotation is weekly.

Prod is the P37 fix: `pull_from_secret_manager()` builds a dict and passes
kwargs to `Settings(...)`. Values land in the instance attribute and
**never touch `os.environ`**. A subprocess will not inherit them.

### Step 3 — Secret Manager pull (GCP example; AWS / Vault in reference)

```python
from google.cloud import secretmanager

def pull_from_secret_manager() -> dict[str, str]:
    client = secretmanager.SecretManagerServiceClient()
    project = os.environ["GCP_PROJECT_ID"]
    secret_names = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "LANGSMITH_API_KEY"]
    out: dict[str, str] = {}
    for name in secret_names:
        resource = f"projects/{project}/secrets/{name}/versions/latest"
        response = client.access_secret_version(request={"name": resource})
        out[name] = response.payload.data.decode("utf-8")
    # Non-secret passthrough (model id, prompt hash, endpoints)
    for key in ["LANGCHAIN_ENV", "LANGCHAIN_MODEL_ID", "LANGCHAIN_PROMPT_COMMIT",
                "LANGCHAIN_VECTOR_INDEX", "LANGCHAIN_CHECKPOINTER_URL",
                "OTEL_EXPORTER_OTLP_ENDPOINT"]:
        if key in os.environ:
            out[key] = os.environ[key]
    return out
```

No `os.environ[k] = v` line. The dict goes straight into
`Settings(**values)`. Workload-identity IAM handles auth; no static key on
disk. For AWS / Vault see [Secret Manager Integration](references/secret-manager-integration.md).

### Step 4 — Per-env model and prompt pinning

Dev, staging, and prod run **different** model ids and **different** prompt
commit hashes. Pinning happens at env-var level so app code is env-agnostic
(see the Env Matrix below for values). One function reads
`settings.prompt_commit_hash` and pulls from LangSmith
(cross-ref `langchain-prompt-engineering`):

```python
from langsmith import Client
ls = Client(api_key=settings.langsmith_api_key.get_secret_value())

def get_prompt(settings: Settings) -> ChatPromptTemplate:
    return ls.pull_prompt(f"triage-prompt:{settings.prompt_commit_hash}")
```

**Prevents:** staging loading a prod prompt commit. Pinning per env makes
promotion explicit — dev → staging → prod moves one hash at a time. See
[Per-Env Pinning](references/per-env-pinning.md).

### Step 5 — Per-env checkpointer selection

Checkpointer choice is per-env too:

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver

def build_checkpointer(settings: Settings):
    if settings.env == "dev":
        return MemorySaver()          # ephemeral, resets on restart
    # staging + prod: Postgres with env-isolated schema
    # cross-ref langchain-langgraph-checkpointing (P20) for schema migration
    return PostgresSaver.from_conn_string(
        str(settings.checkpointer_url)
    )
```

Dev uses `MemorySaver` — no infra dependency, no state between runs.
Staging and prod use `PostgresSaver` against **separate** databases (or
separate schemas). Never share a checkpointer DB between envs; P20 explains
— schema migrations on a version bump corrupt cross-env threads.

### Step 6 — Startup smoke test (< 10 seconds budget)

```python
import time
from anthropic import Anthropic

def validate_integrations(settings: Settings) -> None:
    t0 = time.monotonic()

    # 1. Model reachable (1-token ping ~ $0.00001)
    anthropic = Anthropic(api_key=settings.anthropic_api_key.get_secret_value())
    anthropic.messages.create(
        model=settings.model_id,
        max_tokens=1,
        messages=[{"role": "user", "content": "hi"}],
    )

    # 2. Checkpointer reachable
    if settings.env != "dev":
        checkpointer = build_checkpointer(settings)
        checkpointer.setup()  # runs SELECT 1 + schema check

    # 3. Vector store reachable (see langchain-embeddings-search)
    # ... describe_index call here ...

    # 4. Observability endpoint reachable (OTLP HTTP health)
    # ... requests.get(f"{settings.otel_endpoint}/health", timeout=2) ...

    elapsed = time.monotonic() - t0
    if elapsed > 10.0:
        raise RuntimeError(
            f"startup smoke test took {elapsed:.1f}s (budget 10s)"
        )
```

Call `validate_integrations(settings)` **before** the HTTP server binds.
Failure aborts the deploy — the readiness probe never goes green, the
rollout halts, the bad version takes no traffic. Budget: **10 seconds**.
Past 10s an integration is degraded — fail loudly rather than ship a 30s
cold start. See [Startup Smoke Test](references/startup-smoke-test.md).

## Output

- `Settings` class on `pydantic-settings` with `SecretStr` for keys, `Literal` env, `HttpUrl` endpoints, `extra="forbid"`
- Env-specific loader (file → dev; env vars → staging; Secret Manager → prod); values land in `Settings` only, never `os.environ`
- Cloud Secret Manager integration (GCP / AWS / Vault) with IAM-bound auth; no static keys on disk
- Per-env pinning for `model_id`, `prompt_commit_hash`, `vector_index_name`, `checkpointer_url`
- Per-env checkpointer (`MemorySaver` dev, `PostgresSaver` on isolated DBs staging/prod)
- Startup smoke test — model / vector / checkpointer / observability under 10-second budget

## Env Matrix

| Dimension | dev | staging | prod |
|---|---|---|---|
| Secret backend | `.env.dev` file (git-ignored) | orchestrator env vars | cloud Secret Manager, memory only |
| `os.environ` holds keys | yes (local) | yes (sidecar visible) | **no** (P37 fix) |
| `model_id` | `claude-haiku-4-6` | `claude-sonnet-4-6` | `claude-sonnet-4-6` |
| `prompt_commit_hash` | WIP | canary | stable (1 week old) |
| `temperature` | 0.7 | 0.2 | 0.2 |
| Checkpointer | `MemorySaver` | `PostgresSaver` (staging DB) | `PostgresSaver` (prod DB) |
| Vector index | `dev-index` | `staging-index` | `prod-index` |
| OTEL sample rate | 1.0 | 1.0 | 0.1 |
| RPM limit | 10 | 60 | provider tier |
| Daily budget | $1 | $10 | $500-$5000 |
| Smoke probes | model | model + checkpointer + OTEL | all four |

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `docker exec POD env` shows `ANTHROPIC_API_KEY=...` in prod (P37) | `dotenv` / plain env injection in prod | Pull from Secret Manager into `Settings(**values)`; never write to `os.environ` |
| Staging answers with prod prompts / wrong model | Loader defaulted or picked stale `LANGCHAIN_ENV` | `Literal["dev","staging","prod"]` on env; raise on unknown; no default |
| `ValidationError: extra fields forbidden` at startup | Typo (`LANGCHIN_MODEL_ID`) | Fix the typo — `extra="forbid"` working as intended |
| Startup takes 30s before first request | Serialized probes or degraded integration | Enforce 10s budget; parallelize probes; fail the deploy |
| `repr(settings)` in a log leaks the API key | Plain `str` used, not `SecretStr` | Change field to `SecretStr`; repr masks to `'**********'` |
| Prod silently using `MemorySaver` | `build_checkpointer` defaulted when `checkpointer_url` was None | Require `checkpointer_url` in staging/prod via a model validator |
| Secret Manager auth fails in CI | SA not bound; `google.auth` fell back to ADC | Bind SA with `roles/secretmanager.secretAccessor` |
| Prompt hash rolled forward in staging without dev validation | Promotion skipped the dev gate | Enforce dev → staging → prod order in CI (see per-env pinning ref) |

## Examples

### Graduating a `.env`-in-dev service to prod

Start: a single `.env` committed (or leaked via `docker exec env`). End:
`Settings` class, three loaders, Secret Manager in prod, smoke test under
10s. Three PRs — (1) introduce `Settings` without changing loader behavior,
(2) add `SecretStr` and migrate call sites to `.get_secret_value()`,
(3) swap prod to Secret Manager and remove the prod `.env` from the image.
See [Settings Skeleton](references/settings-skeleton.md) and
[Secret Manager Integration](references/secret-manager-integration.md).

### Wrong-env prompt loaded in staging — postmortem

Staging inherited `LANGCHAIN_ENV=production` from a stale shell. The
`Literal["dev","staging","prod"]` field rejects `production`; CI promotion
sets `LANGCHAIN_ENV` explicitly; `direnv` pins it per-project. See
[Per-Env Pinning](references/per-env-pinning.md).

### Smoke test blocked a bad model id

A prod deploy went out with `LANGCHAIN_MODEL_ID=claude-sonnet-4-7` (not yet
rolled out). The 1-token ping failed with `model not found`,
`validate_integrations` raised, the container crash-looped, the rollout
halted, the previous version kept taking traffic. Zero user impact; failure
budget stayed under 3s. See [Startup Smoke Test](references/startup-smoke-test.md).

## Resources

- [Pydantic Settings docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Pydantic `SecretStr`](https://docs.pydantic.dev/latest/api/types/#pydantic.types.SecretStr)
- [GCP Secret Manager client](https://cloud.google.com/secret-manager/docs/reference/libraries)
- [AWS Secrets Manager `boto3`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html)
- [HashiCorp Vault `hvac`](https://hvac.readthedocs.io/)
- [LangChain 1.0 release notes](https://blog.langchain.com/langchain-langgraph-1dot0/)
- Related skills in pack: `langchain-security-basics` (secrets lifecycle, owns rotation and revocation — not duplicated here); `langchain-langgraph-checkpointing` (P20 schema migration); `langchain-prompt-engineering` (prompt pin / LangSmith pull workflow); `langchain-reference-architecture` (where `Settings` fits in the DI layer)
- Pack pain catalog: `docs/pain-catalog.md` (entries P37 primary, P20 cross-ref)

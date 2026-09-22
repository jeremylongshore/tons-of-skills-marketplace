---
name: langchain-deploy-integration
description: >-
  Deploy a LangChain 1.0 / LangGraph 1.0 app to Cloud Run, Vercel, or LangServe
  correctly — with timeouts sized for chain length, cold-start mitigation, SSE
  anti-buffering headers, and Secret Manager over .env. Use when prepping a first
  production deploy, debugging a stream that hangs behind a proxy, or diagnosing
  p99 latency spikes. Trigger with "langchain deploy", "langchain cloud run",
  "langchain vercel python", "langchain langserve", or "langchain docker".
allowed-tools: Read, Write, Edit, Bash(docker:*), Bash(gcloud:*), Bash(vercel:*)
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- deployment
- cloud-run
- vercel
- langserve
compatibility: Designed for Claude Code
---
# LangChain Deploy Integration (Python)

## Overview

An engineer ships a working LangGraph agent to Vercel. Every non-trivial request
returns `FUNCTION_INVOCATION_TIMEOUT`. The Python runtime on Vercel defaults to
a **10-second** cap (P35) — a three-tool agent with one RAG round easily runs
20-40s. Local dev never exposed the wall because `uvicorn` on a laptop has no
timeout. Two fixes apply together and each is load-bearing:

```json
// vercel.json — the baseline cap bump (Pro plan max is 60s, Enterprise 900s)
{ "functions": { "api/chat.py": { "maxDuration": 60 } } }
```

```python
# app/api/chat.py — stream the response so partial output arrives before the cap
from fastapi.responses import StreamingResponse

@app.post("/api/chat")
async def chat(req: ChatRequest):
    async def gen():
        async for chunk in chain.astream(req.input):
            yield f"data: {chunk.model_dump_json()}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"X-Accel-Buffering": "no"})
```

The `maxDuration: 60` raises the Vercel-imposed wall; streaming reduces
time-to-first-byte to under a second so the user sees progress even on a
40-second completion. Once the Vercel cap is fixed, the next three walls are:
Cloud Run cold starts (**5-15s** p99 on Python + LangChain — P36), `.env`
secrets leaking via `docker exec <pod> env` (P37), and SSE streams hanging
because Nginx / Cloud Run buffer the final chunk (P46).

This skill walks through a production-grade multi-stage Dockerfile, Cloud Run
flags for cold-start mitigation, Vercel `maxDuration` + streaming, LangServe
route mounting with FastAPI lifespan, SSE anti-buffering headers, and Secret
Manager via `pydantic.SecretStr`. Pin: `langchain-core 1.0.x`, `langgraph 1.0.x`,
`langserve 1.0.x`. Pain-catalog anchors: **P35** (Vercel 10s default),
**P36** (Cloud Run cold start), **P37** (`.env` leaks), **P46** (SSE buffering).

## Prerequisites

- Python 3.11+ (3.12 preferred for `uvicorn` startup speed)
- `langchain-core >= 1.0, < 2.0`, `langgraph >= 1.0, < 2.0`, `langserve >= 1.0, < 2.0`
- `fastapi >= 0.110`, `uvicorn[standard] >= 0.27`
- Target platform: `gcloud` CLI (Cloud Run), `vercel` CLI (Vercel), or `docker` (generic)
- For Cloud Run: a GCP project with Secret Manager API enabled
- For Vercel: a project with `@vercel/python` runtime configured

## Instructions

### Step 1 — Multi-stage Dockerfile with slim runtime and `uvicorn`

A multi-stage build keeps the runtime image under 400MB, which cuts Cloud Run
cold starts by 2-3 seconds. Use `python:3.12-slim` as the final stage (not
`python:3.12` — that base adds ~900MB for dev tooling that never runs in prod).

```dockerfile
# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder
WORKDIR /build
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv export --format requirements-txt --no-hashes > requirements.txt \
 && pip wheel --wheel-dir=/wheels -r requirements.txt

FROM python:3.12-slim AS runtime
RUN useradd -m -u 10001 app
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
 && rm -rf /wheels
COPY --chown=app:app app/ ./app/
USER app
EXPOSE 8080
ENV PORT=8080 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
```

Single worker is correct — Cloud Run handles horizontal scale; in-process
multi-worker just duplicates LangChain client memory. See [Dockerfile and
Secrets](references/dockerfile-and-secrets.md) for the distroless variant
and the `.dockerignore` hardening for `.env` files.

### Step 2 — Deploy to Cloud Run with cold-start mitigation

Python + LangChain + `tiktoken` + one embedding model imports take 5-15
seconds (P36). At `--min-instances=0`, every scale-from-zero request eats that
as user-facing latency. Paying for one always-on instance is usually cheaper
than the lost requests.

```bash
gcloud run deploy langchain-api \
  --source=. \
  --region=us-central1 \
  --min-instances=1 \
  --max-instances=20 \
  --cpu=2 --memory=2Gi \
  --cpu-boost \
  --no-cpu-throttling \
  --timeout=3600 \
  --concurrency=80 \
  --set-secrets=ANTHROPIC_API_KEY=anthropic-key:latest,OPENAI_API_KEY=openai-key:latest \
  --service-account=langchain-api@PROJECT.iam.gserviceaccount.com
# --timeout=3600 is the Cloud Run per-request maximum (1 hour) — needed
# because multi-tool LangGraph agents routinely run 1-5 minutes end-to-end.
```

The load-bearing flags: `--min-instances=1` kills cold-start p99 (one always-warm
replica costs ~$15/mo and dominates p99 improvement); `--cpu-boost` doubles CPU
for the first 10 seconds; `--no-cpu-throttling` (CPU-always-allocated billing)
keeps `astream` running between keepalive pings so long LangGraph runs do not
stall at tool boundaries; `--concurrency=80` matches typical I/O-bound
workloads (drop to 10 if embedding large docs in-process).

See [Cloud Run Deploy](references/cloud-run-deploy.md) for VPC egress, file
secret mounts, revision traffic splitting, and the full cost model.

### Step 3 — Vercel Python: `maxDuration: 60` + streaming to beat the cap

On Vercel Hobby the max is **10s** by default (P35); Pro is **60s**, Enterprise
**900s**. Always set `maxDuration` explicitly — the default is a trap.

```json
// vercel.json
{
  "functions": {
    "api/chat.py": { "maxDuration": 60, "memory": 1024 }
  }
}
```

Streaming is not just a UX fix — it is the mitigation for bursts that still
exceed `maxDuration`. Time-to-first-byte under a second keeps the proxy
considering the request alive; partial content renders on the client; when
the cap finally triggers, the user has already seen most of the answer. The
Vercel entrypoint pattern mirrors the Overview snippet above — pair with the
SSE headers from Step 5.

Edge Runtime is **not** an option here — `@vercel/edge` is JavaScript-only.
Anything that imports `langchain` must run on `@vercel/python` (serverless,
Node-free Python container). See [Vercel Python Deploy](references/vercel-python-deploy.md)
for env vars vs Vercel Secrets, cold-start profiling, and the serverless vs
fluid-compute tradeoff.

### Step 4 — LangServe: `add_routes` + FastAPI lifespan for pool cleanup

LangServe ships typed HTTP routes over any `Runnable`. The `playground` path
is invaluable in dev but **must be disabled in production** — it leaks chain
topology to anyone who can hit the URL. Mount behind a FastAPI `lifespan`
that closes `asyncpg` / `httpx` / Redis pools on revision retirement;
`on_shutdown` fires too late on Cloud Run and connections leak across
revisions.

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from langserve import add_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.chain = build_chain()
    yield
    await db_pool.close()

app = FastAPI(lifespan=lifespan)
add_routes(app, build_chain(), path="/chat",
           enable_feedback_endpoint=False,
           playground_type="chat" if __debug__ else None)  # None = off in prod
```

See [LangServe Patterns](references/langserve-patterns.md) for typed input/output
schemas, auth middleware, and coexisting with raw FastAPI handlers.

### Step 5 — SSE anti-buffering: survive Nginx, Cloud Run, Cloudflare

Nginx, Cloud Run's load balancer, and Cloudflare all buffer responses by
default. On SSE, buffering means the client never sees the final `end` event
and `LangGraph.astream` hangs forever (P46). Two headers plus one response
flush fix it:

```python
from fastapi.responses import StreamingResponse

def sse_headers() -> dict:
    return {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache, no-transform",
        "X-Accel-Buffering": "no",          # disables Nginx buffering
        "Connection": "keep-alive",
    }

@app.post("/api/chat/stream")
async def stream(payload: dict):
    async def gen():
        async for event in graph.astream_events(payload, version="v2"):
            yield f"data: {event['data']}\n\n".encode("utf-8")
        yield b"event: end\ndata: [DONE]\n\n"
    return StreamingResponse(gen(), headers=sse_headers())
```

Cross-reference: this is the same anti-buffering pattern used by
`langchain-langgraph-streaming` (L29) — that skill covers the `astream_events`
event shapes and client reconnection; this skill covers the proxy surface.
If you see the stream work locally but hang in prod, the header is missing on
the upstream response, not the client.

### Step 6 — Secret Manager over `.env` with `pydantic.SecretStr`

`python-dotenv` populates `os.environ`. Anyone with container access runs
`docker exec <pod> env` and reads every API key in plain text (P37). Mount
secrets from Secret Manager on Cloud Run, Vercel Secrets on Vercel; wrap in
`pydantic.SecretStr` so `repr()`, logs, and tracebacks print `**********`
instead of the value.

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")
    anthropic_api_key: SecretStr
    openai_api_key: SecretStr

settings = Settings()  # reads real env vars only; never .env in prod
```

Cloud Run: `--set-secrets=VAR=secret-name:latest` (Step 2). Vercel:
`vercel env add ANTHROPIC_API_KEY production`. Never commit `.env`; add
`.env*` to `.dockerignore` so it does not enter the build context.

Cross-reference: this skill sets the deployment boundary. `langchain-security-basics`
(P18) covers key-rotation cadence, PII log redaction, and the broader threat
model — get the boundary right here, then layer on P18.

## Output

- Multi-stage Dockerfile, runtime image under 400MB, non-root user, `uvicorn` entrypoint
- Cloud Run deployment with `--min-instances=1 --cpu-boost --no-cpu-throttling --timeout=3600 --concurrency=80`
- `vercel.json` with `maxDuration: 60` plus streaming response for requests that may exceed the cap
- LangServe `add_routes(app, chain, path="/chat")` behind a FastAPI `lifespan` that closes resource pools on revision retirement
- SSE responses with `X-Accel-Buffering: no` and `Cache-Control: no-cache` so proxies do not buffer the final `end` event
- Runtime secrets sourced from Secret Manager / Vercel Secrets and wrapped in `pydantic.SecretStr`; no `.env` in the image

## Platform Decision Table

| Platform | Max timeout | Cold start (p99) | SSE default | Cost baseline (1 agent, 1M req/mo) | Pick when |
|----------|-------------|------------------|-------------|------------------------------------|-----------|
| **Cloud Run** | 3600s | 5-15s (mitigable with min-instances) | Buffers without header override | ~$40-80/mo + min-instance | Long agents, heavy imports, VPC egress, GCP-native |
| **Vercel Python** | 10s Hobby / 60s Pro / 900s Enterprise | 2-5s (warmed) | No buffering when streaming response | ~$20/mo Pro plan flat | Fast iteration, Next.js frontend colocation, short agents |
| **Fly.io** | No hard cap (per-request soft) | 1-3s (always-on VM) | No default buffer | ~$30/mo for shared-cpu-1x + 1GB | Need persistent state, low cold start, non-serverless model |
| **Railway** | 30 min default | 2-4s | No default buffer | ~$25/mo on Hobby replica | Prototype to production on one platform, Postgres bundled |
| **Self-hosted (k8s + Nginx)** | Ingress-controlled | 0s (warm pod) | Buffers — requires `proxy_buffering off` | Variable, fixed infra cost | Compliance constraints, existing k8s, egress control |

Cloud Run is the default for most LangChain production deployments — the 3600s
timeout is the only mainstream serverless option long enough for multi-tool
agents, and Secret Manager integration is native.

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `FUNCTION_INVOCATION_TIMEOUT` (Vercel) | 10s Python default on Hobby, 60s on Pro (P35) | Set `maxDuration: 60` in `vercel.json`; stream the response |
| `504 Gateway Timeout` from Cloud Run | Missing `--timeout=3600`; default is 300s | Redeploy with `--timeout=3600 --concurrency=80` |
| p99 latency 10x p95 | Cold start from Python + LangChain imports (P36) | `--min-instances=1 --cpu-boost`, defer `tiktoken` import to request time |
| Client hangs forever on SSE stream | Proxy buffering the final `end` event (P46) | Add `X-Accel-Buffering: no` and `Cache-Control: no-cache` headers |
| `docker exec <pod> env` shows API keys | `python-dotenv` leaked `.env` into `os.environ` (P37) | Delete `.env` from image, use Secret Manager + `pydantic.SecretStr` |
| `RuntimeError: Event loop is closed` on shutdown | `asyncpg` / `httpx` pool not closed before revision retirement | Move pool lifecycle into FastAPI `lifespan` context manager |
| Stream works locally, stalls on Cloud Run | CPU throttling between keepalive pings | Deploy with `--no-cpu-throttling` (CPU-always-allocated) |
| `ModuleNotFoundError` in Vercel build | `requirements.txt` not generated from `pyproject.toml` | Add build step: `uv export --format requirements-txt > requirements.txt` |

## Examples

### A: Cloud Run with min-instances, secret mounts, VPC egress

One always-warm replica, two secrets from Secret Manager, egress routed
through a VPC connector for private Postgres. See [Cloud Run Deploy](references/cloud-run-deploy.md)
for the full flag set, revision traffic splitting, and the cost model.

### B: Vercel with streaming and maxDuration

`vercel.json` with `maxDuration: 60` plus the FastAPI streaming entrypoint
from Step 3. The combination gives a 40-second completion a 60-second wall
and <1s time-to-first-byte. See [Vercel Python Deploy](references/vercel-python-deploy.md)
for Edge Runtime limits and the Vercel Secrets vs env var split.

### C: LangServe behind FastAPI with lifespan

Single `add_routes` call mounting `/chat` and `/chat/stream` with a shared
connection pool closed via `lifespan`. Playground disabled in prod via the
`__debug__` check. See [LangServe Patterns](references/langserve-patterns.md)
for typed schemas, auth middleware, and raw-handler coexistence.

## Resources

- Cloud Run: Configuring services
- [Cloud Run: Always-on CPU (no CPU throttling)](https://cloud.google.com/run/docs/configuring/cpu-allocation)
- [Vercel: Python runtime](https://vercel.com/docs/functions/runtimes/python)
- [Vercel: `maxDuration` and streaming](https://vercel.com/docs/functions/configuring-functions/duration)
- [LangServe: Getting started](https://python.langchain.com/docs/langserve/)
- [FastAPI: Lifespan events](https://fastapi.tiangolo.com/advanced/events/)
- [Pydantic: `SecretStr`](https://docs.pydantic.dev/latest/api/types/#pydantic.types.SecretStr)
- Pack pain catalog: `docs/pain-catalog.md` (entries P35, P36, P37, P46)
- Related skills: `langchain-langgraph-streaming` (L29), `langchain-security-basics` (P18)

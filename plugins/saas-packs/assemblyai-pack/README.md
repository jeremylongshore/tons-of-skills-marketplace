# AssemblyAI Operator Skill Pack

> 18 governed workflows for current pre-recorded Speech-to-Text, Streaming v3, Speech Understanding, and LLM Gateway operations.

This pack helps operators build AssemblyAI integrations without leaking speech data, confusing pre-recorded and streaming contracts, or preserving retired LeMUR and Streaming v2 assumptions. It is grounded in current first-party AssemblyAI documentation reviewed on 2026-09-12.

## Installation

```bash
/plugin install assemblyai-pack@claude-code-plugins-plus
```

## What You Get

Each skill distinguishes repository inspection, implementation, live audio processing, privileged changes, and destructive cleanup. The workflows require explicit pre-recorded speech models, Streaming v3 lifecycle handling, authenticated callbacks, regional routing, bounded retries and concurrency, privacy-safe evidence, and downstream deletion propagation.

Legacy LeMUR integrations are routed to LLM Gateway, and legacy `/v2/realtime/ws` integrations are routed to Streaming v3 at `/v3/ws`.

## Skills Included

### Core workflows

| Skill | What It Does |
|-------|-------------|
| `assemblyai-install-auth` | Configure keys, regions, hosts, and safe browser token issuance |
| `assemblyai-hello-world` | Run a bounded pre-recorded smoke test with explicit models |
| `assemblyai-local-dev-loop` | Build deterministic synthetic fixtures and optional live checks |
| `assemblyai-sdk-patterns` | Isolate SDK drift behind a typed application-owned adapter |
| `assemblyai-core-workflow-a` | Operate governed pre-recorded transcription jobs |
| `assemblyai-core-workflow-b` | Operate Streaming v3 sessions and explicit termination |
| `assemblyai-common-errors` | Triage REST, job, streaming, webhook, and gateway failures |
| `assemblyai-debug-bundle` | Produce privacy-safe support evidence |
| `assemblyai-rate-limits` | Control account concurrency, request budgets, and retries |
| `assemblyai-security-basics` | Govern secrets, consent, residency, retention, and deletion |
| `assemblyai-prod-checklist` | Gate production readiness and rollback |
| `assemblyai-upgrade-migration` | Migrate Streaming v2 and LeMUR to current contracts |

### Delivery and architecture

| Skill | What It Does |
|-------|-------------|
| `assemblyai-ci-integration` | Verify offline contracts with a protected live lane |
| `assemblyai-deploy-integration` | Deploy reversible workers, token services, and callbacks |
| `assemblyai-webhooks-events` | Authenticate, acknowledge, deduplicate, and process callbacks |
| `assemblyai-performance-tuning` | Measure model, latency, throughput, and turn behavior |
| `assemblyai-cost-tuning` | Control duration, feature, retry, session, and gateway spend |
| `assemblyai-reference-architecture` | Design lifecycle, trust, retention, and failure boundaries |

## Current Contract Highlights

- Pre-recorded requests require an explicit `speech_models` list.
- Streaming uses the v3 WebSocket contract and must terminate explicitly.
- Browser and mobile streaming use backend-minted temporary tokens, never project keys.
- Pre-recorded and streaming webhook payloads differ and both require authentication and deduplication.
- LLM Gateway replaces retired LeMUR workflows.
- Prices, limits, model support, and retention behavior are verified against current first-party sources before live changes.

## License

MIT

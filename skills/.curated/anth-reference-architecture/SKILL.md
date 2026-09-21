---
name: anth-reference-architecture
description: 'Implement Claude API reference architectures for common use cases.

  Use when designing a Claude-powered application, choosing between

  direct API vs queue-based, or planning a multi-model architecture.

  Trigger with phrases like "anthropic architecture", "claude system design",

  "anthropic reference architecture", "design claude integration".

  '
allowed-tools: Read, Write, Edit, Grep
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Reference Architecture

## Overview

Three validated architecture patterns for Claude API integrations: synchronous API gateway, async queue-based processing, and multi-model routing.

## Architecture 1: Sync API Gateway (Simple)

```
User → API Gateway → Claude Service → Messages API
                                     ↓
                                   Response → User
```

```python
# Best for: chatbots, interactive tools, low-volume (<100 RPM)
from fastapi import FastAPI
import anthropic

app = FastAPI()
client = anthropic.Anthropic(max_retries=3, timeout=60.0)

@app.post("/chat")
async def chat(prompt: str):
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return {"text": msg.content[0].text, "tokens": msg.usage.output_tokens}
```

## Architecture 2: Async Queue-Based (Scalable)

```
User → API → Queue (Redis/SQS) → Worker Pool → Messages API
  ↑                                                ↓
  └──────────── Status/Result ←── Result Store ←───┘
```

```python
# Best for: batch processing, high-volume, background tasks
from redis import Redis
from rq import Queue
import anthropic

redis = Redis()
task_queue = Queue("claude-tasks", connection=redis)
result_store = Redis(db=1)

def process_task(task_id: str, prompt: str, model: str):
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    result_store.setex(f"result:{task_id}", 3600, msg.content[0].text)

# Enqueue
import uuid
task_id = str(uuid.uuid4())
task_queue.enqueue(process_task, task_id, prompt, "claude-sonnet-4-20250514")
```

## Architecture 3: Multi-Model Router

```
User → Router → Haiku    (classify/extract)
              → Sonnet   (general/code)
              → Opus     (research/complex)
              → Batches  (bulk/offline)
```

```python
class ModelRouter:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.classifier = anthropic.Anthropic()  # Can be same client

    def route_and_execute(self, prompt: str, context: dict) -> str:
        # Step 1: Classify with Haiku (cheap, fast)
        classification = self.classifier.messages.create(
            model="claude-haiku-4-20250514",
            max_tokens=32,
            messages=[{
                "role": "user",
                "content": f"Classify this request as: simple|moderate|complex|bulk\n\n{prompt[:200]}"
            }]
        )
        complexity = classification.content[0].text.strip().lower()

        # Step 2: Route to appropriate model
        model_map = {
            "simple": "claude-haiku-4-20250514",
            "moderate": "claude-sonnet-4-20250514",
            "complex": "claude-opus-4-20250514",
        }
        model = model_map.get(complexity, "claude-sonnet-4-20250514")

        # Step 3: Execute with selected model
        msg = self.client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
```

## Project Layout

```
my-claude-app/
├── src/
│   ├── main.py              # FastAPI app
│   ├── claude/
│   │   ├── client.py         # Singleton + config
│   │   ├── router.py         # Model routing logic
│   │   ├── tools.py          # Tool definitions
│   │   └── prompts/          # System prompts as files
│   ├── workers/
│   │   └── claude_worker.py  # Queue consumer
│   └── middleware/
│       ├── rate_limiter.py   # App-level rate limiting
│       └── cost_tracker.py   # Spend monitoring
├── tests/
│   ├── unit/                 # Mocked tests
│   └── integration/          # Live API tests
└── config/
    ├── .env.development
    ├── .env.staging
    └── .env.production
```

## Error Handling

| Architecture | Failure Mode | Mitigation |
|-------------|-------------|------------|
| Sync Gateway | 429/5xx blocks user | Circuit breaker + fallback response |
| Queue-Based | Worker crashes | Dead-letter queue + retry policy |
| Multi-Model | Router misclassifies | Default to Sonnet (safest middle) |

## Prerequisites

- Choose the workload class, availability/latency SLOs, data classification, approved destinations, and synchronous versus asynchronous behavior with an owner.
- Provide an isolated workspace, least-privileged secret-manager credential, synthetic fixtures, bounded queue/concurrency settings, and a tested rollback/circuit-breaker plan.
- Define idempotency, retention, dead-letter, and redacted evidence requirements before selecting an architecture.

## Instructions

1. Select the smallest architecture that meets the workload: gateway for interactive calls, queue for asynchronous work, or a router only when model policy and quality tests justify it.
2. Keep credentials and policy enforcement at the service boundary. Validate model, token, rate, data-class, source, and destination scope before enqueueing or sending a request.
3. Exercise success, timeout, 429/5xx, duplicate, queue-retry, tool-use, and partial-response paths with synthetic fixtures. Ensure traces and result stores exclude prompts, responses, and secrets.
4. Canary the selected topology in an isolated workspace, observe SLOs/cost/rate limits, and require approval before production traffic. Preserve the prior topology and configuration.
5. On policy, reliability, or cost regression, open the circuit or pause workers, drain/quarantine unsafe work, roll back, and retain a redacted architecture receipt.

## Output

Produce an architecture receipt naming the selected pattern, component/config digests, workspace and model classes, scope/idempotency/retention controls, synthetic test results, canary and SLO outcomes, approval, and rollback reference. Exclude request content, user identifiers, credentials, and raw queue payloads.

## Examples

For 100 synthetic asynchronous classification jobs, use a sandbox queue with a bounded worker pool, assert `duplicate_jobs=0; contacts_exported=0; content_logged=0`, and canary one internal consumer. A queue failure yields `paused=true; dead_letter=synthetic-only; rollback=worker-v1`.

## Resources

- [API Overview](https://platform.claude.com/docs/en/api/overview)
- [Tool Use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Prompt Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

## Next Steps

For multi-environment setup, see `anth-multi-env-setup`.

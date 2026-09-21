---
name: anth-architecture-variants
description: 'Choose and implement Claude API architecture patterns for different
  scales:

  serverless, microservice, event-driven, and edge deployment.

  Trigger with phrases like "anthropic architecture", "claude serverless",

  "claude microservice design", "edge claude deployment".

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
# Anthropic Architecture Variants

## Overview

Four validated architecture patterns for Claude API integrations at different scales and use cases.

## Variant 1: Serverless (AWS Lambda / Cloud Functions)

```python
# Best for: < 100 RPM, event-driven, pay-per-invocation
# lambda_function.py
import anthropic
import json

def handler(event, context):
    client = anthropic.Anthropic()  # Key from Lambda env var

    body = json.loads(event["body"])
    msg = client.messages.create(
        model="claude-haiku-4-20250514",  # Haiku for Lambda speed
        max_tokens=512,
        messages=[{"role": "user", "content": body["prompt"]}]
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "text": msg.content[0].text,
            "tokens": msg.usage.input_tokens + msg.usage.output_tokens
        })
    }
```

**Trade-offs:** Cold starts add 1-3s. Lambda timeout (15min) limits long generations. No connection pooling between invocations.

## Variant 2: Streaming Microservice (FastAPI + WebSocket)

```python
# Best for: chatbots, interactive UIs, real-time responses
from fastapi import FastAPI, WebSocket
import anthropic

app = FastAPI()
client = anthropic.Anthropic()

@app.websocket("/chat")
async def chat_ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        prompt = await websocket.receive_text()
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                await websocket.send_text(text)
            await websocket.send_text("[DONE]")
```

## Variant 3: Queue-Based Pipeline (Celery / Cloud Tasks)

```python
# Best for: batch processing, async workflows, high volume
from celery import Celery
import anthropic

app = Celery("tasks", broker="redis://localhost")

@app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_document(self, doc_id: str, content: str):
    try:
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": f"Summarize:\n\n{content}"}]
        )
        save_result(doc_id, msg.content[0].text)
    except anthropic.RateLimitError as e:
        self.retry(exc=e, countdown=int(e.response.headers.get("retry-after", 30)))
```

## Variant 4: Multi-Model Orchestrator

```python
# Best for: complex workflows needing different model strengths
class ClaudeOrchestrator:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def classify_then_respond(self, user_input: str) -> str:
        # Step 1: Classify intent with Haiku (fast, cheap)
        classification = self.client.messages.create(
            model="claude-haiku-4-20250514",
            max_tokens=32,
            messages=[{
                "role": "user",
                "content": f"Classify as: question|task|creative|code\nInput: {user_input[:200]}"
            }]
        )
        intent = classification.content[0].text.strip().lower()

        # Step 2: Route to optimal model
        model = {
            "question": "claude-haiku-4-20250514",
            "task": "claude-sonnet-4-20250514",
            "creative": "claude-sonnet-4-20250514",
            "code": "claude-sonnet-4-20250514",
        }.get(intent, "claude-sonnet-4-20250514")

        # Step 3: Generate response
        msg = self.client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": user_input}]
        )
        return msg.content[0].text
```

## Architecture Selection Guide

| Factor | Serverless | Microservice | Queue-Based | Orchestrator |
|--------|-----------|-------------|-------------|-------------|
| Latency | High (cold start) | Low (streaming) | N/A (async) | Medium |
| Volume | Low (<100 RPM) | Medium | High | Medium |
| Cost | Pay-per-use | Fixed infra | Batch savings | Optimized per-task |
| Complexity | Low | Medium | Medium | High |
| Best for | APIs, triggers | Chatbots | ETL, processing | Complex workflows |

## Prerequisites

- Document latency, throughput, availability, data residency, retention, budget, and side-effect requirements before choosing a variant.
- Provide an approved model/workspace allowlist, secret-manager integration, authenticated ingress/egress, shared rate limiter where needed, and a rollback owner.
- Use synthetic fixtures and a no-op tool/sink in a sandbox. Logs must contain topology and aggregate metrics only, not prompts, completions, credentials, or tool arguments.

## Instructions

1. Select the smallest architecture that satisfies measured latency and volume, then record why its timeout, queue, connection, and failure boundaries are adequate.
2. Keep API keys server-side, validate tenant/model/destination scope at ingress, and apply least privilege to workers and queues. Isolate streaming connections from batch consumers.
3. Add bounded retries, circuit breaking, backpressure, idempotent result handling, and health checks appropriate to the selected variant. Protect every tool or downstream write with an allowlist and approval gate.
4. Exercise the design with synthetic load and failure injection, then release to a limited canary. Compare error rate, latency, queue depth, token/cost aggregates, and data-scope assertions.
5. Promote only after owner approval; otherwise restore the prior topology/configuration and remove temporary fixtures, queues, and credentials.

## Output

Produce an architecture decision receipt with selected variant, constraints, trust boundaries, model/workspace scope, scaling and failure controls, aggregate test results, canary outcome, rollback reference, and retention/cleanup status. Exclude all content and secrets.

## Error Handling

- If measured demand exceeds the selected variant's safe envelope, apply backpressure and choose a queue or scale path; do not simply increase concurrency against the provider.
- If a worker, stream, or queue loses its authorization context, fail closed and quarantine the item rather than retrying with broader credentials.
- If partial output or duplicate delivery occurs, mark the result incomplete, deduplicate by an application ID, and roll back the consumer if duplicates persist.
- If an architecture gate cannot be observed, stop promotion and retain the last known-good variant.

## Examples

For a synthetic 20-RPM interactive workload with a strict streaming UX, select the microservice variant, use a shared limiter and a no-op sink, and record `scope=staging; external_side_effects=0; canary=pass; rollback=ready`. For offline summaries, select the queue/batch variant and retain only aggregate completion counts.

## Resources

- [API Getting Started](https://platform.claude.com/docs/en/api/overview)
- [Streaming](https://platform.claude.com/docs/en/build-with-claude/streaming)
- [Batches](https://platform.claude.com/docs/en/api/messages/batches/create)

## Next Steps

For common pitfalls, see `anth-known-pitfalls`.

---
name: anth-webhooks-events
description: 'Implement event-driven patterns with Claude API: streaming SSE events,

  Message Batches callbacks, and async processing architectures.

  Use when building real-time Claude integrations or processing batch results.

  Trigger with phrases like "anthropic events", "claude streaming events",

  "anthropic async processing", "claude batch callbacks".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Events & Async Processing

## Overview

The Claude API does not use traditional webhooks. Instead it provides two event-driven patterns: Server-Sent Events (SSE) for real-time streaming and the Message Batches API for async bulk processing. This skill covers both.

## SSE Streaming Events

```python
import anthropic

client = anthropic.Anthropic()

# Process each SSE event type
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Explain microservices."}]
) as stream:
    for event in stream:
        match event.type:
            case "message_start":
                print(f"Started: {event.message.id}")
            case "content_block_start":
                if event.content_block.type == "tool_use":
                    print(f"Tool call: {event.content_block.name}")
            case "content_block_delta":
                if event.delta.type == "text_delta":
                    print(event.delta.text, end="", flush=True)
                elif event.delta.type == "input_json_delta":
                    print(event.delta.partial_json, end="")
            case "message_delta":
                print(f"\nStop: {event.delta.stop_reason}")
                print(f"Output tokens: {event.usage.output_tokens}")
            case "message_stop":
                print("[Complete]")
```

## SSE Event Reference

| Event | When | Key Data |
|-------|------|----------|
| `message_start` | Stream begins | `message.id`, `message.model`, `message.usage.input_tokens` |
| `content_block_start` | New block begins | `content_block.type` (text or tool_use), `index` |
| `content_block_delta` | Incremental content | `delta.text` or `delta.partial_json` |
| `content_block_stop` | Block finishes | `index` |
| `message_delta` | Message-level update | `delta.stop_reason`, `usage.output_tokens` |
| `message_stop` | Stream complete | (empty) |
| `ping` | Keepalive | (empty) |

## Async Batch Processing

```python
# Submit batch (up to 100K requests, 50% cheaper)
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"doc-{i}",
            "params": {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": f"Summarize: {doc}"}]
            }
        }
        for i, doc in enumerate(documents)
    ]
)

# Poll for completion
import time
while True:
    status = client.messages.batches.retrieve(batch.id)
    if status.processing_status == "ended":
        break
    counts = status.request_counts
    print(f"Processing: {counts.processing} | Done: {counts.succeeded} | Errors: {counts.errored}")
    time.sleep(30)

# Stream results
for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        print(f"[{result.custom_id}]: {result.result.message.content[0].text[:100]}")
    else:
        print(f"[{result.custom_id}] ERROR: {result.result.error}")
```

## Event-Driven Architecture Pattern

```python
# Use queues to decouple Claude requests from user-facing endpoints
from redis import Redis
from rq import Queue

redis = Redis()
queue = Queue(connection=redis)

def process_with_claude(prompt: str, callback_url: str):
    """Background job for async Claude processing."""
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    # Notify your system via internal callback
    import requests
    requests.post(callback_url, json={
        "text": msg.content[0].text,
        "usage": {"input": msg.usage.input_tokens, "output": msg.usage.output_tokens}
    })

# Enqueue from your API handler
job = queue.enqueue(process_with_claude, prompt="...", callback_url="https://internal/callback")
```

## Error Handling

| Issue | Cause | Fix |
|-------|-------|-----|
| Stream disconnects | Network timeout | Reconnect and re-request (responses are not resumable) |
| Batch `expired` | Not processed in 24h | Resubmit the batch |
| `errored` results | Individual request was invalid | Check `result.error.message` per request |

## Prerequisites

- Choose an approved sandbox workspace, synthetic documents, bounded batch size, queue with durable retry/dead-letter behavior, and an authenticated internal callback destination.
- Treat SSE as a provider stream and callbacks as application-owned events: Anthropic does not use traditional webhooks for the patterns described here.
- Define an event retention period and redaction policy. Do not log prompts, completions, document content, tool arguments, API keys, or callback secrets.

## Instructions

1. Validate the stream or batch request against an allowlist of model, source, destination, and maximum size before sending it. Use synthetic fixtures and assert `side_effects=0`.
2. For SSE, process known event types, preserve ordering by message/block index, and mark a response incomplete until `message_stop`. Never assume a disconnected stream is resumable.
3. For batches and queues, use stable custom IDs, authenticate internal callbacks, and make result handling idempotent. A duplicate event must not duplicate a write or notification.
4. Enforce bounded polling, retries, and queue visibility timeouts. Quarantine errored or expired items for review instead of repeatedly resubmitting unknown data.
5. Release from sandbox to a small canary, verify counts, suppression/data-scope checks, and retention cleanup, then roll back the consumer or producer configuration on regression.

## Output

Produce an event-processing receipt with correlation/batch ID, event types and counts, succeeded/errored/expired counts, retry/dead-letter counts, callback authentication result, idempotency result, `side_effects=0` for tests, canary status, rollback reference, and cleanup status. Include error classes, not raw payloads.

## Examples

Submit two synthetic fixtures with custom IDs `demo-001` and `demo-002`, consume each result twice, and assert one stored result per ID. A safe receipt can state `batch=redacted; succeeded=2; duplicates_suppressed=2; callbacks_authenticated=true; side_effects=0; cleanup=verified` without including document text or generated output.

## Resources

- [Streaming API](https://platform.claude.com/docs/en/build-with-claude/streaming)
- [Message Batches API](https://platform.claude.com/docs/en/api/messages/batches/create)

## Next Steps

For performance optimization, see `anth-performance-tuning`.

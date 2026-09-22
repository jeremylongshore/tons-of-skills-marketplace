---
name: anth-reliability-patterns
description: 'Implement reliability patterns for Claude API: circuit breakers,

  graceful degradation, idempotency, and fallback strategies.

  Trigger with phrases like "anthropic reliability", "claude circuit breaker",

  "claude fallback", "anthropic fault tolerance".

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
# Anthropic Reliability Patterns

## Overview

Production reliability patterns for Claude API: circuit breaker (prevent cascading failures), graceful degradation (serve fallbacks), idempotency (safe retries), and timeout management.

## Circuit Breaker

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, reject requests
    HALF_OPEN = "half_open" # Testing recovery

class ClaudeCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = 0.0

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker OPEN — Claude API unavailable")

        try:
            result = func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.threshold:
                self.state = CircuitState.OPEN
            raise

# Usage
breaker = ClaudeCircuitBreaker(failure_threshold=5, recovery_timeout=60)

def safe_claude_call(prompt: str) -> str:
    try:
        return breaker.call(
            client.messages.create,
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        ).content[0].text
    except Exception:
        return "AI assistant is temporarily unavailable."
```

## Graceful Degradation

```python
import anthropic

def complete_with_fallback(prompt: str) -> str:
    """Try Sonnet → Haiku → cached response → static fallback."""
    models = ["claude-sonnet-4-20250514", "claude-haiku-4-20250514"]

    for model in models:
        try:
            msg = client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return msg.content[0].text
        except anthropic.RateLimitError:
            continue  # Try cheaper model
        except anthropic.APIStatusError:
            continue  # Try next model

    # All models failed — return cached or static response
    cached = cache.get(f"claude:{hash(prompt)}")
    if cached:
        return f"[Cached response] {cached}"

    return "Our AI assistant is temporarily unavailable. Please try again in a few minutes."
```

## Idempotent Requests

```python
import hashlib
import json

class IdempotentClaude:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.cache = {}  # Use Redis in production

    def create_message(self, idempotency_key: str | None = None, **kwargs) -> str:
        # Generate deterministic key from request params if not provided
        if not idempotency_key:
            idempotency_key = hashlib.sha256(
                json.dumps(kwargs, sort_keys=True, default=str).encode()
            ).hexdigest()

        # Return cached result for duplicate requests
        if idempotency_key in self.cache:
            return self.cache[idempotency_key]

        msg = self.client.messages.create(**kwargs)
        result = msg.content[0].text
        self.cache[idempotency_key] = result
        return result
```

## Timeout Configuration

```python
# Layer timeouts for defense-in-depth
client = anthropic.Anthropic(
    timeout=60.0,      # SDK-level timeout (covers connect + read)
    max_retries=3,     # Auto-retry on 429/5xx
)

# Per-request timeout override
msg = client.messages.create(
    model="claude-haiku-4-20250514",
    max_tokens=64,
    messages=[{"role": "user", "content": "Quick question"}],
    timeout=10.0  # Override for fast operations
)
```

## Reliability Checklist

- [ ] Circuit breaker prevents cascading failures
- [ ] Graceful degradation serves fallback responses
- [ ] Idempotency keys prevent duplicate processing
- [ ] Timeouts configured at SDK and application level
- [ ] Health check probes API connectivity
- [ ] Retry logic uses exponential backoff (SDK default)
- [ ] Rate limit headers monitored for pre-emptive throttling

## Prerequisites

- Define an approved model/workspace policy, request timeout, retry and circuit thresholds, fallback behavior, idempotency store, and rollback owner.
- Exercise the controls in a sandbox using synthetic prompts and a no-op downstream sink before enabling production traffic.
- Permit telemetry to contain only correlation IDs, status classes, model IDs, token counts, latency, breaker state, and aggregate fallback counts. Never store prompts, completions, credentials, or sensitive tool arguments.

## Instructions

1. Validate request scope and estimate budget before the call; reject unapproved models, destinations, or data classes before invoking the API.
2. Apply bounded retries only to transient, repeat-safe failures. Coordinate backoff and breaker state across instances so a provider incident does not create a retry storm.
3. Generate an application idempotency key from a stable request identity, not from an unredacted prompt. Cache only completed, policy-approved results and never deduplicate operations with unreviewed side effects.
4. Route to an explicitly approved fallback or a static response when the breaker opens. A fallback must preserve authorization and data-handling rules rather than silently widening scope.
5. Run a canary after configuration changes, compare error/latency/fallback metrics, and restore the prior configuration if thresholds or data controls regress. Expire test fixtures and temporary cache entries.

## Output

Return a reliability receipt with correlation ID, breaker transition, retry attempts and reasons, fallback route, idempotency outcome, timeout, aggregate token/cost counters, canary result, rollback reference, and cleanup status. Keep content and secret fields redacted.

## Error Handling

- Do not retry validation, authentication, permission, or policy failures; surface a stable operator-safe error and preserve the original request ID.
- When all fallbacks fail, fail closed with a bounded user-facing message and queue only work that has an explicit retention and replay policy.
- If a cached response is stale, scope-mismatched, or missing its policy version, discard it and use the static fallback.
- If duplicate suppression or breaker state is unavailable, stop new nonessential traffic rather than issuing uncoordinated retries.

## Examples

In a sandbox, inject five synthetic 529 responses, confirm the breaker opens, then allow one half-open probe. Record `retries=bounded; fallback=static; duplicate_writes=0; canary=pass; rollback=not-needed`, with no prompt or completion in the receipt.

## Resources

- [API Error Types](https://platform.claude.com/docs/en/api/errors)
- [Rate Limits](https://platform.claude.com/docs/en/api/rate-limits)

## Next Steps

For policy guardrails, see `anth-policy-guardrails`.

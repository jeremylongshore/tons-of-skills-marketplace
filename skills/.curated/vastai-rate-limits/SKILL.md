---
name: vastai-rate-limits
description: >-
  Diagnose and design bounded Vast.ai CLI and REST traffic around per-endpoint, per-identity rate limits and the absence of Retry-After headers. Use when implementing polling, batch automation, or 429 recovery. Trigger with: "handle Vast.ai 429", "reduce Vast.ai polling", "set Vast.ai retry policy".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[client-endpoints-and-call-budget]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - rate-limits
  - retries
  - api
compatibility: 'Requires an inventory of Vast.ai endpoints, calling identities, deadlines, and the current CLI or REST client.'
---

# Bounded Vast.ai API Traffic

## Overview

Prefer the CLI's built-in 429 retry for ordinary commands and add one orchestration-level call budget around it. For direct REST clients, implement capped backoff because the API does not return standard rate-limit headers.

## Prerequisites

- Endpoint and HTTP-method inventory with expected call volume
- Single owner for retry count, polling interval, deadline, and concurrency
- Metrics for calls, 429s, latency, cached hits, and abandoned work

## Instructions

### Step 1: Map the identity boundary

Group calls by endpoint, method, bearer token, session user, query key, and client IP because each can contribute to the enforced identity.

### Step 2: Choose one retry layer

For CLI commands, configure `--retry` and do not wrap them in another exponential retry. For REST, retry only 429 with a capped backoff and total deadline.

### Step 3: Replace tight polling

Cache stable offer and account data, poll only resources still in transitional states, stop on terminal states, and progressively lengthen the interval.

### Step 4: Flatten bursts

Queue work, spread scheduled jobs, and batch operations where the documented endpoint supports it. Bound concurrency per endpoint.

### Step 5: Honor the call budget

Stop when attempts, elapsed time, or request count reaches the approved ceiling; surface a retryable operational result instead of looping.

### Step 6: Escalate sustained pressure

Report endpoint, identity shape, measured call rate, 429 rate, and business need to support when production volume requires a higher limit.

## Authentication

Use the narrowest key for each worker and never rotate keys merely to evade a limit. Redact tokens and query credentials from request and retry logs.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Endpoint/identity traffic inventory
- Retry, polling, caching, concurrency, and deadline policy
- Measured before/after call volume and 429 receipt

Return endpoints, identity partition, client type, retry owner, call ceiling, observed 429s, elapsed time, and final disposition.

## Examples

A readiness watcher uses one CLI command with `--retry 3`, polls only while state is transitional, lengthens the interval, and exits immediately on `running`, `exited`, `unknown`, or `offline`.

## Error Handling

| Failure | Response |
| --- | --- |
| REST response is 429 | Back off within the total deadline; do not expect `Retry-After`. |
| Non-429 4xx occurs | Do not retry automatically; repair arguments, authentication, or permission. |
| Retry layers multiply | Remove the outer retry or disable the inner one so only one owner controls attempts. |
| Deadline expires | Return the last state and next safe action without another call. |

## Resources

- [First-party source notes](references/official-docs.md)
- [API rate limits and errors](https://docs.vast.ai/api-reference/rate-limits-and-errors)
- [CLI rate limits](https://docs.vast.ai/cli/rate-limits)
- [Official CLI global flags](https://github.com/vast-ai/vast-cli/blob/master/vastai/SKILL.md#global-flags)

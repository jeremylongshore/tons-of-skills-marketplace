---
name: clade-prod-checklist
description: "Production readiness checklist for Claude-powered applications \u2014\
  \nUse when working with prod-checklist patterns.\nerror handling, monitoring, fallbacks,\
  \ cost controls, and security.\nTrigger with \"anthropic production\", \"claude\
  \ production ready\",\n\"anthropic launch checklist\", \"go live with claude\".\n"
allowed-tools: Read, Write, Edit
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- production
- checklist
compatibility: Designed for Claude Code
---
# Anthropic Production Checklist

## Overview

Before going live with a Claude-powered app, verify every item below.

## Authentication & Security

- [ ] API key stored in secrets manager (not in code or env file on disk)
- [ ] Key rotated — not the same one used during development
- [ ] Server-side only — no key exposed to client/browser
- [ ] Per-user rate limiting in place
- [ ] Input validation: max length, content filtering
- [ ] System prompt includes injection guardrails

## Output

- All checklist items verified (authentication, error handling, streaming, cost, monitoring, reliability, content, performance)
- Production API key configured with appropriate spending limits
- Monitoring and alerting in place
- Fallback behavior tested for API outages

## Error Handling

- [ ] All Anthropic API calls wrapped in try/catch
- [ ] `RateLimitError` (429) → backoff and retry
- [ ] `OverloadedError` (529) → fallback model or queue
- [ ] `AuthenticationError` (401) → alert team, don't retry
- [ ] `InvalidRequestError` (400) → log and fix, don't retry
- [ ] Network errors → retry with backoff
- [ ] Request IDs logged for every error (for support tickets)

## Streaming

- [ ] Using `client.messages.stream()` for user-facing responses
- [ ] Stream errors handled (connection drops, incomplete responses)
- [ ] `stop_reason` checked: `end_turn` vs `max_tokens` (incomplete)

## Cost Controls

- [ ] `max_tokens` set to realistic values (not 4096 for short answers)
- [ ] Correct model for each task (Haiku for simple, Sonnet for balanced)
- [ ] Prompt caching enabled for repeated system prompts
- [ ] Usage logging in place — tracking tokens and cost per request
- [ ] Spending alerts set in Anthropic console

## Monitoring

- [ ] Response latency tracked (TTFT and total)
- [ ] Token usage tracked (input/output per request)
- [ ] Error rates dashboarded (by error type)
- [ ] Anthropic status page monitored ([status.anthropic.com](https://status.anthropic.com))

## Reliability

- [ ] SDK `maxRetries` set (default 2 is fine for most)
- [ ] Timeout configured for your use case (`timeout` option)
- [ ] Single client instance reused (not created per request)
- [ ] Graceful degradation if Claude is down (cached responses, fallback)

## Content & Compliance

- [ ] System prompt tested against edge cases and adversarial inputs
- [ ] Output validated before showing to users (JSON parsing, length)
- [ ] Data retention settings configured in Anthropic console
- [ ] No unnecessary PII in prompts
- [ ] Usage policy compliance (Anthropic's Acceptable Use Policy)

## Performance

- [ ] p95 latency acceptable for your UX
- [ ] Prompt caching for latency-sensitive paths
- [ ] Parallel requests where possible (`Promise.all`)
- [ ] Client-side streaming UI implemented

## Examples

Each section above is a verifiable checklist. Work through Authentication & Security, Error Handling, Streaming, Cost Controls, Monitoring, Reliability, Content & Compliance, and Performance sections.

## Resources

- [API Best Practices](https://platform.claude.com/docs/en/build-with-claude/overview)
- [Error Handling](https://platform.claude.com/docs/en/api/errors)
- [Rate Limits](https://platform.claude.com/docs/en/api/rate-limits)
- Acceptable Use Policy

## Next Steps

See `clade-observability` for monitoring setup.

## Prerequisites

- All other anthropic skills reviewed
- Application feature-complete and tested locally
- Production API key created (separate from dev)
- Deployment platform selected

## Instructions

### Step 1: Review the patterns below

Each section contains production-ready code examples. Copy and adapt them to your use case.

### Step 2: Apply to your codebase

Integrate the patterns that match your requirements. Test each change individually.

### Step 3: Verify

Run your test suite to confirm the integration works correctly.

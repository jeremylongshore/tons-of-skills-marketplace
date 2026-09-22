---
name: anth-upgrade-migration
description: 'Upgrade Anthropic SDK versions and migrate between Claude API versions.

  Use when upgrading the Python/TypeScript SDK, migrating from Text Completions

  to Messages API, or adopting new API features like tool use or batches.

  Trigger with phrases like "upgrade anthropic sdk", "anthropic migration",

  "update claude sdk", "migrate to messages api".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(pip:*), Bash(git:*)
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Upgrade & Migration

## Overview

Guide for upgrading the Anthropic SDK and migrating between API versions. The SDK follows semver — major versions may have breaking changes.

## Check Current Versions

```bash
# Python
pip show anthropic | grep Version
# Version: 0.40.0

# TypeScript
npm list @anthropic-ai/sdk
# @anthropic-ai/sdk@0.35.0

# Check latest available
pip index versions anthropic 2>/dev/null | head -1
npm view @anthropic-ai/sdk version
```

## Upgrade Path

### Step 1: Create Upgrade Branch

```bash
git checkout -b upgrade/anthropic-sdk
```

### Step 2: Upgrade SDK

```bash
# Python
pip install --upgrade anthropic
pip show anthropic | grep Version

# TypeScript
npm install @anthropic-ai/sdk@latest
```

### Step 3: Review Breaking Changes

Key breaking changes by version:

**Python SDK 0.20+ (anthropic-version: 2023-06-01)**

```python
# OLD: Text Completions API (deprecated)
response = client.completions.create(
    model="claude-2",
    prompt="\n\nHuman: Hello\n\nAssistant:",
    max_tokens_to_sample=256
)

# NEW: Messages API
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=256,
    messages=[{"role": "user", "content": "Hello"}]
)
```

**Python SDK 0.30+ (streaming changes)**

```python
# OLD: Manual SSE parsing
response = client.messages.create(..., stream=True)
for line in response.iter_lines():
    ...

# NEW: High-level streaming
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        print(text)
```

**TypeScript SDK 0.20+ (import path change)**

```typescript
// OLD
import Anthropic from 'anthropic';

// NEW
import Anthropic from '@anthropic-ai/sdk';
```

### Step 4: Update API Version Header

```python
# The SDK sends anthropic-version header automatically
# To pin a specific version:
client = anthropic.Anthropic(
    default_headers={"anthropic-version": "2023-06-01"}
)

# For beta features:
client = anthropic.Anthropic(
    default_headers={"anthropic-beta": "token-counting-2024-11-01"}
)
```

### Step 5: Run Tests and Verify

```bash
# Run your test suite
python -m pytest tests/ -v
npm test

# Verify a live call
python3 -c "
import anthropic
c = anthropic.Anthropic()
m = c.messages.create(model='claude-haiku-4-20250514', max_tokens=8, messages=[{'role':'user','content':'hi'}])
print(f'OK: {m.model} {m.usage}')
"
```

## Migration: Text Completions to Messages

| Text Completions | Messages API |
|-----------------|--------------|
| `client.completions.create()` | `client.messages.create()` |
| `prompt` (string) | `messages` (array) |
| `max_tokens_to_sample` | `max_tokens` |
| `model: "claude-2"` | `model: "claude-sonnet-4-20250514"` |
| `\n\nHuman:...\n\nAssistant:` | `[{role: "user"}, {role: "assistant"}]` |
| `response.completion` | `response.content[0].text` |

## Rollback

```bash
# Python — pin to previous version
pip install anthropic==0.39.0

# TypeScript — pin to previous version
npm install @anthropic-ai/sdk@0.34.0

# Git rollback
git checkout main -- package.json package-lock.json
npm install
```

## Prerequisites

- Record the current SDK version, lockfile digest, API version header, model identifiers, supported runtime versions, and a tested rollback revision.
- Obtain release notes from the official SDK/API sources and an approved sandbox workspace with synthetic prompts; production credentials must not be used for migration tests.
- Define compatibility, latency, cost, and response-shape acceptance thresholds and identify the owner who approves promotion.

## Instructions

1. Create a migration branch and lock the current dependency graph. Compare the target SDK and API behavior against official release notes; do not infer compatibility from a package version alone.
2. Update the SDK and request shapes in a sandbox, preserving explicit model IDs, `max_tokens`, authentication through the secret manager, and least-privileged workspace access.
3. Run unit, contract, streaming, tool-use, error, and token-count tests using synthetic fixtures. Compare redacted response-shape and usage receipts with the baseline; never log prompt or response content.
4. Canary the pinned artifact on an isolated workspace with zero customer traffic. Promote only after owner approval and threshold checks; monitor errors, latency, rate limits, and spend during the rollout.
5. If any gate fails, stop promotion, restore the prior lockfile/revision, revoke temporary credentials, and preserve the redacted migration receipt.

## Output

Produce a migration receipt containing source and target SDK versions, API-version header, lockfile/artifact digests, test and canary results, model IDs, workspace/environment, approval, rollout state, rollback reference, and retention deadline. Exclude API keys, prompt/response text, customer identifiers, and raw exception payloads.

## Error Handling

| Failure | Response |
|---|---|
| Dependency or API contract test fails | Pin the prior version, isolate the failing fixture, and do not promote. |
| Authentication or permission failure | Stop the canary, verify the secret-manager reference and workspace scope, and never print the key. |
| 429/5xx, timeout, or latency regression | Respect SDK retry guidance, apply a bounded circuit breaker, and roll back when the canary threshold is exceeded. |
| Response-shape or tool-use drift | Quarantine the result, update the adapter only after an approved contract decision, and rerun the full suite. |

## Examples

For a synthetic migration fixture, pin `anthropic` from `0.39.0` to the reviewed target, run 100 sandbox Messages API calls with `customer=fixture-017`, assert response-shape parity and `customer_content_logged=0`, then promote to a 1% internal canary. A failed threshold yields `promotion=halted; rollback=prior-lockfile`.

## Resources

- [Python SDK Changelog](https://github.com/anthropics/anthropic-sdk-python/releases)
- [TypeScript SDK Changelog](https://github.com/anthropics/anthropic-sdk-typescript/releases)
- [API Versioning](https://platform.claude.com/docs/en/api/versioning)

## Next Steps

For CI integration during upgrades, see `anth-ci-integration`.

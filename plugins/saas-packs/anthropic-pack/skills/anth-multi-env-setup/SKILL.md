---
name: anth-multi-env-setup
description: 'Configure Claude API across dev, staging, and production environments

  with isolated keys, model routing, and spend controls per environment.

  Trigger with phrases like "anthropic environments", "claude multi-env",

  "anthropic staging setup", "claude dev vs prod config".

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
# Anthropic Multi-Environment Setup

## Overview

Configure isolated Claude API environments with per-env API keys, model selection, and spend controls using Anthropic Workspaces.

## Environment Configuration

```python
# config.py
import os
from dataclasses import dataclass

@dataclass
class ClaudeConfig:
    api_key: str
    model: str
    max_tokens: int
    max_retries: int
    timeout: float
    monthly_budget_usd: float

CONFIGS = {
    "development": ClaudeConfig(
        api_key=os.environ["ANTHROPIC_API_KEY_DEV"],
        model="claude-haiku-4-20250514",       # Cheap for dev
        max_tokens=256,
        max_retries=1,
        timeout=15.0,
        monthly_budget_usd=10.0,
    ),
    "staging": ClaudeConfig(
        api_key=os.environ["ANTHROPIC_API_KEY_STAGING"],
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        max_retries=2,
        timeout=30.0,
        monthly_budget_usd=50.0,
    ),
    "production": ClaudeConfig(
        api_key=os.environ["ANTHROPIC_API_KEY_PROD"],
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        max_retries=5,
        timeout=120.0,
        monthly_budget_usd=5000.0,
    ),
}

def get_config() -> ClaudeConfig:
    env = os.getenv("APP_ENV", "development")
    return CONFIGS[env]
```

## Anthropic Workspaces (Key Isolation)

Create separate Workspaces in [console.anthropic.com](https://console.anthropic.com/settings/workspaces):

| Workspace | Purpose | Rate Limit Tier |
|-----------|---------|-----------------|
| `dev` | Development & testing | Tier 1 |
| `staging` | Pre-production validation | Tier 2 |
| `production` | Live traffic | Tier 3+ |

Each workspace has independent API keys, usage tracking, and rate limits.

## Environment Files

```bash
# .env.development
ANTHROPIC_API_KEY_DEV=sk-ant-api03-dev-...
APP_ENV=development

# .env.staging
ANTHROPIC_API_KEY_STAGING=sk-ant-api03-stg-...
APP_ENV=staging

# .env.production (stored in secret manager, not files)
ANTHROPIC_API_KEY_PROD=sk-ant-api03-prd-...
APP_ENV=production
```

## Client Factory

```python
import anthropic

def create_client() -> anthropic.Anthropic:
    config = get_config()
    return anthropic.Anthropic(
        api_key=config.api_key,
        max_retries=config.max_retries,
        timeout=config.timeout,
    )
```

## Per-Environment Model Override

```python
# Development: always use Haiku (cheapest)
# Staging: use production model for accuracy testing
# Production: use configured model

def get_model(override: str | None = None) -> str:
    if override:
        return override
    return get_config().model
```

## Error Handling

| Issue | Cause | Fix |
|-------|-------|-----|
| Dev key used in prod | Wrong env loaded | Validate key prefix matches environment |
| Staging rate limited | Low tier workspace | Upgrade staging workspace tier |
| Cost overrun in dev | No budget guard | Add per-env spend limits |

## Prerequisites

- Define the environment inventory, workspace/key ownership, model policy, rate and spend budgets, data classification, and promotion approver.
- Provision separate least-privileged credentials through a secret manager; production secrets must not exist in repository files, shell history, examples, or CI logs.
- Prepare synthetic fixtures, environment isolation tests, a canary route, and a rollback configuration before changing any workspace or client factory.

## Instructions

1. Map each environment to exactly one approved Anthropic workspace and secret-manager reference. Validate environment identity at startup and fail closed on a missing or mismatched key.
2. Load configuration through the environment-specific client factory, pin model and API settings, and enforce per-environment token, rate, timeout, retry, data, and destination limits.
3. Run authentication, cross-environment isolation, budget, and request-shape tests with synthetic fixtures. Capture only aggregate pass/fail and usage metadata.
4. Promote a reviewed artifact from staging to a small internal canary before production. Require owner approval and verify no production traffic or data can reach non-production workspaces.
5. On drift, leaked scope, or failed health checks, disable the route, restore the previous environment mapping, rotate affected credentials, and retain a redacted receipt.

## Output

Produce an environment receipt containing environment/workspace classes, config and artifact digests, model policy, isolation and synthetic-test results, canary/approval state, secret rotation status, retention, and rollback reference. Exclude API keys, endpoint tokens, prompts, responses, and member identifiers.

## Examples

Run a synthetic `fixture-request-001` through development and staging with separate keys, assert `workspace_crossing=0; production_key_in_nonprod=0; content_logged=0`, and record `canary=internal; approval=pending`. Promotion remains blocked until the owner approves the staging receipt.

## Resources

- [Workspaces](https://platform.claude.com/docs/en/manage-claude/workspaces)
- [Console](https://console.anthropic.com)

## Next Steps

For monitoring, see `anth-observability`.

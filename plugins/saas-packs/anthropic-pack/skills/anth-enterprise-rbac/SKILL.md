---
name: anth-enterprise-rbac
description: 'Configure Anthropic enterprise organization management, Workspaces,

  and role-based access control for teams.

  Trigger with phrases like "anthropic enterprise", "claude rbac",

  "anthropic workspaces", "claude team access", "anthropic organization".

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
# Anthropic Enterprise RBAC

## Overview

Anthropic provides organization-level access control through Workspaces, API key scoping, and member roles via the Console at [console.anthropic.com](https://console.anthropic.com).

## Organization Structure

```
Organization (billing entity)
├── Workspace: Production
│   ├── API Key: sk-ant-api03-prod-main-...
│   ├── API Key: sk-ant-api03-prod-batch-...
│   └── Rate limits: Tier 4
├── Workspace: Staging
│   ├── API Key: sk-ant-api03-stg-...
│   └── Rate limits: Tier 2
└── Workspace: Development
    ├── API Key: sk-ant-api03-dev-...
    └── Rate limits: Tier 1
```

## Console Roles

| Role | Capabilities |
|------|-------------|
| Owner | Full access, billing, member management |
| Admin | Manage workspaces, API keys, view usage |
| Developer | Create/revoke own API keys, view own usage |
| Billing | View invoices and usage reports only |

## Application-Level RBAC

```python
# Implement your own RBAC on top of Anthropic Workspaces
from enum import Enum
import anthropic

class UserRole(Enum):
    VIEWER = "viewer"       # Can read Claude responses (no direct API)
    USER = "user"           # Can send prompts (rate limited)
    POWER_USER = "power"    # Can use Opus, higher limits
    ADMIN = "admin"         # Can access all models, no limits

ROLE_CONFIG = {
    UserRole.VIEWER: {"allowed": False},
    UserRole.USER: {
        "allowed": True,
        "models": ["claude-haiku-4-20250514"],
        "max_tokens": 512,
        "rpm_limit": 10,
    },
    UserRole.POWER_USER: {
        "allowed": True,
        "models": ["claude-haiku-4-20250514", "claude-sonnet-4-20250514", "claude-opus-4-20250514"],
        "max_tokens": 4096,
        "rpm_limit": 60,
    },
    UserRole.ADMIN: {
        "allowed": True,
        "models": ["claude-haiku-4-20250514", "claude-sonnet-4-20250514", "claude-opus-4-20250514"],
        "max_tokens": 8192,
        "rpm_limit": 200,
    },
}

def create_message(user_role: UserRole, model: str, **kwargs):
    config = ROLE_CONFIG[user_role]
    if not config["allowed"]:
        raise PermissionError("Role does not allow API access")
    if model not in config["models"]:
        raise PermissionError(f"Role cannot access model: {model}")
    kwargs["max_tokens"] = min(kwargs.get("max_tokens", 1024), config["max_tokens"])

    client = anthropic.Anthropic()
    return client.messages.create(model=model, **kwargs)
```

## Key Management Best Practices

| Practice | Implementation |
|----------|---------------|
| One key per service | `prod-auth-service`, `prod-search-service` |
| Rotate quarterly | Calendar reminder + automated rotation |
| Least privilege | Dev workspace for dev keys only |
| Audit trail | Log which key made each request |
| Revoke immediately | On employee departure or compromise |

## Error Handling

| Issue | Cause | Fix |
|-------|-------|-----|
| Key works in dev, fails in prod | Wrong workspace key | Verify key belongs to prod workspace |
| New team member can't access | Not added to workspace | Invite via Console > Members |
| Usage not visible | Viewing wrong workspace | Switch workspace in Console |

## Prerequisites

- Obtain the organization owner’s approved workspace map, role matrix, service inventory, key owners, rotation schedule, and incident/revocation contacts.
- Create isolated dev/staging workspaces with synthetic requests; production changes require an approved change record and least-privileged service identity.
- Define the allowed models, token/rate budgets, data classes, destinations, and redacted audit fields for each role and service.

## Instructions

1. Map each human and service to the minimum Console role and workspace required for its job. Separate development, staging, and production keys; store them only in the approved secret manager.
2. Enforce application RBAC before constructing a request, including model, token, rate, data-class, and destination checks. Treat unknown roles, stale memberships, and missing workspace mappings as deny.
3. Test grants, denials, key rotation, revocation, and cross-workspace isolation with synthetic fixtures. Verify that audit records identify the actor and decision without recording prompts, responses, credentials, or personal data.
4. Roll out policy changes to one sandbox workspace or internal canary. Require owner approval and review aggregate authorization failures, usage, and spend before production promotion.
5. On suspected compromise or policy drift, revoke the affected key, disable the route, restore the last approved role policy, and document the redacted evidence.

## Output

Produce an RBAC receipt containing policy/version, workspace and service classes, role decision counts, model/token/rate constraints, test and canary outcomes, key rotation/revocation status, approver, and rollback reference. Exclude key values, member emails, prompts, responses, and raw Console exports.

## Examples

In a sandbox, assign `fixture-service` the user role, request a permitted Haiku call, and assert an Opus request is denied with `decision=deny; reason=model_scope; prompt_logged=0`. Rotate the synthetic service key, verify the old key is rejected, and record only the redacted receipt.

## Resources

- [Console](https://console.anthropic.com)
- [Workspaces](https://platform.claude.com/docs/en/manage-claude/workspaces)

## Next Steps

For major migration strategies, see `anth-migration-deep-dive`.

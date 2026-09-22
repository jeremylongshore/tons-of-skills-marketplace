---
name: clade-upgrade-migration
description: 'Upgrade Anthropic SDK versions and migrate between Claude model generations.

  Use when working with upgrade-migration patterns.

  Trigger with "upgrade anthropic sdk", "migrate claude model",

  "anthropic breaking changes", "new claude model".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(pip:*), Grep
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- migration
- upgrade
compatibility: Designed for Claude Code
---
# Anthropic Upgrade & Migration

## Overview

Upgrade the Anthropic SDK to new versions and migrate between Claude model generations. Covers version checking, changelog review, model ID updates across the codebase, output comparison testing, and gradual rollout via environment variables.

## SDK Upgrade

```bash
# Check current version
npm list @claude-ai/sdk
pip show anthropic

# Upgrade to latest
npm install @claude-ai/sdk@latest
pip install --upgrade anthropic

# Check changelog for breaking changes
#
```

## Model Migration Checklist

When Anthropic releases new model versions:

1. **Read the model card** — check for behavior changes, new capabilities
2. **Update model IDs** — find and replace old IDs

```bash
# Find all model references in your codebase
grep -r "claude-" --include="*.ts" --include="*.py" --include="*.json" .
```

1. **Test with new model** — run integration tests against both old and new
2. **Compare outputs** — spot-check key prompts for quality regression
3. **Update max_tokens** — new models may have different limits
4. **Gradual rollout** — use env var to control model selection

```typescript
// Environment-based model selection for safe rollout
const MODEL = process.env.CLAUDE_MODEL || 'claude-sonnet-4-20250514';

const message = await client.messages.create({
  model: MODEL,
  max_tokens: 1024,
  messages,
});
```

## Common Migration Issues

| Issue | Fix |
|-------|-----|
| Model ID not found (404) | Update to current model ID |
| Different output format | Adjust parsing — test with real prompts |
| Higher/lower token usage | Re-evaluate max_tokens and cost estimates |
| Deprecated SDK method | Check SDK changelog for replacement |

## Output

- SDK upgraded to latest version
- Model IDs updated across all files
- Integration tests passing with new model
- Output quality verified against previous model
- Gradual rollout configured via `CLAUDE_MODEL` environment variable

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See SDK Upgrade commands, grep patterns for finding model references, environment-based model selection, and Common Migration Issues table above.

## Resources

- SDK Releases (TS)
- SDK Releases (Python)
- [Model Deprecation Policy](https://platform.claude.com/docs/en/models/overview)

## Next Steps

See `clade-known-pitfalls` for common mistakes to avoid.

## Prerequisites

- Existing Anthropic SDK integration to upgrade
- Access to the codebase with grep/search capability
- Test suite for comparing model outputs

## Instructions

### Step 1: Review the patterns below

Each section contains production-ready code examples. Copy and adapt them to your use case.

### Step 2: Apply to your codebase

Integrate the patterns that match your requirements. Test each change individually.

### Step 3: Verify

Run your test suite to confirm the integration works correctly.

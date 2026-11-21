---
name: specstream-mcp-setup
description: |
  Configure and validate SpecStream remote MCP server connections (https://api.specstream.ai/mcp), OAuth or scoped API key setup, zero-retention and EU-egress flags, and A2A discovery. Use when connecting an MCP client to SpecStream. Trigger with "connect SpecStream MCP", "setup SpecStream key", or "validate SpecStream MCP config".
argument-hint: "[mcp-config.json]"
allowed-tools: Read, Bash(python3:*)
version: 1.0.0
author: Tarek Etman <tarek@specstream.ai>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, specstream, mcp, auth, a2a]
---
# SpecStream Remote MCP and Auth Setup

## Overview

Configure Claude Code or compatible MCP clients to connect to SpecStream's remote Streamable HTTP MCP server at `https://api.specstream.ai/mcp`, using either OAuth or a scoped `SPECSTREAM_API_KEY` Bearer token. This workflow also covers agent signup, least-privilege key scoping, zero-retention and EU-egress key flags, and A2A discovery.

## Prerequisites

- An MCP client configuration file (for example `.mcp.json` or local client config) or an existing SpecStream account (`https://specstream.ai/workspace`).
- No key is required to validate MCP configuration files offline or to read the A2A Agent Card (`GET https://api.specstream.ai/.well-known/agent-card.json`).
- Python 3.10+ to validate MCP client JSON offline against [the MCP and auth contract](references/api-contract.md).

## Instructions

1. Use `Read` to inspect the user's MCP config file and check [the MCP and auth contract](references/api-contract.md).
2. Configure the `specstream` Streamable HTTP server entry with these fields (never commit literal tokens):

   | Field | Value |
   | --- | --- |
   | `type` | `http` |
   | `url` | `https://api.specstream.ai/mcp` |
   | `headers.Authorization` (if using key auth instead of OAuth) | `Bearer ${SPECSTREAM_API_KEY}` |

3. Validate the MCP config JSON offline so literal tokens and mismatched URLs are caught before saving:

   ```bash
   python3 scripts/validate_specstream_payload.py --kind mcp --file mcp-config.json
   ```

4. When issuing keys programmatically (`POST https://api.specstream.ai/v1/account/keys`), scope them narrowly (`account:read`, `finds:spend`, `finds:read`), set `spend_cap_cents` and optional `expires_in_days`, and enable `"zero_retention": true`, `"eu_egress_only": true`, or `"engine_rule": {"deny": ["CN"]}` where policy requires it.
5. For headless onboarding without a browser, explain the two-step agent signup (`POST /v1/agent/signup` with user email -> user provides 6-digit code -> `POST /v1/agent/signup/verify`), noting that the $10 starter credit activates when the user signs in to the workspace in a browser.

## Output

Return the validated Streamable HTTP MCP configuration, recommended key scopes and privacy flags (`zero_retention`, `eu_egress_only`), `tools/list` discovery step, and offline validator result. Never print secret values.

## Error Handling

| Condition | Response |
| --- | --- |
| Literal token detected in `Authorization` header | Replace the literal token with `${SPECSTREAM_API_KEY}` and rely on environment injection. |
| `401` (`missing_api_key` or `invalid_token`) | Re-authenticate via OAuth or verify `SPECSTREAM_API_KEY` is exported in the client environment. |
| `403` (`owner_only`) | Key limit/expiry changes (`spend_cap_cents`, `expires_at`) require the owner's signed-in session (or a `keys:manage` key for keys it created). |
| `503` on key creation | Account key creation rate limit reached (10/hour unpaid, 1,000/hour paid); wait before retrying. |

## Examples

**Example 1: Validate an MCP client config file offline**

```bash
# Validate a local client config with ${SPECSTREAM_API_KEY} env interpolation or OAuth
python3 scripts/validate_specstream_payload.py --kind mcp --file mcp-config.json
```

**Example 2: Discover the A2A Agent Card without credentials**

```bash
# Unauthenticated discovery endpoint returning SpecStream A2A capabilities
curl -sSf https://api.specstream.ai/.well-known/agent-card.json
```

## Resources

- [MCP and auth contract](references/api-contract.md)
- [SpecStream MCP Docs](https://specstream.ai/docs/mcp)
- [SpecStream Auth Docs](https://specstream.ai/auth.md)

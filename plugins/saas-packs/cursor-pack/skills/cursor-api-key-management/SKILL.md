---
name: cursor-api-key-management
description: 'Configure BYOK API keys for OpenAI, Anthropic, Google, Azure, and custom
  models in Cursor.

  Triggers on "cursor api key", "cursor openai key", "cursor anthropic key", "own
  api key cursor",

  "BYOK cursor", "cursor azure key".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- api
- authentication
compatibility: Designed for Claude Code
---
# Cursor API Key Management

## Overview

Manage any Cursor BYOK/provider credentials as individual, least-privilege secrets with approved routing, ownership, rotation, spending limits, and exposure response.

## Prerequisites

- An approved provider/model route, named key owner, secrets-manager integration, and budget policy.
- Confirmation that BYOK is permitted for the intended data classification and tenant configuration.

## Instructions

1. Issue one scoped key per owner or approved service through the provider/secrets manager.
2. Configure it through the approved UI/injection path; never commit it, paste it into rules, or share it between users.
3. Set provider spending/rate controls, review usage, and rotate on schedule or suspected exposure.
4. Revoke first, then investigate, when a key is lost, leaked, or no longer required.

## Output

- An attributable, scoped credential with rotation, budget, and revocation evidence.

## Examples

Create a personal provider key in the approved secret manager, configure it only in the local secure setting, verify a low-cost non-sensitive request, and confirm usage attribution. If it appears in logs, chat, or git, revoke it immediately and replace it; do not attempt to redact history before revocation.

Configure Bring Your Own Key (BYOK) for AI model providers in Cursor. BYOK lets you use your own API keys to bypass Cursor's monthly quota, pay per token directly, and access models not included in Cursor's subscription.

## Supported Providers

| Provider | Key Format | Models Available |
|----------|-----------|-----------------|
| OpenAI | `sk-proj-...` or `sk-...` | GPT-4o, GPT-4o-mini, o1, o3, GPT-5 |
| Anthropic | `sk-ant-api03-...` | Claude Sonnet, Claude Opus, Claude Haiku |
| Google | `AIzaSy...` | Gemini 2.5 Pro, Gemini Flash |
| Azure OpenAI | Azure portal key | Any deployed Azure OpenAI model |
| AWS Bedrock | IAM credentials | Claude, Titan, Llama models |
| OpenAI-compatible | Varies | Ollama, LM Studio, Together AI, etc. |

## Configuration Steps

### OpenAI

1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new API key (project-scoped recommended)
3. In Cursor: `Cursor Settings` > `Models` > check `Use own API key`
4. Paste key in the OpenAI API Key field
5. Select model from dropdown (e.g., `gpt-4o`)

### Anthropic

1. Go to [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
2. Create a new API key
3. In Cursor: `Cursor Settings` > `Models` > check `Use own API key`
4. Paste key in the Anthropic API Key field
5. Select Claude model from dropdown

### Google (Gemini)

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Create API key
3. In Cursor: `Cursor Settings` > `Models` > check `Use own API key`
4. Paste key in the Google API Key field

### Azure OpenAI

Azure requires additional configuration beyond a simple API key:

1. In Azure Portal: create an Azure OpenAI resource
2. Deploy your desired model (e.g., `gpt-4o`)
3. Note the **Endpoint URL** and **API Key** from the resource
4. In Cursor: `Cursor Settings` > `Models`:

```
Azure Configuration:
  API Key:        xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  Endpoint:       https://your-instance.openai.azure.com
  Deployment:     your-gpt4o-deployment-name
  API Version:    2024-10-21
```

### Custom OpenAI-Compatible Endpoints

For self-hosted models (Ollama, vLLM) or third-party providers:

1. `Cursor Settings` > `Models` > `Add Model`
2. Model name: e.g., `llama-3.1-70b`
3. Check `Override OpenAI Base URL`
4. Enter base URL:

```
Ollama:        http://localhost:11434/v1
LM Studio:    http://localhost:1234/v1
Together AI:  https://api.together.xyz/v1
```

1. Enter API key if required by the provider
2. The model appears in the Chat/Composer model dropdown

## What BYOK Covers (and What It Does Not)

```
BYOK key used:                    Cursor model (always):
┌──────────────────────┐         ┌──────────────────────┐
│  Chat (Cmd+L)        │         │  Tab Completion      │
│  Composer (Cmd+I)    │         │  Apply from Chat     │
│  Agent Mode          │         │  (diff application)  │
│  Inline Edit (Cmd+K) │         │                      │
└──────────────────────┘         └──────────────────────┘
```

**Tab Completion and Apply always use Cursor's proprietary models.** You cannot route these through your own API key.

## Cost Management

### Monitoring Usage

With BYOK, you pay the provider directly. Monitor costs at:

- OpenAI: [platform.openai.com/usage](https://platform.openai.com/usage)
- Anthropic: [console.anthropic.com/settings/billing](https://console.anthropic.com/settings/billing)
- Azure: Azure Cost Management portal

### Setting Spending Limits

Set monthly spending limits at the provider level:

- **OpenAI**: Settings > Limits > Set monthly budget
- **Anthropic**: Settings > Limits > Set spending limit
- **Azure**: Create budget alerts in Azure Cost Management

### Cost-Saving Strategies

1. **Use Auto mode**: Cursor selects cheaper models for simple tasks
2. **Default to Sonnet/GPT-4o**: Reserve Opus/o1 for hard problems
3. **Shorter context**: Use `@Files` not `@Codebase` when you know the location
4. **Fewer round-trips**: Write detailed prompts to reduce back-and-forth

### Approximate Token Costs (as of early 2026)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|----------------------|
| GPT-4o | $2.50 | $10.00 |
| GPT-4o-mini | $0.15 | $0.60 |
| Claude Sonnet | $3.00 | $15.00 |
| Claude Opus | $15.00 | $75.00 |
| o1 | $15.00 | $60.00 |

A typical Composer session generating multi-file code uses 5K-20K tokens.

## Security Best Practices

### Key Storage

Cursor stores API keys locally in its settings database:

- macOS: `~/Library/Application Support/Cursor/`
- Linux: `~/.config/Cursor/`
- Windows: `%APPDATA%\Cursor\`

Keys are stored in the local Cursor configuration, not in project files. They do not sync between machines.

### Rotation

1. Generate a new key at the provider
2. Update the key in `Cursor Settings` > `Models`
3. Revoke the old key at the provider
4. Verify Chat/Composer work with the new key

### Team Key Management

For teams using BYOK:

- **Individual keys**: Each developer uses their own key. Simplest setup, hardest to audit.
- **Shared project key**: Create a project-scoped key at the provider. Share via secure channel. Track usage per project.
- **Azure gateway**: Route all requests through a central Azure OpenAI deployment. Full audit logging, spending controls, model governance.

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Unauthorized` | Invalid or expired API key | Regenerate key at provider |
| `429 Rate Limited` | Too many requests | Wait, or upgrade provider plan |
| `403 Forbidden` | Key lacks model access | Enable model access at provider |
| Model not appearing | Key not saved or wrong provider | Re-enter key in Cursor Settings |
| Azure connection refused | Wrong endpoint or API version | Verify endpoint URL and version |
| Slow responses with BYOK | Provider rate limits apply | Check provider dashboard |

## Enterprise Considerations

- **Compliance**: BYOK routes requests directly to the provider, bypassing Cursor's infrastructure. Verify this meets your data governance requirements.
- **Azure private endpoints**: Enterprise Azure deployments can use private endpoints for network-level isolation
- **Key rotation policy**: Implement quarterly key rotation as standard practice
- **SSO + BYOK**: Team admins can configure shared BYOK keys via the admin dashboard (Enterprise plan)

## Resources

- [Cursor API Keys Documentation](https://docs.cursor.com/advanced/api-keys)
- [Cursor Data Use Policy](https://cursor.com/data-use)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Anthropic API Reference](https://platform.claude.com/docs/en/api/overview)

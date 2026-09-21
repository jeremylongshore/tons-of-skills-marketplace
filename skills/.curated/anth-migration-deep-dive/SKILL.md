---
name: anth-migration-deep-dive
description: 'Migrate to Claude API from OpenAI, Gemini, or other LLM providers.

  Use when switching from GPT-4 to Claude, migrating from Text Completions,

  or building a multi-provider abstraction layer.

  Trigger with phrases like "migrate to claude", "openai to anthropic",

  "switch from gpt to claude", "multi-provider llm".

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
# Anthropic Migration Deep Dive

## Overview

Migration strategies for switching to Claude from OpenAI, Google, or other LLM providers, including API mapping, prompt translation, and multi-provider abstraction.

## OpenAI to Anthropic API Mapping

| OpenAI | Anthropic | Notes |
|--------|-----------|-------|
| `openai.ChatCompletion.create()` | `anthropic.messages.create()` | Different response shape |
| `model: "gpt-4"` | `model: "claude-sonnet-4-20250514"` | Different model IDs |
| `messages: [{role, content}]` | `messages: [{role, content}]` | Same format |
| `functions` / `tools` | `tools` | Similar but different schema key names |
| `function_call` | `tool_choice` | Different naming |
| `response.choices[0].message.content` | `response.content[0].text` | Different access path |
| `stream: true` → yields chunks | `stream: true` → SSE events | Different event format |
| System message in `messages[]` | `system` parameter (separate) | Claude separates system prompt |
| `n` (multiple completions) | Not supported | Use multiple requests |
| `logprobs` | Not supported | N/A |

## Side-by-Side Code Comparison

```python
# === OpenAI ===
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello"}
    ],
    max_tokens=1024,
    temperature=0.7
)
text = response.choices[0].message.content

# === Anthropic ===
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    system="You are helpful.",           # System prompt is separate
    messages=[
        {"role": "user", "content": "Hello"}
    ],
    max_tokens=1024,                     # Required (not optional)
    temperature=0.7
)
text = response.content[0].text
```

## Tool Use Migration

```python
# OpenAI tools format
openai_tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}}
    }
}]

# Anthropic tools format — flatter structure
anthropic_tools = [{
    "name": "get_weather",
    "description": "Get weather for a city",  # Required in Anthropic
    "input_schema": {"type": "object", "properties": {"city": {"type": "string"}}}
}]
```

## Multi-Provider Abstraction

```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, system: str = "", **kwargs) -> str: ...

class AnthropicProvider(LLMProvider):
    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic()

    def complete(self, prompt: str, system: str = "", **kwargs) -> str:
        msg = self.client.messages.create(
            model=kwargs.get("model", "claude-sonnet-4-20250514"),
            max_tokens=kwargs.get("max_tokens", 1024),
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text

class OpenAIProvider(LLMProvider):
    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI()

    def complete(self, prompt: str, system: str = "", **kwargs) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = self.client.chat.completions.create(
            model=kwargs.get("model", "gpt-4"),
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 1024)
        )
        return resp.choices[0].message.content
```

## Migration Checklist

- [ ] Map model names (GPT-4 → Claude Sonnet, GPT-3.5 → Claude Haiku)
- [ ] Move system prompts from `messages[]` to `system` parameter
- [ ] Update response access path (`.choices[0].message.content` → `.content[0].text`)
- [ ] Make `max_tokens` explicit (required in Anthropic, optional in OpenAI)
- [ ] Update tool definitions to Anthropic format
- [ ] Test prompt behavior (Claude may respond differently to same prompts)
- [ ] Update error handling for Anthropic error types

## Prerequisites

- Inventory provider models, prompts, tools, response consumers, data flows, budgets, and retention rules. Obtain owner approval for the target model/workspace and rollback window.
- Define a provider-neutral contract with explicit fields for model, token budget, stop reason, tool calls, errors, usage, and correlation ID; keep provider-specific details behind the adapter.
- Prepare representative synthetic fixtures and a no-op tool registry in a sandbox. Configure redacted comparison logs and exclude prompts, completions, PII, credentials, and tool arguments.

## Instructions

1. Map request and response fields using the tables above, preserving semantics rather than assuming identical tokenization, tool behavior, stop reasons, or safety behavior.
2. Move system instructions to the Anthropic `system` parameter, make `max_tokens` explicit, and validate alternating message roles and tool schemas before calling the target provider.
3. Run old and new providers in a shadow or replay lane with synthetic fixtures. Compare structured outcomes, latency, token/cost aggregates, refusal/guardrail decisions, and tool-call counts—not raw content in shared logs.
4. Release behind a feature flag to a small canary with a bounded budget and authorized destinations. Monitor for scope, retention, error, or quality regressions.
5. Promote only after acceptance evidence is approved. If any invariant fails, disable the flag and restore the prior provider adapter/configuration; delete temporary replay data.

## Output

Return a migration receipt containing source/target provider classes, adapter version, mapped capabilities, fixture and comparison counts, aggregate parity metrics, canary decision, rollback reference, and cleanup/retention status. Redact all prompt, completion, tool, account, and credential values.

## Error Handling

- If a source capability has no Anthropic equivalent (for example, multiple completions or logprobs), fail the compatibility check and choose an explicit product fallback; do not silently drop it.
- If tool schemas or role ordering are invalid, reject before the API call and report the field path without including user content.
- If shadow results diverge beyond the approved threshold, freeze rollout and keep the source provider active while the prompt/adapter is corrected.
- If rollback cannot be verified, do not widen the canary; preserve the last known-good deployment and escalate to the owner.

## Examples

Replay a synthetic fixture with one system instruction, one user turn, and a no-op `get_weather` tool through both adapters. Record `fixture_count=1; tool_side_effects=0; source_status=pass; target_status=pass; content_logged=0; canary=approved`, while comparing content through an access-controlled evaluator rather than the receipt.

## Resources

- [Anthropic vs OpenAI Migration](https://platform.claude.com/docs/en/models/overview)
- [Messages API Reference](https://platform.claude.com/docs/en/api/messages)

## Next Steps

For advanced debugging, see `anth-advanced-troubleshooting`.

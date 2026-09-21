---
name: cursor-model-selection
description: 'Configure and select AI models in Cursor for Chat, Composer, and Agent
  mode. Triggers on "cursor model",

  "cursor gpt", "cursor claude", "change cursor model", "cursor ai model", "cursor
  auto mode".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-model
compatibility: Designed for Claude Code
---
# Cursor Model Selection

## Overview

Choose models by task risk, reasoning needs, data-handling policy, latency, and approved spend—not by apparent confidence in a single response.

## Prerequisites

- The organization's approved model/provider list and data-routing constraints.
- A defined task, budget/latency expectation, and normal human review/test path.

## Instructions

1. Use an approved economical model for simple explanations or edits; escalate only for a defined complex task.
2. Confirm the model's data-handling route before attaching proprietary or regulated content.
3. Record material model decisions for high-risk work and independently validate all generated output.
4. Reassess model choice when quality, cost, privacy, or latency exceeds the agreed threshold.

## Output

- A model selection tied to task requirements, policy, and a validation plan.

## Error Handling

| Condition | Safe response |
|---|---|
| Model is not approved for the data class | Stop and use an approved route or seek formal approval. |
| Cost/latency exceeds budget | Downgrade or narrow the task; do not bypass spending controls. |
| Output quality is inadequate | Use a better-suited approved model and retain independent review. |

## Examples

Use an approved fast model for a localized type annotation with its focused test. For a high-impact architecture proposal, use the approved reasoning model, attach only necessary design documents, and require human reviewers to validate alternatives and rollback implications.

Configure AI models for Chat, Composer, and Agent mode. Cursor supports models from OpenAI, Anthropic, Google, and its own proprietary models. Choosing the right model per task is a major productivity lever.

## Available Models

### Included with Cursor Subscription

| Model | Provider | Best For | Context |
|-------|----------|----------|---------|
| **GPT-4o** | OpenAI | General coding, fast responses | 128K |
| **GPT-4o-mini** | OpenAI | Simple tasks, cost-efficient | 128K |
| **Claude Sonnet** | Anthropic | Code quality, detailed explanations | 200K |
| **Claude Haiku** | Anthropic | Fast simple tasks | 200K |
| **cursor-small** | Cursor | Quick completions, simple edits | 8K |
| **Auto** | Cursor | Automatic model selection per query | Varies |

### Premium Models (count against fast request quota)

| Model | Provider | Best For | Context |
|-------|----------|----------|---------|
| **Claude Opus** | Anthropic | Complex architecture, hard bugs | 200K |
| **GPT-5** | OpenAI | Advanced reasoning, complex code | 128K+ |
| **o1 / o3** | OpenAI | Deep reasoning, mathematical logic | 128K |
| **Gemini 2.5 Pro** | Google | Design, large context analysis | 1M |

## Model Selection by Task

### Quick Reference

```
Bug fix in one file        → GPT-4o or Claude Sonnet
Multi-file refactoring     → Claude Sonnet or Opus
Architecture planning      → Claude Opus or GPT-5
Test generation            → GPT-4o (fast + good patterns)
Complex algorithm design   → o1/o3 reasoning models
Large codebase analysis    → Gemini 2.5 Pro (1M context)
Simple autocomplete        → cursor-small (automatic via Tab)
"I don't know"             → Auto mode
```

### How to Switch Models

**Per conversation:** Click the model name in the top-right of Chat or Composer panel.

**Default model:** `Cursor Settings` > `Models` > set default for Chat and Composer separately.

**Auto mode:** Select "Auto" as the model. Cursor picks the best model per query based on complexity and current server load.

## Bring Your Own Key (BYOK)

Use your own API keys to bypass Cursor's quota system. You pay the provider directly at their rates.

### Configuration

`Cursor Settings` > `Models` > enable `Use own API key`:

**OpenAI:**

```
API Key: sk-proj-xxxxxxxxxxxxxxxxxxxx
```

**Anthropic:**

```
API Key: sk-ant-xxxxxxxxxxxxxxxxxxxx
```

**Google (Gemini):**

```
API Key: AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Azure OpenAI

For enterprise Azure deployments:

```
Cursor Settings > Models > Azure:
  API Key:       xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  Endpoint:      https://my-instance.openai.azure.com
  Deployment:    gpt-4o-deployment-name
  API Version:   2024-10-21
```

### Adding Custom Models

For OpenAI-compatible providers (Ollama, LM Studio, Together AI):

1. `Cursor Settings` > `Models` > `Add Model`
2. Enter model name (e.g., `llama-3.1-70b`)
3. Enable `Override OpenAI Base URL`
4. Enter base URL: `http://localhost:11434/v1` (Ollama) or provider URL
5. Enter API key if required

### BYOK Limitations

| Feature | Uses BYOK Key? | Uses Cursor Model? |
|---------|---------------|-------------------|
| Chat | Yes | -- |
| Composer | Yes | -- |
| Agent mode | Yes | -- |
| **Tab Completion** | **No** | **Always Cursor model** |
| **Apply from Chat** | **No** | **Always Cursor model** |

Tab Completion always uses Cursor's proprietary model regardless of BYOK configuration.

## Cost Optimization Strategies

### Tiered Model Usage

```
Tier 1 (Fast + Cheap):    cursor-small, GPT-4o-mini, Claude Haiku
  Use for: simple questions, syntax help, boilerplate

Tier 2 (Balanced):        GPT-4o, Claude Sonnet
  Use for: most coding tasks, debugging, refactoring

Tier 3 (Premium):         Claude Opus, GPT-5, o1/o3
  Use for: architecture decisions, critical bugs, complex logic
```

### Quota Management

Cursor subscription includes a monthly quota of "fast requests" (premium model uses). When exceeded, requests queue behind other users ("slow requests").

- Check remaining quota: `cursor.com/settings` > Usage
- Pro plan: ~500 fast requests/month
- Business plan: ~500 fast requests/month per seat

### Tips to Reduce Usage

1. Use Auto mode -- it picks cheaper models when they suffice
2. Start with Sonnet/GPT-4o, escalate to Opus/o1 only if needed
3. Write detailed prompts to avoid back-and-forth (fewer requests)
4. Use BYOK for heavy usage -- pay per token instead of per request

## Model Behavior Differences

### Code Generation Style

```python
# Claude models: Verbose, well-documented, defensive
def process_order(order: Order) -> Result[ProcessedOrder, OrderError]:
    """Process an order through the payment and fulfillment pipeline.

    Args:
        order: The order to process.

    Returns:
        Result containing the processed order or an error.

    Raises:
        Never raises -- errors returned as Result.Err.
    """
    if not order.items:
        return Err(OrderError.EMPTY_ORDER)
    ...

# GPT models: Concise, pragmatic, fewer comments
def process_order(order: Order) -> ProcessedOrder:
    if not order.items:
        raise ValueError("Order has no items")
    ...
```

### Reasoning Models (o1, o3)

These models "think" before responding. They are slower but significantly better at:

- Multi-step logic problems
- Finding subtle bugs in complex code
- Mathematical or algorithmic optimization
- Understanding implicit requirements

They are overkill for simple tasks. Use them deliberately for hard problems.

## Enterprise Considerations

- **Model access control**: Admins can restrict which models team members access via the admin dashboard
- **Spending limits**: Set per-user or per-team spending caps when using BYOK
- **Compliance**: Some models route through different providers -- verify data handling per model
- **Azure preference**: Enterprise teams on Azure can route all requests through their own Azure OpenAI deployments
- **Audit**: Model selection per request is visible in usage analytics (Business/Enterprise plans)

## Resources

- [Cursor Models Documentation](https://docs.cursor.com/settings/models)
- [API Key Configuration](https://docs.cursor.com/advanced/api-keys)
- [Pricing and Plans](https://cursor.com/pricing)

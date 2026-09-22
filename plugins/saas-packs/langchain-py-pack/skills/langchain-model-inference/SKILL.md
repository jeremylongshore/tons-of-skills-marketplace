---
name: langchain-model-inference
description: 'Invoke Claude, GPT-4o, and Gemini through LangChain 1.0 without tripping
  on

  the content-block, token-accounting, and structured-output quirks that silently

  break production code. Use when initializing chat models, routing across providers,

  iterating AIMessage content, or choosing a structured-output method.

  Trigger with "langchain model inference", "ChatAnthropic", "ChatOpenAI",

  "with_structured_output", "AIMessage content blocks", "langchain routing".

  '
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(pip:*), Grep
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- model-inference
compatibility: Designed for Claude Code
---
# LangChain Model Inference (Python)

## Overview

`AIMessage.content` is a `str` on simple OpenAI calls and a `list[dict]` on Claude
the instant any `tool_use`, `thinking`, or `image` block enters the response.
Code that does `message.content.lower()` crashes with
`AttributeError: 'list' object has no attribute 'lower'` — the #1 first-production-call
LangChain 1.0 bug on Anthropic. And that is one of four separate "content shape"
pitfalls in this skill:

- P02 — `AIMessage.content` list-vs-string divergence
- P03 — `with_structured_output(method="function_calling")` silently drops
  `Optional[list[X]]` fields on ~40% of real schemas
- P05 — `temperature=0` is not deterministic on Anthropic even though it is on OpenAI
- P58 — Claude expects the system message at position 0; middleware that reorders
  messages makes it silently ignored

This skill walks through `ChatAnthropic`, `ChatOpenAI`, and `ChatGoogleGenerativeAI`
initialization; model routing; token counting that is actually correct during
streaming; content-block iteration; and a decision tree for `with_structured_output`
methods that holds up on real schemas. Pin: `langchain-core 1.0.x`,
`langchain-anthropic 1.0.x`, `langchain-openai 1.0.x`, `langchain-google-genai 1.0.x`.
Pain-catalog anchors: P01, P02, P03, P04, P05, P53, P54, P58, P63, P64, P65.

## Prerequisites

- Python 3.10+
- `langchain-core >= 1.0, < 2.0`
- At least one provider package: `pip install langchain-anthropic langchain-openai`
- Provider API key(s): `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`

## Instructions

### Step 1 — Initialize a chat model with explicit, version-safe defaults

```python
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

claude = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=0,
    max_tokens=4096,
    timeout=30,       # seconds. Default is None — hangs forever on provider stall.
    max_retries=2,    # Retries, not attempts. See P30 in pain catalog.
)

gpt4o = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    timeout=30,
    max_retries=2,
)
```

Explicit `timeout` and `max_retries` are not optional in production — the defaults
are wrong for every workload we have measured. `max_retries=6` (the default on
`ChatOpenAI`) means a single logical call can bill as **7** requests on flaky
networks.

### Step 2 — Iterate `AIMessage.content` as typed blocks, not strings

```python
from langchain_core.messages import AIMessage

def extract_text(msg: AIMessage) -> str:
    """Safe on both provider shapes. Works for streaming deltas too.

    Handles both dict blocks (provider-native) and typed block objects
    (LangChain 1.0 wrappers) — which Gemini, OpenAI tools, and future
    SDK versions may return.
    """
    if isinstance(msg.content, str):
        return msg.content
    parts = []
    for block in msg.content:
        # Block may be a dict (provider-native) or a typed object (1.0 wrapper)
        block_type = block.get("type") if isinstance(block, dict) else getattr(block, "type", None)
        if block_type == "text":
            parts.append(block["text"] if isinstance(block, dict) else block.text)
    return "".join(parts)
```

`AIMessage.text()` (1.0+) does this for you in most cases — prefer it. Roll your
own only when you need to filter by block type (`tool_use`, `image`, `thinking`).
See [Content Blocks](references/content-blocks.md) for the full block-type
reference and streaming-delta shape.

### Step 3 — Route across providers with a factory, not a conditional

```python
from langchain_core.language_models import BaseChatModel

# Version-safe defaults applied to every model the factory builds.
# Callers can override via **kwargs.
_SAFE_DEFAULTS = {"timeout": 30, "max_retries": 2}

def chat_model(provider: str, **kwargs) -> BaseChatModel:
    defaults = {**_SAFE_DEFAULTS, **kwargs}  # caller's kwargs win
    if provider == "anthropic":
        return ChatAnthropic(model="claude-sonnet-4-6", **defaults)
    if provider == "openai":
        return ChatOpenAI(model="gpt-4o", **defaults)
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model="gemini-2.5-pro", **defaults)
    raise ValueError(f"Unknown provider: {provider!r}")
```

A factory centralizes the version-safe defaults from Step 1 (`timeout=30`,
`max_retries=2`) and the structured-output method pick from Step 5. Chains depend
on the `BaseChatModel` protocol, not the concrete class. Callers override with
`chat_model("openai", timeout=60)` when they need it.

### Step 4 — Count tokens correctly during streaming

`ChatAnthropic.stream()` does *not* populate `response_metadata["token_usage"]`
until the stream closes (P01). If your cost dashboard reads `on_llm_end`, it
lags by the stream duration. Use `astream_events(version="v2")`:

```python
async for event in claude.astream_events({"input": "..."}, version="v2"):
    if event["event"] == "on_chat_model_stream":
        chunk = event["data"]["chunk"]
        if hasattr(chunk, "usage_metadata") and chunk.usage_metadata:
            meter.record(chunk.usage_metadata["input_tokens"],
                         chunk.usage_metadata["output_tokens"])
```

See [Token Accounting](references/token-accounting.md) for per-provider differences
(Anthropic reports input/output/cache separately; OpenAI aggregates; Gemini
reports completion-only on stream start).

### Step 5 — Pick the right `with_structured_output` method

| Provider | Model class | Recommended method | Why |
|---|---|---|---|
| Anthropic | Claude 3.5+, 4.x | `json_schema` | Provider-enforced, supports `$ref` and unions |
| OpenAI | GPT-4o, GPT-4-turbo | `json_schema` | Strict schema, `additionalProperties: false` enforced |
| OpenAI | GPT-3.5, legacy | `function_calling` | Pre-`json_schema` fallback |
| Gemini | Gemini 2.5 Pro/Flash | `json_schema` | Native structured output in 1.0+ |
| Any | Older or unknown | `json_mode` + Pydantic validate + retry | JSON-parseable only, no schema enforcement (P54) |

```python
from pydantic import BaseModel, ConfigDict

class Plan(BaseModel):
    model_config = ConfigDict(extra="ignore")  # P53 — models add helpful extra fields
    steps: list[str]
    estimated_minutes: int

structured = claude.with_structured_output(Plan, method="json_schema")
plan = structured.invoke("Plan a 3-step deploy")
```

Avoid `Optional[list[X]]` fields — they silently return `None` on some providers (P03).
See [Structured Output Methods](references/structured-output-methods.md) for a
concrete comparison matrix and fallback pattern.

## Output

- Chat models initialized with explicit timeouts (30s) and `max_retries=2`
- Content-safe extractor that handles both `str` and `list[dict]` shapes
- Factory-based routing with a single `BaseChatModel` return type
- Streaming token counter that reports incrementally, not at stream end
- `with_structured_output` chosen per provider capability, with Pydantic validation

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `AttributeError: 'list' object has no attribute 'lower'` | Treating Claude `AIMessage.content` as `str` (P02) | Use `msg.text()` or the Step 2 extractor |
| `ValidationError: extra fields not permitted` | Pydantic v2 strict default; model added fields (P53) | Set `model_config = ConfigDict(extra="ignore")` |
| `ValidationError: Field required` on `Optional[list[X]]` | `method="function_calling"` drops ambiguous unions (P03) | Switch to `method="json_schema"` |
| `anthropic.BadRequestError: tool_choice requires tools` | Forcing tool without binding any (P63) | Call `.bind_tools([tool])` before `.with_config(tool_choice=...)` |
| `google.api_core.exceptions.InvalidArgument: finish_reason=SAFETY` | Gemini default safety thresholds (P65) | Override `safety_settings` per model init or switch provider |
| Streaming response `response_metadata["token_usage"] == {}` | Stream end not yet reached (P01) | Use `astream_events(version="v2")` |
| `ImportError: cannot import name 'ChatOpenAI' from 'langchain.chat_models'` | Legacy 0.2 import path (P38) | `from langchain_openai import ChatOpenAI` |

## Examples

### Routing: cheap draft, expensive final

A common pattern — draft with `gpt-4o-mini`, finalize with `claude-sonnet-4-6`.
The factory in Step 3 makes this trivial; combined with `with_structured_output`
the finalize step returns a typed object.

See [Provider Quirks](references/provider-quirks.md) for the full
draft-then-finalize example including the token budget calculation.

### Extracting tool calls from a single-shot response

A classification task that should return one tool call with a typed argument.
Use `bind_tools([...], tool_choice={"type": "tool", "name": "Classify"})` for
a single forced call — but never loop on a forced choice (P63).

See [Structured Output Methods](references/structured-output-methods.md) for the
worked example and the decision tree for tool vs structured-output for extraction.

### Multi-modal: screenshot plus prompt

Images are passed as content blocks, but the block shape differs between providers
(P64). LangChain 1.0 abstracts this into a universal `image` content block.

See [Content Blocks](references/content-blocks.md) for the universal shape and
per-provider adapter examples.

## Resources

- [LangChain Python: Chat models](https://python.langchain.com/docs/integrations/chat/)
- [`AIMessage` API reference](https://python.langchain.com/api_reference/core/messages/langchain_core.messages.ai.AIMessage.html)
- [`with_structured_output`](https://python.langchain.com/docs/how_to/structured_output/)
- [`astream_events` v2](https://python.langchain.com/docs/how_to/streaming/#using-stream-events)
- [LangChain 1.0 release notes](https://blog.langchain.com/langchain-langgraph-1dot0/)
- Pack pain catalog: `docs/pain-catalog.md` (entries P01-P05, P53, P54, P58, P63-P65)

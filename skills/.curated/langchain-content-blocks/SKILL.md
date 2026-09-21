---
name: langchain-content-blocks
description: "Works correctly with LangChain 1.0's typed content blocks on AIMessage.content\n\
  \u2014 text, tool_use, image, thinking, document \u2014 across Claude, GPT-4o, and\n\
  Gemini, including multi-modal composition and tool-call iteration. Use when\ncomposing\
  \ multi-modal messages, iterating tool_use blocks, handling Claude's\nthinking content,\
  \ or unifying image inputs across providers. Trigger with\n\"langchain content blocks\"\
  , \"AIMessage.content\", \"tool_use block\", \"claude\nimage input\", \"langchain\
  \ multimodal\", \"thinking block replay\",\n\"claude citations\".\n"
allowed-tools: Read, Write, Edit, Bash(python:*)
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- content-blocks
- multimodal
- tool-use
compatibility: Designed for Claude Code
---
# LangChain Content Blocks (Python)

## Overview

On Claude, `AIMessage.content` is `list[dict]` even for pure text — so any
code from an OpenAI-first tutorial that calls `message.content.lower()` or
`message.content.split()` crashes with `AttributeError: 'list' object has
no attribute 'lower'` on the first production Claude call (P02).
Multi-modal code that works on GPT-4o breaks on Claude because pre-1.0
image-block shapes differed across providers (P64). Multi-turn Claude
replay with extended thinking fails with
`anthropic.BadRequestError: missing signature` when prior `thinking`
blocks are stripped. Forced `tool_choice` prevents
`stop_reason="end_turn"` and loops forever (P63).

This is the deep-dive companion to `langchain-model-inference`. That
skill's `references/content-blocks.md` covers the `str` vs `list[dict]`
divergence and a safe text extractor. **This skill goes further**:

- `tool_use` block iteration mechanics — IDs, args as dict vs JSON string, streaming deltas
- `thinking` blocks — signature, redaction, multi-turn replay semantics
- `document` blocks — Claude citations API, source types, citation extraction
- Multi-modal composition — universal 1.0 `image` shape, per-provider adapter behavior
- Per-provider size limits (Anthropic 5 MB/image up to 20 images, OpenAI 20 MB/image, Gemini 20 MB/request)

Pin: `langchain-core 1.0.x`, `langchain-anthropic >= 1.0`,
`langchain-openai >= 1.0`, `anthropic >= 0.40`. Pain-catalog anchors:
P02, P58, P63, P64.

## Prerequisites

- Python 3.10+
- `langchain-core >= 1.0, < 2.0`
- At least one provider package: `pip install langchain-anthropic langchain-openai`
- For extended thinking: `langchain-anthropic >= 1.0` and Claude Sonnet 4+ / Opus 4+
- For citations: `anthropic >= 0.40` and Claude Sonnet 4+
- Familiarity with `langchain-model-inference` (reads `references/content-blocks.md` first)

## Instructions

### Step 1 — Learn the block-type taxonomy

LangChain 1.0 defines six typed content blocks on `AIMessage.content`
(and on chunks during streaming):

| Block type | Produced by | Notes |
|------------|-------------|-------|
| `text` | All providers | On Claude, always wrapped as `[{"type":"text","text":"..."}]` |
| `tool_use` | Claude, GPT-4o, Gemini | Always round-trip via `msg.tool_calls`, not hand-parsed |
| `tool_result` | You (via `ToolMessage`) | One per `tool_use`; `tool_call_id` must match byte-for-byte |
| `image` | Claude vision, GPT-4o, Gemini | Universal 1.0 shape; adapter handles wire format per provider |
| `thinking` | Claude extended thinking only | Must preserve `signature` for replay |
| `document` | Claude citations API (Sonnet 4+) | Input-side only; citations attach to output `text` blocks |

See [Block-Type Matrix](references/block-type-matrix.md) for the full table
with streaming behavior and per-type gotchas.

### Step 2 — Iterate mixed content safely

For most code, use the helpers:

```python
text = msg.text()                    # concatenated text across all text blocks
tool_calls = msg.tool_calls          # normalized list[ToolCall]
usage = msg.usage_metadata           # input_tokens, output_tokens, cache_*
```

Hand-roll block iteration only when you need to (a) preserve order,
(b) extract `thinking` blocks for replay, or (c) read `citations`
metadata from `text` blocks. Order-preserving iteration:

```python
from langchain_core.messages import AIMessage

def iter_blocks(msg: AIMessage):
    if isinstance(msg.content, str):
        yield "text", {"type": "text", "text": msg.content}
        return
    for block in msg.content:
        if isinstance(block, dict):
            yield block.get("type", "unknown"), block
        else:
            yield getattr(block, "type", "unknown"), block
```

### Step 3 — Compose multi-modal messages with the universal `image` block

```python
import base64
from pathlib import Path
from langchain_core.messages import HumanMessage

def image_block(path: str) -> dict:
    data = base64.standard_b64encode(Path(path).read_bytes()).decode("ascii")
    mime = {"png": "image/png", "jpg": "image/jpeg",
            "jpeg": "image/jpeg", "webp": "image/webp"}[
        Path(path).suffix.lstrip(".").lower()]
    return {
        "type": "image",
        "source_type": "base64",   # or "url"
        "data": data,
        "mime_type": mime,
    }

msg = HumanMessage(content=[
    image_block("screenshot.png"),                         # put image FIRST
    {"type": "text", "text": "What is broken here?"},      # instruction LAST
])
response = claude.invoke([msg])
```

Three invariants:

1. `content` **must be `list[dict]`** when including non-text blocks.
2. Put the image *before* the instruction — Claude attends most to trailing tokens.
3. Respect provider limits (Anthropic: 5 MB/image, up to 20 images; OpenAI: 20 MB/image; Gemini: 20 MB/request total).

LangChain's adapter translates the universal shape to each provider's
wire format. See [Multi-Modal Composition](references/multimodal-composition.md)
for the full adapter table, MIME-type compatibility, and the
`document`/citations pattern.

### Step 4 — Iterate `tool_use` correctly across stream deltas

Canonical non-streaming:

```python
for tc in msg.tool_calls:
    output = tools[tc["name"]](**tc["args"])
    history.append(ToolMessage(content=str(output), tool_call_id=tc["id"]))
```

`tc["args"]` is already a parsed `dict` — do not `json.loads` it.
`tc["id"]` is provider-shaped (`toolu_*` on Anthropic, `call_*` on
OpenAI, 24+ chars) and must be copied verbatim to the `ToolMessage`.

Streaming is different. `tool_use.input` arrives as partial JSON
fragments across `on_chat_model_stream` events. Buffer with
`tool_call_chunks`, parse once at `on_chat_model_end`:

```python
from collections import defaultdict
import json

partial = defaultdict(str)   # index -> accumulated JSON fragment
meta = {}                     # index -> {name, id}

async for event in model.astream_events({"messages": [...]}, version="v2"):
    if event["event"] != "on_chat_model_stream":
        continue
    for tc_chunk in getattr(event["data"]["chunk"], "tool_call_chunks", []) or []:
        idx = tc_chunk["index"]
        if tc_chunk.get("name"):
            meta[idx] = {"name": tc_chunk["name"], "id": tc_chunk["id"]}
        if tc_chunk.get("args"):
            partial[idx] += tc_chunk["args"]

completed = [{**meta[i], "args": json.loads(partial[i])} for i in meta]
```

See [Tool-Use Iteration](references/tool-use-iteration.md) for
multi-tool-per-turn handling, `ToolMessage` ordering, and the forced-
`tool_choice` infinite-loop trap (P63).

### Step 5 — Preserve Claude `thinking` blocks for replay

Claude extended thinking (Sonnet 4+, Opus 4+) returns `thinking` blocks
carrying a cryptographic `signature`. The next turn must round-trip
those blocks **intact** or Anthropic rejects the request:

```
anthropic.BadRequestError: messages.1.content.0: missing signature
```

The foot-gun: `msg.text()` strips thinking blocks. Never do:

```python
# WRONG — thinking blocks lost, replay fails
history.append(AIMessage(content=ai_1.text()))
```

Correct — pass the `AIMessage` back verbatim:

```python
history.append(ai_1)   # preserves full content list + signatures
```

For persistence across sessions, serialize with
`messages_to_dict(...)` (not custom JSON), which preserves block
structure:

```python
import json
from langchain_core.messages import messages_to_dict, messages_from_dict

serialized = json.dumps(messages_to_dict([ai_1]))
restored = messages_from_dict(json.loads(serialized))
```

See [Thinking Blocks](references/thinking-blocks.md) for redaction
handling, the budget-tokens rule, and the interaction with tool calls.

### Step 6 — Provider-adapter checklist

Before sending any multi-modal or tool-using message:

1. Is `content` a `list[dict]` when it contains non-text blocks?
2. Are image blocks in the universal 1.0 shape (`source_type`, `data`, `mime_type`)?
3. Is each image under the target provider's limit? (5 MB / 20 MB / 20 MB total.)
4. If `tool_use` is involved, am I passing `msg.tool_calls` — not parsed `content`?
5. If extended thinking is on, am I returning the full `AIMessage` — not `msg.text()`?
6. System message at position 0 (P58) — not reordered by middleware?

## Output

- Block-type matrix applied to a specific response (which types present, which helper used)
- Safe iteration that preserves order, citations, and thinking signatures
- Multi-modal `HumanMessage` in the universal 1.0 `image` shape, portable across Claude/GPT-4o/Gemini
- `tool_use` stream-delta accumulator that buffers partial `input` JSON and parses once at end
- Multi-turn Claude replay that keeps `thinking` blocks intact (no `missing signature` errors)
- `document`/citations extractor that reads `citations` metadata from `text` blocks

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `AttributeError: 'list' object has no attribute 'lower'` | Treating `AIMessage.content` as `str` on Claude (P02) | Use `msg.text()` or iterate blocks |
| `anthropic.BadRequestError: messages.N.content.M: missing signature` | Stripped `thinking` block on replay | Pass `AIMessage` object back verbatim; never rebuild from `text()` |
| `anthropic.BadRequestError: tool_use_id not found in corresponding tool_result` | Typo / case mismatch in `ToolMessage.tool_call_id` | Copy `tc["id"]` verbatim |
| `anthropic.BadRequestError: tool_use ids were found without tool_result blocks` | Skipped a tool call | Emit one `ToolMessage` per `tool_call` (use `status="error"` on failure) |
| `anthropic.BadRequestError: image exceeds 5 MB limit` | Un-resized screenshot | Pre-resize to < 5 MB (1024x1024 JPEG 85 is ~500 KB) |
| `openai.BadRequestError: Invalid image data` | Hand-rolled `image_url` with wrong prefix | Use the universal block; adapter emits the `data:image/...;base64,` prefix |
| Infinite agent loop | Forced `tool_choice` inside a loop (P63) | Use `tool_choice="auto"` for agents; forced-choice only for single-call extraction |
| `json.JSONDecodeError` inside stream loop | Parsing partial `tool_use.input` fragment | Buffer in a `defaultdict(str)`; parse once at `on_chat_model_end` |
| Citations silently missing | Read via `msg.text()` which strips metadata | Iterate `msg.content` and read `block["citations"]` on text blocks |

## Examples

### Single-shot multi-modal on Claude + GPT-4o with one message object

```python
msg = HumanMessage(content=[
    image_block("ui.png"),
    {"type": "text", "text": "Identify the broken UI element."},
])
# Same message works on both providers via adapter translation
claude_resp = claude.invoke([msg])
gpt4o_resp = gpt4o.invoke([msg])
```

### Multi-turn Claude replay with extended thinking

```python
claude = ChatAnthropic(
    model="claude-sonnet-4-6",
    max_tokens=8192,
    thinking={"type": "enabled", "budget_tokens": 4096},
)

ai_1 = claude.invoke([HumanMessage(content="What is the capital of France?")])
# ai_1.content == [{"type":"thinking",...,"signature":"..."}, {"type":"text",...}]

# Turn 2 — pass ai_1 VERBATIM
ai_2 = claude.invoke([
    HumanMessage(content="What is the capital of France?"),
    ai_1,                                                    # thinking preserved
    HumanMessage(content="And the population?"),
])
```

See [Thinking Blocks](references/thinking-blocks.md) for the full replay
invariants and persistence pattern.

### Extracting Claude citations from `document` input

```python
doc_block = {
    "type": "document",
    "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64},
    "title": "Q3 Earnings Report",
    "citations": {"enabled": True},
}
resp = claude.invoke([HumanMessage(content=[
    doc_block,
    {"type": "text", "text": "What drove revenue this quarter?"},
])])

for block in resp.content:
    if block.get("type") != "text":
        continue
    print(block["text"])
    for c in block.get("citations", []):
        print(f"  -> {c['document_title']}: {c['cited_text']!r}")
```

`msg.text()` flattens this — you lose citations. See
[Multi-Modal Composition](references/multimodal-composition.md) for the
full `document` block reference including supported source types.

### Streaming `tool_use` with live argument rendering

See [Tool-Use Iteration](references/tool-use-iteration.md) for the
complete `tool_call_chunks` accumulator including multi-tool-per-turn
handling and the `ToolMessage` ordering invariant.

## Resources

- [LangChain messages concept](https://python.langchain.com/docs/concepts/messages/)
- [LangChain multimodality](https://python.langchain.com/docs/concepts/multimodality/)
- [`AIMessage` API reference](https://python.langchain.com/api_reference/core/messages/langchain_core.messages.ai.AIMessage.html)
- [Anthropic content blocks / messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages)
- [Anthropic extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
- [Anthropic citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- [OpenAI vision](https://platform.openai.com/docs/guides/vision)
- [Gemini multimodal](https://ai.google.dev/gemini-api/docs/vision)
- Companion skill: `langchain-model-inference` (read its `references/content-blocks.md` for the `str` vs `list[dict]` fundamentals)
- Pack pain catalog: `docs/pain-catalog.md` (entries P02, P58, P63, P64)

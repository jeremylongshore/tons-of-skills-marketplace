# Claude `thinking` Blocks — Signature & Replay

Extended thinking is a Claude-only feature (Opus 4+, Sonnet 4+, as of
`langchain-anthropic >= 1.0`). When enabled, Claude emits `thinking`
content blocks *before* the visible `text`/`tool_use` blocks. These
blocks carry a cryptographic `signature` that Anthropic uses to verify
the reasoning was produced by the model and not forged by the client.
Any multi-turn replay that strips or reorders these blocks will be
rejected.

## Enabling extended thinking

```python
from langchain_anthropic import ChatAnthropic

claude = ChatAnthropic(
    model="claude-sonnet-4-6",
    max_tokens=8192,
    thinking={"type": "enabled", "budget_tokens": 4096},
)
```

`budget_tokens` must be strictly less than `max_tokens`. Typical ratio
is 50/50 split: 4096 thinking + 4096 response with `max_tokens=8192`.
With `temperature=0`, thinking is deterministic per request but still
counts against output tokens (billed at standard output rate, not
cached).

## Block shape

A non-redacted thinking block:

```python
{
    "type": "thinking",
    "thinking": "The user is asking about X. I need to consider...",
    "signature": "EqoBCkgIBBABGAIiQKg..."  # ~120-char base64
}
```

A redacted block (Anthropic's safety system may redact high-risk
reasoning):

```python
{
    "type": "redacted_thinking",
    "data": "EuYBCkQIBBABGAI..."  # encrypted payload, opaque
}
```

You cannot read `redacted_thinking.data`. But you still have to
**pass the entire block back intact** on the next turn.

## The replay invariant

Anthropic validates three things on every multi-turn request that
follows a thinking-enabled response:

1. Every `thinking` or `redacted_thinking` block from the prior
   assistant turn is present in the new message list.
2. Blocks appear in the same order they were produced.
3. The `signature` field is byte-identical to what the API returned.

Violate any of these and you get:

```
anthropic.BadRequestError: messages.1.content.0: missing signature
anthropic.BadRequestError: messages.1.content.0.thinking: signature mismatch
```

This is why **`msg.text()` is unsafe for multi-turn Claude replay with
thinking enabled** — it flattens thinking blocks away, and the next
request then fails validation.

## Safe round-trip pattern

```python
from langchain_core.messages import AIMessage, HumanMessage

# Turn 1
msg_in_1 = HumanMessage(content="What is the capital of France?")
ai_1 = claude.invoke([msg_in_1])
# ai_1.content is list[dict]: [thinking_block, text_block]

# Turn 2 — must include ai_1 VERBATIM, including thinking
msg_in_2 = HumanMessage(content="And the population?")
ai_2 = claude.invoke([msg_in_1, ai_1, msg_in_2])
```

The `ai_1` message, when serialized back into the request, must carry
its `content` list unmodified. LangChain's `langchain-anthropic >= 1.0`
adapter does this correctly *if* you pass the `AIMessage` object back
as-is. The common footgun is:

```python
# WRONG — strips thinking
ai_1_text = ai_1.text()
history.append(AIMessage(content=ai_1_text))  # signature gone
```

```python
# RIGHT — preserves full block list
history.append(ai_1)  # or ai_1.model_dump(), keeping content intact
```

## Storing thinking blocks across sessions

If your app persists conversation history (Redis, Postgres, etc.) you
must serialize the *full* `content` list, not just the text. Use:

```python
import json
from langchain_core.messages import messages_to_dict, messages_from_dict

# Serialize
serialized = json.dumps(messages_to_dict([ai_1]))

# Deserialize
restored = messages_from_dict(json.loads(serialized))
```

`messages_to_dict` preserves block structure including signatures.
Rolling your own serializer that strips to `{"role": "assistant",
"content": ai_1.text()}` breaks replay — and the failure only surfaces
on the next turn, not at save time.

## Extracting just the thinking text (read-only)

When you want to display reasoning in a UI without sending it back:

```python
def extract_thinking(msg: AIMessage) -> list[str]:
    """Return plaintext thinking strings. Redacted blocks return a placeholder."""
    if isinstance(msg.content, str):
        return []
    out = []
    for block in msg.content:
        if not isinstance(block, dict):
            continue
        t = block.get("type")
        if t == "thinking":
            out.append(block["thinking"])
        elif t == "redacted_thinking":
            out.append("[redacted]")
    return out
```

Display, log, or summarize this — but never modify the underlying
`msg.content` in place.

## Interaction with tool calls

With tools bound and thinking enabled, the block order is
`thinking → tool_use`. When the model returns a tool call, the
`ToolMessage` you emit back lands *after* `ai_1` in the messages list:

```
messages = [
    HumanMessage("Analyze sales.csv"),
    ai_1,                          # [thinking, tool_use(analyze)]
    ToolMessage(content=..., tool_call_id=tc_id),
    # assistant turn 2 triggers here
]
```

Anthropic does not require you to pass thinking blocks from the
*previous-previous* turn once a new assistant turn has produced its own
thinking. You only need the immediately-prior assistant's thinking
intact. For long agent loops this matters — you do not accumulate all
thinking from all prior turns, only the most recent.

## Errors you will hit

| Error | Cause | Fix |
|-------|-------|-----|
| `anthropic.BadRequestError: messages.N.content.M: missing signature` | Thinking block stripped between turns | Pass `AIMessage` object back verbatim; do not reconstruct |
| `anthropic.BadRequestError: messages.N.content.M.thinking: signature mismatch` | Signature modified (e.g., whitespace re-encoding) | Serialize via `messages_to_dict`, not custom JSON |
| `ValueError: thinking.budget_tokens must be less than max_tokens` | `budget_tokens >= max_tokens` | Split: e.g., 4096 thinking + 4096 response with `max_tokens=8192` |
| `BadRequestError: extended thinking not supported on this model` | Using Haiku or pre-4.x model | Extended thinking requires Sonnet 4+ / Opus 4+ |
| Redacted block treated as text and concatenated into `msg.text()` output | `msg.text()` skips redacted (correct) but you may not notice reasoning is missing | Check `extract_thinking()` explicitly if you need to know whether redaction happened |

## References

- Anthropic extended thinking: <https://platform.claude.com/docs/en/build-with-claude/extended-thinking>
- `langchain-anthropic` release notes: <>
- `messages_to_dict` / `messages_from_dict`: <https://python.langchain.com/api_reference/core/messages/langchain_core.messages.utils.messages_to_dict.html>

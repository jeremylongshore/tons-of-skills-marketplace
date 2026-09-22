---
name: langchain-sdk-patterns
description: 'Compose LangChain 1.0 Python runnables with the production defaults
  the docs

  do not warn about: parallel batching, narrow fallbacks, and brace-safe prompts.

  Use when building an LCEL chain with RunnableSequence / RunnableParallel,

  adding resilience via .with_fallbacks(), tuning throughput with .batch()

  or .abatch(), or wrapping user input in a prompt template.

  Trigger with "langchain runnable", "with_fallbacks", "langchain batch",

  "runnable sequence", "lcel", "runnableparallel", "chain composition".

  '
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(pip:*)
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- lcel
- runnables
compatibility: Designed for Claude Code
---
# LangChain SDK Patterns (Python)

## Overview

`chain.batch(inputs)` in LangChain 1.0 does **not** parallelize by default. The
`max_concurrency` parameter defaults to **1** in several provider packages
(notably older `langchain-openai`), so a call like `chain.batch(inputs_1000)`
runs 1,000 sequential round-trips — same wall-clock time as a `for` loop, plus
the overhead of the batch machinery. Users file "batch is slow" tickets,
benchmark it against asyncio, and move to a different framework — when the fix
is two lines:

```python
# BAD — silently serializes (P08)
chain.batch(inputs_1000)

# GOOD — 10 in flight at once
chain.batch(inputs_1000, config={"max_concurrency": 10})
```

Then three more traps wait:

- **P07** — `.with_fallbacks([backup])` defaults `exceptions_to_handle=(Exception,)`,
  and on Python <3.12 that tuple includes `KeyboardInterrupt`. A `Ctrl+C` during
  a long run does not stop the process — it silently hands off to the fallback
  chain and keeps billing.
- **P57** — `ChatPromptTemplate.from_messages(..., template_format="f-string")`
  (the default) parses every `{` in every string, including user input. A user
  who pastes `{"error": "..."}` raises `KeyError: 'error'` at invoke time.
- **P53** — Pydantic v2 rejects extra fields by default; models cheerfully add
  `summary` or `confidence` to your `Plan` schema and `with_structured_output`
  crashes with `ValidationError: extra fields not permitted`.

This skill walks through LCEL composition (`RunnableSequence`, `RunnableParallel`,
`RunnableBranch`, `RunnablePassthrough`, `RunnableLambda`); the correct
`exceptions_to_handle` whitelist per provider; `max_concurrency` tuning with
safe ceilings (10 for most providers, 20+ with a semaphore); and prompt
templates that survive untrusted input. Pin: `langchain-core 1.0.x`,
`langchain-anthropic 1.0.x`, `langchain-openai 1.0.x`. Pain-catalog anchors:
P07, P08, P53, P57.

## Prerequisites

- Python 3.10+ (3.12+ fixes the `KeyboardInterrupt` half of P07 — upgrade if you can)
- `langchain-core >= 1.0, < 2.0`
- At least one provider: `pip install langchain-anthropic langchain-openai`
- `pydantic >= 2.0` for schema-aware composition
- Completed `langchain-model-inference` — the chat-model factory from that skill is reused here

## Instructions

### Step 1 — Compose with typed runnables, not lambdas

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

llm = ChatAnthropic(model="claude-sonnet-4-6", timeout=30, max_retries=2)

prompt = ChatPromptTemplate.from_messages(
    [("system", "You are a summarizer."), ("human", "{text}")],
    template_format="jinja2",  # P57 — see Step 4
)

# Sequence: prompt -> llm -> str
chain = prompt | llm | StrOutputParser()

# Parallel: run two sub-chains and merge
enriched = RunnableParallel(
    summary=chain,
    original=RunnablePassthrough(),
)
```

The `|` operator creates a `RunnableSequence`. Each step has a declared input
and output shape — swap a concrete model for a router and the type contract
holds. See [Runnable Composition Matrix](references/runnable-composition-matrix.md)
for when to reach for `RunnableSequence` vs `RunnableParallel` vs `RunnableBranch`
vs `RunnableLambda`, with input/output shape conventions for each.

### Step 2 — Add fallbacks with a narrow exception whitelist

```python
from anthropic import APIError, APITimeoutError, RateLimitError
from langchain_openai import ChatOpenAI

backup = ChatOpenAI(model="gpt-4o", timeout=30, max_retries=2)
backup_chain = prompt | backup | StrOutputParser()

# GOOD — only retry on transient provider errors
resilient = chain.with_fallbacks(
    [backup_chain],
    exceptions_to_handle=(RateLimitError, APIError, APITimeoutError),
)

# BAD — default `(Exception,)` catches KeyboardInterrupt on Python <3.12 (P07)
# resilient_bad = chain.with_fallbacks([backup_chain])
```

The default `exceptions_to_handle=(Exception,)` on Python <3.12 inherits
`KeyboardInterrupt` and `SystemExit` into the caught set — which means a
`Ctrl+C` during a long `.batch()` run falls through to the backup instead of
stopping. Python 3.12+ moved these under `BaseException` directly, which fixes
the inheritance path, but the default is still too broad: a Pydantic
`ValidationError` or a `ToolException` will trigger a pointless backup call.
See [Fallback Exception List](references/fallback-exception-list.md) for the
curated whitelist per provider with concrete imports.

### Step 3 — Batch with explicit concurrency

```python
import asyncio

inputs = [{"text": doc} for doc in documents]

# Synchronous batch — blocks until done
results = chain.batch(inputs, config={"max_concurrency": 10})

# Async batch — non-blocking
results = await chain.abatch(inputs, config={"max_concurrency": 10})
```

Safe ceilings: **10** for Anthropic and OpenAI at default tier; **20+** only
behind an `asyncio.Semaphore` if you are also tracking rate-limit headers.
Claude TPM/RPM limits vary by tier; OpenAI's TPD (tokens per day) is the
binding limit at scale. See [Batch Concurrency Tuning](references/batch-concurrency-tuning.md)
for per-provider ceilings and the semaphore pattern.

`invoke` vs `batch` vs `stream` — when each is correct:

| Method | Input shape | Concurrency | Error behavior | When to use |
|---|---|---|---|---|
| `.invoke(x)` | Single | 1 | Raises on failure | One-shot call, interactive, tests |
| `.batch(xs, config={"max_concurrency": N})` | List | N parallel | Raises on first failure unless `return_exceptions=True` | Bulk sync workloads, ETL, eval harnesses |
| `.abatch(xs, config={"max_concurrency": N})` | List | N parallel (async) | Same as `.batch` | Event loops, async web servers, LangGraph nodes |
| `.stream(x)` | Single | 1, chunked | Raises on failure | Interactive UI, live token display |
| `.astream(x)` / `.astream_events(x, version="v2")` | Single | 1, chunked (async) | Raises on failure | Async UIs, event-driven pipelines, token metering (see `langchain-model-inference`) |

Pass `return_exceptions=True` in the config to keep a batch from aborting on
the first failure — exceptions come back in the result list instead of raising.

### Step 4 — Escape prompt templates for untrusted input

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# BAD — default f-string format crashes on literal `{` in user input (P57)
bad = ChatPromptTemplate.from_messages(
    [("system", "Reply in JSON"), ("human", "{user_text}")]
)
bad.invoke({"user_text": '{"error": "oops"}'})  # KeyError: 'error'

# GOOD — jinja2 treats `{...}` as literal, uses `{{ var }}` for substitution
good = ChatPromptTemplate.from_messages(
    [("system", "Reply in JSON"), ("human", "{{ user_text }}")],
    template_format="jinja2",
)
good.invoke({"user_text": '{"error": "oops"}'})  # OK

# MIXED — message history is a list, use MessagesPlaceholder
with_history = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder("history"),
    ("human", "{{ question }}"),
], template_format="jinja2")
```

Rule of thumb: if any variable can contain user-provided free text (a paste,
a transcript, a code block), use `template_format="jinja2"`. The f-string
format is fine for trusted template authors composing fixed instructions, but
it is the wrong tool for user input. See [Prompt Template Escaping](references/prompt-template-escaping.md)
for the full brace-escaping rules and a `MessagesPlaceholder` reference.

### Step 5 — Validate structured output with `extra="ignore"`

```python
from pydantic import BaseModel, ConfigDict, Field

class Plan(BaseModel):
    # P53 — without this, the chain crashes when the model adds extra fields
    model_config = ConfigDict(extra="ignore")
    steps: list[str] = Field(default_factory=list)
    estimated_minutes: int

structured_chain = prompt | llm.with_structured_output(Plan, method="json_schema")
```

Pydantic v2 rejects unknown fields by default. Models trained on "be helpful"
add `summary`, `confidence`, `rationale` — the schema crashes instead of
dropping them. `extra="ignore"` is the right default for model outputs.

## Output

- `RunnableSequence` / `RunnableParallel` composition with declared input/output shapes
- `.with_fallbacks(exceptions_to_handle=(...))` with a narrow, provider-specific whitelist
- `.batch()` / `.abatch()` with explicit `max_concurrency` (10 default, 20+ behind semaphore)
- `ChatPromptTemplate.from_messages(..., template_format="jinja2")` for any template touching user input
- Pydantic schemas with `ConfigDict(extra="ignore")` for structured output
- A clear `invoke` / `batch` / `abatch` / `stream` / `astream` decision matrix for each chain stage

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `Ctrl+C` does not stop a long `.batch()`; fallback keeps running | `exceptions_to_handle=(Exception,)` swallows `KeyboardInterrupt` on Python <3.12 (P07) | Pass a narrow tuple: `exceptions_to_handle=(RateLimitError, APIError, APITimeoutError)` |
| `.batch(inputs)` takes same time as sequential loop | `max_concurrency` defaults to 1 (P08) | `config={"max_concurrency": 10}`; raise to 20+ only with a semaphore |
| `KeyError: '<some-token>'` when invoking a `ChatPromptTemplate` | f-string parser reads user input's `{` as a variable (P57) | `template_format="jinja2"`; escape literals as `{{`/`}}` in f-string mode |
| `ValidationError: extra fields not permitted` on structured output | Pydantic v2 strict-by-default (P53) | `model_config = ConfigDict(extra="ignore")` on the schema |
| `ValidationError` caught by fallback and treated as transient | Fallback whitelist too broad | Remove `ValidationError` from `exceptions_to_handle` so it surfaces |
| `.batch` aborts on the first failure, losing all results | Default raises on first error | Pass `config={"max_concurrency": 10, "return_exceptions": True}` and filter |
| Fallback chain never fires even on genuine `RateLimitError` | Provider's own `max_retries` consumes the error first | Lower `max_retries=0` on the primary when a fallback chain is the retry strategy |

## Examples

### Fan-out enrichment with RunnableParallel

A common pattern — given a document, produce a summary, extracted entities,
and sentiment in parallel. `RunnableParallel` runs sub-chains concurrently and
merges results into a dict. Combined with `.batch()` at the outer level, you
get N documents times 3 sub-chains in flight up to `max_concurrency`.

See [Runnable Composition Matrix](references/runnable-composition-matrix.md)
for the fan-out/fan-in pattern and the input/output shape of each runnable type.

### Resilient chain with per-provider fallback

Primary: Claude Sonnet 4.6. Fallback: GPT-4o. Catch only `RateLimitError`,
`APIError`, and `APITimeoutError` from each SDK — let `AuthenticationError`
and `ValidationError` crash the process so they get debugged, not masked.

See [Fallback Exception List](references/fallback-exception-list.md) for the
concrete imports per provider and a note on why `BadRequestError` should not
be in the whitelist.

### High-throughput batch with semaphore-bounded concurrency

At N >= 20 concurrent in-flight calls, provider rate-limit headers become the
bottleneck. Wrap `.abatch()` in an `asyncio.Semaphore` and honor the
`retry-after` header on 429 responses.

See [Batch Concurrency Tuning](references/batch-concurrency-tuning.md) for the
semaphore pattern and a table of provider TPM/RPM limits per tier.

### Prompt template over user-pasted JSON payload

Support ticket triage where users paste arbitrary JSON from their app's error
log. Without `template_format="jinja2"`, every single ticket with a JSON body
crashes the chain at template-render time.

See [Prompt Template Escaping](references/prompt-template-escaping.md) for the
worked example and the `MessagesPlaceholder` pattern for chat history.

## Resources

- [LangChain Python: Runnable interface](https://python.langchain.com/docs/concepts/runnables/)
- [LangChain Python: `with_fallbacks`](https://python.langchain.com/docs/how_to/fallbacks/)
- [LangChain Python: `batch` and `abatch`](https://python.langchain.com/docs/how_to/parallel/)
- [`ChatPromptTemplate` reference](https://python.langchain.com/api_reference/core/prompts/langchain_core.prompts.chat.ChatPromptTemplate.html)
- [Pydantic v2 `ConfigDict`](https://docs.pydantic.dev/latest/api/config/)
- [LangChain 1.0 release notes](https://blog.langchain.com/langchain-langgraph-1dot0/)
- Pack pain catalog: `docs/pain-catalog.md` (entries P07, P08, P53, P57)

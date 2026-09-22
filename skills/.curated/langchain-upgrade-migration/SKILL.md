---
name: langchain-upgrade-migration
description: "Migrate a LangChain 0.3.x Python codebase to LangChain 1.0 / LangGraph\
  \ 1.0 without\nbreaking production \u2014 named breaking changes, codemod patterns,\
  \ and a phased rollout.\nUse when upgrading LangChain or LangGraph from 0.2 or 0.3\
  \ to 1.0, when hitting\nImportError after an upgrade, or when preparing a migration\
  \ PR.\nTrigger with \"langchain 1.0 migration\", \"langchain upgrade\", \"LLMChain\
  \ removed\",\n\"initialize_agent removed\", \"ConversationBufferMemory removed\"\
  , \"astream_log deprecated\",\n\"langchain-anthropic 1.0\".\n"
allowed-tools: Read, Write, Edit, Grep, Bash(python:*)
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- migration
- upgrade
compatibility: Designed for Claude Code
---
# LangChain 1.0 Upgrade Migration (Python)

## Overview

The first deploy after `pip install -U langchain` crashes on import with:

```
ImportError: cannot import name 'ChatOpenAI' from 'langchain.chat_models'
```

Fix the import, restart, and the next error lands:

```
ImportError: cannot import name 'LLMChain' from 'langchain.chains'
AttributeError: module 'langchain.agents' has no attribute 'initialize_agent'
AttributeError: 'ConversationBufferMemory' object has no attribute 'save_context'
```

LangChain 1.0 removed four entire public-API surfaces in one release:

- Provider imports under `langchain.chat_models` / `langchain.llms` (pain code **P38**).
- The `LLMChain` family under `langchain.chains` (**P39**).
- `ConversationBufferMemory` and siblings under `langchain.memory` (**P40**).
- `initialize_agent` under `langchain.agents` (**P41**).

Anything that inspected `intermediate_steps` also breaks because the tuple shape changed from `(AgentAction, observation)` to `(ToolCall, observation)` (**P42**).

This skill walks a reversible, phased migration:

1. A pre-flight grep audit.
2. A pinned package upgrade (including the `langchain-anthropic` 1.0 peer-pin against `anthropic >= 0.40`, **P66**).
3. Codemod patterns for the seven removed APIs.
4. A rollout playbook with shadow traffic and a sub-five-minute rollback.

It covers **7 named breaking changes** and typically touches **10–100 files** in a mid-sized service.

The fix for the error above:

```python
# BEFORE (0.3)
from langchain.chat_models import ChatOpenAI

# AFTER (1.0)
from langchain_openai import ChatOpenAI
```

See [codemod-patterns.md](references/codemod-patterns.md) for the other six patterns.

## Prerequisites

- Python 3.10+ (LangChain 1.0 dropped 3.8/3.9).
- A working test suite for the service being migrated (the playbook runs `pytest -W error::DeprecationWarning` at every phase).
- Git on a clean working tree — the migration uses per-module commits so rollback is per-commit.
- Access to staging traffic or a request-mirror. Phase 4 of the playbook needs real-shape traffic.
- If conversations are persisted (Redis / Postgres / DynamoDB), a snapshot of the chat-history store before Phase 2. The LangGraph checkpointer uses a new schema and a naive rollback is data-lossy.

## Instructions

### Step 1 — Pre-flight grep audit

Inventory every 0.3 usage before touching a `requirements.txt`. Each grep below maps to one pain code and one codemod pattern.

```bash
grep -rn "from langchain\.chat_models\|from langchain\.llms" --include="*.py" .          # P38
grep -rn "from langchain\.chains\b\|\bLLMChain\b\|\bRetrievalQA\b" --include="*.py" .    # P39
grep -rn "from langchain\.memory\|ConversationBufferMemory" --include="*.py" .           # P40
grep -rn "initialize_agent\|AgentType\." --include="*.py" .                              # P41
grep -rn "\.tool_input\b\|intermediate_steps" --include="*.py" .                         # P42
grep -rn "astream_log\b" --include="*.py" .                                              # P67
```

Pipe the full set into `langchain-0.3-hits.txt` — that file is the migration work list. The [migration-detection.md](references/migration-detection.md) reference has the one-shot bundled block and a line-count triage table.

### Step 2 — Pin and upgrade packages together

LangChain 1.0 spans six coordinated packages. A partial upgrade (e.g. `pip install -U langchain-anthropic` without bumping `anthropic`) triggers `AttributeError` at import time (**P66**). Update all six in the same commit:

```
langchain>=1.0,<2
langchain-core>=0.3,<0.4
langchain-openai>=1.0
langchain-anthropic>=1.0
langgraph>=1.0,<2
anthropic>=0.40,<1
```

Apply:

```bash
pip install -U \
  "langchain>=1.0,<2" \
  "langchain-core>=0.3,<0.4" \
  "langchain-openai>=1.0" \
  "langchain-anthropic>=1.0" \
  "langgraph>=1.0,<2" \
  "anthropic>=0.40,<1"
```

Then snapshot the prior state for the rollback: `pip freeze > requirements.lock.pre-1.0.txt`.

### Step 3 — Codemod the four removed APIs

Work through the hits from Step 1 in this order (lowest blast radius first):

1. **Provider imports (P38)** — mechanical find/replace. `from langchain.chat_models import ChatOpenAI` → `from langchain_openai import ChatOpenAI`. Same pattern for `ChatAnthropic`, `OpenAIEmbeddings`, `Chroma`, etc.
2. **`LLMChain` → LCEL (P39)** — replace `chain = LLMChain(llm=llm, prompt=prompt)` with `chain = prompt | llm | StrOutputParser()`. Caller changes from `chain.run(x=1)` to `chain.invoke({"x": 1})`. If the caller treated the result as a dict, unwrap — `invoke` returns the string directly.
3. **`initialize_agent` → `create_react_agent` (P41)** — swap the import to `from langgraph.prebuilt import create_react_agent`. Tools written with `Tool(name=..., func=...)` still work; prefer the `@tool` decorator from `langchain_core.tools`. Agent input becomes `{"messages": [("user", "...")]}`; the final reply is `result["messages"][-1].content`.
4. **`ConversationBufferMemory` → LangGraph checkpointer (P40)** — swap the memory object for `MemorySaver()` (dev) or `SqliteSaver.from_conn_string(...)` (prod). Compile the graph/agent with `checkpointer=saver`, then pass `config={"configurable": {"thread_id": "..."}}` on every `invoke`. The `thread_id` is the conversation primary key.

Full before/after snippets for all four are in [codemod-patterns.md](references/codemod-patterns.md).

### Step 4 — Update streaming callers (P67)

`astream_log` still works in 1.0 but is soft-deprecated. The replacement is `astream_events(version="v2")`:

```python
# BEFORE
async for patch in chain.astream_log({"input": "hi"}):
    for op in patch.ops:
        if op["op"] == "add" and op["path"].endswith("/streamed_output/-"):
            print(op["value"], end="")

# AFTER
async for event in chain.astream_events({"input": "hi"}, version="v2"):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="")
```

Event names in v2: `on_chain_start`, `on_chain_end`, `on_chat_model_start`, `on_chat_model_stream`, `on_chat_model_end`, `on_tool_start`, `on_tool_end`. The payload under `data` is typed — `chunk` is an `AIMessageChunk`, not a raw string.

### Step 5 — Fix `intermediate_steps` consumers (P42)

If any code iterates `result["intermediate_steps"]` and reads `.tool` / `.tool_input`, it breaks silently in 1.0 — the tuples now hold `ToolCall` dicts, not `AgentAction` objects. The 1.0 equivalent reads from graph state:

```python
# BEFORE
for action, observation in result["intermediate_steps"]:
    log(action.tool, action.tool_input, observation)

# AFTER
for msg in result["messages"]:
    for tc in getattr(msg, "tool_calls", []) or []:
        log(tc["name"], tc["args"])   # .tool -> "name", .tool_input -> "args"
```

`ToolCall` dict keys are `name`, `args`, `id`. There is no `tool` or `tool_input` accessor anywhere in 1.0.

### Step 6 — Gate on deprecation-as-error tests

Turn `DeprecationWarning` into a test failure so any surviving 0.3 pattern surfaces before the rollout:

```bash
pytest -W error::DeprecationWarning
```

Do not promote to staging while this is red. Re-run the Step 1 greps — they should now return zero hits outside intentionally-pinned 0.3 test fixtures.

### Step 7 — Phased rollout on production traffic

Deploy behind a feature flag (`LANGCHAIN_1_0_ENABLED`), canary at 1%, and ramp to 100% over 2–4 hours with a 15-minute soak at each step. The rollback is always "flip the flag off" — not a redeploy. Full playbook (shadow traffic in staging, dual-write for persistent chat histories, per-phase exit criteria) is in [phased-rollout-playbook.md](references/phased-rollout-playbook.md).

## Output

- `requirements.txt` pinning all six 1.0 packages with the `anthropic >= 0.40` peer-pin (P66).
- `requirements.lock.pre-1.0.txt` in the repo root for five-minute rollback.
- Per-module git commits referencing pain codes (e.g. `refactor: migrate P39 LLMChain in billing-summariser to LCEL`).
- `langchain-0.3-hits.txt` work-list returning zero non-test hits on re-run.
- `pytest -W error::DeprecationWarning` green on the migration branch.
- Feature-flagged production cutover at 100%, flag removed after a full day of soak.

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `ImportError: cannot import name 'ChatOpenAI' from 'langchain.chat_models'` | **P38** — provider imports moved to partner packages | `from langchain_openai import ChatOpenAI` |
| `ImportError: cannot import name 'LLMChain' from 'langchain.chains'` | **P39** — `LLMChain` removed | Replace with LCEL: `prompt \| llm \| StrOutputParser()` |
| `AttributeError: 'ConversationBufferMemory' object has no attribute 'save_context'` | **P40** — memory classes removed from the public API | Swap for LangGraph `MemorySaver` / `SqliteSaver` with a `thread_id` |
| `AttributeError: module 'langchain.agents' has no attribute 'initialize_agent'` | **P41** — legacy agent constructor removed | `from langgraph.prebuilt import create_react_agent` |
| `AttributeError: 'ToolCall' object has no attribute 'tool'` | **P42** — tuple shape changed, fields renamed | Read `tc["name"]` and `tc["args"]` instead of `.tool` / `.tool_input` |
| `AttributeError: module 'anthropic' has no attribute 'AsyncAnthropic'` | **P66** — `langchain-anthropic 1.0` needs `anthropic >= 0.40` | Pin `anthropic>=0.40,<1` in the same commit as the `langchain-anthropic` bump |
| `DeprecationWarning: astream_log is deprecated; use astream_events(version="v2")` | **P67** — soft deprecation | Switch to `astream_events(version="v2")` and update event-name handling |

## Examples

### Example 1 — Minimal LLMChain to LCEL

```python
# BEFORE (0.3)
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([("system", "Summarise in one line."), ("user", "{text}")])
chain = LLMChain(llm=llm, prompt=prompt)
print(chain.run(text="LangChain 1.0 removed LLMChain."))

# AFTER (1.0)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([("system", "Summarise in one line."), ("user", "{text}")])
chain = prompt | llm | StrOutputParser()
print(chain.invoke({"text": "LangChain 1.0 removed LLMChain."}))
```

### Example 2 — Stateful agent with LangGraph checkpointer

```python
# AFTER (1.0)
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver    # use SqliteSaver / PostgresSaver in prod

@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(llm, [add], checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "user-42"}}
r1 = agent.invoke({"messages": [("user", "What's 2 + 3?")]}, config=config)
r2 = agent.invoke({"messages": [("user", "And plus 10?")]}, config=config)   # remembers "5"
print(r2["messages"][-1].content)
```

### Example 3 — Rollback pin

If Phase 5 of the rollout regresses and the feature flag is already off:

```bash
git checkout main
pip install -r requirements.lock.pre-1.0.txt
pytest                      # confirm green on the rollback pin
# deploy
```

## Resources

- [LangChain migration guide](https://python.langchain.com/docs/versions/migrating/)
- [LangChain release policy](https://python.langchain.com/docs/versions/release_policy/)
- [LangGraph prebuilt `create_react_agent`](https://langchain-ai.github.io/langgraph/reference/prebuilt/)
- [`astream_events` v2 reference](https://python.langchain.com/docs/concepts/streaming/)
- [Breaking changes matrix](references/breaking-changes-matrix.md) — all 7 named changes mapped to pain codes
- [Codemod patterns](references/codemod-patterns.md) — before/after for the 7 most common migrations
- [Phased rollout playbook](references/phased-rollout-playbook.md) — shadow traffic, dual-write, rollback
- [Migration detection](references/migration-detection.md) — pre-flight grep audit
- [One-pager](references/one-pager.md) — executive summary

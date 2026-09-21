---
name: langchain-langgraph-checkpointing
description: "Persist LangGraph agent state correctly with MemorySaver and PostgresSaver\
  \ \u2014\nthread_id discipline, JSON-serializable state rules, time-travel, schema\n\
  migration. Use when adding chat memory, migrating from ConversationBufferMemory,\n\
  or time-traveling an agent state to debug an incident.\nTrigger with \"langgraph\
  \ checkpointer\", \"MemorySaver\", \"PostgresSaver\",\n\"thread_id\", \"langgraph\
  \ time travel\", \"langgraph state persistence\".\n"
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(psql:*)
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- checkpointing
- persistence
- memory
compatibility: Designed for Claude Code
---
# LangGraph Checkpointing (Python)

## Overview

A chat agent that "keeps introducing itself" is almost always P16. The caller
invokes `graph.invoke(state)` without passing `config={"configurable":
{"thread_id": ...}}` — LangGraph's checkpointer silently spawns a fresh state per
call. No error, no warning, no log line. The user sees it; the code does not.

That is one of five separate checkpointing pitfalls this skill covers:

- **P16** — missing `thread_id` silently resets memory
- **P17** — `interrupt_before` raises `TypeError` when state holds non-JSON values
  (`datetime`, `Decimal`, custom classes) — and it raises *at the interrupt
  boundary*, not when the bad value was first assigned, so the traceback points
  at the wrong line
- **P20** — `PostgresSaver` does not auto-migrate checkpoint schema; upgrading
  `langgraph` silently reads old checkpoints as empty state
- **P40** — `ConversationBufferMemory` and the rest of legacy chat memory were
  removed in LangChain 1.0; checkpointers are the replacement
- **P51** — Deep Agent virtual-FS state in `state["files"]` grows unboundedly
  and eventually makes checkpoint writes a latency hotspot

This skill walks through picking a checkpointer by environment, enforcing
`thread_id` at the application boundary, constraining state to JSON-safe
primitives, Postgres setup + migration, and time-travel for incident debugging.
Pinned to `langgraph >= 1.0, < 2.0`, `langgraph-checkpoint-postgres >= 1.0, <
2.0`. Pain-catalog anchors: P16, P17, P18, P20, P22, P40, P51.

## Prerequisites

- Python 3.10+
- `pip install langgraph langchain-core` (both `>= 1.0, < 2.0`)
- For Postgres: `pip install langgraph-checkpoint-postgres` and a Postgres 13+
  instance
- For async Postgres: the same package plus `asyncpg`
- A `thread_id` strategy — typically a UUID4 string per conversation; see
  [thread-id-discipline.md](references/thread-id-discipline.md)

## Instructions

### Step 1 — Pick a checkpointer by environment

| Env | Checkpointer | Import |
|---|---|---|
| Dev, tests, notebooks | `MemorySaver` | `langgraph.checkpoint.memory` |
| Single-host CLI / desktop | `SqliteSaver` | `langgraph.checkpoint.sqlite` |
| Staging, prod (sync) | `PostgresSaver` | `langgraph.checkpoint.postgres` |
| Staging, prod (async / FastAPI) | `AsyncPostgresSaver` | `langgraph.checkpoint.postgres.aio` |

`MemorySaver` is in-process only. State vanishes on restart. Every worker has
its own (P22 analog for LangGraph). Use it anywhere state loss is acceptable;
never in a multi-worker web backend.

`PostgresSaver` and its async sibling require `setup()` on every startup *and
after every `langgraph` upgrade* (see Step 5). Checkpoint storage overhead is
typically **1-10 KB per step** of serialized state; plan your DB size
accordingly — a 2,000-turn conversation with 3 KB average state fits in
~6 MB per thread.

See [checkpointer-comparison.md](references/checkpointer-comparison.md) for the
full matrix including latency, concurrency, and the FastAPI lifespan pattern.

### Step 2 — Require `thread_id` at every invocation

This is the fail-loud middleware that prevents P16:

```python
from typing import Any

def require_thread_id(config: dict[str, Any]) -> dict[str, Any]:
    """Raise if thread_id is missing. Fails loud so P16 surfaces in tests,
    not in user-visible conversation logs."""
    configurable = (config or {}).get("configurable", {})
    thread_id = configurable.get("thread_id")
    if not thread_id:
        raise ValueError(
            "thread_id missing from config['configurable']. "
            "Every graph invocation must carry a thread_id."
        )
    if not isinstance(thread_id, str):
        raise TypeError(
            f"thread_id must be str (UUID), got {type(thread_id).__name__}"
        )
    return config
```

Call it at every application boundary:

```python
import uuid

config = {"configurable": {"thread_id": str(uuid.uuid4())}}
require_thread_id(config)
result = graph.invoke(initial_state, config=config)
```

For web endpoints, extract to a FastAPI dependency (`Header(...)` with no
default — forces `422` on missing). For multi-tenant apps, scope the thread id by composing tenant + user +
conversation ids into a single colon-delimited string (example:
`"acme:alice:conv-1"`). See
[thread-id-discipline.md](references/thread-id-discipline.md) for UUID
generation, rotation, and the integration test that proves tenants do not share
state.

### Step 3 — Keep state JSON-serializable (TypedDict, primitives only)

```python
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage


class AgentState(TypedDict):
    # Messages are safe — LangGraph registers a custom serializer.
    messages: Annotated[list[AnyMessage], add_messages]

    # Primitives only below. NO datetime, NO Decimal, NO custom classes.
    user_id: str
    turn_count: int
    last_action_at: str           # ISO string, not datetime.datetime
    pending_approval: bool
    metadata: dict[str, str]      # dict keys must be str
    plan: list[dict[str, str]]    # list of primitive dicts
```

The rule: **state fields must be JSON-safe primitives or recursive structures
of them** (`str`, `int`, `float`, `bool`, `None`, `list`, `dict[str, ...]`).
`json.dumps(state)` must succeed. If it raises, the checkpointer raises —
often at a HITL interrupt many steps later (P17), which is why the traceback
never points at the line that introduced the bad value.

For non-primitive inputs, coerce at node output boundaries with a helper:

```python
from datetime import datetime
from decimal import Decimal

def record_purchase(state: AgentState) -> dict:
    now = datetime.utcnow()
    price = Decimal("19.99")
    return {
        "last_action_at": now.isoformat(),
        "metadata": {**state["metadata"], "price": str(price)},
    }
```

Forbidden-types reference and the full `to_state` / `from_state` helper pair
are in [json-serializability-rules.md](references/json-serializability-rules.md).

### Step 4 — Compile the graph with a checkpointer (Postgres, sync)

```python
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph
import os

DB_URI = os.environ["DATABASE_URL"]

def build_graph() -> StateGraph:
    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("human_approval", human_approval_node)
    builder.set_entry_point("agent")
    builder.add_edge("agent", "human_approval")
    builder.set_finish_point("human_approval")
    return builder

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()     # Idempotent. Creates checkpoint tables if missing.
    graph = build_graph().compile(
        checkpointer=checkpointer,
        interrupt_before=["human_approval"],
    )

    config = {"configurable": {"thread_id": "user-123"}}
    require_thread_id(config)
    result = graph.invoke({"messages": [HumanMessage("hi")]}, config=config)
```

For async, mirror the pattern with `AsyncPostgresSaver.from_conn_string(...)`
inside a FastAPI `@asynccontextmanager` lifespan; every call site uses
`await graph.ainvoke(...)`.

### Step 5 — Run `setup()` on startup AND after every `langgraph` upgrade

P20 is the quiet one: you `pip install --upgrade langgraph`, tests pass, CI
goes green, you deploy. Existing threads come back empty. No DB error.

```python
# Put this in your deploy script / migration runbook:
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()
    # Sanity check: read one known thread and assert it's not empty.
    snap = checkpointer.get({"configurable": {"thread_id": "canary-thread"}})
    assert snap is not None, "Canary thread lost after schema migration"
```

Run this in **staging** first, with a canary thread whose state you pre-populated
from an older `langgraph` version. If the assertion holds, promote. If not,
the migration path is: dump checkpoints, upgrade, restore via a migration
script. Do **not** promote to production on a version bump without this check.

### Step 6 — Time-travel for incident debugging

Every checkpoint is keyed by `(thread_id, checkpoint_id)` and reachable via
`graph.get_state_history(config)`:

```python
config = {"configurable": {"thread_id": bad_thread_id}}
history = list(graph.get_state_history(config))

for i, snap in enumerate(history):
    print(i, snap.metadata.get("step"), snap.next, list(snap.values.keys()))

# Resume from a specific prior checkpoint — None as input = "use this state":
past = history[3]                                    # history is newest-first
result = graph.invoke(None, config=past.config)       # past.config pins checkpoint_id
```

To fix state and replay:

```python
graph.update_state(
    past.config,
    {"retry_count": 0, "error_reason": None},
    as_node="validator",
)
graph.invoke(None, config=past.config)
```

The original branch is preserved — `update_state` creates a new checkpoint
alongside the old one. Useful for forensics and for A/B comparing an old vs
new model on the exact same state.

See [time-travel-and-replay.md](references/time-travel-and-replay.md) for the
full incident playbook, branching for A/B eval, and checkpoint pruning SQL.

## Output

- A checkpointer selected by environment, not copy-pasted from a tutorial
- A `require_thread_id` middleware that fails loud on missing `thread_id`, and
  at least one integration test that asserts two tenants do not share state
- An `AgentState` TypedDict constrained to JSON-safe primitives, plus a
  `to_state` helper at node output boundaries for `datetime` / `Decimal` /
  Pydantic / enums
- `PostgresSaver.setup()` wired into startup **and** every deploy that bumps
  `langgraph`
- An incident runbook that uses `get_state_history` + `update_state` to
  time-travel an agent state, with prior branches preserved

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Agent forgets every turn, no error logged | Missing `thread_id` (P16) | Add `require_thread_id` middleware at app boundary; FastAPI `Header(...)` with no default |
| `TypeError: Object of type datetime is not JSON serializable` at a HITL pause | Non-JSON value in state (P17) | Coerce at node output: `dt.isoformat()`, `str(decimal)`, `model.model_dump(mode="json")` |
| Upgrading `langgraph` returns empty state for existing threads | Checkpoint schema drift (P20) | `PostgresSaver.setup()` after every upgrade; canary-thread assertion in staging before prod |
| `ImportError: cannot import name 'ConversationBufferMemory'` | Legacy memory removed in 1.0 (P40) | Migrate to `MemorySaver`/`PostgresSaver` + `thread_id` per conversation |
| Checkpoint writes take 500+ ms on Deep Agent runs | Unbounded `state["files"]` growth (P51) | Add cleanup node that prunes `state["files"]` older than N steps |
| `Command(update={"messages": [x]})` erases prior messages | Missing reducer (P18) | `messages: Annotated[list[AnyMessage], add_messages]` |
| Mixed `graph.invoke` with `AsyncPostgresSaver` | Sync call on async saver | Use `await graph.ainvoke(...)` everywhere, or switch to sync `PostgresSaver` |

## Examples

### Minimal chat agent with `MemorySaver`

Dev-mode multi-turn chat that survives within a single process. Good for local
iteration and pytest fixtures; state vanishes on restart.

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic

checkpointer = MemorySaver()
agent = create_react_agent(
    model=ChatAnthropic(model="claude-sonnet-4-6"),
    tools=[...],
    checkpointer=checkpointer,
)
config = {"configurable": {"thread_id": "dev-session-1"}}
agent.invoke({"messages": [HumanMessage("hi")]}, config=config)
agent.invoke({"messages": [HumanMessage("remember my name is alice")]}, config=config)
agent.invoke({"messages": [HumanMessage("what's my name?")]}, config=config)  # alice
```

### Multi-tenant Postgres + FastAPI lifespan

Async production shape. One `AsyncPostgresSaver` pool, thread-id extracted from
a required header, tenants isolated by a composite key.

See [checkpointer-comparison.md](references/checkpointer-comparison.md) for the
complete FastAPI lifespan pattern and pool sizing advice (`max_size` needs to
exceed concurrent graph count, and the LangGraph pool should be separate from
the application's primary DB pool).

### Migrating from `ConversationBufferMemory` (P40)

Legacy 0.x pattern replaced end-to-end:

```python
# OLD — raises ImportError on 1.0:
# from langchain.memory import ConversationBufferMemory
# memory = ConversationBufferMemory()
# chain = LLMChain(llm=llm, memory=memory)

# NEW:
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres import PostgresSaver

with PostgresSaver.from_conn_string(DB_URI) as cp:
    cp.setup()
    agent = create_react_agent(model=llm, tools=tools, checkpointer=cp)
    config = {"configurable": {"thread_id": user_session_id}}
    agent.invoke({"messages": [HumanMessage(user_input)]}, config=config)
```

The `thread_id` is now the "session key" that `ConversationBufferMemory` used
to carry implicitly.

### Incident time-travel

Production returned a wrong answer for `thread_id=bad-thread` at 14:03.
Walk history newest-first, inspect the prior state, patch and replay:

```python
config = {"configurable": {"thread_id": "bad-thread"}}
history = list(graph.get_state_history(config))
for i, snap in enumerate(history):
    print(i, snap.metadata.get("step"), snap.next)
# Assume step 7 wrote the bad output; step 6 is the input.
prior = history[-7]  # or index by metadata["step"]
print("input to bad node:", prior.values)
graph.update_state(prior.config, {"retry_count": 0}, as_node="validator")
graph.invoke(None, config=prior.config)  # new branch with correct result
```

Full playbook (finding `thread_id` in logs, inspecting `writes` metadata,
pruning history) in
[time-travel-and-replay.md](references/time-travel-and-replay.md).

## Resources

- [LangGraph persistence concepts](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [Checkpointer API reference](https://langchain-ai.github.io/langgraph/reference/checkpoints/)
- [LangGraph HITL concepts](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
- [LangGraph 1.0 release notes](https://blog.langchain.com/langchain-langgraph-1dot0/)
- Pack pain catalog: `docs/pain-catalog.md` (entries P16, P17, P18, P20, P22, P40, P51)
- Related skills in this pack: `langchain-langgraph-basics`, `langchain-langgraph-agents`, `langchain-upgrade-migration`, `langchain-common-errors`

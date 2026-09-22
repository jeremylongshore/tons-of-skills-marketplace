---
name: langchain-langgraph-basics
description: "Build a correct LangGraph 1.0 StateGraph \u2014 typed TypedDict state\
  \ with reducers,\nnodes, edges, compile, and recursion budgets \u2014 without hitting\
  \ the silent-termination\nand state-replacement traps. Use when writing your first\
  \ LangGraph StateGraph,\ndiagnosing why a graph halted without reaching END, or\
  \ picking recursion_limit.\nTrigger with \"langgraph statgraph\", \"langgraph basics\"\
  , \"GraphRecursionError\",\n\"langgraph conditional edges\".\n"
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
- statgraph
compatibility: Designed for Claude Code
---
# LangChain LangGraph Basics (Python)

## Overview

A conditional edge whose router returns a string that is not in `path_map` halts
the graph without reaching `END`. No exception. No log line. The invocation just
returns whatever state existed at the halt point — pain-catalog entry P56, and
the single most common reason a newly wired `StateGraph` "almost works." The
sibling pain: `Command(update={"messages": [msg]})` wipes the prior message
history because `messages` was declared as a plain `list[AnyMessage]` instead of
`Annotated[list[AnyMessage], add_messages]` — the reducer is what turns `update`
into "append" instead of "replace" (P18).

Two more gotchas this skill defuses:

- P55 — `GraphRecursionError: Recursion limit of 25 reached` fires on graphs
  that never loop, because `recursion_limit` counts **supersteps** (one step
  per synchronous batch of node executions), not loop iterations. A planner
  - executor + validator + summarizer can hit 25 without any cycle.
- P20 — Upgrading `langgraph` silently reads old `PostgresSaver` checkpoints
  as empty state. Checkpoint schemas evolve; `PostgresSaver.setup()` must be
  rerun after every version bump before production traffic.

This skill walks through a minimal `StateGraph` end to end: a `TypedDict` state
with reducers on every list field, node functions that return partial-state
dicts, edges and defensive conditional edges with `END` as a fallback in
`path_map`, compilation with a checkpointer, `recursion_limit` sizing, and
invocation with an explicit `thread_id`. Pin: `langgraph 1.0.x`,
`langchain-core 1.0.x`. Pain-catalog anchors: P16, P18, P20, P55, P56.

## Prerequisites

- Python 3.10+
- `pip install langgraph>=1.0,<2.0 langchain-core>=1.0,<2.0`
- A chat model (see `langchain-model-inference`), or a pure-logic graph with no LLM
- For persistence beyond a single process: `pip install langgraph-checkpoint-postgres` and a Postgres 14+ instance

## Instructions

### Step 1 — Define state as a `TypedDict` with reducers on list fields

Every list-shaped field in state needs a reducer. Without one, `Command(update=...)`
and node returns *replace* the field. The message-history reducer lives in
`langgraph.graph.message`:

```python
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
import operator

class AgentState(TypedDict):
    # Reducer "add_messages" appends + dedupes by message id (P18)
    messages: Annotated[list[AnyMessage], add_messages]

    # Plain list field also needs a reducer — use operator.add to concat
    scratchpad: Annotated[list[str], operator.add]

    # Scalars don't need a reducer; update replaces them
    step_count: int
    done: bool
```

If you forget the reducer on `messages`, a resume with
`Command(update={"messages": [new_msg]})` will overwrite the entire prior
history. Validate reducers are in place with `graph.get_graph().draw_mermaid()` —
annotated fields render with their reducer name.

See [State Reducers](references/state-reducers.md) for the built-in list
(`add_messages`, `operator.add`, `max`, `min`) and how to write a custom merger
for non-trivial merge logic.

### Step 2 — Write nodes as functions that return partial-state dicts

A node takes the full state and returns only the keys it wants to update. The
reducer handles merge:

```python
def plan(state: AgentState) -> dict:
    # Returning a dict means "update these fields"
    return {
        "messages": [("assistant", "Plan: step 1, step 2, step 3")],
        "scratchpad": ["planned_at_step_1"],
        "step_count": state["step_count"] + 1,
    }

def execute(state: AgentState) -> dict:
    return {
        "messages": [("assistant", f"Executed {state['step_count']} steps")],
        "done": state["step_count"] >= 3,
    }
```

Nodes must be deterministic on their inputs — LangGraph re-runs them during
time-travel replay, and a side-effecting node (DB write without idempotency key)
will double-fire. Push side effects to the checkpointer boundary or tool calls.

### Step 3 — Wire edges and conditional edges defensively

```python
from typing import Literal
from langgraph.graph import StateGraph, START, END

# Router MUST return a value in the path_map keyset (P56)
def should_continue(state: AgentState) -> Literal["execute", "end"]:
    if state["done"] or state["step_count"] >= 10:
        return "end"
    return "execute"

builder = StateGraph(AgentState)
builder.add_node("plan", plan)
builder.add_node("execute", execute)

builder.add_edge(START, "plan")

# path_map ALWAYS includes END as a fallback — if the router returns anything
# else, the graph reaches END instead of halting silently (P56)
builder.add_conditional_edges(
    "plan",
    should_continue,
    path_map={"execute": "execute", "end": END},
)
builder.add_edge("execute", "plan")  # loop back to plan
```

The `Literal` return annotation on `should_continue` is a static guard — mypy
catches typos before runtime. `path_map={"execute": "execute", "end": END}`
is the spelled-out form; the compact form `path_map=["execute", END]` also works
when router return values match node names directly.

See [Conditional Edges](references/conditional-edges.md) for all four
`add_conditional_edges` signatures, the `path` vs `path_map` distinction, and
a pytest pattern that asserts every router return value hits a known route.

### Step 4 — Compile with a checkpointer

```python
from langgraph.checkpoint.memory import MemorySaver

# MemorySaver is in-process — use PostgresSaver in production (P20)
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

For production, swap to `langgraph.checkpoint.postgres.PostgresSaver`. After
every `langgraph` version bump, run `PostgresSaver.setup()` in staging before
prod traffic — the schema evolves and old rows are silently read as empty state.

### Step 5 — Pick `recursion_limit` for the graph's superstep count

`recursion_limit` defaults to **25**. It is not a loop counter; it counts
**total supersteps**, and a superstep is one synchronous round of node
executions (parallel branches in the same step count as one). Typical shapes:

| Graph shape | Supersteps per run | Suggested `recursion_limit` |
|---|---|---|
| Simple ReAct agent (plan → tool → observe → done) | 6-12 | 15 |
| Planner + executor + validator | 12-25 | 30 |
| Deep agent with sub-plans, reflection, branch merge | 30-60 | 75 |
| Fan-out with N parallel branches that re-join | N + merge steps | 2 × max depth |

```python
config = {
    "configurable": {"thread_id": "user-42"},  # required for checkpointing (P16)
    "recursion_limit": 30,
}
result = graph.invoke({"messages": [], "scratchpad": [], "step_count": 0, "done": False}, config)
```

If you hit `GraphRecursionError` on a graph that clearly isn't looping (P55),
add `print(state["step_count"])` at the entry of each node to see the actual
superstep count, then either raise the limit or restructure with a subgraph
so each subgraph gets its own budget.

See [Recursion Limits](references/recursion-limits.md) for the full derivation
and a diagnostic script that traces superstep count at runtime.

### Step 6 — Invoke with `thread_id` in `config["configurable"]`

Every invocation against a checkpointer-backed graph needs a `thread_id` in
`config["configurable"]`. Without it, each call gets a fresh state with no
warning (P16). Enforce it at your application boundary:

```python
def run_agent(user_id: str, user_message: str) -> dict:
    config = {
        "configurable": {"thread_id": user_id},
        "recursion_limit": 30,
    }
    assert config["configurable"].get("thread_id"), "thread_id required"
    return graph.invoke(
        {"messages": [("user", user_message)], "scratchpad": [], "step_count": 0, "done": False},
        config,
    )
```

See [First Graph Walkthrough](references/first-graph-walkthrough.md) for a
line-by-line annotation of a minimal 3-node graph that demonstrates typed
state, a reducer, and a conditional edge to `END`.

## Decision Tree

```
Is your field a list you want to append?
  -> Annotate with add_messages (for messages) or operator.add (for plain lists)

Is your router adding a new output string?
  -> Add that string to path_map BEFORE deploying; include END as a fallback

Hitting GraphRecursionError on a non-looping graph?
  -> supersteps != iterations; raise recursion_limit to 50 or split into subgraphs

Upgraded langgraph minor version?
  -> Re-run PostgresSaver.setup() in staging before routing prod traffic

Multi-turn agent forgets between calls?
  -> thread_id missing from config["configurable"] — enforce at boundary
```

## Output

- `TypedDict` state with reducer annotations on every list field
- Node functions returning partial-state dicts, free of hidden side effects
- Conditional edges with `Literal`-typed routers and `END` in every `path_map`
- Compiled graph with a checkpointer matched to the deployment shape
- `recursion_limit` sized from the superstep count table, not the default 25
- Invocations with explicit `thread_id` validated at the app boundary

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `GraphRecursionError: Recursion limit of 25 reached` | Supersteps counter, not loops (P55) | Raise `recursion_limit` or split into subgraphs; add per-node logging to count actual steps |
| Graph halts without reaching `END`, no error | Router returned a value not in `path_map` (P56) | Type router as `Literal[...]`; include `END` as a default key in `path_map` |
| `Command(update={"messages": [msg]})` wipes history | Missing reducer on list field (P18) | Annotate as `Annotated[list[AnyMessage], add_messages]` |
| Multi-turn memory resets between calls, no warning | Missing `thread_id` in config (P16) | Assert `config["configurable"]["thread_id"]` at app boundary |
| Old checkpoints read as empty state after upgrade | Schema change; `PostgresSaver` doesn't auto-migrate (P20) | Run `PostgresSaver.setup()` in staging after every `langgraph` bump |
| `TypeError: Object of type datetime is not JSON serializable` at interrupt | Non-primitive in state (P17) | Keep state primitives-only; serialize complex types to ISO strings |
| Node runs twice during replay | Time-travel re-executes deterministic nodes | Push side effects to tools or the checkpointer write boundary |

## Examples

### Building a minimal linear graph (no loop)

Three nodes (`plan` → `execute` → `summarize`), no conditionals, one reducer on
`messages`. Runs in 4 supersteps (START counts as one). Safe at default
`recursion_limit=25`, but set it to 10 explicitly so readers see the budget.

See [First Graph Walkthrough](references/first-graph-walkthrough.md) for the
line-by-line annotation and the `graph.get_graph().draw_mermaid()` output.

### Adding a conditional loop with a bounded retry budget

A validator node that either completes (`"end"` → `END`) or retries
(`"retry"` → back to executor), bounded by `step_count >= 3`. The router is
`Literal["retry", "end"]` and `path_map` maps both. Caps at 7 supersteps, so
`recursion_limit=15` is plenty of headroom.

See [Conditional Edges](references/conditional-edges.md) for the full example
and the pytest that iterates every `Literal` branch.

### Diagnosing a mystery `GraphRecursionError`

A planner that fans out to 4 parallel executors, then a validator, then a
summarizer. Looks linear in the mermaid diagram, hits
`GraphRecursionError: Recursion limit of 25 reached` on 10% of runs. Cause:
each parallel executor counts as its own superstep branch when the merge node
is conditional. Fix: raise to 50 or wrap the fan-out in a subgraph.

See [Recursion Limits](references/recursion-limits.md) for the diagnostic
script and the subgraph refactor.

## Resources

- [LangGraph: Low-level concepts (StateGraph, reducers, nodes, edges)](https://langchain-ai.github.io/langgraph/concepts/low_level/)
- [LangGraph: Persistence and checkpointing](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [LangGraph: `add_messages` reducer](https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.message.add_messages)
- [LangGraph: `add_conditional_edges` API](https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.state.StateGraph.add_conditional_edges)
- [LangGraph: Recursion limit and supersteps](https://langchain-ai.github.io/langgraph/how-tos/recursion-limit/)
- [LangChain 1.0 release notes](https://blog.langchain.com/langchain-langgraph-1dot0/)
- Pack pain catalog: `docs/pain-catalog.md` (entries P16, P17, P18, P20, P55, P56)

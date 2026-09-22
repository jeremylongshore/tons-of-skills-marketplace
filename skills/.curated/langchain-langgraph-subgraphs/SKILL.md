---
name: langchain-langgraph-subgraphs
description: "Compose LangGraph 1.0 subgraphs correctly \u2014 shared state key propagation,\n\
  Send / Command(graph=...) dispatch, callback scoping, per-subgraph recursion\nbudgets,\
  \ and testing each subgraph in isolation. Use when building a planner +\nexecutor,\
  \ a nested agent team, or a reusable subgraph library. Trigger with\n\"langgraph\
  \ subgraph\", \"langgraph composition\", \"langgraph send\",\n\"nested agents\"\
  , \"langgraph state propagation\", \"Command(graph=...)\",\n\"langgraph subgraph\
  \ callbacks\".\n"
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
- subgraphs
- composition
compatibility: Designed for Claude Code
---
# LangGraph Subgraphs and Composition (Python)

## Overview

A parent `StateGraph` invokes a compiled child subgraph as a node. The child
node writes `state["answer"] = "42"` and returns. The parent's next node reads
`state["answer"]` and gets `None`. No error, no warning, no deprecation notice —
just a silent `None` that surfaces as a wrong answer three nodes later when the
router picks the "couldn't find it" branch.

The cause is pain-catalog entry **P21**: LangGraph subgraphs run on an
**independent state schema**. Only keys declared in *both* the parent's
`TypedDict` and the child's `TypedDict` propagate across the subgraph boundary.
`answer` existed in the child schema but not the parent schema, so it was
discarded on return. The fix is to declare `answer` in both schemas (with
matching reducers, if the field is a list) or to use explicit
`Command(graph=ParentGraph, update={"answer": "42"})` to bubble it up.

The second silent failure waits one step further. Attach a tracing callback to
the parent runnable via `parent.with_config(callbacks=[tracer])` and invoke.
The tracer fires on parent nodes and never on child tool calls. This is
pain-catalog entry **P28**: LangGraph creates a fresh runtime per subgraph, so
callbacks bound at *definition time* do not inherit. The fix is to pass
callbacks at *invocation time* via `config["callbacks"]`, which does propagate.

This skill walks through the shared-state contract, three dispatch patterns
(compiled subgraph as a node, `Send` fan-out, `Command(graph=Parent)` bubble-up),
callback scoping, per-subgraph `recursion_limit` budgets, and a testing pattern
that exercises every subgraph in isolation before composition. Pin:
`langgraph 1.0.x`, `langchain-core 1.0.x`. Pain-catalog anchors: **P21, P28**,
with supporting references to P18 (reducers), P19 (stream modes on nested
graphs), and P55 (recursion budget).

A planner-executor is typically **1 parent + 2-4 subgraphs**; a hierarchical
agent team with a supervisor and N specialists is **1 parent + N subgraphs**.
Each subgraph has its own independent `recursion_limit` (default 25) — a parent
at step 20 can still invoke a child that runs 25 of its own steps.

## Prerequisites

- Python 3.10+
- `langgraph >= 1.0, < 2.0`
- `langchain-core >= 1.0, < 2.0`
- Completion of `langchain-langgraph-basics` (L25) — `StateGraph`, `TypedDict`
  state, `Annotated[list, add_messages]` reducer, `MemorySaver` checkpointing
- Test tooling: `pytest`, `langchain_core.language_models.fake_chat_models.FakeListChatModel`

## Instructions

### Step 1 — Declare the shared-state contract explicitly

The single most important decision when composing subgraphs is: **which keys
cross the boundary?** Every key that must survive the call *must* appear in
both `TypedDict` schemas with compatible types and reducers.

```python
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

# Keys both schemas declare -> these propagate
# Keys only in parent -> invisible to child
# Keys only in child -> discarded on return (P21)

class ParentState(TypedDict):
    # Shared with every subgraph
    messages: Annotated[list[AnyMessage], add_messages]  # P18 reducer required
    session_id: str

    # Parent-only coordination fields
    plan: list[str]
    current_step: int

class ExecutorState(TypedDict):
    # Shared with parent — must match reducer exactly (P18)
    messages: Annotated[list[AnyMessage], add_messages]
    session_id: str

    # Executor-only scratch — parent never sees these
    tool_result: dict | None
    retries: int
```

If `messages` on the child used a different reducer (or no reducer), list
updates would silently replace instead of append on one side of the boundary
(P18). The `messages` + `session_id` pair is the propagation contract. Everything
else is private to its owner.

See [State Contract](references/state-contract.md) for the full
state-propagation matrix and the "subset rule" for schema inheritance.

### Step 2 — Pick the dispatch pattern

Three ways a parent can invoke a subgraph, and each solves a different problem.

**A. Compiled subgraph as a node** — Simplest. Subgraph runs, returns a state
update, parent continues.

```python
from langgraph.graph import StateGraph, END

executor_graph = (
    StateGraph(ExecutorState)
    .add_node("run_tool", run_tool_node)
    .add_node("summarize", summarize_node)
    .add_edge("run_tool", "summarize")
    .add_edge("summarize", END)
    .set_entry_point("run_tool")
    .compile()
)

parent_graph = (
    StateGraph(ParentState)
    .add_node("plan", planner_node)
    .add_node("execute", executor_graph)   # compiled subgraph as a node
    .add_node("finalize", finalize_node)
    .add_edge("plan", "execute")
    .add_edge("execute", "finalize")
    .set_entry_point("plan")
    .compile()
)
```

Only `messages` and `session_id` cross the boundary in either direction (from
Step 1). `tool_result` stays inside the child; `plan` stays inside the parent.

**B. `Send(graph, state)` for fan-out** — One parent step spawns N parallel
subgraph invocations, each with a different slice of state.

```python
from langgraph.types import Send

def dispatch_specialists(state: ParentState) -> list[Send]:
    return [
        Send("specialist_graph", {"messages": state["messages"],
                                   "session_id": state["session_id"],
                                   "topic": topic})
        for topic in state["plan"]
    ]
```

Use `Send` when the number of subgraph calls depends on runtime state.
Reducers on shared keys merge the parallel results.

**C. `Command(graph=ParentGraph, update=...)` to bubble up** — A subgraph node
jumps control back to the parent with an explicit state update, skipping the
rest of the subgraph.

```python
from langgraph.types import Command

def specialist_early_exit(state: ExecutorState) -> Command:
    if state.get("tool_result") and state["tool_result"].get("done"):
        return Command(
            graph=Command.PARENT,
            update={"messages": [AIMessage("done")]},
            goto="finalize",
        )
    return {"retries": state.get("retries", 0) + 1}
```

`Command(graph=Command.PARENT)` is the explicit opposite of P21 — it forces a
field up to the parent scope regardless of schema overlap.

See [Dispatch Patterns](references/dispatch-patterns.md) for the full decision
tree (inline function vs subgraph-as-node vs `Send` vs `Command` vs separate
service) and a sizing guide.

### Step 3 — Scope callbacks at invocation time, not definition time

```python
# WRONG — callbacks bind at definition time and do NOT propagate to subgraphs (P28)
traced_parent = parent_graph.with_config(callbacks=[tracer])
traced_parent.invoke({"messages": [HumanMessage("...")], "session_id": "s1"})
# tracer fires on parent nodes only. Child tool calls are invisible.

# RIGHT — callbacks pass via config at invocation time, propagating into every subgraph
parent_graph.invoke(
    {"messages": [HumanMessage("...")], "session_id": "s1"},
    config={
        "configurable": {"thread_id": "s1"},
        "callbacks": [tracer],
    },
)
# tracer fires on parent nodes AND every child tool, LLM, and chain event.
```

Every production invocation path — API handler, batch worker, test harness —
should pass callbacks via `config["callbacks"]`. Lint for
`with_config(callbacks=` on compiled graphs in CI and flag it.

See [Callback Scoping](references/callback-scoping.md) for the debugging
playbook when a callback "should be firing but isn't."

### Step 4 — Budget recursion per subgraph

LangGraph's `recursion_limit` (default **25** supersteps) is **per-graph, not
global**. A parent graph at superstep 20 invoking a subgraph resets the counter
inside that subgraph to zero. Pros: one runaway subgraph cannot starve the
parent. Cons: adding subgraphs does not reduce your global budget — a poorly
bounded specialist can still rack up 25 of its own steps while the parent
thinks it spent only one.

```python
# Parent gets 10 steps of its own planning.
# Each executor call gets its own 15-step budget, independent of the parent's 10.
parent_graph.invoke(
    initial_state,
    config={
        "configurable": {"thread_id": "s1"},
        "recursion_limit": 10,
    },
)

executor_graph.invoke(
    sub_state,
    config={"recursion_limit": 15},
)
```

For a parent that dispatches `N` specialists via `Send`, worst-case step count
is `parent_limit + N * specialist_limit`. Monitor the actual distribution with
a callback on `on_chain_start` / `on_chain_end` at each graph boundary —
`GraphRecursionError` with no obvious loop is P55 in the pain catalog, and
subgraph composition is the most common cause.

### Step 5 — Test every subgraph in isolation before composing

A subgraph that works alone and breaks in composition is almost always a
state-contract bug (Step 1) or a callback-scoping bug (Step 3). Catch both by
unit-testing each subgraph with a `FakeListChatModel` and an in-memory
checkpointer before wiring it into a parent.

```python
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langgraph.checkpoint.memory import MemorySaver

def test_executor_subgraph_standalone():
    fake = FakeListChatModel(responses=['{"done": true, "result": 42}'])
    graph = build_executor(llm=fake).compile(checkpointer=MemorySaver())
    out = graph.invoke(
        {"messages": [HumanMessage("do the thing")],
         "session_id": "test",
         "tool_result": None,
         "retries": 0},
        config={"configurable": {"thread_id": "test"},
                "recursion_limit": 5},
    )
    # Assert the shared-contract fields (Step 1) are present on return
    assert "messages" in out
    assert out["session_id"] == "test"
    # Assert child-only field is scoped correctly
    assert out["tool_result"] == {"done": True, "result": 42}
```

See [Testing Subgraphs](references/testing-subgraphs.md) for the full isolation
pattern — fixtures, state-shape assertions per node, and how to assert callback
propagation with a capturing handler.

### Step 6 — Version subgraphs independently of the parent

A reusable subgraph should ship with its own semantic version and a pinned
schema contract. Breaking either the shared-state contract (Step 1) or the
dispatch signature (Step 2) is a major-version bump; adding a new private
child-only field is a patch.

```python
# executor_subgraph/__init__.py
__version__ = "1.2.0"

SHARED_KEYS = frozenset({"messages", "session_id"})  # parent must declare these

def build_executor(llm) -> StateGraph:
    """v1.2.0 executor — adds 'retries' field (child-only, backward-compatible)."""
    ...
```

Parents pin `executor_subgraph>=1.2.0,<2.0.0`. A v2.0.0 that renames `session_id`
forces every parent to re-sync its `TypedDict`. This is how you catch P21 at
`pip install` time instead of at runtime.

## Output

- `ParentState` + per-subgraph child `TypedDict`s with the shared-key contract
  declared explicitly; every shared list field has a matching reducer
- Dispatch pattern chosen per subgraph (node vs `Send` vs `Command(graph=PARENT)`)
  with rationale recorded in code comments
- Every invocation path (API, batch, test) passes `callbacks` via
  `config["callbacks"]` so observability propagates into every subgraph
- `recursion_limit` set explicitly on parent and each subgraph, with the
  worst-case superstep count documented
- Unit tests for each subgraph in isolation, asserting shared-contract fields
  on return and callback propagation via a capturing handler
- Reusable subgraphs ship with their own `__version__` and a frozen
  `SHARED_KEYS` set

## Error Handling

| Error / Symptom | Cause | Fix |
|---|---|---|
| Parent reads `state["foo"]` and gets `None` after subgraph call | Key declared only in child schema; discarded on return (P21) | Add `foo` to parent `TypedDict`; use matching reducer; or return `Command(graph=Command.PARENT, update={"foo": ...})` |
| Tracer attached to parent never fires on child tool calls | Callback bound at definition time via `.with_config(callbacks=[...])` (P28) | Pass `callbacks=[tracer]` in `config` at each `invoke()` / `ainvoke()` call |
| `TypeError: unhashable type` from the message reducer in the parent after a `Send` fan-out | Child schema used `list` instead of `Annotated[list, add_messages]` (P18) | Match reducers on both sides of the boundary |
| `GraphRecursionError: Recursion limit of 25 reached` inside a subgraph only | Subgraph has its own 25-step budget; long sub-loop (P55) | Set `config={"recursion_limit": N}` explicitly or restructure subgraph |
| Subgraph returns state but parent sees empty `messages` | List field not using `add_messages` reducer on the parent side (P18) | `messages: Annotated[list[AnyMessage], add_messages]` in both `TypedDict`s |
| `Command(goto="next_node")` halts instead of continuing | `Command` did not set `graph=Command.PARENT` — tried to `goto` a parent node from inside the child scope | Use `Command(graph=Command.PARENT, goto="next_node", update=...)` |
| Subgraph runs but thread state never persists | Checkpointer attached only to parent; child `invoke()` without `thread_id` | Compile subgraphs with `checkpointer` too, or invoke with a `thread_id` matching the parent |

## Examples

### Planner-executor — shared messages, private scratch

The prototypical 1 + 2-4 composition: a planner writes a step list, an executor
runs each step, a finalizer summarizes. `messages` and `session_id` cross every
boundary; `plan` is parent-only; `tool_result` and `retries` are executor-only.
Uses a compiled-subgraph-as-node dispatch (Step 2A). See
[Dispatch Patterns](references/dispatch-patterns.md) for the full worked example.

### Hierarchical agent team — supervisor fans out to N specialists

A supervisor picks which specialists to invoke and calls `Send("specialist",
...)` in parallel. Each specialist runs its own subgraph with its own recursion
budget. Results merge via the `messages` reducer. See
[Dispatch Patterns](references/dispatch-patterns.md) for the `Send`-based
fan-out and the callback propagation pattern needed to trace the team.

### Reusable subgraph library — pinned contract with versioned exports

An `executor_subgraph` package exports `build_executor(llm)` and a frozen
`SHARED_KEYS` set, ships with a semantic version, and its CI fails if
`SHARED_KEYS` changes without a major-version bump. See
[State Contract](references/state-contract.md) for the schema-pinning pattern.

### Testing a specialist with a capturing callback

A `CaptureHandler` subclasses `BaseCallbackHandler`, appends every `on_*` event
to a list, and asserts both parent and child events are present after a single
`parent_graph.invoke(..., config={"callbacks": [handler]})`. Catches P28 at PR
review. See [Testing Subgraphs](references/testing-subgraphs.md) for the full
fixture and assertion pattern.

## Resources

- [LangGraph subgraph concepts](https://langchain-ai.github.io/langgraph/concepts/subgraphs/)
- [LangGraph subgraph how-to](https://langchain-ai.github.io/langgraph/how-tos/subgraph/)
- [`Send` API reference](https://langchain-ai.github.io/langgraph/reference/types/#langgraph.types.Send)
- [`Command` API reference](https://langchain-ai.github.io/langgraph/reference/types/#langgraph.types.Command)
- [LangGraph callback propagation](https://langchain-ai.github.io/langgraph/how-tos/streaming/)
- [LangChain 1.0 release notes](https://blog.langchain.com/langchain-langgraph-1dot0/)
- Sibling skill: `langchain-langgraph-basics` (L25) — prerequisite `StateGraph`, reducers, checkpointing
- Pack pain catalog: `docs/pain-catalog.md` (entries P18, P19, P21, P28, P55)

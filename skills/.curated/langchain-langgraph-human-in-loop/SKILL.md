---
name: langchain-langgraph-human-in-loop
description: "Build LangGraph 1.0 human-in-the-loop approval flows with interrupt_before\
  \ /\ninterrupt_after and Command(resume=...) \u2014 JSON-serializable state,\
  \ clean\nresume semantics, and UI wiring for approval decisions. Use when adding\
  \ an\napproval gate before an expensive tool call, wiring a Slack/web UI for agent\n\
  approvals, or debugging a graph that crashes on interrupt.\nTrigger with \"langgraph\
  \ human in loop\", \"langgraph interrupt_before\",\n\"langgraph approval flow\"\
  , \"Command resume\", \"langgraph HITL\".\n"
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
- human-in-loop
- approval
- interrupts
compatibility: Designed for Claude Code
---
# LangChain LangGraph Human-in-the-Loop (Python)

## Overview

A team adds `interrupt_before=["send_email"]` to require a human approval
before the email goes out. First integration test crashes at the interrupt
boundary with:

```
TypeError: Object of type datetime is not JSON serializable
```

The culprit is two nodes upstream: a `classify` node stashed
`"received_at": datetime.utcnow()` into state. Every node-level unit test
passed because node completion does not serialize state — only the
checkpointer does, and only at supersteps that include an interrupt. The
failure is invisible until interrupt time (P17).

A week later the resume path ships. The human reviews the draft, clicks
"approve with edits," and the backend runs:

```python
graph.invoke(Command(update={"messages": [corrected_msg]}, resume="approved"), config)
```

The prior 47 messages vanish. `messages` was typed as plain
`list[AnyMessage]` with no reducer, so `update` replaces the field instead of
appending (P18).

This skill covers: three interrupt styles (`interrupt_before`,
`interrupt_after`, inline `interrupt()`), the JSON-only state invariant with
a pre-interrupt scanner, the `Command(resume=...)` /
`Command(update=..., resume=...)` contract, an approval UI wire format
(GET pending / POST decision with optimistic concurrency), safe-cancellation
routing to `END`, and the tradeoff between native interrupts and a separate
approval service. Pin: `langgraph 1.0.x`, `langgraph-checkpoint 2.0.x`.
Pain-catalog anchors: **P17**, **P18** (adjacent: P16, P20).

## Prerequisites

- Python 3.10+
- `langgraph >= 1.0, < 2.0`
- A checkpointer: `MemorySaver` (dev), `PostgresSaver` (prod), or `SqliteSaver` (single-box)
- A `thread_id` contract at the app boundary (see `langchain-langgraph-checkpointing`)
- Familiarity with `langchain-langgraph-basics` — nodes, edges, `TypedDict` state with reducers

## Instructions

### Step 1 — Choose the interrupt style

LangGraph 1.0 exposes three interrupt mechanisms. They are not interchangeable.

| Style | Syntax | Use when |
|-------|--------|----------|
| `interrupt_before=[node]` | `compile(interrupt_before=["send_email"])` | Review inputs before an irreversible tool. Graph pauses *before* node runs. State shown is the input. |
| `interrupt_after=[node]` | `compile(interrupt_after=["draft_email"])` | Review output of a node (e.g., an LLM draft). Graph pauses *after* node completes. |
| Inline `interrupt()` | Inside a node: `decision = interrupt({"kind": "..."})` | Structured prompt mid-node with custom payload. Most flexible; lives in node code. |

Rule of thumb: prefer `interrupt_before` for hard gates (tool must not run
without approval). Use `interrupt_after` for review loops (draft → approve →
send). Use inline `interrupt()` when the prompt varies on intermediate
computation.

Typical interrupt round-trip latency in production is **50-300 ms** from
pause to checkpoint write (local Postgres) plus UI time; budget **1-5 s**
total for a Slack-based approval. Checkpoint row sizes average **2-20 KB** on
small graphs and cap at **~1 MB** on `PostgresSaver` before historical
checkpoints need pruning.

See [Interrupt Decision Tree](references/interrupt-decision-tree.md) for full
criteria, multiple-interrupt-per-graph patterns, and the interrupt-vs-tool
comparison.

### Step 2 — Enforce the JSON-serializable state invariant (P17)

Checkpointers serialize state to JSON on every superstep. Any non-JSON type
raises `TypeError` at the interrupt boundary — not at the offending node.
Canonical offenders:

| Type | Fix |
|------|-----|
| `datetime` / `date` | `dt.isoformat()` — ISO 8601 string |
| `bytes` | `base64.b64encode(b).decode()` |
| `set` | `sorted(s)` |
| Pydantic `BaseModel` with non-primitive fields | `.model_dump(mode="json")` |
| Custom classes | `dataclasses.asdict(obj)` or `vars(obj)` |
| `numpy.ndarray` | `.tolist()` |
| `decimal.Decimal` | `str(d)` or `float(d)` (lossy) |
| `float("nan")` / `float("inf")` | `None` (JSON forbids them; some savers crash on `allow_nan=False`) |

Ship a pre-interrupt scanner in dev and CI:

```python
import json
from typing import Any

class NonSerializableStateError(TypeError):
    """Raised when state contains values the checkpointer cannot serialize."""

def assert_state_is_json_serializable(state: dict[str, Any], *, path: str = "state") -> None:
    """Walk state depth-first and raise a typed error naming the offending key path."""
    _walk(state, path)

def _walk(v: Any, path: str) -> None:
    if v is None or isinstance(v, (bool, int, float, str)):
        return
    if isinstance(v, list):
        for i, item in enumerate(v):
            _walk(item, f"{path}[{i}]")
        return
    if isinstance(v, dict):
        for k, val in v.items():
            _walk(val, f"{path}.{k}")
        return
    raise NonSerializableStateError(
        f"{path} is {type(v).__name__}, not JSON-serializable. "
        f"Convert at node boundary."
    )
```

Call `assert_state_is_json_serializable(state)` at the end of every node
preceding an interrupt-flagged node, or attach as LangGraph middleware. In
CI, run the full graph to interrupt against a fixture that exercises every
branch — the only way to catch P17 before prod.

See [State Serialization for Interrupts](references/state-serialization-for-interrupts.md)
for the full forbidden-types list, the Pydantic-in-state pattern, and the
integration-test harness.

### Step 3 — The resume contract

Two shapes. They are not equivalent.

```python
from langgraph.types import Command

# Shape A — resume only: human approved as-is
graph.invoke(Command(resume="approved"), config)

# Shape B — update + resume: human edited state mid-graph
graph.invoke(
    Command(update={"recipient": "new@example.com"}, resume="approved"),
    config,
)
```

`resume="..."` is the value returned from inline `interrupt()` inside the
node (if any). For `interrupt_before` / `interrupt_after`, no node reads
`resume`, but the checkpoint records it for audit.

`update={...}` merges into state via the reducer declared in the `TypedDict`.
**Without a reducer, `update` replaces the field** (P18). Always annotate
list and dict state:

```python
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]      # append, not replace
    approvals: Annotated[list[dict], lambda l, r: l + r]     # custom append reducer
    draft: Annotated[dict, lambda l, r: {**l, **r}]          # dict merge reducer
    last_decision: str                                        # scalar: replace is fine
```

See [Resume Patterns](references/resume-patterns.md) for the five canonical
resume shapes (plain approve, approve with edits, reject to `END`, partial
approval, inline-interrupt structured return), the reducer cookbook, and the
audit-log write order.

### Step 4 — Wire the approval UI

Two HTTP endpoints. Keep them boring.

**GET `/approvals/pending`** lists paused threads:

```json
[
  {
    "thread_id": "conv-abc123",
    "checkpoint_id": "01JABC...",
    "interrupted_at": "2026-04-21T15:32:11Z",
    "node": "send_email",
    "state_diff": {"draft": {"to": "user@example.com", "subject": "Welcome"}}
  }
]
```

**POST `/approvals/<thread-id>/decision`** applies the decision:

```json
{
  "decision": "approve" | "reject" | "edit",
  "edits": {"recipient": "corrected@example.com"},
  "approver": "jeremy@intentsolutions.io",
  "reason": "Verified against ticket INT-4821",
  "expected_checkpoint_id": "01JABC...",
  "idempotency_key": "c2f5e8a0-..."
}
```

Optimistic concurrency (the `expected_checkpoint_id` check) matters the
moment two approvers open the same thread in two browser tabs. Without it,
the second click silently overwrites the first. Return `409 Conflict` on
mismatch; UI refreshes.

Server-side flow: authz → idempotency dedupe → checkpoint check → audit-log
write (BEFORE mutation) → build `Command` → `graph.ainvoke(cmd, config)` →
audit-log finalize.

See [Approval UI Wiring](references/approval-ui-wiring.md) for the full
HTTP contract with status codes, FastAPI implementation, Slack Block Kit
mapping, state-diff redaction, and an audit-log schema compatible with SOC2
evidence requirements.

### Step 5 — Safe cancellation: route to `END` on reject

When the human rejects, the gated node must NOT execute. Two clean patterns:

**Pattern A — conditional edge after the interrupted node (preferred):**

```python
from langgraph.graph import END

def route_after_approval(state: AgentState) -> str:
    if state.get("last_decision") == "rejected":
        return END
    return "send_email"

builder.add_conditional_edges("await_approval", route_after_approval, {
    "send_email": "send_email",
    END: END,
})
```

**Pattern B — `Command(goto=END)` at resume:**

```python
graph.invoke(Command(resume="rejected", goto=END), config)
```

Prefer Pattern A in production: graph topology stays the source of truth,
audit replays work without the UI. Always log the rejection to the checkpoint
via `Command(update={"last_decision": "rejected", "reject_reason": ...})`
BEFORE routing to END — otherwise the audit trail lives only in the UI DB.

### Step 6 — Native interrupts vs a separate approval service

| Dimension | LangGraph interrupts | Separate approval service |
|-----------|---------------------|---------------------------|
| **Latency** | 50-300 ms pause + human time | Human time + queue latency |
| **State coherence** | Single source of truth (checkpoint) | Two systems to reconcile |
| **Concurrency** | Checkpoint-based optimistic locking | Whatever the queue provides |
| **Multi-graph** | Per-graph, per-thread | Centralized policy engine |
| **Observability** | `get_state()` + checkpoint history | Separate audit system |
| **Failure mode** | JSON-serialization at interrupt (P17) | Network partition between services |
| **Best for** | Single LangGraph app, 1-10 approval types, <1k/day | Multi-app enterprise, complex RBAC, 10k+/day |

Single LangGraph app with fewer than a dozen approval types: native
interrupts are simpler and more reliable. Cross-app approval platform with
escalations, delegations, and SLAs: run a dedicated service and call it from
a tool, not from an interrupt.

## Output

- Graph compiled with explicit `interrupt_before` / `interrupt_after` lists, or inline `interrupt()` calls where payload structure matters
- JSON-only state: `datetime` → ISO strings, `bytes` → base64, Pydantic → `.model_dump(mode="json")`, custom classes → dicts
- `TypedDict` state with explicit reducers on every list and dict field
- Pre-interrupt state scanner attached as middleware or called at node exits; raises `NonSerializableStateError` with a key path
- Approval HTTP endpoints: GET pending with state diffs, POST decision with `expected_checkpoint_id` optimistic-concurrency check and `idempotency_key` dedupe
- Rejection routes to `END` via conditional edge (Pattern A) with `last_decision` recorded in state for audit
- Audit log written BEFORE state mutation with `approver`, `reason`, `thread_id`, `checkpoint_id_before`, `checkpoint_id_after`

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `TypeError: Object of type datetime is not JSON serializable` at interrupt | Non-JSON value in state (P17) | Convert at node boundary; add pre-interrupt scanner in CI |
| Resume with `Command(update={"messages": [new]})` loses history | `messages` field missing reducer (P18) | Annotate as `Annotated[list[AnyMessage], add_messages]` |
| `ValueError: Thread ... has no interrupted nodes` on resume | Graph already ran to completion, or `thread_id` mismatch | Call `graph.get_state(config)` first; assert `snapshot.next` is non-empty |
| Human clicks approve, nothing happens | Missing checkpointer on `compile()` — interrupts require persistence | `graph.compile(checkpointer=MemorySaver() or PostgresSaver(...))` |
| Two approvers both click approve, second one's edits win silently | No optimistic concurrency | Include `expected_checkpoint_id` in POST body; return 409 on mismatch |
| `KeyError: 'configurable'` at resume | `config` dict missing `thread_id` | `config = {"configurable": {"thread_id": tid}}` — required by every checkpointer |
| Approval UI shows stale state after another approver acted | Cached GET /pending response | `Cache-Control: no-store` on the pending endpoint |
| Graph halts silently after reject | Conditional edge router returned value not in `path_map` | Include `END` in `path_map`; assert router output in keyset |

## Examples

### Approval gate before an expensive tool

Email-sending agent that must not send without approval. State carries
`draft: {to, subject, body}`, graph compiles with
`interrupt_before=["send_email"]`, resume either invokes the send tool or
routes to `END` on reject. See
[Resume Patterns](references/resume-patterns.md) for the full worked example
including audit-log write order.

### Partial approval — approve one argument, edit another

Human accepts the recipient but rewrites the subject. Resume is
`Command(update={"draft": {**state["draft"], "subject": new_subject}}, resume="approved")`.
Note the spread — without it the draft is replaced. Scalar dicts replace by
default; declare a dict reducer to merge partials cleanly. See
[Resume Patterns](references/resume-patterns.md).

### Inline `interrupt()` with a custom payload

Inside a `validate_purchase` node, the model has decided to buy three items
at USD 450 total. The node calls
`decision = interrupt({"kind": "confirm_purchase", "items": items, "total": 450})`
and the UI reads the payload to render a rich confirmation dialog. On resume,
`decision` is whatever the UI sent via
`Command(resume={"approved": True, "notes": "..."})`. See
[Interrupt Decision Tree](references/interrupt-decision-tree.md).

### Slack-driven approval

GET /pending feeds a cron that posts Block Kit messages with approve/reject
buttons. Button callback POSTs to /decision. Slack's interaction payload
carries `user.id`, which becomes `approver` in the audit log. See
[Approval UI Wiring](references/approval-ui-wiring.md) for the Block Kit
template and signing-secret validation.

## Resources

- [LangGraph: Human-in-the-loop (concepts)](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
- LangGraph: How to add human-in-the-loop
- [LangGraph: `Command` type reference](https://langchain-ai.github.io/langgraph/reference/types/#langgraph.types.Command)
- [LangGraph: `interrupt` function reference](https://langchain-ai.github.io/langgraph/reference/types/#langgraph.types.interrupt)
- [LangGraph: Persistence and checkpointers](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [LangGraph 1.0 release notes](https://blog.langchain.com/langchain-langgraph-1dot0/)
- Pack pain catalog: `docs/pain-catalog.md` (entries P16, P17, P18, P20)
- Related skills: `langchain-langgraph-basics`, `langchain-langgraph-checkpointing`, `langchain-middleware-patterns`

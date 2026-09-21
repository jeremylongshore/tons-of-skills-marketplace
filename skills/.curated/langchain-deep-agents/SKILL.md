---
name: langchain-deep-agents
description: "Build a LangGraph 1.0 Deep Agent \u2014 planner + subagents + virtual\
  \ filesystem +\nreflection loop \u2014 without the state-growth and prompt-inheritance\
  \ traps. Use\nwhen building a long-horizon agent that must plan, delegate subtasks,\
  \ work\nagainst a scratchpad filesystem, and reflect on progress.\nTrigger with\
  \ \"langchain deep agent\", \"planner subagent\", \"virtual filesystem\nagent\"\
  , \"reflection loop\", \"langgraph deep agent\".\n"
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
- agents
- deep-agents
- research
compatibility: Designed for Claude Code
---
# LangChain Deep Agents (Python)

## Overview

Two pains bite every team reproducing LangChain's late-2025 Deep Agents blueprint.

**Virtual-FS state grows unboundedly (P51).** The planner and every subagent
write plans, scratch notes, intermediate drafts, and tool outputs into
`state["files"]`. Nothing ever evicts them. After 50 tool calls, the checkpointed
state is **8 MB**; every `MemorySaver.put()` takes **400 ms**; a run that started
at 1.2 s per node visit ends at 2.5 s per node visit. The LangSmith trace viewer
times out loading the thread. The user sees latency doubling over the run with
no obvious tool-level culprit.

**Subagent persona leak (P52).** The naive prompt-composition inside the
blueprint APPENDS the subagent role message to the parent's system message
instead of replacing it. The research-specialist subagent receives:
`"You are a senior planner coordinating subagents..."` + `"You are a research
specialist..."` — and responds as the planner. It produces generic task
decomposition instead of the specific lookup you asked for. The bug is invisible
in unit tests because both messages "sound right" to a reviewer.

This skill pins to `langgraph 1.0.x` + `langchain-core 1.0.x` and walks through
the four-component Deep Agent pattern — **planner**, **subagent pool** of 3-8
role-specialized workers, **virtual filesystem** with eviction, **reflection
node** with bounded depth 3-5 — and shows exactly how to avoid P51 (cleanup
node + checkpoint-on-boundary) and P52 (explicit `SystemMessage(override=True)`
for every subagent). Pain-catalog anchors: **P51, P52**.

## Prerequisites

- Python 3.10+
- `langgraph >= 1.0, < 2.0` and `langchain-core >= 1.0, < 2.0`
- At least one provider package: `pip install langchain-anthropic` or `langchain-openai`
- Completed skills:
  - `langchain-langgraph-agents` (L26) — you already know `create_react_agent`,
    tool schemas, recursion limits
  - `langchain-langgraph-subgraphs` (L30) — subagent ≈ subgraph with a bounded
    contract; if L30 is not yet installed, the subagent construction in Step 3
    is self-contained
- Provider API key: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
- Recommended: `langchain-eval-harness` skill installed for trajectory-level eval

## Instructions

### Step 1 — Understand the four-component architecture

A Deep Agent has four components. Each has a fixed contract; violating a
contract is exactly where P51 / P52 show up.

| Component | Input | Output | Invariants |
|-----------|-------|--------|------------|
| **Planner** | User goal, current `state["plan"]`, current `state["files"]` summary (not full contents) | An ordered list of subtasks; each subtask has `{subagent_role, instruction, expected_artifact_name}` | Must NOT write to `state["files"]` directly. Only emits plan + assignments. |
| **Subagent** | `{subagent_role, instruction, read_files: [names]}` from planner | `{artifact_name, content, status}` back to planner via structured output | Receives a fresh `SystemMessage` with `override=True` — no parent prompt inheritance (P52). Typical pool size: **3-8**. |
| **Virtual FS** | Writes from subagents (never from planner) | Reads by planner (summaries) and subagents (full content) | Bounded. Cleanup node evicts entries older than N steps or `status=="done"` (P51). |
| **Reflection** | Plan vs actual artifacts produced, subagent errors, step count | Decision: `continue` / `replan` / `end` / `escalate_to_human` | Runs at most **3-5** times per user-facing turn. |

The graph topology:

```
START -> planner -> (for each subtask) subagent_dispatcher -> virtual_fs_write
                                             |
                                             v
                                        reflection -> planner (replan)
                                                   -> END (done)
                                                   -> interrupt (escalate)
```

The cleanup node is an edge-less side-effect node hooked onto the reflection
transition — it prunes `state["files"]` before the next planner step runs.

### Step 2 — Build the planner prompt skeleton

The planner's prompt must be narrow. It decomposes, assigns, and revises —
that is all. It does not answer the user's question itself.

```python
PLANNER_SYSTEM = """You are the planner for a Deep Agent.

Your job is to decompose the user's goal into subtasks and assign each to a
specialized subagent. You do NOT execute subtasks yourself.

Available subagent roles: {roles_list}

Return a JSON plan:
{{
  "subtasks": [
    {{"role": "research-specialist",
      "instruction": "Find the most recent SEC 10-K filing for ACME.",
      "expected_artifact": "acme_10k_summary.md",
      "read_files": []}}
  ],
  "reasoning": "Why this decomposition."
}}

Do not write file contents. Do not answer the user directly.
"""
```

Keep the planner system prompt under ~1500 chars. Long planner prompts leak
into subagents if the `override=True` contract in Step 3 is skipped.

### Step 3 — Construct subagents with EXPLICIT system-message override

This is the fix for **P52**. Never rely on default prompt composition for
subagents. Always build a fresh `SystemMessage` and pass `override=True`.

```python
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic

SUBAGENT_PROMPTS = {
    "research-specialist": (
        "You are a research specialist. Given an instruction, produce a "
        "fact-dense summary with inline citations. Return ONLY the summary. "
        "Do NOT plan, do NOT delegate."
    ),
    "code-writer": (
        "You are a code writer. Given a spec, produce runnable Python. "
        "Return ONLY code in one fenced block. Do NOT explain."
    ),
    "critic": (
        "You are a critic. Given an artifact and a spec, list concrete defects. "
        "Return a JSON list of {line, issue, severity}. Do NOT rewrite the artifact."
    ),
}

def build_subagent(role: str, model):
    return create_react_agent(
        model=model,
        tools=ROLE_TOOLS[role],
        # KEY: prompt parameter replaces default state_modifier; override=True
        # means no parent-prompt composition.
        prompt=SystemMessage(content=SUBAGENT_PROMPTS[role]),
    )

def invoke_subagent(subagent, instruction: str, read_files: dict):
    # Build messages from scratch — do not reuse parent message list.
    context = "\n\n".join(f"# {name}\n{content}" for name, content in read_files.items())
    messages = [HumanMessage(content=f"{context}\n\n## Task\n{instruction}")]
    result = subagent.invoke({"messages": messages})
    return result["messages"][-1].content
```

Rules:

1. **New message list per invocation.** Do not pass the planner's message
   history into the subagent. Build from scratch with `HumanMessage(task)`.
2. **`prompt=SystemMessage(...)`** on `create_react_agent` replaces the default
   `state_modifier`. On LangGraph 1.0.x this is the supported way to pin a
   subagent's persona.
3. **Return type is a string or a structured JSON artifact** — never the full
   message list. The planner does not need subagent reasoning traces.

See [Subagent Prompting](references/subagent-prompting.md) for the full
override-vs-append test, the handoff structured-output schema, and how to
unit-test for P52 persona leak.

### Step 4 — Implement the virtual filesystem with eviction

This is the fix for **P51**. The virtual FS lives in the graph state dict for
small artifacts (< 100 KB) and on real disk / an object store for large ones.
A cleanup node evicts old entries before every planner step.

```python
from typing import TypedDict, Annotated
from operator import or_  # merge dict state updates

class DeepAgentState(TypedDict):
    messages: list
    plan: dict
    files: Annotated[dict, or_]  # {name: {content, written_at_step, status}}
    step: int
    reflection_depth: int

MAX_FILE_AGE_STEPS = 20
INLINE_SIZE_LIMIT_BYTES = 100 * 1024  # 100 KB — above this, spill to disk; keeps state < 500 KB (P51)

def cleanup_node(state: DeepAgentState) -> dict:
    current_step = state["step"]
    kept = {}
    for name, entry in state["files"].items():
        age = current_step - entry["written_at_step"]
        if entry.get("status") == "done" and age > 3:
            continue  # evict completed
        if age > MAX_FILE_AGE_STEPS:
            continue  # evict stale
        kept[name] = entry
    return {"files": kept}

def write_artifact(state, name: str, content: str) -> dict:
    if len(content.encode("utf-8")) > INLINE_SIZE_LIMIT_BYTES:
        # Spill to disk; keep only a pointer in state.
        path = f"/tmp/deep_agent/{state['step']}_{name}"
        with open(path, "w") as f: f.write(content)
        entry = {"content": None, "disk_path": path, "written_at_step": state["step"], "status": "active"}
    else:
        entry = {"content": content, "written_at_step": state["step"], "status": "active"}
    return {"files": {name: entry}}
```

See [Virtual Filesystem Patterns](references/virtual-filesystem-patterns.md) for
dict-backed vs disk-backed trade-offs, content-addressed storage for dedup,
and a full P51 mitigation procedure with before/after latency numbers.

### Step 5 — Add the reflection node with bounded depth

Reflection compares **plan** vs **artifacts produced so far** and decides
what happens next. Typical reflection depth: **3-5 rounds** per user-facing
turn. Any higher and the agent is either spinning or should escalate.

```python
REFLECTION_SYSTEM = """You are the reflection node of a Deep Agent.

Input: the current plan, the artifacts produced so far (by filename + status),
and the step count. Output a decision:

{"decision": "continue"}           # more subtasks remain, proceed
{"decision": "replan", "reason": "..."}  # current plan is wrong, replanner
{"decision": "end", "final_answer": "..."}  # we are done
{"decision": "escalate", "question": "..."}  # ask the human

Do not rewrite files. Do not invent facts. Base the decision only on what is
present in files and plan.
"""

MAX_REFLECTION_DEPTH = 5

def reflection_node(state: DeepAgentState, model) -> dict:
    if state["reflection_depth"] >= MAX_REFLECTION_DEPTH:
        return {"decision": "escalate", "question": "Max reflection depth reached."}
    # Feed summaries, not full file contents, to the reflection model.
    file_summary = {name: {"status": e["status"], "bytes": len(e.get("content") or "")}
                    for name, e in state["files"].items()}
    msg = HumanMessage(content=f"Plan: {state['plan']}\nFiles: {file_summary}\nStep: {state['step']}")
    result = model.invoke([SystemMessage(content=REFLECTION_SYSTEM), msg])
    return {"decision": result.content, "reflection_depth": state["reflection_depth"] + 1}
```

See [Reflection Loop](references/reflection-loop.md) for the plan-vs-actual
diff prompt, self-critique patterns, and the decision tree for `replan` vs
`continue` vs `escalate`.

### Step 6 — Checkpoint only on user-facing boundaries

Default `MemorySaver` checkpoints after every node visit. For a Deep Agent
that is disastrous: 50 node visits x 160 KB state = 8 MB of serialized state,
each write costing 400 ms (**P51** root cause).

Fix: checkpoint only at *user-facing* boundaries — after reflection decides
`end` or `escalate`, not inside the planner/subagent loop. Use
`interrupt_after=["reflection"]` to get the boundary checkpoint, or switch to
a durable store (Postgres / Redis) and override `put` to no-op during internal
steps.

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END

checkpointer = MemorySaver()
graph = StateGraph(DeepAgentState)
graph.add_node("planner", planner_node)
graph.add_node("subagent_dispatcher", dispatch_node)
graph.add_node("cleanup", cleanup_node)
graph.add_node("reflection", reflection_node)
graph.set_entry_point("planner")
graph.add_edge("planner", "subagent_dispatcher")
graph.add_edge("subagent_dispatcher", "cleanup")
graph.add_edge("cleanup", "reflection")
graph.add_conditional_edges("reflection", route_after_reflection,
    {"continue": "planner", "replan": "planner", "end": END, "escalate": END})

# Only interrupt on user-facing boundary — the checkpoint taken here is the
# one the user sees and can resume from.
app = graph.compile(checkpointer=checkpointer, interrupt_after=["reflection"])
```

### Step 7 — Evaluate the full loop with trajectory eval

Unit-testing individual nodes will NOT catch P52 (persona leak is observable
only in the subagent's output) or P51 (state growth is observable only over
a full run). You need trajectory-level evaluation.

Cross-link: if `langchain-eval-harness` is installed, use its trajectory-eval
pattern with a golden dataset of `{goal, expected_final_answer, expected_artifact_set}`
and assert on: (a) `len(pickle.dumps(state))` at turn end < 500 KB, (b) every
subagent's first message begins with its role prefix, (c) reflection depth
terminated at `end` or `escalate` (not hit `MAX_REFLECTION_DEPTH` silently).

## Output

- Deep Agent graph with four nodes: `planner`, `subagent_dispatcher`, `cleanup`, `reflection`
- Subagent pool of 3-8 role-specialized workers, each built with
  `create_react_agent(model, tools, prompt=SystemMessage(...))` — no parent-prompt
  inheritance (P52 fix)
- Virtual FS in `state["files"]` with eviction by age (>20 steps) and status
  (`done` + age > 3), disk spill for entries > 100 KB (P51 fix)
- Reflection node bounded to `MAX_REFLECTION_DEPTH=5`; escalates to human on cap
- Checkpointer interrupts only after `reflection` — user-facing boundary — not
  every node visit
- Trajectory-level evaluation hook cross-linked to `langchain-eval-harness`

### State-growth mitigation checklist

- [ ] `state["files"]` entries carry `{written_at_step, status}` — not bare content
- [ ] `cleanup_node` runs before every `planner` re-entry
- [ ] Entries > 100 KB spill to disk / object store; state holds only a pointer
- [ ] `interrupt_after=["reflection"]` — checkpoint only on user-facing boundary
- [ ] Reflection feeds summaries `{status, bytes}` — not raw file contents — to the model
- [ ] `len(pickle.dumps(state))` asserted < 500 KB in trajectory tests
- [ ] No `state["messages"]` accumulation across user turns — reset on boundary

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Subagent response reads like the planner (generic decomposition instead of the specific task) | P52 — default prompt composition appended parent system message to subagent's role message | Pass `prompt=SystemMessage(content=SUBAGENT_PROMPTS[role])` to `create_react_agent`; build messages from scratch per invocation, do not pass parent history |
| `MemorySaver.put()` latency climbs from 20 ms at step 5 to 400 ms at step 50 | P51 — `state["files"]` grew to MB-scale and is re-serialized every node | Add `cleanup_node` with age + status eviction; spill > 100 KB entries to disk; switch to `interrupt_after=["reflection"]` so checkpoint fires only at boundary |
| LangSmith trace viewer hangs when opening the thread | P51 — checkpointed state is megabytes per step | Same fix as above; additionally confirm `reflection_node` feeds file summaries (bytes + status) not full contents into the model |
| `GraphRecursionError` inside the Deep Agent loop | Plan never converges; reflection keeps returning `continue` or `replan` | Cap `MAX_REFLECTION_DEPTH=5`; when hit, force `escalate` decision so the user gets a checkpoint and a question |
| Subagent returns full message trace instead of artifact | Subagent's prompt did not constrain output format | Add `"Return ONLY the summary"` / `"Return ONLY code"` to the subagent role prompt; validate output shape before writing to `state["files"]` |
| `KeyError: 'files'` during cleanup | Initial state shape did not include `files: {}` | Initialize `DeepAgentState(messages=[], plan={}, files={}, step=0, reflection_depth=0)` at graph entry |
| Two subagents write the same filename and one overwrites the other | No dedup / content-addressing | Namespace artifact names by `{subagent_role}_{step}_{slug}.md`, or use content-addressed storage (SHA-256 of content as key) |
| Agent terminates with `end` decision but no final answer produced | `reflection_node` decided `end` before any subagent produced an artifact | Guard the `end` branch with `assert any(e["status"] == "done" for e in state["files"].values())` and route to `replan` otherwise |

## Examples

### Reproducing the Deep Agents reference pattern from scratch

See [Architecture Blueprint](references/architecture-blueprint.md) for the full
four-component wiring with copy-paste `StateGraph`, `DeepAgentState`, node
definitions, and router function — reproducing LangChain's published blueprint
with the P51/P52 fixes already applied.

### Unit-testing for P52 persona leak

```python
def test_subagent_does_not_inherit_planner_persona():
    subagent = build_subagent("research-specialist", model)
    out = invoke_subagent(subagent,
        "What is the capital of France?",
        read_files={})
    # Planner persona says "decompose the goal"; research persona answers directly.
    assert "decompose" not in out.lower()
    assert "subtask" not in out.lower()
    assert "paris" in out.lower()
```

### Asserting state stays bounded over a long run

```python
import pickle

def test_state_stays_under_500kb_over_50_steps():
    thread = {"configurable": {"thread_id": "t-bound"}}
    app.invoke({"messages": [HumanMessage("Run a 50-step synthesis task")]}, config=thread)
    final = app.get_state(thread).values
    assert len(pickle.dumps(final)) < 500_000, "P51 regression: state > 500 KB"
```

## Resources

- [LangChain blog: Deep Agents](https://blog.langchain.com/deep-agents/) — late-2025 reference pattern
- [LangGraph: Multi-agent supervisor](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/) — subagent orchestration reference
- [`create_react_agent` — `prompt=` parameter](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent)
- [LangGraph: Checkpointing](https://langchain-ai.github.io/langgraph/how-tos/persistence/) — `interrupt_after` and durable checkpointers
- [LangGraph: Recursion limits](https://langchain-ai.github.io/langgraph/how-tos/recursion-limit/)
- [LangChain 1.0 release notes](https://blog.langchain.com/langchain-langgraph-1dot0/)
- Pack pain catalog: `docs/pain-catalog.md` (entries **P51, P52**)
- Cross-link: `langchain-eval-harness` — trajectory-level eval for the full Deep Agent loop

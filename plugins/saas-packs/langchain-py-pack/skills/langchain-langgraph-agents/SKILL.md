---
name: langchain-langgraph-agents
description: >-
  Build a correct LangGraph 1.0 ReAct agent with create_react_agent — typed tools,
  error propagation, recursion caps, and stop conditions that actually stop. Use
  when writing a first tool-calling agent, migrating from AgentExecutor or
  initialize_agent, or diagnosing an agent that loops on vague prompts. Trigger
  with "langgraph agent", "create_react_agent", "langgraph tool calling",
  "AgentExecutor migration", or "agent loop cost".
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
- tool-calling
compatibility: Designed for Claude Code
---
# LangChain LangGraph Agents (Python)

## Overview

Two failure modes hit every team writing their first LangGraph 1.0 ReAct agent:

**Loop-to-cap on vague prompts (P10).** `create_react_agent` defaults to
`recursion_limit=25`. A prompt like "help me with my account" never converges —
the model calls a retrieval tool, gets irrelevant results, calls another tool,
and repeats until `GraphRecursionError: Recursion limit of 25 reached without
hitting a stop condition` fires. Cost dashboards show the damage *after* the
fact: $5-$15 per runaway loop on Sonnet with a 3-tool agent, assuming no tool
is itself expensive.

**Silent tool errors on legacy `AgentExecutor` (P09).** The legacy executor
defaults `handle_parsing_errors=True` and catches tool exceptions, feeding the
error string back as the next observation. When the error serializes to empty
(e.g., a `ValueError("")` or an HTTP 500 with no body), the loop continues with
no signal. The agent says "I couldn't find the answer" — which was actually a
silent crash three tool calls ago.

This skill walks through defining typed tools with `@tool` + Pydantic; building
an agent with `create_react_agent(model, tools, checkpointer=MemorySaver())`;
invoking with `{"messages": [...]}` and a thread-scoped config; setting
`recursion_limit` per expected agent depth (5-10 interactive, 20-30 planner);
adding middleware for a per-session token budget; and raise-by-default error
propagation. Pin: `langgraph >= 1.0, < 2.0`, `langchain-core >= 1.0, < 2.0`.
Pain-catalog anchors: P09, P10, P11, P32, P41, P42, P63.

## Prerequisites

- Python 3.10+
- `langgraph >= 1.0, < 2.0` and `langchain-core >= 1.0, < 2.0`
- At least one provider package: `pip install langchain-anthropic` or `langchain-openai`
- Completed skill: `langchain-langgraph-basics` (L25) — you already know `StateGraph`,
  `MessagesState`, and checkpointers
- Provider API key: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`

## Instructions

### Step 1 — Define tools with typed schemas and short docstrings

```python
from typing import Annotated
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class LookupAccountArgs(BaseModel):
    account_id: str = Field(..., description="Account UUID. No email addresses.")

@tool("lookup_account", args_schema=LookupAccountArgs)
def lookup_account(account_id: str) -> dict:
    """Fetch an account record by UUID. Returns status, plan, and owner email."""
    if not account_id:
        raise ValueError("account_id is required")  # raised → agent sees real error
    return {"id": account_id, "status": "active", "plan": "pro", "owner": "a@b.co"}
```

Two rules that catch teams off-guard:

1. **Docstring is the tool description the provider sees.** Keep it under
   **1024 chars** (P11). Anthropic truncates at ~1024; OpenAI's effective cap is
   softer but still bites on tool descriptions over ~2KB. Long docstrings with
   examples should move into a system prompt, not the tool description.
2. **Raise real exceptions.** Unlike the legacy `AgentExecutor`, LangGraph's
   `create_react_agent` does not silently swallow tool errors — the exception
   propagates and surfaces in your observability layer. See Step 6.

For async tools, use `@tool` on an `async def` — LangGraph invokes it via
`await`. For structured return types, annotate the return with a Pydantic model.

See [Tool Definition Patterns](references/tool-definition-patterns.md) for the
`@tool` vs `tool()` decision, async tools, and the `args_schema` vs
auto-inferred trade-off.

### Step 2 — Build the agent with `create_react_agent`

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=0,
    timeout=30,
    max_retries=2,
)

agent = create_react_agent(
    model=model,
    tools=[lookup_account],
    checkpointer=MemorySaver(),  # required for stateful invocations
)
```

`create_react_agent` is the LangGraph 1.0 replacement for the removed
`initialize_agent` factory (P41). Under the hood it builds a `StateGraph` with
a `model` node and a `ToolNode`, plus a conditional edge that routes to
`END` when the model emits no tool calls. The `checkpointer` persists state
per-thread — required for multi-turn conversations and for resuming after
interruption.

### Step 3 — Invoke with a thread-scoped config

```python
config = {"configurable": {"thread_id": "user-42"}}
result = agent.invoke(
    {"messages": [{"role": "user", "content": "look up account uuid-abc"}]},
    config=config,
)
print(result["messages"][-1].content)
```

Key contracts:

- **Input** is `{"messages": [...]}` — a list of message dicts or LangChain
  `HumanMessage` / `SystemMessage` objects. You append to this list across turns.
- **`thread_id`** scopes the checkpointer. Reusing it resumes the conversation.
- **Output** is the full updated state. `result["messages"]` is the complete
  message list; the final assistant message is at index `-1`.

### Step 4 — Set `recursion_limit` to your expected agent depth

`create_react_agent` defaults to `recursion_limit=25`. In LangGraph one
"recursion step" is one node visit, and each tool round-trip is two visits
(model node + tool node), so 25 means ~12 tool calls. For most workloads this
is too generous and hides bugs:

| Agent kind | Suggested `recursion_limit` | Rationale |
|---|---|---|
| Interactive chat with 1-3 tools | 5-10 | One tool call + one final answer is 3 visits. Cap low to expose loops. |
| Task-completion (e.g., booking flow) | 10-15 | 3-5 tool calls + final answer. |
| Planner / research agent | 20-30 | Expect multiple retrieval + synthesis rounds. |
| Multi-agent supervisor | 40+ | Coordinator + worker rounds. Budget tokens separately. |

Apply it on invocation, not at construction time:

```python
result = agent.invoke(
    {"messages": [...]},
    config={"configurable": {"thread_id": "user-42"}, "recursion_limit": 10},
)
```

When the limit fires, LangGraph raises `GraphRecursionError` — catch it and
surface a user-facing message; do not retry without a cost guard.

### Step 5 — Add a per-session token budget via middleware

`recursion_limit` alone does not bound cost. A single tool call that returns a
large document and triggers a long model response can cost more than 10 cheap
tool calls. Cap tokens explicitly:

```python
from langchain_core.callbacks import BaseCallbackHandler

class TokenBudget(BaseCallbackHandler):
    def __init__(self, max_tokens: int = 50_000):
        self.used = 0
        self.max = max_tokens

    def on_llm_end(self, response, **kwargs):
        usage = getattr(response, "llm_output", {}).get("token_usage", {}) or {}
        self.used += usage.get("total_tokens", 0)
        if self.used > self.max:
            raise RuntimeError(f"Token budget exceeded: {self.used}/{self.max}")

budget = TokenBudget(max_tokens=50_000)
result = agent.invoke(
    {"messages": [...]},
    config={
        "configurable": {"thread_id": "user-42"},
        "recursion_limit": 10,
        "callbacks": [budget],
    },
)
```

A per-session budget of 50K tokens on Sonnet is roughly $0.25 — a safe cap for
interactive agents. For background planners raise to 200K-500K. See
[Loop Caps and Budgets](references/loop-caps-and-budgets.md) for a
repeated-tool-call early-stop node and a middleware pattern that terminates on
the N-th identical call.

### Step 6 — Propagate tool errors; do not silently swallow

LangGraph's default is to raise. Legacy `AgentExecutor(handle_parsing_errors=True)`
swallowed everything. The new defaults are safer but different:

```python
# Tool raises → the exception propagates out of agent.invoke()
try:
    result = agent.invoke({"messages": [{"role": "user", "content": "..."}]}, config=config)
except ValueError as e:
    # Your tool's own ValueError — log + user-facing message
    ...
```

When you *want* tolerant behavior (e.g., the tool is a flaky third-party API
and you want the model to try a different approach), wrap the tool itself:

```python
from langchain_core.tools import tool

@tool
def search_kb(query: str) -> str:
    """Search the internal knowledge base. Returns hits or a 'no results' string."""
    try:
        return _real_search(query)
    except HTTPError as e:
        return f"search_kb unavailable: {e.response.status_code}. Try a different query."
```

The key insight: the *tool* decides to degrade gracefully by returning a string
the model can reason about. The *agent* never silently drops an error. See
[Error Propagation](references/error-propagation.md) for a custom error-handler
node that routes tool failures to a fallback tool.

### Step 7 — Choose `create_react_agent` vs custom `StateGraph` vs legacy

| Decision | Use | Why |
|---|---|---|
| Single agent, tool-calling loop | `create_react_agent` | Correct defaults, provider-native tool calling, smallest code surface |
| Multi-stage pipeline (plan → execute → review) | Custom `StateGraph` | You need named nodes, explicit conditional edges, typed state |
| Multi-agent supervisor | `create_supervisor` + workers built with `create_react_agent` | Built-in routing, per-worker checkpointing |
| New code in 2026+ | Never use `AgentExecutor` or `initialize_agent` | Removed / deprecated in 1.0 (P41); shape changes in `intermediate_steps` (P42) |

For a single forced-tool single-shot (e.g., "always classify into one of these
buckets"), skip agents entirely: use `model.bind_tools([Schema],
tool_choice={"type": "tool", "name": "Schema"})`. But never loop a forced
`tool_choice` (P63) — the model cannot emit `stop_reason="end_turn"` under
forced tool_choice, so the agent never terminates.

## Output

- Agent built with `create_react_agent(model, tools, checkpointer=MemorySaver())`
- Tools defined with `@tool` + Pydantic `args_schema`, docstrings under 1024 chars
- Invocations pass `{"configurable": {"thread_id": ...}, "recursion_limit": N}`
- `TokenBudget` callback enforces per-session cost ceiling
- Tool errors raise and surface in observability; graceful-degrade patterns are
  explicit (return-a-string, not silent-swallow)
- Decision table resolved: `create_react_agent` vs custom `StateGraph` vs
  supervisor vs legacy

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `GraphRecursionError: Recursion limit of 25 reached without hitting a stop condition` | Vague prompt never converges; default cap too high (P10) | Lower `recursion_limit` to 5-10 interactive; add repeated-tool-call early-stop node |
| `ImportError: cannot import name 'initialize_agent' from 'langchain.agents'` | Legacy 0.2 agent factory removed (P41) | `from langgraph.prebuilt import create_react_agent` |
| `AttributeError: 'ToolCall' object has no attribute 'tool'` | Old code accessing `step.tool` on new intermediate step shape (P42) | Use `step.tool_name` (or `step["name"]` on dict form); check `isinstance(step, ToolCall)` |
| Agent says "couldn't find answer" but tool actually raised | Legacy `AgentExecutor` `handle_parsing_errors=True` silently swallowed exception (P09) | Migrate to `create_react_agent`; errors raise by default |
| Agent loops when `tool_choice={"type": "tool", "name": "X"}` is set | Forced tool_choice blocks `stop_reason="end_turn"` (P63) | Use `tool_choice="auto"` for agent loops; reserve forced choice for one-shot calls |
| Agent hallucinates a tool name like `exec` that is not in `tools=[...]` | Older free-text ReAct parser accepts any string (P32) | Use `create_react_agent` — it relies on provider-native tool calling; the allowlist is wire-enforced |
| `RuntimeError: Token budget exceeded` | Your `TokenBudget` callback fired | Working as intended; raise the cap or shorten the agent's scope |
| Tool description truncated, model calls with wrong args | Docstring exceeded 1024-char cap (P11) | Shorten docstring; move examples into system prompt |

## Examples

### Migrating a legacy `AgentExecutor` agent

Before (LangChain 0.2):

```python
from langchain.agents import initialize_agent, AgentType
agent = initialize_agent(
    tools, llm, agent=AgentType.OPENAI_FUNCTIONS,
    handle_parsing_errors=True, return_intermediate_steps=True,
)
result = agent.invoke({"input": "..."})
for action, observation in result["intermediate_steps"]:
    print(action.tool, observation)  # .tool attribute
```

After (LangGraph 1.0):

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
agent = create_react_agent(llm, tools, checkpointer=MemorySaver())
result = agent.invoke(
    {"messages": [{"role": "user", "content": "..."}]},
    config={"configurable": {"thread_id": "t1"}, "recursion_limit": 10},
)
# intermediate steps are now ToolMessage entries in the messages list
for m in result["messages"]:
    if m.type == "tool":
        print(m.name, m.content)  # .name, not .tool
```

See [AgentExecutor Migration](references/agent-executor-migration.md) for the
full before/after including `handle_parsing_errors`, `return_intermediate_steps`,
and `max_iterations` translations.

### Interactive agent with a strict cost cap

A customer-support agent with two tools, 10-step recursion cap, and a 30K
token budget. See [Loop Caps and Budgets](references/loop-caps-and-budgets.md)
for the full example with a repeated-tool-call early-stop node.

## Resources

- [LangGraph: Agents overview](https://langchain-ai.github.io/langgraph/agents/overview/)
- [`create_react_agent` reference](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent)
- [LangGraph: Recursion limits](https://langchain-ai.github.io/langgraph/how-tos/recursion-limit/)
- [LangGraph: Tool calling](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/)
- [LangChain: `@tool` decorator](https://python.langchain.com/docs/how_to/custom_tools/)
- [LangChain 1.0 release notes](https://blog.langchain.com/langchain-langgraph-1dot0/)
- Pack pain catalog: `docs/pain-catalog.md` (entries P09, P10, P11, P32, P41, P42, P63)

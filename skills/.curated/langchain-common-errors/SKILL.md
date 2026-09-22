---
name: langchain-common-errors
description: "Paste-match catalog of 14 real LangChain 1.0 / LangGraph 1.0 exceptions\
  \ with named\ncauses and named fixes, plus a triage decision tree. Use when you\
  \ have a traceback\nand want the specific fix, not speculative documentation. Covers\
  \ ImportError (0.2/0.3 \u2192 1.0\nmigration), AttributeError on AIMessage.content,\
  \ KeyError in LCEL and prompts,\nGraphRecursionError, silent thread_id memory loss,\
  \ JSON-serialization crashes,\nand graphs that halt without reaching END. Trigger\
  \ with \"langchain error\",\n\"langgraph traceback\", \"OutputParserException\"\
  , \"GraphRecursionError\",\n\"ImportError langchain\", \"AttributeError AIMessage\
  \ content\".\n"
allowed-tools: Read, Grep
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- errors
- troubleshooting
- debugging
compatibility: Designed for Claude Code
---
# LangChain Common Errors (Python)

## Overview

The same twelve-plus LangChain 1.0 / LangGraph 1.0 tracebacks show up every week
in production: `ImportError: cannot import name 'ChatOpenAI' from 'langchain.chat_models'`,
`AttributeError: 'list' object has no attribute 'lower'`, `GraphRecursionError:
Recursion limit of 25 reached`, `TypeError: Object of type datetime is not JSON
serializable`, `KeyError: 'question'` deep in LCEL internals. Stack traces are
ambiguous, docs sprawl across 0.2 / 0.3 / 1.0 eras, and engineers lose
30–90 minutes per incident re-deriving the fix.

This skill is a **paste-match catalog** of 14 entries (E01–E14) grouped into
3 reference files by category, plus a triage decision tree. Every entry opens
with the **exact exception class and message string** you see in your terminal,
names the cause in one sentence with a pain-catalog code, and gives a one-line
fix or a reference-file pointer. Pinned to `langchain-core 1.0.x`,
`langchain 1.0.x`, `langgraph 1.0.x`, verified 2026-04-21.

Pain-catalog anchors: **P02, P06, P09, P10, P16, P17, P38, P39, P40, P41, P42, P55, P56, P57, P66**.

## Prerequisites

- Python 3.10+
- A traceback or a reproducible bug — **this skill is diagnostic, not preventive**
- `langchain-core >= 1.0, < 2.0`, `langgraph >= 1.0, < 2.0`, and any provider
  integration packages pinned to `1.0.x`
- `anthropic >= 0.42` when using `langchain-anthropic` 1.0 (see E06)

## Instructions

1. **Triage first.** Read the first line of the traceback. Look up the exception
   class in the catalog below or in [Triage Decision Tree](references/errors/triage-decision-tree.md).
2. **Match the message string**, not the call site. Each catalog entry opens with
   the literal message pattern you see.
3. **Apply the named fix.** If the entry points to a reference file, read that
   file for the deep walk-through including codemods, before/after code, and
   adjacent traps. Otherwise use the one-line fix here.
4. **Verify with a test.** Every catalog entry names a test that will catch the
   error in CI next time.
5. **If no match:** check `docs/pain-catalog.md` for the exception class name or
   a message substring. Do not add speculative fixes here without catalog evidence.

## Catalog

Each entry is indexed as **E## — ClassName: "message pattern"** with a one-line
cause (pain-catalog code) and a one-line fix or reference pointer.

### Category A — Import & migration errors (0.2 / 0.3 → 1.0)

Full detail, before/after code, codemod commands: [import-migration.md](references/errors/import-migration.md).

#### E01 — `ImportError: cannot import name 'ChatOpenAI' from 'langchain.chat_models'`

- **Cause:** Top-level `langchain.chat_models` / `langchain.llms` re-exports removed in 1.0 (P38).
- **Fix:** `from langchain_openai import ChatOpenAI`. Run `python -m langchain_cli migrate` for automated rewrites. See E01 in [import-migration.md](references/errors/import-migration.md).

#### E02 — `AttributeError: module 'langchain' has no attribute 'LLMChain'`

- **Cause:** Legacy chain classes (`LLMChain`, `SequentialChain`, `TransformChain`) removed in 1.0 in favor of LCEL (P39).
- **Fix:** `chain = prompt | llm | StrOutputParser()`; `.run(x)` becomes `.invoke({"input": x})`. See E02 in [import-migration.md](references/errors/import-migration.md).

#### E03 — `ImportError: cannot import name 'ConversationBufferMemory'`

- **Cause:** All legacy memory classes removed in 1.0; LangGraph checkpointing is the replacement (P40).
- **Fix:** Use `InMemorySaver` / `PostgresSaver` + `thread_id` via LangGraph `create_react_agent`. See E03 in [import-migration.md](references/errors/import-migration.md).

#### E04 — `ImportError: cannot import name 'initialize_agent'`

- **Cause:** Legacy agent factories (`initialize_agent`, `AgentType`, `create_openai_functions_agent`) removed in 1.0 (P41).
- **Fix:** `from langgraph.prebuilt import create_react_agent`; `create_react_agent(model=llm, tools=tools, checkpointer=InMemorySaver())`. See E04 in [import-migration.md](references/errors/import-migration.md).

#### E05 — `AttributeError: 'AgentAction' object has no attribute 'tool_name'` (or inverse)

- **Cause:** Legacy `AgentAction` / `AgentFinish` shape replaced by `ToolCall` objects; fields renamed `.tool` → `.tool_name`, `.tool_input` → `.args` (P42).
- **Fix:** Access `tool_call["name"]` / `tool_call["args"]` on message `.tool_calls`, not `result["intermediate_steps"]`. See E05 in [import-migration.md](references/errors/import-migration.md).

#### E06 — `KeyError: 'input'` inside tool_use block parsing

- **Cause:** `langchain-anthropic >= 1.0` requires `anthropic >= 0.40`; SDK tool-use schema changed (P66).
- **Fix:** `pip install "langchain-anthropic>=1.0,<2.0" "anthropic>=0.42,<1.0"` in the same commit. See E06 in [import-migration.md](references/errors/import-migration.md).

### Category B — Content-shape & prompt-template errors

Full detail, block-iterator extractor, jinja2 escape pattern: [content-shape.md](references/errors/content-shape.md).

#### E07 — `AttributeError: 'list' object has no attribute 'lower'` (or `.strip`, `.split`, `.format`)

- **Cause:** `AIMessage.content` is `list[dict]` on Claude with any non-text block and on OpenAI once tools are bound (P02).
- **Fix:** Use `msg.text()` (LangChain 1.0+) or iterate and filter `block["type"] == "text"`. See E07 in [content-shape.md](references/errors/content-shape.md).

#### E08 — `KeyError: '<var>'` inside `runnables/passthrough.py` or `runnables/base.py`

- **Cause:** LCEL dict-shape mismatch between runnable stages; error surfaces at the consumer, not the producer (P06).
- **Fix:** Insert `RunnableLambda` debug probes between stages and enable `set_debug(True)`. See E08 in [content-shape.md](references/errors/content-shape.md).

#### E09 — `KeyError: '<var>'` inside `prompts/chat.py` or `prompts/prompt.py` on user input

- **Cause:** `ChatPromptTemplate.from_messages` defaults to f-string parsing; user-provided `{` / `}` characters are parsed as template variables (P57).
- **Fix:** Use `MessagesPlaceholder("history")` for variable content, or `template_format="jinja2"` for free-text templates, or escape literals as `{{` / `}}`. See E09 in [content-shape.md](references/errors/content-shape.md).

### Category C — Agent & graph execution traps

Full detail, diagnostic callbacks, thread_id middleware, router asserts: [graph-traps.md](references/errors/graph-traps.md).

#### E10 — `GraphRecursionError: Recursion limit of 25 reached without hitting a stop condition`

- **Cause:** `create_react_agent` and `StateGraph.compile()` default `recursion_limit=25` counts supersteps, not loop iterations; vague prompts never converge (P10, P55).
- **Fix:** Set `recursion_limit=10` for interactive use; add terminal edge on repeated tool-call names. See E10 in [graph-traps.md](references/errors/graph-traps.md).

#### E11 — `AgentExecutor` returns `"I couldn't find the answer"` on every tool call, no exception

- **Cause:** `handle_parsing_errors=True` catches tool exceptions and passes `str(exc)` (often empty) as observation; loop continues without signal (P09).
- **Fix:** `return_intermediate_steps=True, handle_parsing_errors=False` or migrate to LangGraph `create_react_agent`. See E11 in [graph-traps.md](references/errors/graph-traps.md).

#### E12 — Multi-turn chat forgets everything between calls, no exception

- **Cause:** LangGraph checkpointers key state by `config["configurable"]["thread_id"]`; omitted `thread_id` means every invocation gets a fresh state with no warning (P16).
- **Fix:** Require `thread_id` at app boundary; wrap in middleware that raises on missing key. See E12 in [graph-traps.md](references/errors/graph-traps.md).

#### E13 — `TypeError: Object of type <datetime / bytes / Decimal / set> is not JSON serializable`

- **Cause:** `InMemorySaver` / `PostgresSaver` / `SqliteSaver` serialize state as JSON on every superstep; non-primitives break at interrupt or checkpoint boundary (P17).
- **Fix:** Keep state JSON-primitive only (str/int/float/bool/list/dict); serialize at node boundaries; or use `JsonPlusSerializer` for Pydantic v2. See E13 in [graph-traps.md](references/errors/graph-traps.md).

#### E14 — Graph halts without reaching `END`, no exception, no log

- **Cause:** `add_conditional_edges(node, router, path_map)` where router returns a string not in `path_map` causes silent termination on some 1.0 versions (P56).
- **Fix:** `assert router_return in path_map`; always include `END` explicitly; inspect `graph.get_state(cfg).next`. See E14 in [graph-traps.md](references/errors/graph-traps.md).

## Output

- Named cause tied to a P## pain-catalog code for every traceback
- Named fix (one-line or a reference-file walk-through) tied to E## catalog entry
- A regression test pattern that catches the error in CI next time
- Triage path recorded for the incident retro (which entry matched, how long it took)

## Error Handling

This skill **is** the error-handling reference for the pack. The triage workflow:

1. **First line of traceback** → pick category in the table below.
2. **Exception class + message substring** → pick E## entry above.
3. **Reference file** → read the deep walk-through for before/after code and tests.

| First-line pattern | Category | Entries | Reference |
|---|---|---|---|
| `ImportError` from `langchain.*` | A | E01, E03, E04 | import-migration.md |
| `AttributeError` on `langchain.*` module | A | E02 | import-migration.md |
| `AttributeError` on `AgentAction` / `ToolCall` | A | E05 | import-migration.md |
| `ImportError` / `KeyError` against `langchain-anthropic` | A | E06 | import-migration.md |
| `AttributeError` on `list.lower` / `.strip` | B | E07 | content-shape.md |
| `KeyError` in `runnables/` | B | E08 | content-shape.md |
| `KeyError` in `prompts/` | B | E09 | content-shape.md |
| `GraphRecursionError` | C | E10 | graph-traps.md |
| Silent wrong answers / empty tool errors | C | E11 | graph-traps.md |
| Multi-turn memory loss, no exception | C | E12 | graph-traps.md |
| `TypeError` ... `not JSON serializable` | C | E13 | graph-traps.md |
| Graph halts without reaching `END` | C | E14 | graph-traps.md |

For tracebacks that do not match: consult [triage-decision-tree.md](references/errors/triage-decision-tree.md)
for the full routing flowchart, then `docs/pain-catalog.md` for any remaining
pain codes. Escalate to the main thread before adding speculative fixes.

## Examples

### Example 1 — `ImportError` on a 0.3 → 1.0 upgrade

Incoming traceback:

```
Traceback (most recent call last):
  File "app.py", line 3, in <module>
    from langchain.chat_models import ChatOpenAI
ImportError: cannot import name 'ChatOpenAI' from 'langchain.chat_models'
```

Triage:

1. First line is `ImportError` from `langchain.chat_models` → Category A.
2. Matches **E01** exactly.
3. Cause: top-level re-exports removed in 1.0 (P38).
4. Fix: rewrite imports and bump provider packages.

```bash
pip install "langchain-openai>=1.0,<2.0" "langchain-anthropic>=1.0,<2.0" "langchain-cli>=0.1"
python -m langchain_cli migrate src/
```

```python
# Before
from langchain.chat_models import ChatOpenAI

# After
from langchain_openai import ChatOpenAI
```

Re-run tests. Next failure is almost always **E07** (`AIMessage.content` shape)
once the imports resolve — walk that one next from [content-shape.md](references/errors/content-shape.md).

### Example 2 — `GraphRecursionError` triage

Incoming traceback:

```
Traceback (most recent call last):
  File "worker.py", line 88, in run
    result = agent.invoke({"messages": [("user", q)]}, config=cfg)
  ...
langgraph.errors.GraphRecursionError: Recursion limit of 25 reached without hitting a stop condition. You can increase the limit by setting the `recursion_limit` config key.
```

Triage:

1. Exception class is `GraphRecursionError` → Category C.
2. Matches **E10** exactly.
3. Cause: vague prompt or tool loop; default `recursion_limit=25` (P10, P55).
4. Before raising the limit, **diagnose first** — attach a `StepLogger` callback
   (see [graph-traps.md](references/errors/graph-traps.md) § E10) and count
   real steps. If the same two node names alternate, it is a convergence bug,
   not a budget bug.

Fix (budget only):

```python
cfg = {"configurable": {"thread_id": tid}, "recursion_limit": 10}
agent.invoke(inp, config=cfg)
```

Fix (convergence + budget):

```python
def _should_stop(state):
    recent = [m for m in state["messages"][-6:] if getattr(m, "tool_calls", None)]
    if len(recent) >= 3 and all(
        r.tool_calls[0]["name"] == recent[0].tool_calls[0]["name"] for r in recent
    ):
        return "end"
    return "continue"

graph.add_conditional_edges("agent", _should_stop, {"continue": "agent", "end": END})
```

Pair with a per-session token-budget middleware from `langchain-cost-tuning`.

## Resources

- Pack pain catalog: `docs/pain-catalog.md` — canonical entries for
  P02, P06, P09, P10, P16, P17, P38, P39, P40, P41, P42, P55, P56, P57, P66
- [Import & migration errors](references/errors/import-migration.md) — E01–E06
- [Content-shape & prompt errors](references/errors/content-shape.md) — E07–E09
- [Agent & graph execution traps](references/errors/graph-traps.md) — E10–E14
- [Triage decision tree](references/errors/triage-decision-tree.md) — ASCII flowchart + quick-match table
- [LangChain 1.0 release notes](https://blog.langchain.com/langchain-langgraph-1dot0/)
- [LangChain migration guide](https://python.langchain.com/docs/versions/migrating_chains/)
- LangGraph concepts
- [`langchain-cli` migrate command](https://python.langchain.com/docs/versions/migrating/)
- [`create_react_agent` reference](https://langchain-ai.github.io/langgraph/reference/prebuilt/)

---
name: langchain-core-workflow
description: "Compose LangChain 1.0 chains with RunnableParallel, RunnableBranch,\n\
  RunnablePassthrough.assign, and RunnableLambda \u2014 correct input/output shapes,\n\
  debug probes, and typed composition that catches dict-shape bugs before\ninvocation.\
  \ Use when wiring multi-step chains, parallel retrievals,\nconditional routing,\
  \ or threading state through a chain for RAG,\nclassification, or extraction pipelines.\n\
  Trigger with \"runnable parallel\", \"runnable branch\", \"langchain rag\ncomposition\"\
  , \"passthrough assign\", \"langchain lcel\", \"runnable lambda\",\n\"debug probe\"\
  .\n"
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
- lcel
- runnables
- rag
compatibility: Designed for Claude Code
---
# LangChain Core Workflow (Python)

## Overview

An engineer wires a four-stage LCEL chain: classify the question, retrieve
context, format the prompt, invoke the LLM. It looks clean:

```python
chain = (
    RunnablePassthrough.assign(category=classifier)
    | RunnablePassthrough.assign(docs=retriever)
    | prompt
    | llm
    | StrOutputParser()
)

chain.invoke({"question": "What's our refund policy?"})
```

The call returns this:

```
Traceback (most recent call last):
  ...
  File ".../runnables/base.py", line 3421, in _call_with_config
    output = call_func_with_variable_args(func, input, ...)
  File ".../prompts/chat.py", line 1021, in _format_messages
    return await ... await self.ainvoke({**kwargs})
KeyError: 'question'
```

Nothing in that stack says **which stage produced the wrong dict shape**. The
`RunnablePassthrough.assign(docs=retriever)` call silently rebuilt the dict
and — because `retriever` was itself a `Runnable[str, list[Document]]` that
took the `question` *string*, not the dict — a mis-piped intermediate value
overwrote the `question` key. The prompt template expected `{question}` and
blew up. This is P06 in the pack's pain catalog: `.pipe()` on mismatched dict
shape raises `KeyError` deep in runnable internals with no hint at the
offending stage.

The fix is **two patterns you install once and never remove**:

1. **Debug probes** — a `RunnableLambda` that logs dict keys between every two
   stages. <1ms overhead per invocation. Surfaces the exact stage that mutates
   the shape.
2. **Typed composition** — annotate each chain with `RunnableSerializable[InputT, OutputT]`
   plus pydantic `BaseModel` types so mypy flags the mismatch at lint time
   instead of at `.invoke()`.

Meanwhile, a second trap waits for anyone tempted to wrap tool-using chains
in the legacy `AgentExecutor`: it silently swallows intermediate tool errors
as empty-string observations and the agent cheerfully answers "I couldn't
find the answer" (P09). For agent loops in LangChain 1.0, skip `AgentExecutor`
and use LangGraph's `create_react_agent` — errors raise, not vanish. This
skill cross-references `langchain-langgraph-agents` (L26) for that path.

Composition primitives covered — with input/output shapes and use cases — are
`RunnableParallel` (fan-out, 2–3× wall-clock win on 2 independent retrievals),
`RunnableBranch` (conditional routing with mandatory default), `RunnablePassthrough.assign`
(merge computed fields without losing input), and `RunnableLambda` (arbitrary
Python, used here for debug probes and shape assertions). Pin: `langchain-core 1.0.x`.
Pain-catalog anchors: P06, P09.

## Prerequisites

- Python 3.10+
- `langchain-core >= 1.0, < 2.0`
- `pydantic >= 2.0` for typed composition
- At least one chat provider installed (see `langchain-model-inference`)
- Familiarity with the composition primitives introduced in `langchain-sdk-patterns`

## Instructions

### Step 1 — Fan-out with `RunnableParallel` for independent sub-tasks

`RunnableParallel({"a": chain_a, "b": chain_b})` forwards the same input to
both branches and runs them concurrently, merging results into a dict.
Wall-clock collapses to the slower branch — 2–3× speedup on two parallel
retrievals is typical (dense vector search + BM25, or tool-use + analysis).

```python
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# Hybrid retrieval: dense vector search and BM25 at the same time
hybrid = RunnableParallel(
    dense=dense_retriever,     # Runnable[str, list[Document]]
    bm25=bm25_retriever,       # Runnable[str, list[Document]]
    query=RunnablePassthrough() # keep the original string for downstream stages
)

# Output: {"dense": [...], "bm25": [...], "query": "..."}
result = hybrid.invoke("refund policy for damaged goods")
```

Input shape: whatever the sub-chains accept (all must accept the same shape).
Output shape: `dict` with one key per sub-chain. If one branch takes 5× longer,
your total latency is that branch — not the sum. See
[Parallel vs Sequential](references/parallel-vs-sequential.md) for the async
`.abatch()` variant, shared-state gotchas, and a benchmarking template.

### Step 2 — Route on input with `RunnableBranch`

`RunnableBranch((cond, runnable), ..., default)` dispatches per-input to the
first matching branch. **The default is mandatory** — without one you get a
silent fallthrough on unmatched inputs.

```python
from langchain_core.runnables import RunnableBranch

router = RunnableBranch(
    (lambda x: x["category"] == "refund", refund_chain),
    (lambda x: x["category"] == "shipping", shipping_chain),
    (lambda x: len(x["question"]) > 2000, long_form_chain),
    general_chain,  # default — required
)
```

Classifier-gated routes are the common case: a cheap small-model classifier
runs first, its label goes into the dict via `RunnablePassthrough.assign`, and
`RunnableBranch` dispatches. See [Branch Routing Patterns](references/branch-routing-patterns.md)
for the signature, classifier-gated route recipe, fallback route pattern, and
pytest patterns for each branch in isolation.

### Step 3 — Thread state with `RunnablePassthrough.assign`

`.assign(field=...)` merges a computed field into the input dict without
losing any existing keys. This is the primary pattern for staged context
assembly in RAG:

```python
from langchain_core.runnables import RunnablePassthrough

def format_docs(docs: list) -> str:
    return "\n\n".join(d.page_content for d in docs)

# At each step, the dict grows: {question} -> {question, docs} -> {question, docs, context}
staged = (
    RunnablePassthrough.assign(docs=retriever)         # adds "docs"
    | RunnablePassthrough.assign(context=lambda x: format_docs(x["docs"]))  # adds "context"
)

staged.invoke({"question": "..."})
# {"question": "...", "docs": [...], "context": "..."}
```

The input dict passes through unchanged; the new field is the only mutation.
This is the safest shape-preserving primitive in LCEL — use it whenever a
downstream stage needs both the original input and a computed value. See
[Passthrough Assign Patterns](references/passthrough-assign-patterns.md) for
staged context assembly, the `itemgetter` variant for pulling a single field
into a typed chain, and anti-patterns that re-shadow input keys.

### Step 4 — Use `RunnableLambda` for debug probes (and little else)

`RunnableLambda(fn)` wraps any Python callable into a runnable. Its best use
is **debug probes** — log intermediate values without breaking the pipe:

```python
from langchain_core.runnables import RunnableLambda

def probe(stage: str):
    """<1ms overhead per invocation. Returns input unchanged."""
    def _probe(x):
        keys = list(x.keys()) if isinstance(x, dict) else type(x).__name__
        print(f"[probe:{stage}] keys={keys}")
        return x
    return RunnableLambda(_probe)

chain = (
    probe("input")
    | RunnablePassthrough.assign(category=classifier)
    | probe("after-classify")
    | RunnablePassthrough.assign(docs=retriever)
    | probe("after-retrieve")
    | prompt
    | probe("after-prompt")
    | llm
    | StrOutputParser()
)
```

When P06's `KeyError` strikes, the last probe that printed tells you exactly
which stage produced the wrong shape. Remove the probes (or gate them on an
env var) after debugging. For production chains that stay observable, prefer
`langchain.debug = True` or LangSmith tracing over `print` probes.

See [Debug Probes](references/debug-probes.md) for a shape-assertion decorator,
the `langchain.debug` flag, verbose mode, and a probe that raises instead of
prints (useful in CI).

Avoid `RunnableLambda` for real logic — it loses LangSmith tracing fidelity
(input/output become opaque blobs) and a >3-line lambda is a sign you want a
concrete `Runnable` subclass. See the anti-pattern note in
`langchain-sdk-patterns/references/runnable-composition-matrix.md`.

### Step 5 — Type chains with `RunnableSerializable[InputT, OutputT]`

The root fix for P06 is static typing at chain boundaries. `RunnableSerializable`
carries input and output type parameters; pair it with pydantic `BaseModel`s
and mypy catches dict-shape mismatches at lint time:

```python
from pydantic import BaseModel
from langchain_core.runnables import RunnableSerializable

class RAGInput(BaseModel):
    question: str
    user_id: str

class RAGOutput(BaseModel):
    answer: str
    citations: list[str]

def build_rag_chain() -> RunnableSerializable[RAGInput, RAGOutput]:
    return (
        RunnablePassthrough.assign(docs=retriever)
        | RunnablePassthrough.assign(context=lambda x: format_docs(x["docs"]))
        | prompt
        | llm.with_structured_output(RAGOutput)
    )

rag: RunnableSerializable[RAGInput, RAGOutput] = build_rag_chain()
```

Call `rag.input_schema.model_json_schema()` to dump the runtime-enforced
schema for tests or assertions. Combined with the debug probes from Step 4,
this is the typed-composition pattern that retires P06 in new code.

### Step 6 — RAG composition example (end-to-end)

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer from the context. If not in context, say so."),
    ("human", "Context:\n{{ context }}\n\nQuestion: {{ question }}"),
], template_format="jinja2")

# Hybrid retrieval (parallel) + staged context assembly
rag_chain = (
    RunnableParallel(
        dense=dense_retriever,
        bm25=bm25_retriever,
        question=RunnablePassthrough(),
    )
    | RunnablePassthrough.assign(
        context=lambda x: format_hybrid(x["dense"], x["bm25"])
    )
    | prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("What's the return window for electronics?")
```

This is the reference composition — parallel dual-retrieval (2–3× speedup vs
sequential), staged context assembly via `.assign`, jinja2 prompt templating
(escapes literal `{` from retrieved docs, see `langchain-sdk-patterns`), and
a simple string output. Add debug probes from Step 4 during development.

### Step 7 — For agent loops, skip `AgentExecutor`

Legacy `AgentExecutor` silently catches tool exceptions and feeds the error
message back as an empty-string observation — the agent then answers "I
couldn't find the answer" with no trace of the underlying failure (P09). In
LangChain 1.0, use LangGraph's `create_react_agent` instead: tool errors
raise by default, intermediate steps are inspectable, and recursion limits
are explicit.

See the pack's `langchain-langgraph-agents` skill (L26) for the agent
migration path. The composition primitives in this skill (`RunnableParallel`,
`RunnableBranch`, `.assign`) remain the right tools for the non-agent parts
of any LangGraph workflow — they compose inside a LangGraph node.

## Composition Pattern Table

| Pattern | Input shape | Output shape | Typical use |
|---|---|---|---|
| `a \| b \| c` (RunnableSequence) | `a.input` | `c.output` | Linear pipeline: prompt → llm → parser |
| `RunnableParallel(x=ch1, y=ch2)` | forwarded to both | `{"x": ch1.output, "y": ch2.output}` | Fan-out: hybrid retrieval, tool-use + analysis |
| `RunnableBranch((cond, ch), ..., default)` | anything cond accepts | `ch.output` or `default.output` | Classifier-gated routing, per-input dispatch |
| `RunnablePassthrough()` | any | same as input | Keep original value alongside a transform in a parallel |
| `RunnablePassthrough.assign(k=ch)` | `dict` | input dict with `"k"` added (ch.output) | Staged context assembly, threading state |
| `RunnableLambda(fn)` | `fn`'s arg | `fn`'s return | Debug probes, shape assertions — avoid for real logic |

## Output

- Multi-step chains composed from `RunnableParallel`, `RunnableBranch`, `RunnablePassthrough.assign`, and `RunnableLambda` with declared input/output shapes
- Debug-probe pattern (<1ms per invocation) that surfaces the exact stage producing a wrong dict shape when P06 strikes
- Typed-composition pattern (`RunnableSerializable[InputT, OutputT]` + pydantic `BaseModel`) that catches P06 at lint time before invocation
- RAG composition recipe: hybrid parallel retrieval + staged context assembly + prompt + llm + parser, 2–3× wall-clock win on dual retrieval
- Cross-reference to `langchain-langgraph-agents` (L26) for agent loops that avoid P09's silent-error trap

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `KeyError: 'question'` deep in runnable internals, no stage named in stack | `RunnablePassthrough.assign` or an upstream runnable rebuilt the dict in a way a downstream stage does not expect (P06) | Insert `RunnableLambda` debug probes between stages; annotate with `RunnableSerializable[InputT, OutputT]` + pydantic for lint-time catch |
| Agent returns "I couldn't find the answer" with no error in logs | Legacy `AgentExecutor` swallows tool exceptions as empty-string observations (P09) | Migrate to LangGraph `create_react_agent`; see `langchain-langgraph-agents` (L26) |
| `RunnableBranch` returns wrong branch's output for unmatched input | No default branch supplied; LCEL fell through to the last-declared pair | Always pass a default as the final positional arg to `RunnableBranch((cond, ch), ..., default_ch)` |
| `.assign` computed field shadows input key | `RunnablePassthrough.assign(question=...)` overwrote the original `question` | Name computed fields distinctly from input keys; use `itemgetter` to extract when you need the original |
| `RunnableLambda` call shows as opaque blob in LangSmith | Lambda's input/output are not traced at block-level | Replace with a concrete `Runnable` subclass or use `.assign(key=...)` with a named function |
| `RunnableParallel` branches race on shared mutable state | A lambda closed over a non-thread-safe object | Keep parallel branches side-effect-free; materialize shared state before the parallel block |

## Examples

### Hybrid retrieval with parallel branches

Two retrievers run concurrently on the same query — dense vector search via
an embedding model and BM25 via rank-bm25. `RunnableParallel` merges the
results; a downstream `.assign` step formats the union. Wall-clock is the
slower retriever, not the sum — typically a 2–3× win over sequential dense
then BM25.

See [Parallel vs Sequential](references/parallel-vs-sequential.md) for the
benchmarking template and async variant.

### Classifier-gated routing for a customer support chain

A cheap small-model classifier runs first and tags the input dict with a
`category`. `RunnableBranch` dispatches refunds, shipping, and general
questions to specialist chains. The default branch handles unmatched inputs
with a disclaimer prompt.

See [Branch Routing Patterns](references/branch-routing-patterns.md) for the
classifier-gated recipe and pytest isolation patterns.

### Staged context assembly for RAG with citations

`RunnablePassthrough.assign(docs=retriever)` then
`.assign(context=format_docs)` builds the prompt context without dropping the
original `question`. A final `.assign(citations=lambda x: [d.metadata["url"] for d in x["docs"]])`
threads citations through to the structured output.

See [Passthrough Assign Patterns](references/passthrough-assign-patterns.md)
for the staged pattern and the anti-pattern around key shadowing.

### Debug probe that raises in CI

In development, probes `print`. In CI, they assert on expected keys and raise
on mismatch — catching P06 during test runs instead of at production invoke.

See [Debug Probes](references/debug-probes.md) for the shape-assertion
decorator and the `langchain.debug` flag.

## Resources

- [LangChain Python: Runnable interface](https://python.langchain.com/docs/concepts/runnables/)
- [LangChain Python: RunnableParallel](https://python.langchain.com/docs/how_to/parallel/)
- [LangChain Python: RunnableBranch](https://python.langchain.com/docs/how_to/routing/)
- [LangChain Python: RunnablePassthrough](https://python.langchain.com/docs/how_to/passthrough/)
- [LangChain Python: debug mode](https://python.langchain.com/docs/how_to/debugging/)
- [LangChain 1.0 release notes](https://blog.langchain.com/langchain-langgraph-1dot0/)
- Pair skill: `langchain-sdk-patterns` (composition primitives, fallbacks, concurrency)
- Agent alternative: `langchain-langgraph-agents` (L26) — avoids P09
- Pack pain catalog: `docs/pain-catalog.md` (entries P06, P09)

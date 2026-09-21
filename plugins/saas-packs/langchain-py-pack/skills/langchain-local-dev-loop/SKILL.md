---
name: langchain-local-dev-loop
description: "Build a fast, deterministic local test loop for LangChain 1.0 / LangGraph\
  \ 1.0\n\u2014 FakeListChatModel fixtures, pytest config, VCR cassettes with key\
  \ redaction,\nwarning-filter policy. Use when adding tests to a new chain, fixing\
  \ a flaky\ntest, or making integration tests reproducible.\nTrigger with \"langchain\
  \ pytest\", \"FakeListChatModel\", \"VCR langchain\",\n\"langchain test fixtures\"\
  , \"langchain integration test\".\n"
allowed-tools: Read, Write, Edit, Bash(pytest:*), Bash(python:*), Bash(pip:*)
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- testing
- pytest
- vcr
compatibility: Designed for Claude Code
---
# LangChain Local Dev Loop (Python)

## Overview

An engineer writes the most natural assertion possible:

```python
def test_summarize():
    out = chain.invoke({"text": "..."})
    assert out.content == "expected summary"
```

It passes locally against Claude at `temperature=0`. It fails in CI on the third
run with a one-token delta in the output. That is P05: Anthropic's `temperature=0`
is not greedy — it still samples. Tests against live Claude are not deterministic,
period.

So the engineer swaps in `FakeListChatModel(responses=["expected summary"])` and
the assertion passes. Then the downstream callback that logs cost blows up in CI
with `KeyError: 'token_usage'` — because `FakeListChatModel` does not emit
`response_metadata["token_usage"]` (P43). Production code reads that key, so
either the fake has to synthesize it or the test has to skip the callback.

Meanwhile, the first integration test under VCR records a cassette that ships
`Authorization: Bearer sk-ant-api03-...` in the repo (P44). PR review catches it;
the reviewer revokes the key; the dev loop is hosed for an afternoon.

And none of this matters if pytest cannot even collect the suite because
`import langchain_community` emits a `DeprecationWarning` that `-W error` promotes
to failure (P45).

This skill installs the four layers that make the whole loop fast and safe:
`FakeListChatModel` / `FakeListLLM` with a metadata-emitting subclass (fixes P43);
VCR with `filter_headers` plus a pre-commit hook (fixes P44); pytest
`filterwarnings` policy in `pyproject.toml` (fixes P45); and an env-var-gated
integration marker so the default `pytest` run never touches live APIs.

**Speed targets:** unit tests with `FakeListChatModel` run in **< 100ms** per
test; VCR-replayed integration tests run in **500ms – 2s** per test; live
integration tests (the `RUN_INTEGRATION=1` gate) run only in nightly or
manual workflows.

**Pin:** `langchain-core 1.0.x`, `langgraph 1.0.x`, `pytest` current, `vcrpy`
current. Pain-catalog anchors: P05, P43, P44, P45.

## Prerequisites

- Python 3.10+
- `pip install langchain-core>=1.0,<2.0 langgraph>=1.0,<2.0 pytest vcrpy pytest-recording`
- For integration tests: at least one provider key (`ANTHROPIC_API_KEY`, etc.)
- Project uses `pyproject.toml` (PEP 621) for pytest config

## Instructions

### Step 1 — Deterministic unit tests with `FakeListChatModel`

Use `FakeListChatModel` from `langchain_core.language_models.fake` for chat
chains and `FakeListLLM` for legacy completion LLMs. Responses cycle through
the list.

```python
from langchain_core.language_models.fake import FakeListChatModel
from langchain_core.prompts import ChatPromptTemplate

def test_classifier_picks_positive():
    fake = FakeListChatModel(responses=["positive"])
    prompt = ChatPromptTemplate.from_messages([("user", "Classify: {text}")])
    chain = prompt | fake
    out = chain.invoke({"text": "I love it"})
    assert out.content == "positive"
```

This is deterministic, runs in single-digit milliseconds, and has zero provider
dependency. Use it for every chain assertion that does not specifically require
real model behavior.

### Step 2 — Subclass `FakeListChatModel` to emit `response_metadata` (P43 fix)

The stock fake emits no `response_metadata["token_usage"]`. If your chain has a
callback that records cost, the callback crashes under the fake. Subclass and
synthesize the metadata instead of mocking around the callback:

```python
from langchain_core.language_models.fake import FakeListChatModel
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.messages import AIMessage

class FakeChatWithUsage(FakeListChatModel):
    """FakeListChatModel that emits response_metadata['token_usage'] so
    downstream callbacks reading token usage do not crash under test."""

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        response = self.responses[self.i % len(self.responses)]
        self.i += 1
        message = AIMessage(
            content=response,
            response_metadata={
                "token_usage": {
                    "input_tokens": 10,
                    "output_tokens": len(response.split()),
                    "total_tokens": 10 + len(response.split()),
                },
                "model_name": "fake-chat",
            },
            usage_metadata={
                "input_tokens": 10,
                "output_tokens": len(response.split()),
                "total_tokens": 10 + len(response.split()),
            },
        )
        return ChatResult(generations=[ChatGeneration(message=message)])
```

Use `FakeChatWithUsage` whenever a chain's observability / cost path is in the
assertion surface. See [Fake Model Fixtures](references/fake-model-fixtures.md)
for agent, retriever, and embedder fakes.

### Step 3 — pytest fixtures that wire the fake into chains

Put fixtures in `tests/conftest.py` so they are shared across the suite:

```python
# tests/conftest.py
import pytest
from langchain_core.prompts import ChatPromptTemplate
from tests.fakes import FakeChatWithUsage

@pytest.fixture
def fake_chat():
    """Reusable fake chat model. Override responses per-test via
    monkeypatch.setattr(fake_chat, 'responses', [...])."""
    return FakeChatWithUsage(responses=["ok"])

@pytest.fixture
def summarize_chain(fake_chat):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize the user's text in one line."),
        ("user", "{text}"),
    ])
    return prompt | fake_chat
```

Per-test response override:

```python
def test_summary_shape(summarize_chain, fake_chat):
    fake_chat.responses = ["short summary"]
    out = summarize_chain.invoke({"text": "long input"})
    assert out.content == "short summary"
```

### Step 4 — VCR cassettes for integration tests with key redaction (P44 fix)

Unit tests should never touch the network. Integration tests do, exactly once —
to record a cassette — and every subsequent run replays from the cassette file.
`vcrpy` records headers by default, which means `Authorization: Bearer sk-...`
lands in the fixture unless you filter it.

Configure VCR in `tests/conftest.py`:

```python
# tests/conftest.py (continued)
import pytest

@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            "authorization",
            "x-api-key",
            "anthropic-version",
            "openai-organization",
            "cookie",
        ],
        "filter_query_parameters": ["api_key"],
        # Block accidental re-recording in CI:
        "record_mode": "none",
    }
```

Use `pytest-recording`:

```python
import pytest

@pytest.mark.vcr  # cassette at tests/cassettes/<test_name>.yaml
@pytest.mark.integration
def test_live_claude_short_answer():
    from langchain_anthropic import ChatAnthropic
    chat = ChatAnthropic(model="claude-sonnet-4-6", temperature=0, timeout=30)
    out = chat.invoke("Say 'ok' and nothing else.")
    assert "ok" in out.content.lower()
```

To record (once, locally, with a real key): `pytest --record-mode=once tests/`.
Every other run replays — cassettes are committed, real API is never hit again.

**Pre-commit hook to block key leaks:**

```bash
# .git/hooks/pre-commit or .pre-commit-config.yaml entry
#!/usr/bin/env bash
set -e
if git diff --cached --name-only | grep -q '^tests/cassettes/'; then
    if git diff --cached -U0 -- 'tests/cassettes/' | \
       grep -E '(sk-ant-[a-zA-Z0-9_-]+|sk-[a-zA-Z0-9]{20,}|Bearer\s+[a-zA-Z0-9_-]{20,})'; then
        echo "ERROR: API key pattern found in staged cassette." >&2
        exit 1
    fi
fi
```

See [VCR Cassette Hygiene](references/vcr-cassette-hygiene.md) for the full
pre-commit config, record-new-episodes flow, shared-cassette patterns, and the
PR review checklist.

### Step 5 — Pytest warnings + markers in `pyproject.toml` (P45 fix)

`langchain_community` and some provider SDKs emit `DeprecationWarning` at import
time. If the suite runs `-W error`, collection fails before any test does. Set
the policy once in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "-W", "error",
]
markers = [
    "integration: hits real APIs or replays VCR cassettes (set RUN_INTEGRATION=1)",
    "slow: takes > 1s per test",
    "smoke: minimal healthcheck run in CI",
]
filterwarnings = [
    "error",
    "ignore::DeprecationWarning:langchain_community.*",
    "ignore::DeprecationWarning:pydantic.*",
    "ignore::PendingDeprecationWarning:langchain_core.*",
]
```

See [Pytest Config](references/pytest-config.md) for the full skeleton
including coverage config and parallel execution notes.

### Step 6 — Integration-test gating via env var

Default `pytest` must never hit real APIs. Gate on `RUN_INTEGRATION=1`:

```python
# tests/conftest.py (continued)
import os
import pytest

def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_INTEGRATION") == "1":
        return
    skip_integration = pytest.mark.skip(reason="set RUN_INTEGRATION=1 to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
```

CI default: `pytest` (unit only). Nightly / manual: `RUN_INTEGRATION=1 pytest -m integration`.

### Step 7 — LangGraph tests: per-test `thread_id` + state assertions

LangGraph state is scoped to a `thread_id`. Tests that share a `thread_id` leak
state between each other. Give every test a fresh `thread_id` and a fresh
`MemorySaver`:

```python
from langgraph.checkpoint.memory import MemorySaver
import uuid, pytest

@pytest.fixture
def graph_config():
    return {"configurable": {"thread_id": str(uuid.uuid4())}}

@pytest.fixture
def checkpointed_graph(fake_chat):
    from my_app.graphs import build_graph
    return build_graph(fake_chat).compile(checkpointer=MemorySaver())

def test_node_emits_plan(checkpointed_graph, graph_config, fake_chat):
    fake_chat.responses = ["step 1\nstep 2\nstep 3"]
    result = checkpointed_graph.invoke({"goal": "deploy"}, graph_config)
    # Assert state shape per node, not just the final output:
    assert result["plan"] == ["step 1", "step 2", "step 3"]
    # Time-travel: inspect every checkpoint for debugging
    history = list(checkpointed_graph.get_state_history(graph_config))
    assert history[-1].values == {"goal": "deploy"}  # initial state
```

Subgraph isolation testing cross-references `langchain-langgraph-subgraphs`
(pain P21 — parent cannot read child state unless the key is in the parent
schema). See [LangGraph Test Patterns](references/langgraph-test-patterns.md)
for the subgraph-shared-state test recipe.

## Output

- `tests/fakes.py` with `FakeChatWithUsage` subclass that emits `response_metadata`
- `tests/conftest.py` with fake-model fixtures, VCR config, and `RUN_INTEGRATION` gate
- `pyproject.toml` `[tool.pytest.ini_options]` block with markers and `filterwarnings`
- `tests/cassettes/` committed with filtered headers (no `Authorization` / `x-api-key`)
- Pre-commit hook grepping cassettes for `sk-` / `sk-ant-` / `Bearer` patterns
- LangGraph tests with per-test `thread_id` and `MemorySaver` — no cross-test leakage

## Test-type matrix

| Type | Model | Network | Target speed | Determinism | Use case |
|------|-------|---------|--------------|-------------|----------|
| Unit | `FakeListChatModel` / `FakeChatWithUsage` | none | **< 100ms** | total | Chain shape, parser, routing logic |
| Integration (VCR) | real model, replayed cassette | replay only | **500ms – 2s** | total (once recorded) | End-to-end chain behavior, provider-specific edge cases |
| Integration (live) | real model | live API | 2s – 30s | probabilistic (P05) | Nightly smoke, recording new cassettes, provider regression |
| Smoke | real model, minimal prompt | live API | < 5s | probabilistic | CI healthcheck — 1 test per provider, gated on `RUN_INTEGRATION=1` |
| Load | real model | live API | minutes | probabilistic | Throughput / retry-storm reproduction, never in PR CI |

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `AssertionError` on content despite `temperature=0` | Anthropic `temperature=0` still samples (P05) | Switch to `FakeListChatModel` or VCR replay |
| `KeyError: 'token_usage'` under fake model | `FakeListChatModel` emits no `response_metadata` (P43) | Use `FakeChatWithUsage` subclass from Step 2 |
| PR review flags `Authorization: Bearer sk-...` in cassette | VCR recorded headers by default (P44) | Set `filter_headers` before recording; re-record; add pre-commit grep hook |
| `pytest` fails at collection with `DeprecationWarning` | `-W error` + SDK import warnings (P45) | Add `filterwarnings = ["ignore::DeprecationWarning:langchain_community.*"]` |
| `vcr.errors.CannotOverwriteExistingCassetteException` | Test changed request shape but cassette is stale | `pytest --record-mode=new_episodes` locally, inspect diff, commit |
| LangGraph test pollutes next test's state | Shared `thread_id` + shared `MemorySaver` | Per-test `thread_id=uuid.uuid4()`, per-test `MemorySaver()` |

## Examples

### A flaky chain assertion, fixed in three commits

1. **Commit 1 — failing test** uses real `ChatAnthropic`, passes locally, fails
   1-in-5 in CI at `temperature=0` (P05).
2. **Commit 2 — swap to fake model** uses `FakeListChatModel`, passes
   deterministically, but the cost-logging callback crashes (P43).
3. **Commit 3 — fake with metadata** uses `FakeChatWithUsage`, the callback
   reads `response_metadata["token_usage"]` cleanly, the test is green and
   runs in 40ms.

See [Fake Model Fixtures](references/fake-model-fixtures.md) for the full
worked example including agent and retriever fakes.

### Recording a cassette without leaking a key

```bash
# 1. Ensure conftest.py has filter_headers configured FIRST
# 2. Record with real key present in the environment
ANTHROPIC_API_KEY=sk-ant-... pytest --record-mode=once tests/integration/test_summarize.py
# 3. Verify no leak
grep -E 'sk-|Bearer' tests/cassettes/*.yaml && echo "LEAK" || echo "clean"
# 4. Commit cassettes/ — pre-commit hook runs the same grep as a hard gate
git add tests/cassettes/ && git commit -m "test: record summarize cassette"
```

See [VCR Cassette Hygiene](references/vcr-cassette-hygiene.md) for
record-new-episodes mode, rerecord-on-mismatch, and the PR review checklist.

### LangGraph time-travel debugging on a failing test

When a graph test fails mid-graph, `get_state_history(config)` returns every
checkpoint — you can replay from any point by passing its `config.checkpoint_id`
back into `graph.invoke`. See
[LangGraph Test Patterns](references/langgraph-test-patterns.md) for the full
time-travel debugging recipe and the subgraph-shared-state test pattern
(cross-ref `langchain-langgraph-subgraphs` / pain L30).

## Resources

- [LangChain Python: testing guide](https://python.langchain.com/docs/contributing/testing/)
- [`FakeListChatModel` API](https://python.langchain.com/api_reference/core/language_models/langchain_core.language_models.fake.FakeListChatModel.html)
- [`vcrpy` documentation](https://vcrpy.readthedocs.io/)
- [`pytest-recording`](https://pytest-vcr.readthedocs.io/)
- LangGraph `MemorySaver` + `get_state_history`
- [Pytest `filterwarnings`](https://docs.pytest.org/en/stable/how-to/capture-warnings.html)
- Pack pain catalog: `docs/pain-catalog.md` (entries P05, P43, P44, P45)

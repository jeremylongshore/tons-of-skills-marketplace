---
name: langchain-ci-integration
description: "Wire LangChain 1.0 / LangGraph 1.0 tests into a GitHub Actions pipeline\
  \ \u2014\nunit tests with FakeListChatModel, VCR-gated integration tests, warning-filter\n\
  policy, and eval-regression merge gates. Complements langchain-local-dev-loop\n\
  (F23) which covers the inner loop; THIS covers the CI wire-up. Use when setting\n\
  up GHA for a new LLM service, after a VCR cassette leak incident, or hardening\n\
  an existing pipeline.\nTrigger with \"langchain ci\", \"langchain github actions\"\
  , \"langchain test pipeline\",\n\"vcr ci\", \"langchain eval gate\", \"pytest -W\
  \ error langchain\".\n"
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(pytest:*)
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- ci
- github-actions
- testing
compatibility: Designed for Claude Code
---
# LangChain CI Integration (Python)

## Overview

A PR passes every test on your laptop. You push. GHA runs `pytest` and aborts
during collection — before a single test executes — with:

```
PytestUnraisableExceptionWarning: Exception ignored in: ...
DeprecationWarning: langchain_community.llms ...
```

The org runs `pytest -W error` and a provider SDK emitted a `DeprecationWarning`
at *import* time, which the warning filter promoted to an exception while pytest
was still walking the test tree. This is **P45** and it blocks every PR for the
team until someone pins a `filterwarnings` config.

Meanwhile the integration suite has its own failure mode: a VCR cassette
recorded three months ago at `temperature=0` against Anthropic is now flaking
against a snapshot. `temperature=0` is not deterministic on Claude — it still
nucleus-samples (**P05**) — so the cassette captured *one* valid completion, not
*the* valid completion. And yesterday a reviewer caught
`Authorization: Bearer sk-ant-...` in a cassette file that had been committed
six weeks ago (**P44**) because `vcrpy` records all request headers by default.

This skill covers the outer loop: the GitHub Actions workflow, the unit /
integration / eval gate separation, VCR cassette hygiene, pytest warning
policy, and a merge-blocking eval regression gate. The **inner** loop — fake
model fixtures, VCR recording workflow, local determinism tricks — lives in
`langchain-local-dev-loop` (F23); cross-reference it, do not duplicate it.
Pin: `langchain-core 1.0.x`, `langgraph 1.0.x`, `actions/checkout@v4`,
`actions/setup-python@v5`, `vcrpy 6.x`. Pain-catalog anchors: **P05, P43, P44, P45**.

## Prerequisites

- Python 3.10, 3.11, or 3.12 (matrix)
- `langchain-core >= 1.0, < 2.0`, `langgraph >= 1.0, < 2.0`
- `pytest >= 8`, `pytest-asyncio`, `vcrpy >= 6` (integration)
- `langchain-local-dev-loop` (F23) applied locally — fixtures and recording workflow
- GitHub repo with Actions enabled; secrets set for any live-API nightly job

## Instructions

### Step 1 — GHA workflow skeleton with four jobs

Single workflow at `.github/workflows/tests.yml`. Matrix on unit only; keep
integration and eval single-version to control cost.

```yaml
name: tests

on:
  pull_request:
  push:
    branches: [main]
  schedule:
    - cron: "0 6 * * *"  # nightly live-API re-record check (06:00 UTC)

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  unit:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
          cache: pip
          cache-dependency-path: |
            pyproject.toml
            requirements*.txt
      - run: pip install -e ".[test]"
      - run: pytest tests/unit/ -W error --timeout=30 -q

  integration:
    needs: unit
    if: github.event_name == 'schedule' || contains(github.event.pull_request.labels.*.name, 'run-integration')
    runs-on: ubuntu-latest
    env:
      RUN_INTEGRATION: "1"
      VCR_MODE: "none"  # replay-only; nightly cron flips to "once"
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }
      - run: pip install -e ".[test,integration]"
      - run: pytest tests/integration/ -W error --timeout=60 -q

  eval:
    needs: unit
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }   # need base ref for delta comparison
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }
      - run: pip install -e ".[test,eval]"
      - run: python scripts/run_eval.py --baseline origin/${{ github.base_ref }} --head HEAD --n 100
      # run_eval.py posts a PR comment and exits nonzero on regression > threshold

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: python scripts/dryrun_load_chains.py   # catches ImportError migration regressions
```

See [GHA Workflow Reference](references/github-actions-workflow.md) for the full
job definitions including the secret-injection pattern, the matrix caching
nuance, and the `softprops/action-gh-release`-style PR comment action used by
the eval job.

### Step 2 — Unit job: `-W error` + `filterwarnings` to neutralize P45

Root cause of the collection abort: pytest collects tests by importing them.
Some provider SDKs emit `DeprecationWarning` on import. With `-W error` those
become exceptions during collection. Fix at the *filter* level, not by dropping
`-W error` (which would mask real warnings).

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
filterwarnings = [
    "error",
    # P45 — neutralize known import-time noise; scoped per module so new
    # warnings from YOUR code still fail the build.
    "ignore::DeprecationWarning:langchain_community.*",
    "ignore::DeprecationWarning:pydantic.*",
    "ignore:Pydantic serializer warnings:UserWarning",
]
asyncio_mode = "auto"
testpaths = ["tests"]
```

The ordering matters — `"error"` first, specific `"ignore"` entries after, so
the filters override the global promote-to-error. Keep the list **narrow**: a
blanket `ignore::DeprecationWarning` hides regressions you need to see.

Unit tests use `FakeListChatModel` fixtures from F23 (do not redefine them
here). One CI-specific gotcha (**P43**): `FakeListChatModel` does not emit
`response_metadata["token_usage"]`, so any callback that asserts on token counts
will break. Either subclass the fake and inject `generation_info`, or gate the
assertion:

```python
def test_chain_uses_tokens(patched_chat_model):
    result = chain.invoke({"input": "hi"})
    if patched_chat_model.__class__.__name__ == "FakeListChatModel":
        pytest.skip("fake model doesn't emit token_usage (P43)")
    assert result.response_metadata["token_usage"]["total_tokens"] > 0
```

Budget: unit job should finish in **<2 minutes** across the 3-version matrix.
If it doesn't, something is calling out to a real provider — check with
`pytest --collect-only -q | wc -l` and audit which tests lack fake-model
fixtures.

### Step 3 — Integration job: VCR replay + `filter_headers` (P44)

Integration tests replay pre-recorded VCR cassettes. Three rules:

1. Gate the job. `if: contains(github.event.pull_request.labels.*.name, 'run-integration')` or `env.RUN_INTEGRATION == "1"`, plus a nightly cron that flips to `VCR_MODE=once` and re-records against live APIs. PRs default to pure replay.
2. Enforce `filter_headers` at the fixture level — not per-test. A single `conftest.py` prevents any contributor from recording a cassette with raw credentials.
3. Pre-commit + CI both scan cassettes for leaked keys. Belt and suspenders.

Fixture (lives in `tests/integration/conftest.py`, owned by this skill's
pipeline concern — F23 owns the *recording* workflow):

```python
import vcr
import pytest

@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            "authorization",
            "x-api-key",
            "anthropic-version",
            ("openai-organization", "REDACTED"),
        ],
        "filter_post_data_parameters": ["api_key"],
        "record_mode": "none",  # CI default: replay only
        "match_on": ["method", "scheme", "host", "port", "path", "query"],
    }
```

Integration suite must finish in **<5 minutes** wall-clock on the runner, or
you will start getting cancellation flakes from the `concurrency` block. If
you exceed 5 minutes, split into a nightly-only long tier.

See [Integration Gating](references/integration-gating.md) for the full
live-vs-replay decision tree, cost-per-run budget worksheet, and the
`VCR_MODE` flip pattern.

### Step 4 — Eval-regression gate: merge-blocking PR comment

The eval job runs the `langchain-eval-harness` harness (see that skill for the
harness itself — this skill only covers the CI wire-up) against both the PR
branch and the merge base. Post a comment; block merge on regression.

`scripts/run_eval.py` is a thin CI wrapper: check out baseline and head via
`git worktree`, run the harness at each ref, diff the results, post a PR
comment, exit nonzero on regression. Full implementation in
[Eval Regression Gate](references/eval-regression-gate.md).

Thresholds:

| Gate | Threshold | Rationale |
|------|-----------|-----------|
| Aggregate score | drop >2% | One-sigma noise on n=100 with well-behaved evals |
| Per-example score | drop >5% on any single case | Catches quiet regressions masked by aggregate averaging |
| Sample size floor | n ≥ 100 | Below this, aggregate delta is dominated by noise |

The PR comment is a Markdown table with `before / after / Δ` per metric plus a
**bold red** line if the gate failed. Required-status-check on the `eval` job
completes the enforcement. See [Eval Regression Gate](references/eval-regression-gate.md)
for the comment template and the noise-budget calculation.

### Step 5 — Pre-commit hooks: secret scan + prompt lint

Two layers: local (pre-commit) and CI (re-runs the same hooks as a final
catch). Local alone is not sufficient — contributors can skip with `-n`. CI
alone is slow. Run both.

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: vcr-secret-scan
        name: VCR cassette secret scan (P44)
        entry: python scripts/scan_cassettes.py
        language: system
        files: "tests/integration/cassettes/.*\\.ya?ml$"
        pass_filenames: true

      - id: prompt-convention-lint
        name: prompt-convention lint
        entry: python scripts/lint_prompts.py
        language: system
        files: "prompts/.*\\.j2$|src/.*prompts?\\.py$"

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
```

`scan_cassettes.py` greps for `sk-[A-Za-z0-9]{20,}`, `sk-ant-[A-Za-z0-9_-]{20,}`,
`AIza[A-Za-z0-9_-]{35}` (Google), `xoxb-`, and `Bearer [A-Za-z0-9._-]{20,}`.
Fail on any match. This is your last line of defense before **P44** ships to
`main`. See [Pre-Commit Hooks](references/pre-commit-hooks.md) for the full
pattern list, the prompt-convention lint rules (aligned with
`claude-prompt-conventions`), and the `detect-secrets` baseline-rotation policy.

### Step 6 — Dry-run chain loader: catch ImportError migration breaks

LangChain 0.x → 1.0 moved integrations into provider packages. A chain that
imports `from langchain.chat_models import ChatOpenAI` works in local dev if
you still have the old compat shim installed, and explodes in CI. Dry-run-load
every chain module at lint time:

```python
# scripts/dryrun_load_chains.py
import importlib, pathlib, sys, traceback

failures = []
for py in pathlib.Path("src/chains").rglob("*.py"):
    mod = str(py.with_suffix("")).replace("/", ".")
    try:
        importlib.import_module(mod)
    except Exception:
        failures.append((mod, traceback.format_exc()))

if failures:
    for mod, tb in failures:
        print(f"::error::chain {mod} failed to import\n{tb}")
    sys.exit(1)
```

Runs in the `lint` job. Costs ~5 seconds. Catches every `ImportError` and
every top-level `NameError` from a bad rename before a single unit test fires.

## Output

- GHA workflow with four isolated jobs (unit / integration / eval / lint)
- `pyproject.toml` `filterwarnings` config that survives `-W error` (P45)
- VCR `conftest.py` fixture with enforced `filter_headers` (P44)
- `run_eval.py` CI wrapper that posts PR comments and blocks merge on regression
- `.pre-commit-config.yaml` with cassette secret scan + prompt lint + ruff
- Dry-run chain loader that catches migration `ImportError`s

### Gate policy

| Gate | Required? | Target speed | On failure |
|------|-----------|--------------|------------|
| unit (3 Python versions) | yes, every PR | <2 min | block PR |
| lint + dryrun-load | yes, every PR | <30 s | block PR |
| integration (VCR replay) | on `run-integration` label or nightly | <5 min | block merge when run |
| integration (live, nightly cron) | no | <15 min | open issue on fail |
| eval regression (n≥100) | yes, every PR | <10 min | block merge if agg >2% or per-example >5% |
| pre-commit (local) | yes | <10 s | reject commit |

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `PytestUnraisableExceptionWarning` during collection | `-W error` + SDK import-time `DeprecationWarning` (P45) | Add scoped `filterwarnings = ["ignore::DeprecationWarning:langchain_community.*"]` to `pyproject.toml` |
| VCR replay mismatch after weeks of passing | Cassette recorded at `temp=0` on Anthropic (P05); model drift | Re-record on nightly cron with `VCR_MODE=once`; treat replay mismatches as eval-gate concerns, not unit failures |
| `sk-ant-...` in cassette flagged by reviewer | `vcrpy` records all headers by default (P44) | Enforce `filter_headers` in `conftest.py`; add `scan_cassettes.py` to pre-commit AND CI |
| Callback `AssertionError: 'token_usage' not in response_metadata` | `FakeListChatModel` doesn't emit metadata (P43) | Subclass the fake to inject `generation_info`, or `pytest.skip` on fake-model detection |
| `ImportError: cannot import name 'ChatOpenAI' from 'langchain.chat_models'` in CI only | Legacy compat shim installed locally, not in CI | Add `dryrun_load_chains.py` to lint job; fail at lint, not at test |
| Eval job times out at 10 min | n too large or harness not using `asyncio` concurrency | Cap at n=100 for PRs; run n=500 nightly; see F23 for async harness pattern |
| Concurrency block cancels integration run | Long job + rapid pushes | Do not disable; keep integration <5 min or split long tier to nightly |

## Examples

### Wiring a new repo from scratch

Copy the Step 1 workflow, the Step 2 `pyproject.toml` block, and the Step 5
pre-commit config. Create `tests/unit/`, `tests/integration/cassettes/`,
`scripts/run_eval.py`, `scripts/dryrun_load_chains.py`,
`scripts/scan_cassettes.py`. Apply `langchain-local-dev-loop` (F23) first so
fake-model fixtures exist before the unit job runs. Enable required status
checks: `unit (3.10)`, `unit (3.11)`, `unit (3.12)`, `lint`, `eval`.
Integration stays optional (label-gated).

See [GHA Workflow Reference](references/github-actions-workflow.md) for the
complete copy-pasteable workflow.

### Hardening after a P44 cassette-leak incident

Rotate every leaked key **first** (not a CI concern — incident response).
Then: add `scan_cassettes.py` to pre-commit, re-scan the full history with
`git log -p -- tests/integration/cassettes/`, rewrite history with
`git-filter-repo` if keys hit `main`, enforce the `filter_headers` fixture
going forward. See [Pre-Commit Hooks](references/pre-commit-hooks.md) for the
full pattern list and the `detect-secrets` baseline-rotation playbook.

### Wiring the eval harness into an existing repo

The harness itself lives in `langchain-eval-harness`. THIS skill only supplies
`run_eval.py` (the CI wrapper that reads the harness output, computes deltas,
and posts PR comments) plus the gate thresholds. Drop in the Step 4 script,
add the `eval` job to `.github/workflows/tests.yml`, make `eval` a required
status check. See [Eval Regression Gate](references/eval-regression-gate.md)
for the PR-comment Markdown template and the n≥100 noise-budget derivation.

## Resources

- [LangChain Python: Testing](https://python.langchain.com/docs/how_to/testing/)
- [`FakeListChatModel` API](https://python.langchain.com/api_reference/core/language_models/langchain_core.language_models.fake_chat_models.FakeListChatModel.html)
- [vcrpy docs — filtering sensitive data](https://vcrpy.readthedocs.io/en/latest/advanced.html#filter-sensitive-data-from-the-request)
- [GitHub Actions docs](https://docs.github.com/en/actions)
- [pytest `filterwarnings`](https://docs.pytest.org/en/stable/how-to/capture-warnings.html)
- Pair skill: `langchain-local-dev-loop` (F23) — fake fixtures, local recording
- Pair skill: `langchain-eval-harness` — eval suite the gate runs against
- Pack pain catalog: `docs/pain-catalog.md` (entries P05, P43, P44, P45)

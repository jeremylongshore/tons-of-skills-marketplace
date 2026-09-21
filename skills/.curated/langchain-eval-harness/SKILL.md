---
name: langchain-eval-harness
description: "Build reproducible evaluation pipelines for LangChain 1.0 chains and\
  \ LangGraph 1.0\nagents \u2014 golden datasets, LangSmith evaluate(), ragas RAG\
  \ metrics, deepeval\nLLM-as-judge, agent trajectory analysis, and CI gating on quality\
  \ regressions.\nUse when setting up quality measurement for a new chain, diagnosing\
  \ regression\nafter a model switch, or building an evaluation gate for a pull request.\n\
  Trigger with \"langchain eval\", \"langsmith evaluate\", \"ragas\", \"llm-as-judge\"\
  ,\n\"agent trajectory eval\", \"eval regression gate\".\n"
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(pip:*), Bash(pytest:*)
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- evaluation
- langsmith
- ragas
- deepeval
- research
compatibility: Designed for Claude Code
---
# LangChain Eval Harness (Python)

## Overview

A team swapped `gpt-4o` for `claude-sonnet-4-6` to save money and a week later CS
noticed answer quality dropped on 15% of refund tickets — the regression was
invisible in code review and invisible in CI because no golden set existed.

Fix: a versioned golden set, a stacked eval pipeline (LangSmith +
ragas + deepeval + custom trajectory), and a PR-blocking regression gate
with paired Wilcoxon significance. The tooling exists; the patterns for
wiring it into a statistically honest loop are scattered across five doc sites.

Build a 100-example JSONL golden set, wire LangSmith `evaluate()` with a
custom correctness evaluator, add a ragas quartet (faithfulness, answer
relevance, context precision/recall) for RAG, add deepeval LLM-as-judge
with N=3 judge quorum, score LangGraph trajectories on coverage/precision/
order, and gate PRs on a 2% aggregate drop or 5% per-example drop. Pin:
`langchain-core 1.0.x`, `langgraph 1.0.x`, `langsmith>=0.2`, `ragas>=0.2`,
`deepeval>=2.0`. Pain-catalog anchors: P01, P11, P12, P22, P33.

## Prerequisites

- Python 3.10+
- `langchain-core >= 1.0, < 2.0`, `langgraph >= 1.0, < 2.0` for the system under eval
- `pip install langsmith>=0.2 ragas>=0.2 deepeval>=2.0 scipy`
- LangSmith account + `LANGSMITH_API_KEY` (free tier is sufficient for dataset versioning)
- Provider API keys for the judge LLM: `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY`

## Instructions

### Step 1 — Build a versioned golden set

Format: JSONL, one example per line, with a `dataset_version` tag. Minimum 20
examples to start; grow to 100 for PR gating, 200+ for absolute-metric claims.

```python
# evals/golden_set/v2026.04.jsonl
{"id": "gs-0001", "input": "Refund policy for SKU ABC-42?", "expected": "30 days with receipt", "contexts": ["policy_v3.md"], "tags": ["refund"], "difficulty": "easy", "dataset_version": "2026.04"}
{"id": "gs-0002", "input": "Return policy for opened software?", "expected": "No, opened software is final sale", "contexts": ["policy_v3.md#returns"], "tags": ["refund"], "difficulty": "medium", "dataset_version": "2026.04"}
```

Sample from real traffic (redacted), not imagination. Stratify by tag and
difficulty (aim for 30% hard). Two annotators per example, disagreements
reconciled — reconciliation rate under 90% means your task definition is
ambiguous. Treat the file as immutable within a version; bump the version
to refresh. See [Golden Set Curation](references/golden-set-curation.md) for
sourcing strategy, annotation tool options, and the refresh cadence.

### Step 2 — Wire LangSmith `evaluate()` with a custom evaluator

```python
from langsmith import Client
from langsmith.evaluation import evaluate, EvaluationResult
from langchain_anthropic import ChatAnthropic

client = Client()
DATASET_VERSION = "2026.04"

# One-time: upload golden set as a versioned dataset
def upload_golden_set(jsonl_path, dataset_name):
    examples = [json.loads(line) for line in open(jsonl_path)]
    client.create_dataset(dataset_name)
    client.create_examples(
        inputs=[{"input": e["input"]} for e in examples],
        outputs=[{"expected": e["expected"]} for e in examples],
        metadata=[{"id": e["id"], "tags": e["tags"]} for e in examples],
        dataset_name=dataset_name,
    )

chain = ChatAnthropic(model="claude-sonnet-4-6", temperature=0, timeout=30)

def target(inputs):
    return {"answer": chain.invoke(inputs["input"]).content}

def correctness(outputs, reference_outputs):
    """Deterministic exact-match floor — baseline, not ceiling."""
    match = outputs["answer"].strip().lower() == reference_outputs["expected"].strip().lower()
    return EvaluationResult(key="exact_match", score=float(match))

results = evaluate(
    target,
    data=f"golden-set-v{DATASET_VERSION}",
    evaluators=[correctness],
    experiment_prefix="refund-bot-v3",
    max_concurrency=10,   # Avoid 429s on judge LLM (P22)
)
```

Free-form outputs need semantic scoring (ragas, deepeval, or LLM-as-judge — Step 4).

### Step 3 — Add ragas metrics for RAG pipelines

For a RAG chain returning `{answer, contexts}`, ragas scores four standard
dimensions. The default judge is `gpt-4o-mini`; override to pin model +
cost:

```python
from ragas import evaluate as ragas_evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from datasets import Dataset

judge = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embed = OpenAIEmbeddings(model="text-embedding-3-small")

# Prepare rows — ragas wants HuggingFace Dataset shape
rows = []
for ex in golden_examples:
    result = rag_chain.invoke({"question": ex["input"]})
    rows.append({
        "question": ex["input"],
        "answer": result["answer"],
        "contexts": [d.page_content for d in result["source_documents"]],
        "ground_truth": ex["expected"],
    })

ragas_results = ragas_evaluate(
    Dataset.from_list(rows),
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    llm=judge,
    embeddings=embed,
)
# ragas_results is a dict of per-metric means; call .to_pandas() for per-row
```

Do not use ragas on non-RAG chains — `context_precision` against an empty
context list returns 0 and looks like a regression. See
[Framework Comparison](references/framework-comparison.md) for when each
tool fits.

### Step 4 — Add deepeval LLM-as-judge for free-form outputs

deepeval is pytest-shaped — each example is an `LLMTestCase` asserting against
metrics. Run N=3 judge invocations per example and take the median to tame
LLM-as-judge variance (±5-15% across runs; single-run scores are not CI-ready):

```python
import statistics
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

def eval_with_quorum(test_case, metric, n=3):
    scores = []
    for _ in range(n):
        metric.measure(test_case)
        scores.append(metric.score)
    return statistics.median(scores), statistics.stdev(scores) if n > 1 else 0.0

correctness = GEval(
    name="Correctness",
    criteria="Does the actual output match the expected output in meaning?",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    model="gpt-4o-mini",
)

for ex in golden_examples:
    result = chain.invoke({"input": ex["input"]})
    case = LLMTestCase(input=ex["input"], actual_output=result, expected_output=ex["expected"])
    median, sd = eval_with_quorum(case, correctness, n=3)
    if sd > 0.2:  # judge disagreeing with itself — flag, don't gate
        flag_for_review(ex["id"], median, sd)
```

### Step 5 — LangGraph agent trajectory eval

For agents, final-answer correctness misses the process. Score the tool-call
sequence on three axes — coverage (did required tools run?), precision
(were extra tools used?), and order (Kendall's tau on shared tools):

```python
from langchain_core.messages import AIMessage

def extract_trajectory(final_state: dict) -> list[dict]:
    return [
        {"tool": tc["name"], "args": tc["args"]}
        for msg in final_state["messages"] if isinstance(msg, AIMessage)
        for tc in (msg.tool_calls or [])
    ]

def trajectory_score(expected: list[str], actual: list[str]) -> dict:
    e_set, a_set = set(expected), set(actual)
    coverage = len(e_set & a_set) / len(e_set) if e_set else 1.0
    precision = len(e_set & a_set) / len(a_set) if a_set else 0.0
    shared = [t for t in actual if t in e_set]
    order = _kendall_tau(expected, shared) if len(shared) >= 2 else 1.0
    return {"coverage": coverage, "precision": precision, "order": order}

# Composite: 0.5 * coverage + 0.3 * precision + 0.2 * order
```

Set `temperature=0` for the agent during eval — `temperature > 0` produces
different trajectories across runs (P11) and makes paired comparison
statistically invalid. See [Agent Trajectory Eval](references/agent-trajectory-eval.md)
for args-level matching, efficiency/safety scoring, and the LLM-as-judge
fallback for non-deterministic trajectories.

### Step 6 — Gate PRs on regression

A PR touching prompts, chain code, or model config runs the eval suite on
PR branch and `main`, then blocks merge on any of: aggregate mean drop > **2.0%**,
any single-example drop > **5.0%**, or paired Wilcoxon signed-rank p < 0.05
with negative mean delta.

```python
from scipy.stats import wilcoxon

def paired_regression_check(baseline, candidate, alpha=0.05):
    """Wilcoxon — right test when metric distribution is non-normal (most LLM metrics)."""
    n = len(baseline)
    if n < 50:
        return {"verdict": "too_small_n", "n": n}
    diffs = [c - b for b, c in zip(baseline, candidate)]
    _, p = wilcoxon(diffs, alternative="less")
    return {"n": n, "mean_delta": sum(diffs) / n, "p_value": float(p),
            "regression": p < alpha and sum(diffs) < 0}
```

At n=100 and α=0.05 this detects a ~3-5% true regression at ~80% power. See
[CI Integration](references/ci-integration.md) for the GitHub Actions workflow,
PR-comment delta table, bootstrap CI, and spend/rate-limit safety rails.

## Output

- JSONL golden set at `evals/golden_set/v2026.04.jsonl` with an immutable version tag
- LangSmith dataset uploaded and versioned; experiment runs linked to traces
- Ragas scores (faithfulness, answer relevance, context precision/recall) on RAG chains
- Deepeval `LLMTestCase` assertions in pytest, with median-of-3 judge quorum
- LangGraph trajectory scores (coverage, precision, order) with composite summary
- GitHub Actions workflow gating PRs on 2% aggregate / 5% per-example / Wilcoxon p < 0.05
- PR-comment delta table posted on every eval run

## Framework selection at a glance

| Use case | LangSmith | ragas | deepeval | Custom |
|---|---|---|---|---|
| RAG metrics (faithfulness, context recall) | — | **Primary** | Fallback | — |
| Pytest-style assertion in CI | Secondary | — | **Primary** | — |
| Trace capture + dataset versioning | **Primary** | Complementary | Complementary | — |
| Agent trajectory (tool-call sequence) | Secondary (traces) | — | — | **Primary** |
| Exact match / JSON schema / structured output | — | — | — | **Primary** |
| Free-form paraphrase scoring | Via custom evaluator | — | **Primary (G-Eval)** | — |

Most real pipelines stack two or three. The anti-pattern is running all four
on every example — you pay $10-30 per run for signal you are not using. See
[Framework Comparison](references/framework-comparison.md) for the full
decision tree and dependency weight comparison.

## Error Handling

| Error / Failure mode | Cause | Fix |
|---|---|---|
| `TimeoutError` on eval runs > 20 min | Long agent trajectories on slow models; 100 examples × 30s each exceeds default GH Actions job timeout | Cap `max_concurrency=10`, use `asyncio.gather` with `asyncio.Semaphore`, split eval into sharded jobs |
| Judge disagreement (stdev > 0.2 on [0,1] scale across N=3 runs) | LLM-as-judge variance on ambiguous examples | Flag example for manual review; do not use that row's score for gating |
| `ValidationError: missing 'contexts'` in ragas | Chain does not return retrieved docs | Modify chain to surface `source_documents`, or switch to non-RAG evaluator |
| Wilcoxon p-value is NaN | All paired diffs are 0 (identical outputs) | Expected when the PR did not change behavior — no regression, skip the stat test |
| LangSmith 429 rate limit during upload | > 50 examples/sec to `create_examples` | Batch with `client.create_examples(..., batch_size=20)` and sleep between batches |
| Spend overrun ($50+ per run) | Judge calls scaling with `N_examples × N_metrics × N_judge_runs` | Use `gpt-4o-mini` not `gpt-4o` for judge; cache per `(dataset_version, chain_version)` |
| `AttributeError: 'list' has no attribute 'lower'` in custom evaluator | Claude `AIMessage.content` is `list[dict]` not `str` (P02 — see langchain-model-inference) | Use `msg.text()` or iterate content blocks |
| Trajectory comparison drifts week-over-week on unchanged agent | `temperature > 0` non-determinism (P11) | Set `temperature=0` for all eval runs; pin `seed` where supported |

## Examples

### Setting up eval for a new RAG chain

Start with 20 production-sampled golden examples, wire up `ragas_evaluate`
with four metrics, record scores to `evals/baselines/` as the reference,
and promote to LangSmith dataset versioning once two engineers annotate in
parallel. See [Golden Set Curation](references/golden-set-curation.md).

### Diagnosing regression after a model swap

Run the main-branch chain on the golden set, then swap the model and rerun.
Diff per-example scores sorted by delta — the top-10 regressions usually
cluster by tag (long contexts, one-shot lookups). Report paired Wilcoxon
and per-tag breakdown before deciding to ship. See [CI Integration](references/ci-integration.md).

### Evaluating a LangGraph tool-calling agent

Record expected tool-call sequences for 50 tasks, capture actual trajectories
via `extract_trajectory`, and score on coverage/precision/order. Composite
drops indicate a policy change — diff sequences to find the drift. See
[Agent Trajectory Eval](references/agent-trajectory-eval.md).

## Resources

- [LangSmith evaluation tutorial](https://docs.smith.langchain.com/evaluation/tutorials/evaluation)
- [LangSmith `evaluate()` reference](https://docs.smith.langchain.com/reference/python/sdk_reference/langsmith.evaluation)
- [ragas metrics overview](https://docs.ragas.io/en/latest/concepts/metrics/overview/)
- [deepeval metrics reference](https://docs.confident-ai.com/docs/metrics-introduction)
- [scipy Wilcoxon signed-rank](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html)
- [G-Eval variance paper](https://arxiv.org/abs/2303.16634)
- Pack pain catalog: `docs/pain-catalog.md` (entries P01, P11, P12, P22, P33)

---
name: langfuse-experiment-guardian
description: |
  Compare Langfuse experiment baseline and candidate results at case level using
  reviewed dataset, content and evaluator identities. Detect missing cases,
  evaluator errors and critical regressions before proposing a release. Use when reviewing these cases. Trigger with
  "Langfuse experiment passed on average", "candidate lost evaluation cases" or
  "can this experiment replace our reviewed baseline?".
allowed-tools: Read, Bash(python3:*)
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [langfuse, experiments, evaluation, regression, release-review]
compatibility: Python 3.10+ standard library; SDK result projection is an optional local JavaScript module for the documented Langfuse client 6.0.2 result shape.
argument-hint: '[experiment-comparison.json]'
---

# Langfuse Experiment Guardian

## Overview

Determine whether a candidate meets a reviewed case-level release policy against
an explicit baseline. An average score cannot hide missing cases, failed tasks,
evaluator omissions or a critical regression. The tool compares supplied
evidence; it does not run an experiment, judge model output or release anything.

## Prerequisites

- The reviewed baseline run identity and review reference; never choose the
  newest run automatically.
- Project, dataset/version and required case manifest with content hashes and
  explicit critical-case classifications.
- Versioned evaluators, score ranges, threshold directions and release policy.
- Complete baseline/candidate item evidence with task status and collection
  completeness, mapped using the [receipt contract](references/receipt-contract.md).
- Python 3.10+ and authorized access to the supplied private evaluation data.

Offline comparison needs no authentication or model credentials. Do not start a
paid evaluator or provider call to fill missing evidence during this workflow.

## Instructions

### Step 1: Establish the release question

Name the proposed change and exact baseline/candidate identities. Record the
dataset snapshot, case content, evaluator versions and configuration that make
the comparison meaningful. Same dataset name or aggregate score is insufficient.
If identities or policy are missing, return inconclusive and request the gap.

### Step 2: Preserve item-level evidence

Read the [contract](references/receipt-contract.md) to retain each required case's
identity/hash, task outcome and evaluator observations. Missing scores stay
missing; do not replace them with zero, success or an average. Preserve errored,
unfinished and omitted items. Mark incomplete exports explicitly.

For an existing JavaScript SDK result, the contract documents the optional
`scripts/project-result.mjs` module. It extracts an allowlisted projection without
copying inputs, outputs or evaluator comments. Do not call the experiment again
to obtain a fresh result. Optional task capture must be integrated deliberately
in separately authorized work, not retroactively claimed as execution evidence.

### Step 3: Apply the reviewed policy

```sh
python3 scripts/compare.py private-experiment-comparison.json
```

Run relative to this skill's directory. Choose the policy explicitly:
`all-required` requires passing candidate evidence for required evaluations;
`preserve-baseline-passes` additionally preserves reviewed baseline successes
while handling only explicitly reviewed baseline-failure exceptions. Follow the
contract rather than inventing exception records.

An exception needs an exact case/evaluator target and review reference. Critical
candidate failure is never waived by this comparison. Do not change thresholds,
critical flags, hashes or expected cases simply to make the gate pass.

### Step 4: Assess comparability before success

Inspect project/dataset/version, manifest hashes, evaluator definitions,
duplicate cases, completion and task states before interpreting numeric scores.
An empty result or non-comparable comparison is not a passing release gate.

Separate candidate regressions from pre-existing baseline failures and
inconclusive evidence. The script's known input contract does not authenticate
the source, establish evaluator validity or prove that the benchmark represents
production traffic. Keep those limitations in the review.

### Step 5: Return the release finding

Give the explicit policy result, affected case/evaluator references privately,
critical blockers, incomplete evidence and smallest next check. Preserve the
script's actual status and exit code. A passing comparison can support an owner
decision; it is not deployment authority or a production-quality certificate.

## Output

Return `langfuse-experiment-comparison.json` and a short supplied-data ledger:
reviewed identities and policy, comparable/inconclusive state, case-level
regressions, critical blockers, exceptions and unresolved evidence. Keep raw
prompts, generated text, evaluator comments and secrets out of the shared report.

## Examples

- **Average improved, critical case failed:** retain the critical blocker and
  reject release readiness under the reviewed policy.
- **One evaluator result disappeared:** report missing evaluation evidence;
  an omitted score cannot inherit the baseline's passing result.
- **Baseline itself had a reviewed failure:** handle only the exact allowed
  exception under the chosen policy, preserving critical-case requirements.
- **Candidate used a changed case input:** report non-comparability rather than
  treating the same display ID as an identical test.

## Error Handling

Malformed or oversized receipts exit 2 with a fixed held code. Non-passing
comparisons exit 1; preserve failed and inconclusive distinctions in the JSON.
Do not rerun business tasks or paid evaluators automatically. Missing SDK task
capture remains unknown rather than being inferred from a produced output.

## Resources

- [Receipt, policy and SDK projection contract](references/receipt-contract.md).
- [Experiment comparison authority](https://langfuse.com/docs/evaluation/experiments/compare-experiments).
- [Evaluation specification](eval-spec.yaml): reviewed cases, not a completed behavioral run.

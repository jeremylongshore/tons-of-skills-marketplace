# Experiment comparison receipts

This is an owned normalized evidence format, not a Langfuse response schema.
The analyzer consumes supplied receipts without executing tasks, contacting a
provider, creating scores, or changing a baseline. A supplied approval reference
is evidence to review; the script does not authenticate an approver.

## Required evidence

The top-level object has integer `schema_version: 1`, `policy`, `baseline`, and
`candidate`. Unknown fields are ignored and are not echoed in the result.

The policy records:

| Field                                         | Contract                                                                                                                                  |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `project_id`, `dataset_id`, `dataset_version` | Nonempty, recorded identities. For local datasets, use an immutable dataset manifest identity and version.                                |
| `baseline_run_id`, `baseline_review_ref`      | Exact reviewed baseline and its approval record. Do not silently adopt the latest run.                                                    |
| `mode`                                        | `all-required` or `preserve-baseline-passes`.                                                                                             |
| `expected_cases`                              | Nonempty array of `case_id`, `content_sha256`, and boolean `critical`. Include every required case, including cases with missing results. |
| `evaluators`                                  | Nonempty array of `name`, `version`, numeric `minimum`, `maximum`, `threshold`, and `direction` (`higher` or `lower`).                    |
| `accepted_baseline_failures`                  | Optional array of exact `case_id`, `evaluator`, and `review_ref` exceptions, valid only in preserve mode.                                 |

Keep case identifiers stable across runs. Generate `content_sha256` from the
same recorded canonical representation of each case's input, expected
output, and task-relevant metadata. Retain that representation and hash procedure with the private dataset
manifest. A changed expected output changes the hash. Do not hash only the ID,
copy an old hash onto changed data, or infer case identity from row position.
The analyzer checks supplied hashes against the manifest; it does not inspect
the original inputs or prove their hash derivation.

Each run records `run_id`, the same three project/dataset identity fields,
`application_ref`, `export_complete`, `evaluator_versions` (name to immutable
version), and a `cases` array. Baseline and candidate must be distinct runs.
Their application revisions may differ: that is the change being assessed.

Each case result has `case_id`, `content_sha256`, `task_state` (`ok`, `error`,
or `unknown`), and `evaluations`: an array of `name` and `value` pairs. Values
must be finite numbers or numeric strings within the declared range; booleans
are rejected. Map categorical results through a reviewed, versioned numeric
evaluator before using this comparator. Missing or null scores are unavailable,
not zero. Two selected scores with the same name are ambiguous and rejected.
Unselected evaluator results do not affect the decision.

## Mapping current SDK results

The published JS/TS client 6.0.2 `langfuse.experiment.run(...)` result includes
`experimentId`, `itemResults`, `runEvaluations`, and `runName`, plus optional hosted-run identifiers. Each
item result has `item`, `evaluations`, and `output`. Failed evaluators are
excluded from `evaluations`; an absent required evaluator must remain absent.
Do not substitute the aggregate `runEvaluations` for per-case results.

Project successful per-item `evaluations[].name` and `value` into the receipt.
Resolve case identity from the original dataset manifest or an explicitly
preserved local-case identifier. Record task success/failure at the application's
execution boundary; do not infer success from a nonempty score or output. Retain
SDK/version, application revision, dataset/evaluator versions, and completion
evidence alongside the original result. SDK result objects alone do not establish
all those facts. If a result was truncated, filtered, incompletely exported, or
cannot be reconciled with the manifest, set `export_complete` to false or null.

Use `scripts/project-result.mjs` from the application that already owns the SDK
result. Importing this module performs no task, provider, SDK, or filesystem call.
It imports only Node's built-in crypto module and needs Node 22+.

- `manifestCase(item, critical)` records a reviewed case ID and content hash from
  the actual dataset. Hosted cases use `item.id`; local cases require an explicit
  `item.metadata.guardian_case_id`. Conflicting IDs are rejected.
- `caseContentDigest(item)` hashes supplied `input`, `expectedOutput`, and `metadata`
  fields using UTF-16-sorted object keys and JSON-stringified scalar values. Missing
  and null fields differ. The encoder rejects cycles, accessors, custom object
  prototypes, nonfinite or unsafe integer numbers, and non-JSON values. Content is
  bounded to 2 MiB, depth 64, and 200,000 nodes. If task/evaluator behavior depends
  on other item fields, use a reviewed normalization layer that preserves those
  dependencies in metadata before constructing either manifest or result.
- `captureTask(task)` returns `{task, snapshot}`. Give its `task` function to an
  already-authorized experiment instead of the original callback. It calls that
  callback once per invocation, propagates its exact exception, and records only
  case identity, content hash, attempt count, and state. It does not retry. Take
  `snapshot()` after execution settles. Multiple invocations for one ID, incomplete
  execution, or changed content cannot establish a single successful execution.
- `projectResult(result, context, executionEvidence)` projects an existing result.
  Pass the snapshot as execution evidence. For an existing run without such a
  recorder, a reviewed equivalent sidecar must supply `case_id`, `content_sha256`,
  `attempts: 1`, and `state`. Without matching evidence the state is `unknown`.

The context supplies the three project/dataset identity fields, application
revision, evaluator versions, explicit completeness, and `sdk_version`. The
projector uses the SDK's `experimentId` as `run_id`; it never invents a run ID
from the display name. Optional dataset-run IDs must agree at run and item level.
In client 6.0.2, reusing a hosted dataset's run name can continue the same experiment;
that result cannot be treated as an independent candidate for its own baseline.

The projector intentionally omits run-level aggregates, raw content, comments,
URLs, trace IDs, and unselected result metadata. It limits normalized receipts
to 2 MiB each; the comparator's complete input pair must also fit its 2 MiB limit.
The projection and sidecar are not authenticated receipts. Neither proves the
stated project, approval, completeness, or absence of undisclosed retries.

This projection should omit raw inputs, expected answers, outputs, evaluator
comments, and credentials. Protect original experiment evidence according to the
application's data policy. The normalized receipt still contains business-sensitive
identifiers and scores; no upload or external delivery is authorized by this tool.

## Decision and exit status

Run `python3 scripts/compare.py receipt-pair.json` from the skill directory,
or pipe the JSON to stdin. Input is limited to 2 MiB. Duplicate JSON fields,
ambiguous case/score identities, nonfinite scores, and invalid policies are held
with exit 2 and a fixed error code. No raw parser/provider error is emitted.

- Exit 0: `pass` under the supplied policy, with complete comparable receipts.
- Exit 1: `fail` or `inconclusive`; inspect the decision and findings.
- Exit 2: invalid or unreadable evidence; no comparison was performed.

All-required mode requires every candidate case to pass every selected evaluator.
Preserve mode requires every previous pass to remain passing, each baseline failure
to have an exact reviewed exception, and every critical candidate case to pass.
An accepted historical failure never waives a critical candidate failure.

Incomplete evidence withholds numerical summaries. Complete summaries retain each
evaluator's required-case denominator and new-failure count; equal aggregate pass
rates do not hide a newly failing case. Findings include only hashed identifiers,
are limited to the first 100, and report the full finding count and truncation state.
The CLI binds its result to the exact input-byte SHA-256. It neither approves a
deployment nor establishes model determinism or production safety.

## Primary references

- [Compare experiments](https://langfuse.com/docs/evaluation/experiments/compare-experiments)
- [Experiments via SDK](https://langfuse.com/docs/evaluation/experiments/experiments-via-sdk)
- [ExperimentResult](https://js.reference.langfuse.com/types/_langfuse_client.ExperimentResult.html)
- [ExperimentItemResult](https://js.reference.langfuse.com/types/_langfuse_client.ExperimentItemResult.html)
- [Evaluation](https://js.reference.langfuse.com/types/_langfuse_client.Evaluation.html)

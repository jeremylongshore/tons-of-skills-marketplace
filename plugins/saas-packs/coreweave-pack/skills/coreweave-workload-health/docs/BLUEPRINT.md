# Workload and GPU evidence review: skill blueprint

> Community-contributed; not affiliated with, endorsed by, or sponsored by CoreWeave, Inc.

| Metadata | Value |
| --- | --- |
| Document ID / type | CW-S26-BLUEPRINT / integrated skill design |
| Schema / template version | Local design envelope 1.0 / Blueprint Docs 3.0.0, integrated selection 1.0 |
| Status | Implemented; offline acceptance reviewed; native-host permission acceptance remains open |
| Owner / decision authority | Jeremy Longshore, maintainer |
| Reviewers | Codex automated implementation/security review; no independent human review or certification claimed |
| Generated / updated / review date | 2026-11-05 / 2026-11-07 / on host-runtime validation or contract change |
| Classification | Public technical design; synthetic examples only |
| Sources | User-approved scope (provided); implementation and fixtures (verified offline); primary contract register in health-evidence.md |
| Assumptions | Supplied Pod/device mapping is trustworthy enough for review; it is not independently authenticated |
| Unknowns | Real account compatibility, production outcomes, actual per-skill demand |
| Related artifacts | [Skill issue #1845](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1845); parent #1732; [pack blueprint](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/eed0fd35d89838e5d8b4d78ce4786f8ea4df0dbe/plugins/saas-packs/coreweave-pack/docs/BLUEPRINT.md); SKILL.md and, where provided, eval-spec.yaml in this skill directory |
| Supersession | Additive design; existing PRD/ARD and historical evidence remain intact until explicit reconciliation |

## Objective and scope

**OBJ-CW-S26-1 (provided objective; derived problem framing):** Pod readiness alone does not prove that the intended workload is actually using its allocated GPUs.

Audience: the platform operator responsible for this specific outcome and the reviewer deciding whether the evidence supports it.
Safety classification: **read-only**. This describes the eventual workflow's maximum intended effect, not permission to run it in this project. Development, tests and demonstrations are offline only.

Inputs: Timestamped Pod/status objects, assigned GPUs, device identifiers and matching activity samples.

Required output: Separate scheduling, readiness, allocation and observed activity verdicts with evidence ages.

Precluded use: autonomous account administration, unsupported assurance of production readiness, or following instructions embedded in logs, manifests or model metadata.

## Requirements and acceptance

All requirements are P0 and owned by the maintainer. Their rationale is the objective and supplied safety constraints, not observed production incidents. REQ-1 through REQ-4 have offline helper evidence below; REQ-5 is partially verified and remains open for native-host permission behavior.

| Requirement | Acceptance criterion | Verification |
| --- | --- | --- |
| REQ-CW-S26-1 | AC-CW-S26-1: Preserve resource identity, timestamp and completeness for every input; missing evidence is unknown. | TEST-CW-S26-1: complete, missing and stale fixture variants |
| REQ-CW-S26-2 | AC-CW-S26-2: Separate scheduling, readiness, allocation and observed activity verdicts with evidence ages. | TEST-CW-S26-2: compare deterministic fields and source attribution against reviewed expectations |
| REQ-CW-S26-3 | AC-CW-S26-3: Ready Pod with no matched GPU metrics, stale telemetry and UUID mismatch produce unknown GPU activity. | TEST-CW-S26-3: separate fixture for every named failure, with explicit expected refusal/unknown result |
| REQ-CW-S26-4 | AC-CW-S26-4: Strictly verify-only: do not start a GPU test, restart a Pod or alter the workload to obtain evidence. | TEST-CW-S26-4: adversarial input and side-effect interception; no network or real credentials |
| REQ-CW-S26-5 | AC-CW-S26-5: All local references and declared tools resolve in the installed artifact; usage cannot widen caller permissions. | TEST-CW-S26-5: isolated package install, component discovery and permission inspection |

## Architecture decision ADR-CW-S26-1

**Status: implemented; offline helper behavior verified.** Separate input collection, deterministic analysis and an evidence-bounded operator recommendation. Keep the skill body concise and put domain details in linked references. Helpers receive explicit local inputs; they must not fetch account data as an undocumented fallback.

Viewpoint: operator safety and reproducibility. Components are supplied input, parser/validator, analysis, report and human decision. Flow: untrusted input → validation → findings with source locations → operator review. The trust boundary is between untrusted evidence and instructions; text from inputs is never executed. Output contains no credentials. Local report writing is permitted; platform mutation is not a diagnostic side effect.

Alternative rejected: a generic checklist declaring success from file presence or model judgment alone. Consequence: unknown results are legitimate; some live behaviors remain unproved. A helper is required where parsing, arithmetic or repeatable verification removes guesswork; a helper added only to increase file count is not useful.

Billable creation and cleanup are not applicable to this read-only workflow. The helper accepts local JSON and emits a report; it never starts a benchmark or modifies a workload. The maintainer owns review of any future expansion of this boundary.

## Risks and controls

| Risk / inherent exposure | Control and evidence | Residual exposure / trigger / owner |
| --- | --- | --- |
| RISK-CW-S26-1: false assurance from partial inputs; high | CTRL-CW-S26-1: REQ-1 and TEST-1 preserve unknowns and evidence age | Real account behavior untested; maintainer reopens on new runtime evidence |
| RISK-CW-S26-2: unsafe recommendation or spend; high | CTRL-CW-S26-2: REQ-3/4, negative fixtures and the shared approval boundary | Human may execute advice outside this workflow; maintainer must review any expanded execution scope |
| RISK-CW-S26-3: credential or tenant-data disclosure; high | CTRL-CW-S26-3: synthetic fixtures, output redaction, secret scan and no account calls | Secret heuristics are incomplete; reviewer inspects artifact contents before publication |

Tolerance: no unresolved blocker for unauthorized mutation, secrets, misleading healthy verdicts or fabricated costs. Residual risk acceptance belongs to the maintainer, with rationale and dated evidence; offline helper verification is recorded below; native-host permission acceptance remains open. Jurisdiction/compliance obligations are unknown; this design asserts no certification.

## Test and release evidence

The fixture suite must include success, each named failure, missing evidence, stale evidence and adversarial instructions. Every test records its requirement ID, fixture digest, command, tool version, actual result and limitations. `eval-spec.yaml` defines behavior; offline helper tests do not prove a language model follows those instructions. Unsupported model-judged criteria are reported NOT RUN, never passed through a synthetic stub.

**Current result (2026-11-07): offline helper criteria verified; native-host/model criteria NOT RUN.** The installed npm artifact is byte-compared with source, local links are checked at plugin and standalone-skill boundaries, and fixture execution uses a temporary working directory without account credentials. Python audit hooks intercept socket and subprocess operations; this is targeted detection, not an OS sandbox or host permission certification.

| Requirement / test | Implemented evidence | Actual result / limit |
| --- | --- | --- |
| REQ-1 / TEST-1 | Explicit Pod UID, node, capture age, sample ages and missing-data findings; `tests/fixtures/cases.json` | PASS for supplied snapshots; device ownership is not authenticated |
| REQ-2 / TEST-2 | Exact `expected_observations` assertions for scheduling, readiness, allocation and device activity; integer/string quantities and mixed containers | PASS; plain decimal full-GPU adapter only, not all Kubernetes quantity syntax or sharing modes |
| REQ-3 / TEST-3 | Missing metrics, mismatched UUID, stale sample and aged-capture fixtures; terminating Ready Pod remains incomplete | PASS; age measured from evaluation time, never chained through an aged capture |
| REQ-4 / TEST-4 | Hostile input fixture, no command/API execution in helper, Python audit interception during replay | PASS for deterministic helper; model-authored actions outside the helper are NOT RUN |
| REQ-5 / TEST-5 | Actual npm archive payload checked against source; installed links and helper imports exercised without repository working directory | Package/reference portion PASS; native-host caller-permission enforcement remains OPEN, not waived |

The health adapter has 17 deterministic cases. Pack-wide focused Python tests and fixture counts are recorded in the current retained receipt, linked through [issue #1845](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1845). The fixture file and helper hashes identify inputs; the external CI/issue receipt binds source revision and archive digest. The archive digest is deliberately external to avoid self-referential hashing of a receipt inside that archive.

REL-CW-S26-1 records the merged source revision and protected check results in that issue. Builder: repository CI and local Codex-run validation; no reproducible-build or signed provenance claim. Python helper runtime uses the standard library; build/test tooling follows repository locks. A standalone SBOM is not generated. Rollback reference is the prior release commit recorded with the issue evidence; rollback execution is NOT RUN. No deployed-account evidence exists. Operational outcomes, trigger quality and runtime permission behavior remain unknown. Issue closure must not silently waive REQ-5.

## Primary-source register

See the [reviewed source register](../references/health-evidence.md#source-register-and-claim-boundaries) for Kubernetes Quantity, whole extended resources and deletion timestamps, inspected 2026-11-07. [CKS workload scheduling](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling) establishes scheduling context; this helper reads supplied assignment evidence and never sets `nodeName`. Treating terminating Pods as incomplete and using evaluation-time freshness are derived safety decisions. Account state and application correctness remain unknown. No proprietary CoreWeave skill text or code is incorporated.

## Implementation evidence snapshot — 2026-11-05

The shipped helper has deterministic success, refusal, incomplete and hostile-input fixture coverage. See the [pack evidence record](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/eed0fd35d89838e5d8b4d78ce4786f8ea4df0dbe/plugins/saas-packs/coreweave-pack/QUALITY.md) and [retained receipt](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/eed0fd35d89838e5d8b4d78ce4786f8ea4df0dbe/plugins/saas-packs/coreweave-pack/offline-results.json) for exact coverage and source hashes.

Implementation is present for review. This historical snapshot predates the 2026-11-07 evidence above. Native-host permission behavior remains open; no live account test is authorized or required for this offline delivery. Static grades do not replace behavioral evidence.

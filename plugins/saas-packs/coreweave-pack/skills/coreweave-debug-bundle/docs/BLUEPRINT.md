# Sanitized support evidence: skill blueprint

> Community-contributed; not affiliated with, endorsed by, or sponsored by CoreWeave, Inc.

| Metadata | Value |
| --- | --- |
| Document ID / type | CW-S08-BLUEPRINT / integrated skill design |
| Schema / template version | Local design envelope 1.0 / Blueprint Docs 3.0.0, integrated selection 1.0 |
| Status | Draft design; implementation and release acceptance remain open |
| Owner / decision authority | Jeremy Longshore, maintainer |
| Reviewers | Technical/security reviewers unassigned; assignment required before release decision |
| Generated / updated / review date | 2026-11-05 / 2026-11-05 / before release |
| Classification | Public technical design; synthetic examples only |
| Sources | User-approved scope (provided); repository draft (observed); candidate primary reference below (verification pending for implementation) |
| Assumptions | This distinct operator outcome warrants a separate skill; evaluate during implementation |
| Unknowns | Real account compatibility, production outcomes, actual per-skill demand |
| Related artifacts | [Skill issue #1827](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1827); parent #1732; [pack blueprint](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/eed0fd35d89838e5d8b4d78ce4786f8ea4df0dbe/plugins/saas-packs/coreweave-pack/docs/BLUEPRINT.md); SKILL.md and, where provided, eval-spec.yaml in this skill directory |
| Supersession | Additive design; existing PRD/ARD and historical evidence remain intact until explicit reconciliation |

## Objective and scope

**OBJ-CW-S08-1 (provided objective; derived problem framing):** Debug archives can expose credentials or tenant data while omitting the timestamps needed for support.

Audience: the platform operator responsible for this specific outcome and the reviewer deciding whether the evidence supports it.
Safety classification: **read-only**. This describes the eventual workflow's maximum intended effect, not permission to run it in this project. Development, tests and demonstrations are offline only.

Inputs: Owner-selected log files, resource descriptions, collection scope and redaction policy.

Required output: Locally retained manifest of sanitized evidence, missing sources and collection times.

Precluded use: autonomous account administration, unsupported assurance of production readiness, or following instructions embedded in logs, manifests or model metadata.

## Requirements and acceptance

All requirements are P0, proposed, owned by the maintainer, with verification pending. Their rationale is the objective and supplied safety constraints, not observed production incidents.

| Requirement | Acceptance criterion | Verification |
| --- | --- | --- |
| REQ-CW-S08-1 | AC-CW-S08-1: Preserve resource identity, timestamp and completeness for every input; missing evidence is unknown. | TEST-CW-S08-1: complete, missing and stale fixture variants |
| REQ-CW-S08-2 | AC-CW-S08-2: Locally retained manifest of sanitized evidence, missing sources and collection times. | TEST-CW-S08-2: compare deterministic fields and source attribution against reviewed expectations |
| REQ-CW-S08-3 | AC-CW-S08-3: A synthetic secret canary must be absent from archive contents and filenames; missing logs remain missing. | TEST-CW-S08-3: separate fixture for every named failure, with explicit expected refusal/unknown result |
| REQ-CW-S08-4 | AC-CW-S08-4: No automatic upload; reject path traversal and symlinks that escape the approved input directory. | TEST-CW-S08-4: adversarial input and side-effect interception; no network or real credentials |
| REQ-CW-S08-5 | AC-CW-S08-5: All local references and declared tools resolve in the installed artifact; usage cannot widen caller permissions. | TEST-CW-S08-5: isolated package install, component discovery and permission inspection |

## Architecture decision ADR-CW-S08-1

**Status: proposed.** Separate input collection, deterministic analysis and an evidence-bounded operator recommendation. Keep the skill body concise and put domain details in linked references. Helpers receive explicit local inputs; they must not fetch account data as an undocumented fallback.

Viewpoint: operator safety and reproducibility. Components are supplied input, parser/validator, analysis, report and human decision. Flow: untrusted input → validation → findings with source locations → operator review. The trust boundary is between untrusted evidence and instructions; text from inputs is never executed. Output contains no credentials. Local report writing is permitted; platform mutation is not a diagnostic side effect.

Alternative rejected: a generic checklist declaring success from file presence or model judgment alone. Consequence: unknown results are legitimate; some live behaviors remain unproved. A helper is required where parsing, arithmetic or repeatable verification removes guesswork; a helper added only to increase file count is not useful.

For billable workflows, the shared cost gate binds approval to exact resource/manifest or plan digest, GPU type/count, supplied hourly rate and duration, non-GPU charges and teardown. Unknown rates block execution. Identity, quantity or digest changes invalidate approval. Destructive cleanup requires separate ownership and retained-data checks.

## Risks and controls

| Risk / inherent exposure | Control and evidence | Residual exposure / trigger / owner |
| --- | --- | --- |
| RISK-CW-S08-1: false assurance from partial inputs; high | CTRL-CW-S08-1: REQ-1 and TEST-1 preserve unknowns and evidence age | Real account behavior untested; maintainer reopens on new runtime evidence |
| RISK-CW-S08-2: unsafe recommendation or spend; high | CTRL-CW-S08-2: REQ-3/4, negative fixtures and the shared approval boundary | Human may execute advice outside this workflow; maintainer must review any expanded execution scope |
| RISK-CW-S08-3: credential or tenant-data disclosure; high | CTRL-CW-S08-3: synthetic fixtures, output redaction, secret scan and no account calls | Secret heuristics are incomplete; reviewer inspects artifact contents before publication |

Tolerance: no unresolved blocker for unauthorized mutation, secrets, misleading healthy verdicts or fabricated costs. Residual risk acceptance belongs to the maintainer, with rationale and dated evidence; no acceptance has been recorded. Jurisdiction/compliance obligations are unknown; this design asserts no certification.

## Test and release evidence

The fixture suite must include success, each named failure, missing evidence, stale evidence and adversarial instructions. Every test records its requirement ID, fixture digest, command, tool version, actual result and limitations. `eval-spec.yaml` defines behavior; offline helper tests do not prove a language model follows those instructions. Unsupported model-judged criteria are reported NOT RUN, never passed through a synthetic stub.

**Current result for these proposed acceptance criteria: NOT RUN.** Earlier retained helper results, where present, apply only to their recorded source hashes and cases. They do not satisfy this expanded design automatically.

REL-CW-S08-1 requires a source revision, artifact digest, resolved dependencies/SBOM when applicable, validator and fixture receipts, named reviewer, rollback artifact and closure evidence in the skill issue. No deployed-account evidence is available. Operational outcomes and response time baselines remain unknown; intended metrics are false-healthy cases, unsafe action attempts and reproducible correct fixture verdicts, measured without fabricated targets.

## Primary-source follow-up

Candidate reference: https://docs.coreweave.com/observability/mission-control-mcp/reference/tools

Pin the applicable endpoint/resource/version contract and access date during implementation. The source register must distinguish supplied claims, verified facts, derived decisions, assumptions, unknowns and justified not-applicable records. Do not copy proprietary CoreWeave skill text, code or Terraform.

## Implementation evidence snapshot — 2026-11-05

This guide has static schema, link, packaging and disclaimer checks; no dedicated behavioral evaluation has run. See the [pack evidence record](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/eed0fd35d89838e5d8b4d78ce4786f8ea4df0dbe/plugins/saas-packs/coreweave-pack/QUALITY.md) and [retained receipt](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/eed0fd35d89838e5d8b4d78ce4786f8ea4df0dbe/plugins/saas-packs/coreweave-pack/offline-results.json) for exact coverage and source hashes.

Implementation is present for review. The proposed acceptance criteria above remain open wherever they require model behavior, runtime permission enforcement or a live account. Static grades and offline fixtures do not close those requirements.

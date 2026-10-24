# Langfuse pack

Five evidence-driven operators replace the 24-slot tutorial taxonomy while retaining the `langfuse-pack` install and npm identities.

**Install:** `/plugin install langfuse-pack@claude-code-plugins-plus`

| Operator                                                                    | Concrete output                                                                                                  |
| --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| [Trace Ingestion Medic](skills/langfuse-trace-ingestion-medic/SKILL.md)     | Captured OTLP batch/readback correspondence, lifecycle/context findings and coverage gaps.                       |
| [Experiment Guardian](skills/langfuse-experiment-guardian/SKILL.md)         | Case-level baseline/candidate policy result with missing evidence and critical regressions preserved.            |
| [Prompt Release Guardian](skills/langfuse-prompt-release-guardian/SKILL.md) | Explicit version/label proposal, runtime-name compatibility findings and optional supplied-webhook verification. |
| [Cost Forensics](skills/langfuse-cost-forensics/SKILL.md)                   | Recorded-cost/usage coverage, known-row subtotals and reasons to withhold complete-set totals.                   |
| [Data Boundary Auditor](skills/langfuse-data-boundary-auditor/SKILL.md)     | Reviewed field-policy correspondence, native project retention evidence and separate coverage gaps.              |

Each operator includes deterministic tooling, private receipt contracts, primary references and an evaluation specification. Python 3.10+ standard-library analysis works without credentials or networking. SDK mapping/type checks use the actual 6.0.2 client contract; offline synthetic compile fixtures do not prove production behavior. Optional experiment-result projection is a local JavaScript module, not an experiment runner. Webhook verification reads an already approved signing secret through a named environment variable and does not create a receiver or durable deduplication store.

The tools never rerun business operations, execute models, collect live telemetry, create credentials, mutate permissions, promote prompt labels, change retention or delete records. Missing evidence stays missing. Supplied receipts and review references are not independently authenticated. Keep raw prompts, outputs, IDs, configuration and logs private; reports containing hashes remain operational evidence, not automatically public material.

## Value decision and validation status

The baseline reviewed all 24 entrypoints and all 11 supporting implementation references at Git `280c69f94a7a06f3247c74f6f93daf5cd68644ac`, pack tree `6d23ee7fffa6c6bd845b1e03a4930e59082fa8aa`. Immutable Freshie run 139 graded that historical 24-skill portfolio at mean 86.7, with 14 below A. That result is historical and does not grade or certify this replacement.

Keep the Langfuse capability and consolidate around distinct operator decisions. The old slots repeated setup/tutorial/checklist material and contained unsupported current SDK calls, incomplete exports presented as complete, a business-callback retry fallback, partial secret redaction, unsafe cost totals and an incorrect webhook envelope/signature recipe. No adoption or market-demand study is claimed. Five follows the different evidence/decision contracts; it is not a target to be padded back to 24.

Static schema/rubric validation, deterministic fixture tests, SDK contract checks and Freshie inventory grading are different evidence planes. Evaluation specs describe proposed behavioral cases; their presence does not mean paid/live evaluation ran. No helper result certifies live service health, model quality, billing, anonymization, deletion, security or DoD compliance. The source-stable replacement needs its own immutable Freshie cohort before release review; never overwrite run 139 or hand-edit grade exports.

## Migration from v1

The table chooses one primary public redirect target for every retired name. Experiment/prompt work formerly bundled in core workflow B now has separate operators; debug/migration/privacy work also uses the data-boundary contract. Setup, access, runtime compatibility and lifecycle diagnostics are supporting material in [runtime diagnostics](skills/langfuse-trace-ingestion-medic/references/runtime-diagnostics.md), not extra standalone filler slots. Useful retention, masking and access boundaries live with the [data review contract](skills/langfuse-data-boundary-auditor/references/receipt-contract.md).

| Retired skill                     | Primary successor                                                                      |
| --------------------------------- | -------------------------------------------------------------------------------------- |
| `langfuse-ci-integration`         | [`langfuse-experiment-guardian`](skills/langfuse-experiment-guardian/SKILL.md)         |
| `langfuse-common-errors`          | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-core-workflow-a`        | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-core-workflow-b`        | [`langfuse-experiment-guardian`](skills/langfuse-experiment-guardian/SKILL.md)         |
| `langfuse-cost-tuning`            | [`langfuse-cost-forensics`](skills/langfuse-cost-forensics/SKILL.md)                   |
| `langfuse-data-handling`          | [`langfuse-data-boundary-auditor`](skills/langfuse-data-boundary-auditor/SKILL.md)     |
| `langfuse-debug-bundle`           | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-deploy-integration`     | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-enterprise-rbac`        | [`langfuse-data-boundary-auditor`](skills/langfuse-data-boundary-auditor/SKILL.md)     |
| `langfuse-hello-world`            | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-incident-runbook`       | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-install-auth`           | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-local-dev-loop`         | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-migration-deep-dive`    | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-multi-env-setup`        | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-observability`          | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-performance-tuning`     | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-prod-checklist`         | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-rate-limits`            | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-reference-architecture` | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-sdk-patterns`           | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-security-basics`        | [`langfuse-data-boundary-auditor`](skills/langfuse-data-boundary-auditor/SKILL.md)     |
| `langfuse-upgrade-migration`      | [`langfuse-trace-ingestion-medic`](skills/langfuse-trace-ingestion-medic/SKILL.md)     |
| `langfuse-webhooks-events`        | [`langfuse-prompt-release-guardian`](skills/langfuse-prompt-release-guardian/SKILL.md) |

The obsolete passive scaffolds and CSV under `plugins/saas-packs/skill-databases/langfuse/` are also retired. Their 19 files remain recoverable at the baseline Git commit; the shared scaffold generator now refuses Langfuse so it cannot recreate the tutorial taxonomy. They were not executable operator definitions or a frozen Freshie grade export.

All 24 retired public skill names have 301 mappings in the canonical redirect registry. Generated ingress configuration must follow normal reviewed deployment; source configuration alone does not prove production activation. Existing unrelated redirect entries remain intact.

## Exact restoration and distribution boundary

The full pre-rebuild source remains recoverable from Git `280c69f94a7a06f3247c74f6f93daf5cd68644ac`, path `plugins/saas-packs/langfuse-pack/`. For offline inspection:

```sh
git archive --format=tar --output=langfuse-pre-v2.tar 280c69f94a7a06f3247c74f6f93daf5cd68644ac plugins/saas-packs/langfuse-pack
```

A rollback is a normal reviewed restoration of that exact source, reversal of only this migration's 24 redirect entries, restoration of pack metadata, and canonical regeneration of catalog/package/curated/evaluation projections. Preserve unrelated work and history; do not force-push or restore old grade claims as if they applied to new source.

At assessment, Git plugin/catalog version was 1.17.0, tracked generated npm manifest was 1.0.6, and the registry's latest published `@intentsolutionsio/langfuse-pack` artifact was 1.0.1 (24 skills, published 2026-06-08). Its registry SHA-512 was verified independently; archive SHA-256 was `9e49929e39113d0bfacf451ec030b1f18c4b64eaf43822033df3d872b2773b04`. Do not imply 1.17.0 was published. Version 2.0.0 here is the prepared source migration; publication is a separate release state, with no manual npm publish or unpublish performed by this rebuild.

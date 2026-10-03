# Sentry pack v2 — scaffold inventory

**Status:** local draft under `/workspace/sentry-v2/pack/`. Not pushed. Not editing live GitHub tree.
**Date:** 2026-10-03 (ET).
**Locked ADR:** `000-docs/008-AT-ADEC-sentry-v2-cto-decision.md`
**Absorb (MODIFY):** `000-docs/010-AT-ADEC-sentry-v2-modify-absorb.md` (wins over 008 on six items)
**Pressure test:** `000-docs/009-RA-REVW-sentry-v2-pressure-test.md`
**Kill list:** `000-docs/phase0-kill-list.md`
**Discipline mirror:** `plugins/saas-packs/databricks-pack/` (shape only).

**File count:** 157

## Nested-checklist path rule (Absorb A1 — chosen + verified)

Per Absorb A1 (amends ADR Decision 4): nested procedures are

`skills/<parent>/agents/<agent>/skills/<child>/CHECKLIST.md`

**Not** `SKILL.md`. Verified against repo `scripts/corpus-resolver.mjs`:
`isGradedSkill` uses `/\/skills\/[^/]+\/SKILL\.md$/` with no `/agents/` exclusion.
Agent frontmatter: `skills: []`; agents Read checklists.

Shared `transaction-cardinality` lives once under quota; triage has
`agents/trace-bottleneck/skills/transaction-cardinality/OWNER.md` pointer only.

## Amended tree highlights (Absorb A2)

- triage: `fingerprint-auditor`, `noise-classifier`, `perf-span-auditor` (additive)
- PII: `replay-privacy` (PI06); PI07 Relay = parent reference only
- quota: `org-key-boundaries` + SC04; category fan-out = script + `usage-auditor` only
- Labeled `OWNER.md` / `COPIED-FROM.md` reference copies on Decision 3 edges (A3)
- v1 stub redirects under `skills/<v1-slug>/SKILL.md` (A5)
- Shared client: `scripts/lib/sentry_readonly.py` (A6)

## Org-topology nesting

- `key-boundary-mapper` + `org-key-boundaries` (+ SC04) under `sentry-quota-leak-hunter`
- `config-drift-auditor` + `sentry-config-audit` under `sentry-pii-scrub-enforcer`

## Every path created

- `.claude-plugin/plugin.json`
- `000-docs/000-INDEX.md`
- `000-docs/002-RL-RSRC-operator-pain.md`
- `000-docs/003-RL-RSRC-cost-quota-sampling.md`
- `000-docs/004-RL-RSRC-security-pii-scrubbing.md`
- `000-docs/005-RL-RSRC-release-ci-sourcemaps.md`
- `000-docs/006-RL-RSRC-scale-multi-env.md`
- `000-docs/007-SY-SYNTH-sentry-v2-skill-cut.md`
- `000-docs/008-AT-ADEC-sentry-v2-cto-decision.md`
- `000-docs/009-RA-REVW-sentry-v2-pressure-test.md`
- `000-docs/010-AT-ADEC-sentry-v2-modify-absorb.md`
- `000-docs/010-migration-stubs-plan.md`
- `000-docs/README-SOURCE.md`
- `000-docs/phase0-kill-list.md`
- `CHANGELOG.md`
- `LICENSE`
- `README.md`
- `SCAFFOLD.md`
- `hooks/hooks.json`
- `package.json`
- `scripts/lib/__init__.py`
- `scripts/lib/sentry_readonly.py`
- `skills/sentry-advanced-troubleshooting/SKILL.md`
- `skills/sentry-architecture-variants/SKILL.md`
- `skills/sentry-ci-integration/SKILL.md`
- `skills/sentry-common-errors/SKILL.md`
- `skills/sentry-cost-tuning/SKILL.md`
- `skills/sentry-data-handling/SKILL.md`
- `skills/sentry-debug-bundle/SKILL.md`
- `skills/sentry-deploy-integration/SKILL.md`
- `skills/sentry-enterprise-rbac/SKILL.md`
- `skills/sentry-error-capture/SKILL.md`
- `skills/sentry-event-forensics/SKILL.md`
- `skills/sentry-event-forensics/agents/debug-bundler.md`
- `skills/sentry-event-forensics/agents/debug-bundler/skills/support-debug-bundle/CHECKLIST.md`
- `skills/sentry-event-forensics/agents/drop-tracer.md`
- `skills/sentry-event-forensics/agents/drop-tracer/skills/silent-drop-diagnosis/CHECKLIST.md`
- `skills/sentry-event-forensics/agents/sdk-conflict-checker.md`
- `skills/sentry-event-forensics/agents/sdk-conflict-checker/skills/sdk-conflict-isolation/CHECKLIST.md`
- `skills/sentry-event-forensics/agents/sdk-migrator.md`
- `skills/sentry-event-forensics/agents/sdk-migrator/skills/sdk-major-upgrade/CHECKLIST.md`
- `skills/sentry-event-forensics/agents/sdk-migrator/skills/vendor-cutover/CHECKLIST.md`
- `skills/sentry-event-forensics/agents/sourcemap-debugger.md`
- `skills/sentry-event-forensics/agents/sourcemap-debugger/skills/ci-sourcemap-upload/CHECKLIST.md`
- `skills/sentry-event-forensics/agents/sourcemap-debugger/skills/ci-sourcemap-upload/COPIED-FROM.md`
- `skills/sentry-event-forensics/agents/sourcemap-debugger/skills/ci-sourcemap-upload/OWNER.md`
- `skills/sentry-event-forensics/agents/sourcemap-debugger/skills/sourcemap-resolution/CHECKLIST.md`
- `skills/sentry-event-forensics/docs/ADR.md`
- `skills/sentry-event-forensics/docs/ONE-PAGER.md`
- `skills/sentry-event-forensics/docs/PRD.md`
- `skills/sentry-event-forensics/eval-spec.yaml`
- `skills/sentry-event-forensics/references/.gitkeep`
- `skills/sentry-event-forensics/scripts/.gitkeep`
- `skills/sentry-event-forensics/scripts/parse-resolved-with.py`
- `skills/sentry-hello-world/SKILL.md`
- `skills/sentry-incident-runbook/SKILL.md`
- `skills/sentry-install-auth/SKILL.md`
- `skills/sentry-issue-triage/SKILL.md`
- `skills/sentry-issue-triage/agents/fingerprint-auditor.md`
- `skills/sentry-issue-triage/agents/fingerprint-auditor/skills/fingerprint-rules/CHECKLIST.md`
- `skills/sentry-issue-triage/agents/issue-investigator.md`
- `skills/sentry-issue-triage/agents/issue-investigator/skills/issue-triage-loop/CHECKLIST.md`
- `skills/sentry-issue-triage/agents/log-correlator.md`
- `skills/sentry-issue-triage/agents/log-correlator/skills/event-log-correlation/CHECKLIST.md`
- `skills/sentry-issue-triage/agents/noise-classifier.md`
- `skills/sentry-issue-triage/agents/noise-classifier/skills/inbound-filter-matrix/CHECKLIST.md`
- `skills/sentry-issue-triage/agents/noise-classifier/skills/inbound-filter-matrix/OWNER.md`
- `skills/sentry-issue-triage/agents/perf-span-auditor.md`
- `skills/sentry-issue-triage/agents/perf-span-auditor/skills/span-fingerprint/CHECKLIST.md`
- `skills/sentry-issue-triage/agents/trace-bottleneck.md`
- `skills/sentry-issue-triage/agents/trace-bottleneck/skills/transaction-cardinality/OWNER.md`
- `skills/sentry-issue-triage/docs/ADR.md`
- `skills/sentry-issue-triage/docs/ONE-PAGER.md`
- `skills/sentry-issue-triage/docs/PRD.md`
- `skills/sentry-issue-triage/eval-spec.yaml`
- `skills/sentry-issue-triage/references/.gitkeep`
- `skills/sentry-issue-triage/scripts/.gitkeep`
- `skills/sentry-known-pitfalls/SKILL.md`
- `skills/sentry-load-scale/SKILL.md`
- `skills/sentry-local-dev-loop/SKILL.md`
- `skills/sentry-migration-deep-dive/SKILL.md`
- `skills/sentry-multi-env-setup/SKILL.md`
- `skills/sentry-observability/SKILL.md`
- `skills/sentry-performance-tracing/SKILL.md`
- `skills/sentry-performance-tuning/SKILL.md`
- `skills/sentry-pii-scrub-enforcer/SKILL.md`
- `skills/sentry-pii-scrub-enforcer/agents/config-drift-auditor.md`
- `skills/sentry-pii-scrub-enforcer/agents/config-drift-auditor/references/sampler-rules/CHECKLIST.md`
- `skills/sentry-pii-scrub-enforcer/agents/config-drift-auditor/references/sampler-rules/COPIED-FROM.md`
- `skills/sentry-pii-scrub-enforcer/agents/config-drift-auditor/references/sampler-rules/OWNER.md`
- `skills/sentry-pii-scrub-enforcer/agents/config-drift-auditor/skills/sentry-config-audit/CHECKLIST.md`
- `skills/sentry-pii-scrub-enforcer/agents/gdpr-deletion.md`
- `skills/sentry-pii-scrub-enforcer/agents/gdpr-deletion/skills/gdpr-delete/CHECKLIST.md`
- `skills/sentry-pii-scrub-enforcer/agents/pii-scrubber.md`
- `skills/sentry-pii-scrub-enforcer/agents/pii-scrubber/skills/before-send-scrub/CHECKLIST.md`
- `skills/sentry-pii-scrub-enforcer/agents/pii-scrubber/skills/server-scrub-rules/CHECKLIST.md`
- `skills/sentry-pii-scrub-enforcer/agents/replay-privacy.md`
- `skills/sentry-pii-scrub-enforcer/agents/replay-privacy/skills/replay-privacy/CHECKLIST.md`
- `skills/sentry-pii-scrub-enforcer/agents/replay-privacy/skills/replay-privacy/OWNER.md`
- `skills/sentry-pii-scrub-enforcer/docs/ADR.md`
- `skills/sentry-pii-scrub-enforcer/docs/ONE-PAGER.md`
- `skills/sentry-pii-scrub-enforcer/docs/PRD.md`
- `skills/sentry-pii-scrub-enforcer/eval-spec.yaml`
- `skills/sentry-pii-scrub-enforcer/references/.gitkeep`
- `skills/sentry-pii-scrub-enforcer/scripts/.gitkeep`
- `skills/sentry-pii-scrub-enforcer/scripts/print-gdpr-delete-request.py`
- `skills/sentry-pii-scrub-enforcer/scripts/settings-diff.py`
- `skills/sentry-policy-guardrails/SKILL.md`
- `skills/sentry-prod-checklist/SKILL.md`
- `skills/sentry-quota-leak-hunter/SKILL.md`
- `skills/sentry-quota-leak-hunter/agents/cardinality-hunter.md`
- `skills/sentry-quota-leak-hunter/agents/cardinality-hunter/skills/transaction-cardinality/CHECKLIST.md`
- `skills/sentry-quota-leak-hunter/agents/key-boundary-mapper.md`
- `skills/sentry-quota-leak-hunter/agents/key-boundary-mapper/references/config-drift/CHECKLIST.md`
- `skills/sentry-quota-leak-hunter/agents/key-boundary-mapper/references/config-drift/COPIED-FROM.md`
- `skills/sentry-quota-leak-hunter/agents/key-boundary-mapper/references/config-drift/OWNER.md`
- `skills/sentry-quota-leak-hunter/agents/key-boundary-mapper/skills/org-key-boundaries/CHECKLIST.md`
- `skills/sentry-quota-leak-hunter/agents/usage-auditor.md`
- `skills/sentry-quota-leak-hunter/agents/usage-auditor/skills/quota-usage-audit/CHECKLIST.md`
- `skills/sentry-quota-leak-hunter/agents/volume-cutter.md`
- `skills/sentry-quota-leak-hunter/agents/volume-cutter/references/replay-privacy/CHECKLIST.md`
- `skills/sentry-quota-leak-hunter/agents/volume-cutter/references/replay-privacy/COPIED-FROM.md`
- `skills/sentry-quota-leak-hunter/agents/volume-cutter/references/replay-privacy/OWNER.md`
- `skills/sentry-quota-leak-hunter/agents/volume-cutter/skills/inbound-filter-matrix/CHECKLIST.md`
- `skills/sentry-quota-leak-hunter/agents/volume-cutter/skills/inbound-filter-matrix/COPIED-FROM.md`
- `skills/sentry-quota-leak-hunter/agents/volume-cutter/skills/inbound-filter-matrix/OWNER.md`
- `skills/sentry-quota-leak-hunter/agents/volume-cutter/skills/sampler-and-filters/CHECKLIST.md`
- `skills/sentry-quota-leak-hunter/docs/ADR.md`
- `skills/sentry-quota-leak-hunter/docs/CFO-ONE-PAGER.md`
- `skills/sentry-quota-leak-hunter/docs/ONE-PAGER.md`
- `skills/sentry-quota-leak-hunter/docs/PRD.md`
- `skills/sentry-quota-leak-hunter/eval-spec.yaml`
- `skills/sentry-quota-leak-hunter/references/.gitkeep`
- `skills/sentry-quota-leak-hunter/scripts/.gitkeep`
- `skills/sentry-quota-leak-hunter/scripts/parse-usage-stats.py`
- `skills/sentry-rate-limits/SKILL.md`
- `skills/sentry-reference-architecture/SKILL.md`
- `skills/sentry-release-management/SKILL.md`
- `skills/sentry-release-medic/SKILL.md`
- `skills/sentry-release-medic/agents/release-finalizer.md`
- `skills/sentry-release-medic/agents/release-finalizer/skills/release-health/CHECKLIST.md`
- `skills/sentry-release-medic/agents/sourcemap-uploader.md`
- `skills/sentry-release-medic/agents/sourcemap-uploader/skills/ci-sourcemap-upload/CHECKLIST.md`
- `skills/sentry-release-medic/agents/sourcemap-uploader/skills/sourcemap-resolution/CHECKLIST.md`
- `skills/sentry-release-medic/agents/sourcemap-uploader/skills/sourcemap-resolution/COPIED-FROM.md`
- `skills/sentry-release-medic/agents/sourcemap-uploader/skills/sourcemap-resolution/OWNER.md`
- `skills/sentry-release-medic/docs/ADR.md`
- `skills/sentry-release-medic/docs/ONE-PAGER.md`
- `skills/sentry-release-medic/docs/PRD.md`
- `skills/sentry-release-medic/eval-spec.yaml`
- `skills/sentry-release-medic/references/.gitkeep`
- `skills/sentry-release-medic/scripts/.gitkeep`
- `skills/sentry-release-medic/scripts/grep-debug-id.sh`
- `skills/sentry-reliability-patterns/SKILL.md`
- `skills/sentry-sdk-patterns/SKILL.md`
- `skills/sentry-security-basics/SKILL.md`
- `skills/sentry-upgrade-migration/SKILL.md`

## Not done (by design)

- No git commit / push / PR
- No edits under `plugins/saas-packs/sentry-pack/` on GitHub
- No MCP server, no write tools, no PreToolUse SDK-edit hooks
- Checklist / script / eval bodies remain stubs to fill in pilot phase
- Cross-skill agent-call spike not run (copies remain mandatory)

# Unofficial community operator pack for CoreWeave

**26 skills for GPU operations, evidence review and bounded provisioning workflows.**
Community-contributed; not affiliated with, endorsed by, or sponsored by CoreWeave, Inc.
The stable pack name is `coreweave-pack`. This community implementation is MIT licensed.

For CoreWeave's official skills, see [github.com/coreweave/skills](https://github.com/coreweave/skills).
That separate distribution's proprietary text, scripts and Terraform are not included here.
This pack emphasizes Day-2 GPU forensics, fabric interpretation, cost provenance,
permission review and operational recovery.

## Start with evidence

Supply redacted logs, snapshots or the packaged fixtures. Helpers run locally;
they never authenticate to CoreWeave, create resources or execute commands from input.
A healthy-looking Pod is not proof of GPU activity; usage is not an invoice; an Xid
code alone does not authorize hardware recovery. Missing evidence remains unknown.

The three original diagnostic helpers remain available for raw logs and cost rows.
Eight additional reviewers cover inference, DDP training, RBAC, CI, incidents,
Terraform plans, CAIOS transfers and workload/GPU health. Three read-only plugin
agents preload the relevant skills to review supplied findings; their execution
permissions remain restricted. Direct skill use works without agent orchestration.

## Safety and costs

Before a billable action, show exact resources and target, GPU type/count, supplied
hourly rates and duration, other charges, artifact digest and teardown. Obtain
explicit user confirmation. The [shared cost gate](shared/cost-gate.md) and local
copies enforce the review contract. A matching JSON confirmation is not authenticated
permission and must not independently unlock deployment. Default to offline review.
Server dry-run, Terraform plan and cloud CLI previews may still contact an account.

## Skill inventory

Every skill has an individual blueprint with requirements, risks and proposed
acceptance. Safety describes the eventual operator workflow; no account operation
was used to validate this pack.

| Skill | Workflow safety | Offline executable evidence |
| --- | --- | --- |
| [coreweave-caios-stage-model](skills/coreweave-caios-stage-model/SKILL.md) | Creates billable resources; confirmation required | Fixture reviewer |
| [coreweave-ci-integration](skills/coreweave-ci-integration/SKILL.md) | Creates billable resources; confirmation required | Fixture reviewer |
| [coreweave-cks-provisioning](skills/coreweave-cks-provisioning/SKILL.md) | Creates billable resources; confirmation required | Fixture reviewer |
| [coreweave-common-errors](skills/coreweave-common-errors/SKILL.md) | Read-only review | Static guide checks |
| [coreweave-core-workflow-a](skills/coreweave-core-workflow-a/SKILL.md) | Creates billable resources; confirmation required | Fixture reviewer |
| [coreweave-core-workflow-b](skills/coreweave-core-workflow-b/SKILL.md) | Creates billable resources; confirmation required | Fixture reviewer |
| [coreweave-cost-tuning](skills/coreweave-cost-tuning/SKILL.md) | Read-only review | Static guide checks |
| [coreweave-data-handling](skills/coreweave-data-handling/SKILL.md) | Read-only review | Static guide checks |
| [coreweave-debug-bundle](skills/coreweave-debug-bundle/SKILL.md) | Read-only review | Static guide checks |
| [coreweave-deploy-integration](skills/coreweave-deploy-integration/SKILL.md) | Creates billable resources; confirmation required | Static guide checks |
| [coreweave-enterprise-rbac](skills/coreweave-enterprise-rbac/SKILL.md) | Read-only review | Fixture reviewer |
| [coreweave-fabric-diagnostics](skills/coreweave-fabric-diagnostics/SKILL.md) | Read-only review | Diagnostic self-tests + regressions |
| [coreweave-gpu-cost-leak-hunter](skills/coreweave-gpu-cost-leak-hunter/SKILL.md) | Read-only review | Diagnostic self-tests + regressions |
| [coreweave-gpu-node-forensics](skills/coreweave-gpu-node-forensics/SKILL.md) | Read-only review | Diagnostic self-tests + regressions |
| [coreweave-hello-world](skills/coreweave-hello-world/SKILL.md) | Creates billable resources; confirmation required | Static guide checks |
| [coreweave-incident-runbook](skills/coreweave-incident-runbook/SKILL.md) | Read-only review | Fixture reviewer |
| [coreweave-install-auth](skills/coreweave-install-auth/SKILL.md) | Read-only review | Static guide checks |
| [coreweave-local-dev-loop](skills/coreweave-local-dev-loop/SKILL.md) | Read-only review | Static guide checks |
| [coreweave-multi-env-setup](skills/coreweave-multi-env-setup/SKILL.md) | Creates billable resources; confirmation required | Static guide checks |
| [coreweave-observability](skills/coreweave-observability/SKILL.md) | Read-only review | Static guide checks |
| [coreweave-performance-tuning](skills/coreweave-performance-tuning/SKILL.md) | Creates billable resources; confirmation required | Static guide checks |
| [coreweave-prod-checklist](skills/coreweave-prod-checklist/SKILL.md) | Read-only review | Static guide checks |
| [coreweave-sdk-patterns](skills/coreweave-sdk-patterns/SKILL.md) | Read-only review | Static guide checks |
| [coreweave-security-basics](skills/coreweave-security-basics/SKILL.md) | Read-only review | Static guide checks |
| [coreweave-upgrade-migration](skills/coreweave-upgrade-migration/SKILL.md) | Creates billable resources; confirmation required | Static guide checks |
| [coreweave-workload-health](skills/coreweave-workload-health/SKILL.md) | Read-only review | Fixture reviewer |

The public CI title remains **UNOFFICIAL CI INTEGRATION FOR COREWEAVE**; its stable
identifier is `coreweave-ci-integration`. The five deeper workflows are selected by
operator value; there is no per-skill usage ranking supporting a “most-used” claim.

## Install

In Claude Code, from the Tons of Skills marketplace (it mirrors this repository):

```bash
/plugin marketplace add jeremylongshore/claude-code-plugins
/plugin install coreweave-pack@claude-code-plugins-plus
```

This repository is the source of truth; the marketplace copy is synced from it.

## Reproduce offline validation

Needs Python 3 with PyYAML and pytest, Node 22+ with npm, git and curl:

```bash
tools/setup.sh                 # pinned grader, kernel schemas, j-rig and gitleaks into .cache/
python3 tools/validate-pack.py # schema/rubric, links, 11 eval packages, fixtures, gitleaks
python3 -m pytest tests
```

The gate delegates schema and rubric checks to the Tons of Skills marketplace validator (pinned commit),
checks installed references and agent preloads, checks all 11 eval-spec packages,
replays deterministic contracts and runs gitleaks. It reports model judgments as
NOT RUN. Run a skill's helper with its packaged example for standalone inspection.
Terraform templates have separate mock-provider tests; install the pinned providers
first, then run `terraform test` in each root with credentials absent. No normal
Terraform plan is used as an offline test.

## Evidence and maintenance

- [Quality and limitations](QUALITY.md) and [local validation receipt](offline-results.json)
- [Pack blueprint and per-skill designs](docs/BLUEPRINT.md)
- [Retired scaffold inventory and reasons](docs/SCAFFOLD-DISPOSITION.md)
- [Requirements](docs/PRD.md), [architecture decisions](docs/ADR.md), [review brief](docs/ONE-PAGER.md)

Static grades, package integrity and fixture results do not establish model behavior,
production compatibility, measured savings or endorsement. Preserve that distinction
when sharing this pack. Live account validation and provider-backed model evaluations
have not been performed. Do not publish a verified badge from these local receipts.

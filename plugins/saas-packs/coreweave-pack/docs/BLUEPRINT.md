# CoreWeave community operator pack: delivery blueprint

> Community-contributed; not affiliated with, endorsed by, or sponsored by CoreWeave, Inc.

| Metadata | Value |
| --- | --- |
| Document ID / type | CW-PACK-BLUEPRINT / delivery and architecture design |
| Schema / template version | Local design envelope 1.0 / Blueprint Docs 3.0.0, integrated selection 1.0 |
| Status | In development; original scope approved by owner; added designs remain reviewable drafts |
| Owner / decision authority | Jeremy Longshore, maintainer |
| Reviewers | Technical/security reviewers to be assigned; no vendor approval claimed |
| Generated / updated / review date | 2026-11-05 / 2026-11-05 / before release |
| Classification | Public technical design; no private commercial or legal correspondence |
| Sources | User scope and approval (provided); inspected repository and public runtime docs (verified observations); architecture below (derived/proposed) |
| Assumptions | Five priority workflows selected by operator value; usage ranking is unavailable |
| Unknowns | Actual demand, production compatibility, operating results, vendor review |
| Related artifacts | GitHub parent #1732; per-skill blueprints below; README; QUALITY.md; offline-results.json |
| Supersession | Adds approved implementation scope to October research; preserves historical records and existing draft fixes |

## Objective and evidence boundary

OBJ-CW-1: deliver original, useful Day-2 diagnostics and safe operator workflows, with a reviewable explanation of each skill's value and limits. The expected inventory is 23 existing plus three new skills. The 24 database stubs are not 24 additional product capabilities.

Existing in this review branch: 26 skill guides, three original diagnostic helpers, eight added offline reviewers, shared cost gates, three restricted agent definitions and per-skill blueprints. In development: PR validation and review. Proposed/unverified: runtime agent composition, live platform compatibility and acceptance criteria beyond the retained offline evidence. No live CoreWeave account validation, paid model evaluation, measured savings, certification, endorsement or partnership is established by this work.

Each skill receives its own integrated blueprint under `skills/<name>/docs/BLUEPRINT.md`, covering requirements, architecture decision, controls, risks, acceptance and evidence. This is the smallest useful Blueprint Docs selection for one skill, not 22 empty workbooks. Existing PRD/ARD records will be reconciled explicitly; pack submission documents `docs/PRD.md`, `docs/ADR.md` and `docs/ONE-PAGER.md` will summarize and link the authoritative designs rather than duplicate their requirements.

## Source register and authority

| ID | Source / access | State and use |
| --- | --- | --- |
| SRC-CW-1 | Owner's six-goal scope and subsequent approval, 2026-11-05 | Provided: requirements, no-account rule, original authorship, branch/PR constraints |
| SRC-CW-2 | This checkout, base 8292e1e11 and current uncommitted draft | Verified inventory observation; draft bytes are not a released artifact |
| SRC-CW-3 | [Anthropic Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview), accessed 2026-11-05 | Verified documentation: progressive disclosure; product runtime differences |
| SRC-CW-4 | [Claude Code subagents](https://code.claude.com/docs/en/sub-agents), accessed 2026-11-05 | Verified documentation: preloaded skills, dynamic invocation, plugin-agent field restrictions |
| SRC-CW-5 | [Claude Code skills](https://code.claude.com/docs/en/skills), accessed 2026-11-05 | Verified documentation: forked skill execution and context boundaries |
| SRC-CW-6 | [CoreWeave official skills](https://github.com/coreweave/skills), public repository inspected 2026-11-05 | Upstream discovery and comparison only; user requires proprietary material not be copied |
| SRC-CW-7 | Databricks cost skill docs/PRD.md and docs/ADR.md in this checkout | Verified design pattern; its prices, capabilities and results do not transfer to CoreWeave |
| SRC-CW-8 | Repository CLAUDE.md, schema changelog and canonical validator | Authoritative repository gate rules; kernel-shadow remains advisory |
| SRC-CW-9 | Retained offline-results.json | Historical local fixture/static receipts only, bound to recorded hashes; expanded acceptance not established |

Any provider-specific implementation claim needs its exact primary source, contract version and observation date. A candidate URL in a skill blueprint is research work to resolve, not verified API compatibility. Do not infer legal/compliance applicability from a template. No pricing is invented.

## Goal 1: cost, identity and side-effect boundaries

| Files | Planned change / acceptance |
| --- | --- |
| `shared/cost-gate.md` | Canonical approval contract for exact organization/context, resources, GPU type/count, supplied hourly rate, time window, storage/network charges, uncertainty and teardown |
| `scripts/sync-cost-gates.py` | Generate byte-identical skill-local copies; check mode fails on drift |
| `skills/<billable-skill>/references/cost-gate.md` | Installable copy, with source/digest provenance; no escaping the installed skill root |
| `skills/*/SKILL.md` | Classify read-only versus billable effects, default plan/offline, least privilege and secret handling; keep the disclaimer on every skill |
| `tests/test_coreweave_cost_gates.py` | Missing inputs, changed plan, rejected confirmation, wrong context, retained data and stale approval cases |

CTRL-CW-COST-1: estimates use supplied rates with currency, date and scope. GPU subtotal is count × hourly rate × duration; storage, transfer, holding/commitment charges and uncertainty remain separate. Unknown rates never become zero. A plan review is not approval. Approval binds the exact manifest/plan digest and target scope; changes invalidate it. Cleanup identifies owned resources and data retention separately. Terraform destroy is never prescribed against shared state without its own reviewed destruction plan.

CTRL-CW-SAFETY-1: pasted logs and manifests are untrusted data. No executing embedded commands, unsafe YAML tags or credential plugins. Secrets never appear in commands, receipts or archives. Shell allowlists are not a complete sandbox: helper code, subprocesses and egress must also be checked.

## Goal 2: five priority upgrades

These are chosen for operational importance, not asserted to be the five most-used skills. The three existing diagnostic flagships remain protected by regression cases.

| Skill | Helper path under skill | Distinct acceptance |
| --- | --- | --- |
| `coreweave-core-workflow-a` | `scripts/review-inference.py` | KServe prerequisites, costed resource plan, readiness plus model/endpoint acceptance |
| `coreweave-core-workflow-b` | `scripts/review-training.py` | Rank/rendezvous consistency, transport uncertainty and checkpoint recovery |
| `coreweave-enterprise-rbac` | `scripts/review-access.py` | Effective permission paths, escalation and minimum access |
| `coreweave-ci-integration` | `scripts/review-workflow.py` | PR/deploy trust separation, protected environments, secret cleanup and budget gate |
| `coreweave-incident-runbook` | `scripts/review-incident.py` | Timeline, evidence completeness, bounded containment and recovery criteria |

Each changes `SKILL.md`, adds/deepens `references/operator-notes.md`, keeps its own `docs/BLUEPRINT.md`, and gains `eval-spec.yaml` plus `tests/fixtures/`. Criteria name correct outputs and wrong answers to reject. Helpers must remove concrete parsing or verification ambiguity; file count does not establish quality.

## Goal 3: three original gap skills

| New skill | Planned files and emphasis |
| --- | --- |
| `coreweave-cks-provisioning` | `SKILL.md`, `references/provisioning-contract.md`, `scripts/review-plan.py`, `assets/terraform/{versions,main,variables,outputs}.tf`, `eval-spec.yaml`, `tests/fixtures/`, `docs/BLUEPRINT.md`; original CKS/VPC/node-pool assets, replacement risk, ownership, state and rollback |
| `coreweave-caios-stage-model` | `SKILL.md`, `references/staging-contract.md`, `scripts/review-transfer.py`, `eval-spec.yaml`, `tests/fixtures/`, `docs/BLUEPRINT.md`; provenance, storage/transfer cost, prefix ownership, checksums and safe partial-upload cleanup |
| `coreweave-workload-health` | `SKILL.md`, `references/health-evidence.md`, `scripts/check-health.py`, `eval-spec.yaml`, `tests/fixtures/`, `docs/BLUEPRINT.md`; separate readiness, allocation and observed GPU activity, with stale/missing evidence unknown |

Normal Terraform planning can access providers. Offline validation uses synthetic JSON and supported mock-provider tests; no live Terraform plan, API discovery, upload or workload launch is permitted. Provider resource schemas must be verified before writing original Terraform. No copied upstream scripts or templates.

## Agent and skill composition

ADR-CW-COMPOSE-1 (proposed): add specialists only where a bounded second analysis improves the outcome. Candidate files are plugin-root `agents/coreweave-gpu-evidence-reviewer.md`, `agents/coreweave-access-reviewer.md` and `agents/coreweave-cost-plan-reviewer.md`. They consume, respectively, GPU/fabric/health skills; RBAC/security/CI skills; cost/provisioning review skills. They return findings, evidence locations, confidence and unresolved questions. The parent owns execution and any approval dialogue.

A subagent's `skills:` preloads the full content; runtime Skill invocation is a separate capability and may reach other available skills. Neither a preload list nor a prompt-only whitelist is a security boundary. Review effective tool access, credentials and host policy. Where dynamic invocation cannot be restricted to the reviewed dependency set, use preloading with Skill unavailable. Keep skill → agent → preloaded-skill dependencies acyclic; do not preload a forked entrypoint into the same agent it spawns. Bound turns, inputs, output size and recursion; no automatic delegation loop.

Claude Code plugin-agent `hooks`, `mcpServers` and `permissionMode` fields are ignored by the documented runtime. Register any needed hooks/MCP at supported plugin locations. Prefer an explicit plugin-root agent registry over assuming nested skill directories are auto-discovered. The installed CLI reports 2.1.316; actual loading and installed artifact paths still need verification. Other hosts retain the direct portable skill path and report unsupported agent/hook features explicitly.

No new live MCP server is required to claim offline capability. Use official Mission Control references and pasted tool-result fixtures. A future optional configuration must document its transport, explicit environment references, read-only tool scope and install behavior; do not add an auto-connecting server to satisfy a checklist.

## Validation and acceptance matrix

| Surface | Validator / checks | Required evidence |
| --- | --- | --- |
| Every SKILL.md | `validate-skillmd`: canonical marketplace and deterministic deep checks; manual body/tool review | Actual errors/warnings and scores, not assumed A grades |
| Agents | `validate-agent`: supported schema, 11 plugin-agent required fields, body/allowlist, preload resolution | No undeclared tool calls or unbounded dependencies; static versus runtime results separated |
| Hooks, including inline | `validate-hook`: type/event/handler shape, matchers, exit and feedback semantics | If present, offline allow/deny/malformed-input tests; absent components recorded with rationale |
| MCP, including inline | `validate-mcp`: transport, duplicate keys, types, credentials/headers, actual tool names | Static configuration/fixture inspection only; no connection in CI |
| Plugin/catalog | `validate-plugin` and `validate-marketplace` applicable component checks | Manifest, sources, packaged references and derived catalogs agree |
| Blueprint traceability | Requirement → criterion → issue/component → fixture/test → receipt | No orphan IDs or claim of a result from another source revision |
| Eval specs | J-Rig package check plus a documented offline fixture adapter | Every spec inspected; executable deterministic assertions run; model-judged behavior NOT RUN |
| Security/package | Gitleaks, Unicode hygiene, pinned dependencies and npm dry-run inventory | No secrets, pyc/cache files or unresolved installed references |

REQ-CW-VALIDATE-1: create `scripts/validate-coreweave-pack.py` (repository root scripts) as an orchestrator around existing authorities, not a competing rubric. Add focused regression tests and a named command. Wire into the existing validation workflow's appropriate required job without altering required contexts. Missing tools or malformed receipts must not become success. Offline fixtures run without real account credentials or usable network paths. Capture attempted egress and destructive subprocesses in negative tests.

The authored validation skills contain historical inconsistencies: kernel-first prose does not authorize changing this repository's advisory kernel lane; legacy `--thorough` is not a supported Python validator option. Report discrepancies. MiniMax and paid provider evaluations remain off. Do not claim a full behavioral pass from J-Rig check, an offline stub or a file count.

## Scaffold disposition, branding and delivery

Inspect all 24 `skill-databases/coreweave/` stubs and their CSV index. Record each source path, useful material merged into a real skill, final disposition and reason in `docs/SCAFFOLD-DISPOSITION.md`. Generic duplicates are retired; unsupported examples are removed rather than preserved as advice. Historical content remains recoverable through Git. Update discovery and ensure removed stubs cannot be republished by generation.

Keep `coreweave-pack` and the disclaimer everywhere. Preserve the agreed CI display title **UNOFFICIAL CI INTEGRATION FOR COREWEAVE** and stable skill identifiers. README links to CoreWeave's official distribution and describes complementary Day-2 value without claiming endorsement. Keep proposed commercial activity out of public technical records until separately authorized.

One PR on `fix/coreweave-operator-accuracy`, with small commits by goal. Existing accuracy drafts are preserved, then reconciled with the new requirements. Run canonical catalog regeneration and Freshie against the actual current authority; do not hand-edit grades, fake receipts or cancel a healthy long run. The PR table includes every skill, issue, change, safety level and distinct static/offline/behavioral/live statuses.

REL-CW-1: close a skill issue only with its accepted implementation/design decision, exact-head tests and merged PR evidence. Close retirement cases with destination/reason and a reopening condition. A design draft or static A does not close the implementation issue. Root #1732 stays open until its full acceptance is evidenced. Artifact publication/production validation have separate receipts; merge alone does not prove either.

## Skill inventory and traceability

Each entry below has a distinct objective, input/output contract, failure criteria and proposed test IDs. The GitHub child issue supplies live execution status; these files are design records, not a parallel task tracker.

| ID | Skill blueprint | Issue | Maximum workflow effect |
| --- | --- | --- | --- |
| CW-S01 | [coreweave-install-auth](../skills/coreweave-install-auth/docs/BLUEPRINT.md) | [#1820](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1820) | read-only |
| CW-S02 | [coreweave-hello-world](../skills/coreweave-hello-world/docs/BLUEPRINT.md) | [#1821](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1821) | creates billable resources |
| CW-S03 | [coreweave-local-dev-loop](../skills/coreweave-local-dev-loop/docs/BLUEPRINT.md) | [#1822](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1822) | read-only |
| CW-S04 | [coreweave-sdk-patterns](../skills/coreweave-sdk-patterns/docs/BLUEPRINT.md) | [#1823](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1823) | read-only |
| CW-S05 | [coreweave-core-workflow-a](../skills/coreweave-core-workflow-a/docs/BLUEPRINT.md) | [#1824](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1824) | creates billable resources |
| CW-S06 | [coreweave-core-workflow-b](../skills/coreweave-core-workflow-b/docs/BLUEPRINT.md) | [#1825](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1825) | creates billable resources |
| CW-S07 | [coreweave-common-errors](../skills/coreweave-common-errors/docs/BLUEPRINT.md) | [#1826](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1826) | read-only |
| CW-S08 | [coreweave-debug-bundle](../skills/coreweave-debug-bundle/docs/BLUEPRINT.md) | [#1827](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1827) | read-only |
| CW-S09 | [coreweave-security-basics](../skills/coreweave-security-basics/docs/BLUEPRINT.md) | [#1828](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1828) | read-only |
| CW-S10 | [coreweave-prod-checklist](../skills/coreweave-prod-checklist/docs/BLUEPRINT.md) | [#1829](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1829) | read-only |
| CW-S11 | [coreweave-upgrade-migration](../skills/coreweave-upgrade-migration/docs/BLUEPRINT.md) | [#1830](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1830) | creates billable resources |
| CW-S12 | [coreweave-deploy-integration](../skills/coreweave-deploy-integration/docs/BLUEPRINT.md) | [#1831](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1831) | creates billable resources |
| CW-S13 | [coreweave-performance-tuning](../skills/coreweave-performance-tuning/docs/BLUEPRINT.md) | [#1832](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1832) | creates billable resources |
| CW-S14 | [coreweave-cost-tuning](../skills/coreweave-cost-tuning/docs/BLUEPRINT.md) | [#1833](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1833) | read-only |
| CW-S15 | [coreweave-multi-env-setup](../skills/coreweave-multi-env-setup/docs/BLUEPRINT.md) | [#1834](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1834) | creates billable resources |
| CW-S16 | [coreweave-observability](../skills/coreweave-observability/docs/BLUEPRINT.md) | [#1835](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1835) | read-only |
| CW-S17 | [coreweave-incident-runbook](../skills/coreweave-incident-runbook/docs/BLUEPRINT.md) | [#1836](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1836) | read-only |
| CW-S18 | [coreweave-data-handling](../skills/coreweave-data-handling/docs/BLUEPRINT.md) | [#1837](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1837) | read-only |
| CW-S19 | [coreweave-enterprise-rbac](../skills/coreweave-enterprise-rbac/docs/BLUEPRINT.md) | [#1838](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1838) | read-only |
| CW-S20 | [coreweave-ci-integration](../skills/coreweave-ci-integration/docs/BLUEPRINT.md) | [#1839](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1839) | creates billable resources |
| CW-S21 | [coreweave-gpu-node-forensics](../skills/coreweave-gpu-node-forensics/docs/BLUEPRINT.md) | [#1840](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1840) | read-only |
| CW-S22 | [coreweave-fabric-diagnostics](../skills/coreweave-fabric-diagnostics/docs/BLUEPRINT.md) | [#1841](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1841) | read-only |
| CW-S23 | [coreweave-gpu-cost-leak-hunter](../skills/coreweave-gpu-cost-leak-hunter/docs/BLUEPRINT.md) | [#1842](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1842) | read-only |
| CW-S24 | [coreweave-cks-provisioning](../skills/coreweave-cks-provisioning/docs/BLUEPRINT.md) | [#1843](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1843) | creates billable resources |
| CW-S25 | [coreweave-caios-stage-model](../skills/coreweave-caios-stage-model/docs/BLUEPRINT.md) | [#1844](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1844) | creates billable resources |
| CW-S26 | [coreweave-workload-health](../skills/coreweave-workload-health/docs/BLUEPRINT.md) | [#1845](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1845) | read-only |

## Review state and next decisions

Scope approval is recorded in the conversation; it is not reviewer acceptance of these new designs. Technical/security reviewers, actual account compatibility and all expanded criterion results remain unresolved. Proceed with cost gates first, then the five priority upgrades and three gaps, reconcile scaffolds, and complete the pack-wide evidence. Do not send outreach or claim vendor approval from these records.

## Implementation evidence — 2026-11-05

The expanded implementation is present for review. [QUALITY.md](../QUALITY.md) and [offline-results.json](../offline-results.json) retain the actual offline coverage and source hashes. GitHub parent #1732 and its 26 child issues remain open for acceptance; a static grade is not a behavioral pass.

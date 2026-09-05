---
name: production-upgrade
description: |
  Upgrade an existing skill, plugin, agent, MCP integration, or agent-system
  package to a security-first production standard using pain research,
  architecture decisions, migration planning, deterministic implementation,
  adversarial tests, independent review, and revision-bound evidence. Use when
  modernizing a legacy capability or asking for Databricks-level diligence.
  Trigger with "production upgrade", "modernize this skill", "bring this pack
  to production quality", or "audit and rebuild this plugin".
allowed-tools: Read,Write,Edit
version: 1.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Agent Skills-compatible hosts; subagents and Beads are capability-detected with fail-closed fallback
tags: [production-upgrade, modernization, security, research, validation, beads]
---

# Production Upgrade

Run a risk-adjusted, evidence-bound modernization from discovery through a
pre-release maintainer checkpoint. The workflow is complete without a specific
model, subagent implementation, or task tracker, but it must honor stronger
project requirements when they exist.

## Overview

The quality bar comes from the Databricks rebuild: understand real operator
pain, decide architecture before implementation, move load-bearing logic into
deterministic code, preserve compatibility intentionally, and prove safety with
negative and adversarial evidence. Match the depth to risk rather than matching
another project's document count.

## When to use

Use for a legacy artifact, broad rewrite, breaking migration, unsafe integration,
or production-readiness claim. Do not trigger for a small typo, isolated bug fix,
routine dependency bump, or read-only status question unless the user explicitly
requests the full upgrade workflow.

## Prerequisites

- Target repository or artifact and its project instructions.
- Authority to research and prepare local changes. Publication, deployment,
  merge, destructive cleanup, and external messaging remain separate approvals.
- Current primary sources for externally defined contracts.

The pre-authorized `Read`, `Write`, and `Edit` capabilities apply only to local,
scoped implementation files. Network, shell, task-tracker, subagent, install,
and publication capabilities remain behind host and project approval.

## Orchestration

Use five focused roles. When the host supports isolated subagents, dispatch the
role packets under [references/roles](references/roles/) and have the coordinator
reconcile their evidence. Otherwise execute the same packets sequentially in the
main context. A same-identity or inline review is self-review, never independent.

| Role                    | Mutation authority       | Output                                           |
| ----------------------- | ------------------------ | ------------------------------------------------ |
| Researcher              | None                     | Source ledger, pain catalog, explicit gaps       |
| Architect               | None                     | Scope synthesis, decision record, migration plan |
| Implementation engineer | Local scoped writes only | Minimal implementation and focused tests         |
| Verification engineer   | None                     | Reproduced commands, results, and hashes         |
| Security adversary      | None                     | Threat-driven findings and exploit attempts      |

## Instructions

### 1. Recover context and establish authority

1. Read repository instructions, architecture owners, generated-file rules,
   current status, worktrees, active reviews, and existing task state.
2. If the repository uses Beads, follow
   [references/beads-workflow.md](references/beads-workflow.md): prime, search,
   create or reuse, claim before mutation, and attach receipts. Project policy
   can make Beads mandatory.
3. Preserve dirty work and contributor authorship. Isolate broad changes in a
   branch or worktree when available.
4. Record the exact initial revision and the actions currently authorized.

### 2. Research before designing

1. Audit the existing artifact, every active and retired capability, consumers,
   package identities, installation paths, and known defects.
2. Research current primary sources for product, API, protocol, security, and
   runtime contracts. Add community or issue evidence for real operator pain
   when accessible and appropriate.
3. Build a pain catalog: symptom, trigger, root cause, blast radius, current
   workaround, evidence, and the right agent primitive. Record source gaps
   rather than filling them with assumptions.
4. Compare at least one relevant production benchmark for methodology, then
   explain where narrower or deeper treatment is justified by risk.

### 3. Decide scope and safety

1. Consolidate capabilities around distinct operator outcomes, not quotas.
2. Write an architecture decision covering adopted, modified, and rejected
   alternatives; authority boundaries; compatibility; migration; rollback; and
   explicit non-goals.
3. Threat-model inputs, outputs, credentials, network destinations, file paths,
   dependencies, retries, mutations, reviewers, evidence, and publication.
4. Make offline or read-only behavior the default. Unknown contracts, statuses,
   fields, destinations, or permissions fail closed.
5. Put deterministic classification, arithmetic, validation, transformation,
   and policy decisions in reviewed scripts. Use model reasoning for synthesis
   and ambiguity, not for load-bearing calculations.

### 4. Plan and implement

1. Define measurable acceptance gates before editing. Include structure,
   behavior, security, migration, provenance, and release evidence.
2. Implement the smallest complete design. Keep the portable core independent
   of host adapters and avoid infrastructure that does not add verified
   capability.
3. Preserve IDs or provide a machine-readable migration map. Breaking behavior
   requires an explicit major-version decision and user-facing migration path.
4. Never generate plaintext secrets, remote-pipe installers, unbounded retries,
   silent destructive actions, fabricated provider responses, or blanket
   scanner waivers.

### 5. Validate proportionately

1. Run the narrowest focused tests first, then repository-required gates.
2. Cover positive, negative, edge, adversarial, failure, and rollback paths.
   Deliberately broken variants must fail the same gate when certification is
   claimed.
3. Validate generated projections, packaging file lists, installation from a
   disposable path, and removal or rollback where those surfaces changed.
4. Reproduce every material automated-review finding independently. Reviewer
   silence or billing failure is unavailable evidence, not approval.
5. Record evidence using
   [references/evidence-contract.md](references/evidence-contract.md) and audit
   it without executing recorded commands:

   ```bash
   python3 scripts/audit_evidence.py upgrade-evidence.json --root <repository>
   ```

### 6. Stop at the approval boundary

Report the exact candidate revision, changed surfaces, test results, unresolved
risks, reviewer status, migration impact, rollback, and publication state.
Do not commit, push, open or update a PR, merge, tag, publish, deploy, delete, or
message externally unless that action is authorized by the user and project
policy. High-risk release approval is bound to the exact revision; a changed
revision requires renewed approval.

## Output

Return a concise executive status plus links to the research, decision, threat
model, migration map, tests, and evidence manifest. Use these claim levels:

- `BLOCKED`: a required safety or authority boundary failed.
- `CANDIDATE`: implementation and local evidence exist; independent review or
  approval remains.
- `REVIEWED`: independent review is bound to the exact revision; release is not
  yet authorized.
- `RELEASE-READY`: all required gates and exact-revision authorization exist.

## Error handling

- Missing Beads when project policy requires it: stop before mutation.
- Missing subagents: execute role packets inline and label review self-review.
- Missing current primary source: constrain or remove the affected capability.
- Conflicting authorities: stop and resolve the conflict at the named owner.
- Failed test or unknown reviewer finding: remain `BLOCKED` or `CANDIDATE`;
  never average it into a score.
- Dirty unrelated work: preserve and isolate; do not reset or overwrite it.

## Examples

- A narrow API pack may need fewer documents than Databricks but still requires
  an official contract audit, threat model, migration map, adversarial tests,
  exact-revision evidence, and explicit research gaps.
- An MCP server with destructive methods requires stronger input, authorization,
  rollback, and live-boundary evidence than an offline read-only skill.
- A model-neutral skill can be manually used by any capable model, while named
  native support remains limited to harnesses with registry-backed receipts.

## Resources

- [Beads workflow](references/beads-workflow.md)
- [Evidence contract](references/evidence-contract.md)
- [Runtime portability](references/runtime-portability.md)
- [Specialist role packets](references/roles/)
- [Pain catalog template](templates/pain-catalog.md)
- [Decision record template](templates/decision-record.md)

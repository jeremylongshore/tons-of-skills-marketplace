# Palantir Foundry Operator Skill Pack

Evidence-backed Claude Code workflows for designing, building, securing, releasing, and operating Palantir Foundry systems.

## What this pack covers

The 24 skills separate the major Foundry operating surfaces instead of treating Palantir as one generic REST API:

- Python transforms, incremental transaction semantics, compute-engine selection, build checks, and metrics.
- Ontology modeling and generated OSDK applications, including bounded queries, Functions, validated Actions, and subscriptions.
- Platform SDK clients and Developer Console OAuth grants, scopes, resource restrictions, service users, and secret handling.
- Compute Modules, Developer Console applications, DevOps products, Marketplace installations, spaces, release channels, and rollback.
- Projects, group roles, mandatory controls, Ontology object/property security, log access, audit exports, and data governance.
- Production readiness, observability, incident response, migrations, limits, performance, and upgrade discipline.

Every skill includes a dated `references/official-docs.md` evidence map. Re-check those first-party sources and target-enrollment behavior before any live change.

## Installation

```bash
/plugin install palantir-pack@claude-code-plugins-plus
```

Or install one workflow from the public catalog:

```bash
npx skills add https://github.com/jeremylongshore/tons-of-skills-marketplace --skill palantir-install-auth
```

## Skills

| Skill | Operator job |
|---|---|
| `palantir-install-auth` | Choose generated OSDK or Platform SDK and configure least-privilege OAuth. |
| `palantir-hello-world` | Prove one bounded OSDK read and optional validation-only Action. |
| `palantir-local-dev-loop` | Combine synthetic unit tests, VS Code preview/debug, checks, and Foundry builds. |
| `palantir-sdk-patterns` | Implement pinned, bounded OSDK or Platform SDK client boundaries. |
| `palantir-core-workflow-a` | Build a Python transform pipeline with explicit incremental and compute contracts. |
| `palantir-core-workflow-b` | Build an Ontology application with queries, links, Functions, and Actions. |
| `palantir-common-errors` | Triage API, permission, throttling, resource, and transform failures. |
| `palantir-debug-bundle` | Produce minimal redacted API/build/module evidence for support. |
| `palantir-rate-limits` | Bound principal-level request rates, concurrency, queues, and retries. |
| `palantir-security-basics` | Establish least privilege across roles, controls, applications, logs, and exports. |
| `palantir-prod-checklist` | Run an exact-artifact, target-environment production gate. |
| `palantir-upgrade-migration` | Upgrade generated OSDKs, Platform SDKs, or products reversibly. |
| `palantir-ci-integration` | Use Foundry Code Repository checks, tests, pull requests, and dataset-impact review. |
| `palantir-deploy-integration` | Deploy through Developer Console/Marketplace, DevOps, or Compute Modules. |
| `palantir-webhooks-events` | Choose OSDK/WebSocket subscriptions or supported monitoring webhooks. |
| `palantir-performance-tuning` | Tune builds, queries, and modules from platform telemetry. |
| `palantir-cost-tuning` | Optimize transform and Compute Module usage without invented size bands. |
| `palantir-reference-architecture` | Design governed pipeline, Ontology, SDK, deployment, and operations layers. |
| `palantir-multi-env-setup` | Separate environments with spaces and promote DevOps products safely. |
| `palantir-observability` | Combine metrics, governed logs, monitoring, and audit evidence. |
| `palantir-incident-runbook` | Stabilize API, build, application, module, data, or release incidents. |
| `palantir-data-handling` | Govern sensitive data, propagation, Ontology policies, logs, exports, and retention. |
| `palantir-enterprise-rbac` | Design group/project roles plus mandatory and application controls. |
| `palantir-migration-deep-dive` | Migrate data and applications through dual-run, reconciliation, and cutover. |

## Non-negotiable boundaries

- Use the generated OSDK for the exact Developer Console application; do not invent Ontology entity names.
- Treat OAuth scopes, Developer Console restrictions, principal permissions, project roles, and mandatory controls as separate evidence.
- Treat preview, checks, full builds, metrics, logs, and audit logs as different surfaces.
- Never log, commit, or package bearer tokens, client secrets, protected object values, or raw datasets.
- Require explicit owner approval for production builds, Actions, access changes, exports, deployments, and rollback.
- Do not present external Cloud Run, generic webhook registration, fixed data-size bands, or handwritten SDK migrations as Palantir contracts.

## Primary documentation

- [Foundry developer documentation](https://www.palantir.com/docs/foundry/developers)
- [Developer API reference](https://www.palantir.com/docs/foundry/api-reference)
- [Ontology SDK](https://www.palantir.com/docs/foundry/ontology-sdk/overview)
- [Python transforms](https://www.palantir.com/docs/foundry/transforms-python/overview)
- [DevOps release management](https://www.palantir.com/docs/foundry/devops-release-management/overview)
- [Compute Modules](https://www.palantir.com/docs/foundry/compute-modules/overview)
- [Projects and roles](https://www.palantir.com/docs/foundry/security/projects-and-roles)

## License

MIT

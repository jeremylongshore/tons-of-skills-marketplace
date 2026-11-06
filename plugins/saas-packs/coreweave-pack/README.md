# Community GPU operations for CoreWeave

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

23 skills: three offline diagnostic tools and scoped operator guides for reviewing CKS access, workload releases, storage, security, recovery and cost assumptions.
The source remains MIT-licensed. Structural grades and offline fixtures do not establish production readiness, live account behavior or measured savings.

## Use CoreWeave’s official skills for provisioning

[CoreWeave’s official distribution](https://github.com/coreweave/skills) covers cluster/Node Pool creation, self-managed vLLM deployment, model loading into object storage and workload-health checks.
Install those through their own upstream distribution and review their current requirements and license.
This community pack does not mirror or redistribute those proprietary skills; its original operator diagnostics and review procedures complement them.

## Installation

```bash
/plugin install coreweave-pack@claude-code-plugins-plus
```

Use the existing compatibility identifiers below. The CI skill’s public title remains **UNOFFICIAL CI INTEGRATION FOR COREWEAVE**.

## Offline tools first

- GPU forensics: classify supplied Xid evidence into qualified recommendations; unknown or multi-GPU evidence stays inconclusive.
- Fabric review: distinguish actual NCCL transport from GPU-direct evidence and recognize Kubernetes request defaulting from RDMA limits.
- GPU usage and cost review: validate supplied numeric scenarios, separate billing-backed amounts from estimates, and avoid adding overlapping findings into promised savings.

The scripts do not invoke a cluster, provision capacity, reset hardware or call a model provider.
Python 3 is required; fabric YAML parsing also needs its pinned `scripts/requirements.txt` dependency in an isolated environment.

## Skills

| Public task | Stable identifier |
|---|---|
| [UNOFFICIAL CI INTEGRATION FOR COREWEAVE](skills/coreweave-ci-integration/SKILL.md) | `coreweave-ci-integration` |
| [CoreWeave Evidence-first workload triage](skills/coreweave-common-errors/SKILL.md) | `coreweave-common-errors` |
| [CoreWeave Inference deployment preflight](skills/coreweave-core-workflow-a/SKILL.md) | `coreweave-core-workflow-a` |
| [CoreWeave Training launch and recovery review](skills/coreweave-core-workflow-b/SKILL.md) | `coreweave-core-workflow-b` |
| [CoreWeave Cost experiment planning](skills/coreweave-cost-tuning/SKILL.md) | `coreweave-cost-tuning` |
| [CoreWeave Artifact integrity and storage review](skills/coreweave-data-handling/SKILL.md) | `coreweave-data-handling` |
| [CoreWeave Scoped support evidence](skills/coreweave-debug-bundle/SKILL.md) | `coreweave-debug-bundle` |
| [CoreWeave Manifest promotion review](skills/coreweave-deploy-integration/SKILL.md) | `coreweave-deploy-integration` |
| [CoreWeave Access-boundary review](skills/coreweave-enterprise-rbac/SKILL.md) | `coreweave-enterprise-rbac` |
| [CoreWeave Fabric Diagnostics](skills/coreweave-fabric-diagnostics/SKILL.md) | `coreweave-fabric-diagnostics` |
| [GPU usage and cost review for CoreWeave](skills/coreweave-gpu-cost-leak-hunter/SKILL.md) | `coreweave-gpu-cost-leak-hunter` |
| [CoreWeave GPU Node Forensics](skills/coreweave-gpu-node-forensics/SKILL.md) | `coreweave-gpu-node-forensics` |
| [CoreWeave GPU smoke-test review](skills/coreweave-hello-world/SKILL.md) | `coreweave-hello-world` |
| [CoreWeave Incident stabilization review](skills/coreweave-incident-runbook/SKILL.md) | `coreweave-incident-runbook` |
| [CoreWeave Access and identity verification](skills/coreweave-install-auth/SKILL.md) | `coreweave-install-auth` |
| [CoreWeave Local-to-staging review](skills/coreweave-local-dev-loop/SKILL.md) | `coreweave-local-dev-loop` |
| [CoreWeave Environment promotion boundaries](skills/coreweave-multi-env-setup/SKILL.md) | `coreweave-multi-env-setup` |
| [CoreWeave Signal and alert validation](skills/coreweave-observability/SKILL.md) | `coreweave-observability` |
| [CoreWeave Measured performance experiments](skills/coreweave-performance-tuning/SKILL.md) | `coreweave-performance-tuning` |
| [CoreWeave Release evidence review](skills/coreweave-prod-checklist/SKILL.md) | `coreweave-prod-checklist` |
| [CoreWeave Client boundary design](skills/coreweave-sdk-patterns/SKILL.md) | `coreweave-sdk-patterns` |
| [CoreWeave Workload security review](skills/coreweave-security-basics/SKILL.md) | `coreweave-security-basics` |
| [CoreWeave Migration and rollback planning](skills/coreweave-upgrade-migration/SKILL.md) | `coreweave-upgrade-migration` |

## Before live use

Select an owner-approved organization, context, namespace, resource name and evidence window.
Use a trusted cluster-specific kubeconfig from the approved secret store; Managed Auth kubeconfigs embed a token.
Discover current `node.kubernetes.io/instance-type` values instead of copying legacy GPU-class labels.
Read-only commands can still expose workload data; review and redact evidence before sharing.
Any deployment, benchmark, reset, resource deletion, data export or capacity/contract change requires its own approved scope and budget.

CoreWeave provides [cost/usage monitoring](https://docs.coreweave.com/observability/usage-monitoring) and [Mission Control MCP](https://docs.coreweave.com/observability/mission-control-mcp/reference/tools), including a FOCUS usage tool that returns quantities rather than dollars.
Rates, capacity plans and invoice reconciliation remain separate inputs; no universal discount, per-token ranking or savings percentage is claimed.

## Verification and limitations

See [QUALITY.md](QUALITY.md) and the retained offline-results receipt for actual tests, source hashes and remaining gaps.
No live CoreWeave account or paid model evaluation was used for this review.
The npm package version and plugin display version follow separate repository version contracts; they are intentionally not forced to match.

## Primary references

- [CKS scheduling](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling)
- [CKS Managed Auth](https://docs.coreweave.com/products/cks/auth-access/managed-auth/kubeconfig)
- [Managed lifecycle](https://docs.coreweave.com/platform/fleet-management/node-lifecycle/state-transitions)
- [RDMA configuration](https://docs.coreweave.com/products/networking/hpc-interconnect/use-gpudirect-rdma)
- [NVIDIA Xid catalog](https://docs.nvidia.com/deploy/xid-errors/latest/analyzing-xid-catalog.html)
- [Capacity plans](https://docs.coreweave.com/platform/capacity-plans)

## License

MIT for this community pack. Upstream linked projects retain their own licenses.

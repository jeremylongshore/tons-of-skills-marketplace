# CAST AI Operator Skill Pack

> 18 Grade-A Claude Code workflows for governed Kubernetes cost monitoring and autoscaling with CAST AI

This pack helps platform, SRE, FinOps, and security teams operate CAST AI without guessing API paths, chart topology, quota values, or savings claims. Every skill is a distinct decision or operating workflow, includes dated first-party source notes, and defaults to observation, planning, and bounded canaries before mutation.

## Install

```bash
/plugin install castai-pack@claude-code-plugins-plus
```

The public skills can also be discovered through the official Skills CLI from `jeremylongshore/tons-of-skills-marketplace`.

## Current Product Boundaries

- `castctl` is the recommended connection path for supported Kubernetes clusters.
- New connections use the unified `castai` umbrella Helm chart; legacy standalone releases can be consolidated with the documented migration workflow.
- Cost Monitoring is always enabled. Node Autoscaling and Workload Autoscaling are separate automation decisions.
- REST authentication uses `X-API-Key` and the regional US, EU, or India base. Enterprise child-organization calls also need `X-CastAI-Organization-Id`.
- Workload policies can control vertical recommendations and native `autoscaling/v2` HPAs. HPA ownership transfer is explicit and reviewable.
- Savings reports depend on baseline, adoption, time window, and pricing assumptions. They are reconciled rather than treated as billing truth.

## Skills

### Onboarding and Integration

| Skill | Operator outcome |
|-------|------------------|
| `castai-hello-world` | Prove one observation-only sandbox connection |
| `castai-install-auth` | Separate human, API, enterprise, region, and secret boundaries |
| `castai-core-workflow-a` | Onboard a cluster observation-first and establish a baseline |
| `castai-deploy-integration` | Deliver pinned CAST AI infrastructure through GitOps or Terraform |
| `castai-local-dev-loop` | Validate configuration offline before one sandbox experiment |
| `castai-ci-integration` | Build credential-free required checks and an isolated live probe |

### Autoscaling and Cost

| Skill | Operator outcome |
|-------|------------------|
| `castai-core-workflow-b` | Roll out node and workload automation through a canary |
| `castai-performance-tuning` | Tune vertical, horizontal, and node controls against SLOs |
| `castai-cost-tuning` | Reconcile spend, available savings, realized savings, and pricing |
| `castai-rate-limits` | Bound endpoint-specific concurrency, retries, polling, and deadlines |

### Reliability and Governance

| Skill | Operator outcome |
|-------|------------------|
| `castai-common-errors` | Triage failures by connection, node, workload, disruption, or reporting plane |
| `castai-debug-bundle` | Produce a bounded and redacted escalation bundle |
| `castai-prod-checklist` | Make an evidence-linked production PASS or HOLD decision |
| `castai-security-basics` | Review API, RBAC, cloud IAM, Kvisor, network, and data permissions |
| `castai-upgrade-migration` | Upgrade the umbrella chart or migrate standalone releases safely |
| `castai-webhooks-events` | Operate hardened notifications with Audit-log reconciliation |
| `castai-reference-architecture` | Map real trust zones, components, controls, and failure paths |
| `castai-sdk-patterns` | Build a narrow contract-first REST adapter or choose Terraform instead |

## Recommended Sequence

1. Use `castai-reference-architecture` and `castai-security-basics` to establish ownership and permissions.
2. Use `castai-install-auth`, then `castai-hello-world` or `castai-core-workflow-a` for observation-first onboarding.
3. Use `castai-core-workflow-b` for a measured automation canary.
4. Use the cost, performance, CI, readiness, and upgrade skills for ongoing operations.

## Source Policy

The skills cite current first-party CAST AI documentation and the live API specification. Exact versions, endpoints, policy thresholds, cloud permissions, and release commands must still be derived from the target environment and pinned repository configuration.

## Links

- [CAST AI documentation](https://docs.cast.ai/docs/getting-started)
- [Connect with castctl](https://docs.cast.ai/docs/connect-with-castctl)
- [Hosted components](https://docs.cast.ai/docs/hosted-components)
- [API access](https://docs.cast.ai/docs/api-access)
- [API specification](https://api.cast.ai/spec/)
- [Terraform provider](https://registry.terraform.io/providers/castai/castai/latest/docs)
- [CAST AI GitHub organization](https://github.com/castai)
- [CAST AI status](https://status.cast.ai)

## License

MIT

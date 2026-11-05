---
name: coreweave-enterprise-rbac
description: 'Configure RBAC and namespace isolation for CoreWeave multi-team GPU
  access.

  Use when managing team permissions, isolating GPU quotas,

  or implementing namespace-level access control.

  Trigger with phrases like "coreweave rbac", "coreweave permissions",

  "coreweave namespace isolation", "coreweave team access".

  '
allowed-tools: Read, Write, Edit, Bash(kubectl:*), Grep
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- gpu-cloud
- kubernetes
- inference
- coreweave
compatibility: Designed for Claude Code
---
# CoreWeave Enterprise RBAC

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

CoreWeave runs GPU workloads on Kubernetes, so RBAC maps directly to K8s namespace isolation and ResourceQuotas. Each team gets a dedicated namespace with GPU limits, storage caps, and network policies. This prevents noisy-neighbor problems where one team's training job starves another's inference service. SOC 2 and HIPAA workloads require namespace-level audit logging and team-scoped API key rotation.

## Prerequisites

- A verified human or workload identity group from the organization identity provider.
- Cluster-admin approval for namespace, quota, and RoleBinding changes.
- A team owner, approved GPU quota, and data-classification decision for the namespace.

## Instructions

1. Create a namespace per team and apply ResourceQuota and NetworkPolicy before
   granting workload permissions.
2. Bind an IdP group to the smallest suitable ClusterRole; do not bind individual
   users or reuse a cluster-wide `edit` role without a documented exception.
3. Run a SubjectAccessReview for the intended verbs and resources, then retain the
   redacted decision and audit entry with the access request.
4. Review bindings and service-account tokens on a regular schedule; remove access
   promptly when a team, project, or incident requires it.

## Role Hierarchy

| Role | Permissions | Scope |
|------|------------|-------|
| Cluster Admin | Full CKS control, namespace creation, quota management | All namespaces |
| Team Lead | Deploy workloads, manage team API keys, adjust pod limits | Own namespace |
| ML Engineer | Launch jobs, access PVCs, view logs | Own namespace |
| Inference Operator | Deploy/scale inference endpoints, read metrics | Own namespace |
| Viewer | Read-only pod status, logs, GPU utilization metrics | Own namespace |

## Permission Check

```typescript
import { KubeConfig, RbacAuthorizationV1Api } from '@kubernetes/client-node';

async function checkNamespaceAccess(user: string, namespace: string, verb: string, resource: string): Promise<boolean> {
  const kc = new KubeConfig();
  kc.loadFromDefault();
  const rbac = kc.makeApiClient(RbacAuthorizationV1Api);
  const review = { apiVersion: 'authorization.k8s.io/v1', kind: 'SubjectAccessReview',
    spec: { user, resourceAttributes: { namespace, verb, resource } } };
  const result = await rbac.createSubjectAccessReview(review);
  return result.body.status?.allowed ?? false;
}
```

## Role Assignment

```typescript
async function assignTeamNamespace(team: string, group: string, gpuLimit: number): Promise<void> {
  await kubectl(`create namespace ${team}`);
  await kubectl(`create resourcequota ${team}-gpu --namespace=${team} --hard=requests.nvidia.com/gpu=${gpuLimit}`);
  await kubectl(`create rolebinding ${team}-access --namespace=${team} --clusterrole=edit --group=${group}`);
  console.log(`Namespace ${team} created with ${gpuLimit} GPU quota bound to ${group}`);
}

async function revokeAccess(team: string, binding: string): Promise<void> {
  await kubectl(`delete rolebinding ${binding} --namespace=${team}`);
}
```

## Audit Logging

```typescript
interface CoreWeaveAuditEntry {
  timestamp: string; user: string; namespace: string;
  action: 'gpu_request' | 'deploy' | 'scale' | 'delete' | 'quota_change';
  resource: string; gpuCount?: number; result: 'allowed' | 'denied';
}

function logAccess(entry: CoreWeaveAuditEntry): void {
  console.log(JSON.stringify({ ...entry, cluster: process.env.CW_CLUSTER_ID }));
}
```

## RBAC Checklist

- [ ] Each team has a dedicated namespace with ResourceQuota
- [ ] GPU limits set per namespace to prevent resource starvation
- [ ] RoleBindings use AD/OIDC groups, not individual users
- [ ] Network policies isolate namespace traffic
- [ ] API keys scoped to team namespace, rotated quarterly
- [ ] Viewer role assigned to finance/management for cost visibility
- [ ] Audit logging enabled for all GPU allocation events

## Error Handling

| Issue | Cause | Fix |
|-------|-------|-----|
| `Forbidden: GPU quota exceeded` | Namespace quota reached | Increase ResourceQuota or free idle pods |
| `RoleBinding not found` | Group name mismatch with IdP | Verify AD/OIDC group name matches RoleBinding subject |
| `Namespace not found` | Team namespace not provisioned | Run namespace creation script before role assignment |
| `SubjectAccessReview denied` | Missing ClusterRole binding | Check if ClusterRole exists and verb is permitted |

## Output

- An isolated team namespace with an enforced GPU quota and network boundary.
- Least-privilege group bindings with a recorded access review and audit trail.
- A repeatable revocation path for a compromised identity or completed project.

## Examples

Confirm a deployment identity can create Jobs only in its team namespace before
releasing a workload:

```bash
kubectl auth can-i create jobs.batch \
  --as=system:serviceaccount:research:trainer \
  --namespace=research
kubectl auth can-i create jobs.batch \
  --as=system:serviceaccount:research:trainer \
  --namespace=production
```

The expected result is `yes` only for `research`. If the second check is allowed,
remove the over-broad binding, re-run both checks, and preserve the redacted audit
record before resuming deployments.

## Resources

- [CoreWeave CKS](https://docs.coreweave.com/docs/products/cks)
- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

## Next Steps

See `coreweave-security-basics`.

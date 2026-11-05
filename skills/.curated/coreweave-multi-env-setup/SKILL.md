---
name: coreweave-multi-env-setup
description: 'Configure CoreWeave across development, staging, and production environments.

  Use when setting up multi-environment GPU infrastructure, separating namespaces,

  or managing per-environment GPU quotas.

  Trigger with phrases like "coreweave environments", "coreweave staging",

  "coreweave multi-env", "coreweave namespace setup".

  '
allowed-tools: Read, Write, Edit, Bash(kubectl:*), Bash(kustomize:*), Grep
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
# CoreWeave Multi-Environment Setup

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

CoreWeave GPU cloud requires strict environment separation to control infrastructure costs and prevent resource contention. Each environment maps to an isolated Kubernetes namespace with its own GPU quota, scaling policy, and access controls. Development uses cheaper GPU tiers for iteration speed, staging mirrors production GPU types for accurate benchmarking, and production runs full-scale with no scale-to-zero to guarantee inference latency SLAs.

## Environment Configuration

## Prerequisites

- Separate, approved namespaces and service identities for development, staging, and production.
- Environment-specific secrets injected by a secrets manager, never committed `.env` files.
- A promotion owner, staging evaluation gate, and production rollback manifest.

## Instructions

1. Define overlays that differ only in reviewed capacity, endpoint, and namespace values.
2. Validate required variables and secret references before applying an overlay.
3. Promote dev to staging, run the service evaluation, then use a controlled production rollout.
4. Roll back the production overlay on an SLO, quality, or security-gate failure; do not copy staging credentials into production.

```typescript
const coreweaveConfig = (env: string) => ({
  development: {
    namespace: "app-dev", apiEndpoint: process.env.CW_API_ENDPOINT_DEV!,
    token: process.env.CW_TOKEN_DEV!, gpuType: "L40", scaleToZero: true, replicas: [0, 1],
  },
  staging: {
    namespace: "app-staging", apiEndpoint: process.env.CW_API_ENDPOINT_STG!,
    token: process.env.CW_TOKEN_STG!, gpuType: "A100_PCIE_40GB", scaleToZero: true, replicas: [0, 2],
  },
  production: {
    namespace: "app-prod", apiEndpoint: process.env.CW_API_ENDPOINT_PROD!,
    token: process.env.CW_TOKEN_PROD!, gpuType: "A100_PCIE_80GB", scaleToZero: false, replicas: [2, 10],
  },
}[env]);
```

## Environment Files

```text
# Per-env files: .env.development, .env.staging, .env.production
CW_API_ENDPOINT_{DEV|STG|PROD}=https://k8s.{ord1|ord1|las1}.coreweave.com
CW_TOKEN_{DEV|STG|PROD}=<service-account-token>
CW_NAMESPACE={app-dev|app-staging|app-prod}
CW_GPU_TYPE={L40|A100_PCIE_40GB|A100_PCIE_80GB}
```

## Environment Validation

```typescript
function validateCoreWeaveEnv(env: string): void {
  const required = ["CW_API_ENDPOINT", "CW_TOKEN", "CW_NAMESPACE", "CW_GPU_TYPE"];
  const suffix = { development: "_DEV", staging: "_STG", production: "_PROD" }[env];
  const missing = required
    .map((k) => (k.includes("NAMESPACE") ? k : `${k}${suffix}`))
    .filter((k) => !process.env[k]);
  if (missing.length) throw new Error(`Missing env vars for ${env}: ${missing.join(", ")}`);
}
```

## Promotion Workflow

```bash
# 1. Validate model in dev namespace
kubectl -n app-dev get inferenceservice my-model -o jsonpath='{.status.conditions}'

# 2. Apply staging overlay with production GPU type
kustomize build k8s/overlays/staging | kubectl apply -f -

# 3. Run inference benchmarks against staging endpoint
curl -X POST https://staging.myapp.coreweave.cloud/v1/predict -d @test-payload.json

# 4. Promote to production (blue-green via namespace switch)
kustomize build k8s/overlays/prod | kubectl apply -f -
kubectl -n app-prod rollout status deployment/my-model
```

## Environment Matrix

| Setting | Dev | Staging | Prod |
|---------|-----|---------|------|
| GPU Type | L40 | A100 40GB | A100 80GB |
| Scale-to-Zero | Yes | Yes | No |
| Replicas | 0-1 | 0-2 | 2-10 |
| Namespace | app-dev | app-staging | app-prod |
| Region | ord1 | ord1 | las1 |
| Spot Instances | Yes | No | No |

## Error Handling

| Issue | Cause | Fix |
|-------|-------|-----|
| GPU quota exceeded | Namespace limit reached | Request quota increase via CW support portal |
| Pod stuck Pending | GPU type unavailable in region | Check `kubectl describe node` for capacity; switch region |
| Scale-to-zero not waking | HPA misconfigured | Verify `minReplicas: 0` and KEDA scaler settings |
| Namespace access denied | RBAC not applied to overlay | Apply `RoleBinding` in kustomize overlay |

## Output

- Environment-isolated manifests, identities, and quotas with a documented promotion path.
- A redacted validation and rollout receipt for each environment.
- A production rollback path that preserves the prior known-good revision.

## Examples

Validate a staging overlay server-side before rollout, then wait for its deployment:

```bash
kustomize build k8s/overlays/staging | kubectl apply --dry-run=server -f -
kustomize build k8s/overlays/staging | kubectl apply -f -
kubectl -n app-staging rollout status deployment/my-model --timeout=10m
```

If the staging result fails its signed gate, stop promotion and restore the prior staging revision. Keep credentials out of terminal history, logs, and overlay files.

## Resources

- [CoreWeave CKS](https://docs.coreweave.com/docs/products/cks)

## Next Steps

See `coreweave-deploy-integration`.

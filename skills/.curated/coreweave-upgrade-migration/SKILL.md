---
name: coreweave-upgrade-migration
description: 'Upgrade CoreWeave deployments and migrate between GPU types.

  Use when migrating from A100 to H100, upgrading CUDA versions,

  or updating inference server versions.

  Trigger with phrases like "upgrade coreweave", "coreweave gpu migration",

  "coreweave cuda upgrade", "migrate coreweave".

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
# CoreWeave Upgrade & Migration

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

CoreWeave is a GPU-specialized cloud provider running Kubernetes-native infrastructure. Migrations involve upgrading between GPU instance types (A100 to H100), updating CUDA driver versions, and handling Kubernetes API version changes across namespaces. Tracking API versions is critical because CoreWeave's instance type labels and resource quotas change between platform releases, and deploying to a deprecated instance class will cause scheduling failures.

## Version Detection

```typescript
import { KubeConfig, CoreV1Api } from "@kubernetes/client-node";

async function detectCoreWeaveVersion(): Promise<void> {
  const kc = new KubeConfig();
  kc.loadFromDefault();
  const k8sApi = kc.makeApiClient(CoreV1Api);

  // Check current namespace GPU allocations
  const pods = await k8sApi.listNamespacedPod("my-namespace");
  for (const pod of pods.body.items) {
    const gpuClass = pod.spec?.nodeSelector?.["gpu.nvidia.com/class"];
    const cudaVersion = pod.metadata?.labels?.["cuda-version"];
    console.log(`Pod ${pod.metadata?.name}: GPU=${gpuClass}, CUDA=${cudaVersion}`);
  }

  // Detect deprecated instance types
  const deprecated = ["A100_PCIE_40GB", "V100_PCIE_16GB", "RTX_A5000"];
  const activeGpus = pods.body.items
    .map((p) => p.spec?.nodeSelector?.["gpu.nvidia.com/class"])
    .filter(Boolean);
  const stale = activeGpus.filter((g) => deprecated.includes(g!));
  if (stale.length > 0) console.warn(`Deprecated GPU types in use: ${stale.join(", ")}`);
}
```

## Migration Checklist

- [ ] Review CoreWeave release notes for deprecated instance types
- [ ] Audit all deployments for `gpu.nvidia.com/class` node selectors
- [ ] Verify CUDA version compatibility with target GPU (see matrix below)
- [ ] Update container base images to match new CUDA/cuDNN requirements
- [ ] Test inference latency on new GPU type in staging namespace
- [ ] Update resource requests (`nvidia.com/gpu`) for new instance memory
- [ ] Migrate persistent volumes if switching regions or availability zones
- [ ] Update Kubernetes API version in manifests (e.g., `apps/v1` changes)
- [ ] Validate HPA scaling behavior on new instance type throughput
- [ ] Run canary deployment with traffic split before full cutover

## Schema Migration

```typescript
// CoreWeave instance type labels changed in 2025 platform update
// Old: gpu.nvidia.com/class: "A100_PCIE_80GB"
// New: gpu.nvidia.com/class: "H100_SXM5_80GB"

interface DeploymentMigration {
  oldSelector: Record<string, string>;
  newSelector: Record<string, string>;
  cudaMinVersion: string;
}

const GPU_MIGRATIONS: DeploymentMigration[] = [
  {
    oldSelector: { "gpu.nvidia.com/class": "A100_PCIE_80GB" },
    newSelector: { "gpu.nvidia.com/class": "H100_SXM5_80GB" },
    cudaMinVersion: "12.4",
  },
  {
    oldSelector: { "gpu.nvidia.com/class": "A100_SXM4_80GB" },
    newSelector: { "gpu.nvidia.com/class": "H100_SXM5_80GB" },
    cudaMinVersion: "12.4",
  },
];

function migrateNodeSelector(manifest: any, migration: DeploymentMigration): any {
  const selector = manifest.spec?.template?.spec?.nodeSelector;
  if (!selector) return manifest;
  for (const [key, oldVal] of Object.entries(migration.oldSelector)) {
    if (selector[key] === oldVal) {
      selector[key] = migration.newSelector[key];
    }
  }
  return manifest;
}
```

## Rollback Strategy

## Prerequisites

- A versioned manifest, compatible CUDA/image matrix, and capacity confirmation for the target GPU or cluster change.
- Staging evaluation evidence, named migration owner, and a verified previous deployment revision.
- Backup/retention approval for any PVC, checkpoint, or model-artifact move.

## Instructions

1. Inventory current selectors, images, API versions, volumes, quotas, and service SLOs.
2. Update the manifest in staging, validate server-side, and run compatibility and performance checks.
3. Promote through a bounded canary only after the readiness, quality, latency, and integrity gates pass.
4. Use the prior immutable revision on any failed gate; do not delete old data or nodes until the observation period closes.

```typescript
import { AppsV1Api, KubeConfig } from "@kubernetes/client-node";

async function rollbackDeployment(namespace: string, name: string): Promise<void> {
  const kc = new KubeConfig();
  kc.loadFromDefault();
  const appsApi = kc.makeApiClient(AppsV1Api);

  // Kubernetes rollout undo — reverts to previous revision
  const deployment = await appsApi.readNamespacedDeployment(name, namespace);
  const currentRevision = deployment.body.metadata?.annotations?.["deployment.kubernetes.io/revision"];
  console.log(`Rolling back ${name} from revision ${currentRevision}`);

  // Patch to trigger rollback via revision annotation
  await appsApi.patchNamespacedDeployment(name, namespace, {
    spec: { template: { metadata: { annotations: { "kubectl.kubernetes.io/restartedAt": new Date().toISOString() } } } },
  }, undefined, undefined, undefined, undefined, undefined, { headers: { "Content-Type": "application/strategic-merge-patch+json" } });
  console.log(`Rollback initiated for ${name} in ${namespace}`);
}
```

## Error Handling

| Migration Issue | Symptom | Fix |
|----------------|---------|-----|
| GPU class not schedulable | Pod stuck in `Pending` with `Insufficient nvidia.com/gpu` | Verify instance type exists in target region; check quota |
| CUDA version mismatch | Container crashes with `CUDA driver version is insufficient` | Rebuild container with CUDA matching target GPU driver |
| Namespace quota exceeded | `Forbidden: exceeded quota` on deployment | Request quota increase for new instance type via CoreWeave dashboard |
| PVC migration failure | `VolumeAttachment` timeout on new node | Detach old PVC, recreate in target availability zone |
| API version deprecated | `no matches for kind "Deployment" in version "extensions/v1beta1"` | Update manifest to `apps/v1` and adjust spec fields |

## Output

- A reviewed migration plan with compatibility results, capacity decision, owner, and rollback revision.
- A staged/canary receipt proving readiness, SLO, and artifact-integrity checks.
- A reversible fallback that preserves the old workload and approved data until sign-off.

## Examples

Test the target manifest in staging before moving a production selector:

```bash
kubectl -n inference-staging apply --dry-run=server -f migration.yaml
kubectl -n inference-staging apply -f migration.yaml
kubectl -n inference-staging rollout status deployment/inference --timeout=15m
```

If CUDA compatibility, scheduling, or the evaluation gate fails, undo the staging revision and stop promotion. Do not change production affinity or delete the old PVC to make a migration appear complete.

## Resources

- [CoreWeave GPU Instances](https://docs.coreweave.com/docs/platform/instances/gpu-instances)
- CoreWeave Kubernetes Docs
- [CoreWeave Changelog](https://docs.coreweave.com/docs/release-notes)

## Next Steps

For CI/CD pipeline integration, see `coreweave-ci-integration` (UNOFFICIAL CI INTEGRATION FOR COREWEAVE).

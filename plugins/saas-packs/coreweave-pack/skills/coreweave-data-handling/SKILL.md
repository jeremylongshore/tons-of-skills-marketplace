---
name: coreweave-data-handling
description: 'Handle training data and model artifacts on CoreWeave persistent storage.

  Use when managing large datasets, configuring storage classes,

  or implementing data pipelines for GPU workloads.

  Trigger with phrases like "coreweave data", "coreweave storage",

  "coreweave pvc", "coreweave dataset management".

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
# CoreWeave Data Handling

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

CoreWeave GPU cloud workloads involve large-scale data artifacts: model weights (multi-GB safetensors/GGUF), training datasets (parquet, TFRecord, WebDataset), checkpoint snapshots, and inference cache volumes. Data flows through Kubernetes PersistentVolumeClaims backed by region-specific storage classes. Compliance requires encryption at rest via the storage driver, namespace-scoped RBAC for volume access, and audit logging for any data egress from GPU nodes.

## Prerequisites

- Approved data classification, retention schedule, and region for the artifact.
- A namespace-scoped service account, encrypted storage class, and approved destination.
- Expected artifact size and SHA-256 from a trusted source before import.

## Instructions

1. Create or select an encrypted PVC in the approved region and grant its mount only
   to the intended namespace service account.
2. Import artifacts using a short-lived job; verify the expected SHA-256 before any
   training or serving workload consumes them.
3. Export only to a reviewed destination, preserve the checksum and data-owner
   approval, and enforce the retention policy for checkpoints and datasets.
4. Record storage provisioning, access changes, deletion, and external egress in the
   audit system without copying sensitive artifact contents into logs.

## Data Classification

| Data Type | Sensitivity | Retention | Encryption |
|-----------|-------------|-----------|------------|
| Model weights | Medium | Until deprecated | AES-256 at rest |
| Training datasets | High (may contain PII) | Per data license | AES-256 + TLS in transit |
| Checkpoint snapshots | Medium | 30 days post-training | AES-256 at rest |
| Inference cache | Low | Session/TTL | Volume-level encryption |
| HuggingFace tokens | Critical | Rotate quarterly | K8s Secret + KMS |

## Data Import

```typescript
import { KubeConfig, BatchV1Api } from '@kubernetes/client-node';

async function importDataset(pvcName: string, sourceUrl: string, namespace: string) {
  const kc = new KubeConfig();
  kc.loadFromDefault();
  const batch = kc.makeApiClient(BatchV1Api);
  const job = {
    metadata: { name: `import-${Date.now()}`, namespace },
    spec: { template: { spec: {
      restartPolicy: 'Never',
      containers: [{ name: 'loader', image: 'python:3.11-slim',
        command: ['python3', '-c', `
import urllib.request, hashlib
dest = '/data/dataset.tar.gz'
urllib.request.urlretrieve('${sourceUrl}', dest)
print(f"SHA256: {hashlib.sha256(open(dest,'rb').read()).hexdigest()}")`],
        volumeMounts: [{ name: 'storage', mountPath: '/data' }],
      }],
      volumes: [{ name: 'storage', persistentVolumeClaim: { claimName: pvcName } }],
    }}}
  };
  await batch.createNamespacedJob(namespace, { body: job });
}
```

## Data Export

```typescript
async function exportCheckpoint(pvcName: string, destBucket: string, ns: string) {
  // Validate export destination is in approved region list
  const APPROVED_REGIONS = ['us-east-1', 'us-central-1', 'eu-west-1'];
  const region = destBucket.split('-').slice(0, 3).join('-');
  if (!APPROVED_REGIONS.some(r => destBucket.includes(r))) {
    throw new Error(`Export blocked: ${region} not in approved regions`);
  }
  // Stream from PVC → object storage with integrity check
  const exportCmd = `tar czf - /models | gsutil cp - gs://${destBucket}/export.tar.gz`;
  console.log(`Exporting from PVC ${pvcName} to ${destBucket}`);
  return exportCmd;
}
```

## Data Validation

```typescript
interface ModelArtifact {
  name: string; format: 'safetensors' | 'gguf' | 'bin' | 'pt';
  sizeBytes: number; sha256: string;
}

function validateArtifact(artifact: ModelArtifact): string[] {
  const errors: string[] = [];
  if (!artifact.name || artifact.name.length > 255) errors.push('Invalid artifact name');
  if (artifact.sizeBytes <= 0) errors.push('Size must be positive');
  if (!/^[a-f0-9]{64}$/.test(artifact.sha256)) errors.push('Invalid SHA-256 hash');
  if (!['safetensors', 'gguf', 'bin', 'pt'].includes(artifact.format)) errors.push(`Unsupported format`);
  return errors;
}
```

## Compliance

- [ ] All PVCs use encrypted storage classes (AES-256 at rest)
- [ ] HuggingFace and API tokens stored in Kubernetes Secrets with KMS encryption
- [ ] Namespace-scoped RBAC restricts volume mount access to authorized workloads
- [ ] Data egress from GPU nodes logged via network policy audit
- [ ] Training datasets with PII processed only in approved regions (data residency)
- [ ] Checkpoint retention enforced via CronJob garbage collection (30-day default)
- [ ] SOC 2 Type II audit trail for all storage provisioning and deletion events

## Error Handling

| Issue | Cause | Fix |
|-------|-------|-----|
| PVC pending indefinitely | Storage class unavailable in region | Check `kubectl get sc` and switch to available class |
| Download job OOMKilled | Dataset exceeds container memory limit | Increase resource limits or use streaming download |
| Permission denied on volume | RBAC misconfigured for namespace | Verify ServiceAccount has PVC access via RoleBinding |
| Checksum mismatch after import | Partial transfer or corruption | Re-run import job; enable retry with backoff |
| Secret not found | KMS key rotation or namespace mismatch | Verify secret exists in target namespace with `kubectl get secret` |

## Output

- An encrypted, namespace-scoped storage path with validated artifact integrity.
- A redacted import/export receipt containing source/destination approval, checksum,
  retention, and data-owner information.
- A reversible failure path that prevents corrupted or unauthorized data from being mounted.

## Examples

Import only a manifest-approved artifact and verify its checksum inside the isolated
job before promoting it to a serving or training workload:

```bash
kubectl -n research apply -f dataset-import-job.yaml
kubectl -n research wait --for=condition=complete job/dataset-import --timeout=30m
kubectl -n research logs job/dataset-import | grep SHA256
```

If the checksum differs, quarantine the PVC content, retain the redacted job receipt,
and reacquire the artifact from the approved source. Do not retry into a production
volume or disable integrity verification.

## Resources

- CoreWeave Storage Docs
- [Kubernetes PVC Reference](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)

## Next Steps

See `coreweave-security-basics`.

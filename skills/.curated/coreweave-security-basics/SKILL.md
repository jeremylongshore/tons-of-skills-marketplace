---
name: coreweave-security-basics
description: 'Secure CoreWeave deployments with RBAC, network policies, and secrets
  management.

  Use when hardening GPU workloads, managing model access,

  or configuring namespace isolation.

  Trigger with phrases like "coreweave security", "coreweave rbac",

  "secure coreweave", "coreweave secrets".

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
# CoreWeave Security Basics

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

CoreWeave provides bare-metal GPU cloud on Kubernetes. Security concerns center on compute credential management (kubeconfig, deploy tokens), network isolation between inference workloads, secrets for model registry access (HuggingFace, container registries), and protecting sensitive training data on persistent volumes. A compromised namespace can expose GPU resources, model weights, and customer inference data.

## Prerequisites

- A named namespace owner and a current data classification for the workload.
- Secrets-manager access for deployment credentials; no credentials in manifests or git.
- Authority to apply Kubernetes policies in the target namespace and an approved rollback plan.

## Instructions

1. Store API, registry, and model credentials in the approved secrets manager and
   mount only the minimum secret into the intended workload.
2. Apply namespace-scoped RBAC, ResourceQuota, and default-deny NetworkPolicy before
   exposing an inference endpoint.
3. Validate images and request payloads in CI, then test webhook signatures with a
   known valid and invalid payload without logging raw secrets.
4. Review access events and rotate/revoke the affected secret after suspected exposure.

## API Key Management

```typescript
import { KubeConfig, CoreV1Api } from "@kubernetes/client-node";

function createCoreWeaveClient(): CoreV1Api {
  const apiKey = process.env.COREWEAVE_API_KEY;
  if (!apiKey) {
    throw new Error("Missing COREWEAVE_API_KEY — set via secrets manager");
  }
  const kc = new KubeConfig();
  kc.loadFromDefault();
  const api = kc.makeApiClient(CoreV1Api);
  // Never log kubeconfig or API key contents
  console.log("CoreWeave client initialized for namespace:", process.env.CW_NAMESPACE);
  return api;
}
```

## Webhook Signature Verification

```typescript
import crypto from "crypto";
import { Request, Response, NextFunction } from "express";

function verifyCoreWeaveWebhook(req: Request, res: Response, next: NextFunction): void {
  const signature = req.headers["x-coreweave-signature"] as string;
  const secret = process.env.COREWEAVE_WEBHOOK_SECRET!;
  const expected = crypto.createHmac("sha256", secret).update(req.body).digest("hex");
  const supplied = Buffer.from(signature ?? "");
  const expectedBuffer = Buffer.from(expected);
  if (supplied.length !== expectedBuffer.length || !crypto.timingSafeEqual(supplied, expectedBuffer)) {
    res.status(401).send("Invalid signature");
    return;
  }
  next();
}
```

## Input Validation

```typescript
import { z } from "zod";

const WorkloadRequestSchema = z.object({
  namespace: z.string().regex(/^[a-z0-9-]+$/).max(63),
  gpu_type: z.enum(["A100_80GB", "A100_40GB", "H100_80GB", "RTX_A6000"]),
  gpu_count: z.number().int().min(1).max(8),
  image: z.string().regex(/^[a-z0-9.\-/]+:[a-z0-9.\-]+$/),
  model_id: z.string().min(1).max(200),
});

function validateWorkloadRequest(data: unknown) {
  return WorkloadRequestSchema.parse(data);
}
```

## Data Protection

```typescript
const CW_SENSITIVE_FIELDS = ["kubeconfig", "hf_token", "registry_password", "api_key", "model_weights_url"];

function redactCoreWeaveLog(record: Record<string, unknown>): Record<string, unknown> {
  const redacted = { ...record };
  for (const field of CW_SENSITIVE_FIELDS) {
    if (field in redacted) redacted[field] = "[REDACTED]";
  }
  return redacted;
}
```

## Security Checklist

- [ ] Kubeconfig stored in secrets manager, never in repos
- [ ] Kubernetes Secrets used for model tokens (not env vars in YAML)
- [ ] Network policies restrict inference endpoint access
- [ ] RBAC limits namespace access per team
- [ ] Container images scanned for CVEs before deployment
- [ ] PVCs encrypted at rest for training data
- [ ] GPU workload namespaces isolated with NetworkPolicy
- [ ] Deploy tokens scoped per-namespace, not cluster-wide

## Error Handling

| Vulnerability | Risk | Mitigation |
|---|---|---|
| Leaked kubeconfig | Full cluster access, GPU resource theft | Secrets manager + RBAC scoping |
| Open inference endpoints | Unauthorized model access | NetworkPolicy ingress rules |
| Unscanned container images | CVE exploitation in GPU pods | CI image scanning before deploy |
| Overly broad RBAC | Cross-namespace data leakage | Per-team namespace RBAC bindings |
| Unencrypted PVCs | Training data exposure | Encrypted storage classes |

## Output

- A namespace-level hardening baseline covering secrets, RBAC, network isolation,
  image validation, and protected persistent storage.
- A safe signature-validation and input-validation path that rejects malformed
  requests without leaking credentials or workload data.
- An incident response path that revokes access, preserves redacted evidence, and
  verifies recovery with the namespace owner.

## Examples

Apply a default-deny ingress policy before adding an explicitly reviewed service
exception. Test it in the target namespace with a non-sensitive health endpoint:

```bash
kubectl -n inference apply -f networkpolicy-default-deny.yaml
kubectl -n inference get networkpolicy
kubectl -n inference run policy-check --rm -i --restart=Never \
  --image=curlimages/curl -- curl -fsS http://approved-service/health
```

If the expected workload is blocked, add the smallest labelled ingress rule and
retest. Never temporarily open all namespace ingress as a diagnostic workaround.

## Resources

- [CoreWeave CKS Security](https://docs.coreweave.com/docs/products/cks)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)

## Next Steps

See `coreweave-prod-checklist`.

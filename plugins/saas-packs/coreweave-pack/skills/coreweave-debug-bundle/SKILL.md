---
name: coreweave-debug-bundle
description: 'Collect CoreWeave cluster diagnostics for support tickets.

  Use when preparing a support case, collecting GPU node status,

  or documenting pod failures.

  Trigger with phrases like "coreweave debug", "coreweave support",

  "coreweave diagnostics", "collect coreweave logs".

  '
allowed-tools: Read, Bash(kubectl:*), Bash(tar:*), Grep
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
# CoreWeave Debug Bundle

## Overview

Collect the minimum redacted cluster, workload, and rate-limit evidence needed to
triage a CoreWeave incident. A debug bundle is diagnostic evidence, not an archive
for credentials, prompts, model weights, datasets, kubeconfigs, or raw secret values.

## Prerequisites

- Authorized read-only Kubernetes access to the affected namespace or cluster.
- An incident identifier, retention destination, and named incident owner.
- A local encrypted workspace with sufficient space; do not collect a bundle on a
  shared or unmanaged machine.

## Instructions

1. Create the bundle for the affected scope and set restrictive file permissions.
2. Capture status, events, allocation, and bounded log tails; remove headers or
   values that contain credentials before packaging.
3. Inspect the archive locally for secrets and customer data, then attach it only to
   the approved incident record with the required retention period.
4. Delete the local copy after verified upload, according to the incident policy.

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Scope

Collect GPU node health, Kubernetes pod status, event logs, and API connectivity into a single diagnostic archive for CoreWeave support tickets. This bundle captures cluster-level resource allocation, failed pod logs, GPU device plugin state, and network reachability so support engineers can diagnose infrastructure issues without requesting additional information. Useful when GPU pods are stuck pending, inference workloads OOM, or node autoscaling behaves unexpectedly.

## Debug Collection Script

```bash
#!/bin/bash
set -euo pipefail
BUNDLE="debug-coreweave-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BUNDLE"

# Environment check
echo "=== CoreWeave Debug Bundle ===" | tee "$BUNDLE/summary.txt"
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$BUNDLE/summary.txt"
echo "COREWEAVE_API_KEY: ${COREWEAVE_API_KEY:+[SET]}" >> "$BUNDLE/summary.txt"
echo "KUBECONFIG: ${KUBECONFIG:-default}" >> "$BUNDLE/summary.txt"
echo "kubectl: $(kubectl version --client --short 2>/dev/null || echo 'not found')" >> "$BUNDLE/summary.txt"

# API connectivity
HTTP=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${COREWEAVE_API_KEY}" \
  https://api.coreweave.com/v1/namespaces 2>/dev/null || echo "000")
echo "API Status: HTTP $HTTP" >> "$BUNDLE/summary.txt"

# Cluster state
kubectl get nodes -o wide > "$BUNDLE/nodes.txt" 2>&1 || true
kubectl get pods --all-namespaces -o wide > "$BUNDLE/pods.txt" 2>&1 || true
kubectl get events --sort-by=.lastTimestamp > "$BUNDLE/events.txt" 2>&1 || true

# GPU allocation and device plugin status
kubectl describe nodes | grep -A10 "Allocated resources" > "$BUNDLE/gpu-allocation.txt" 2>&1 || true
kubectl get pods -n kube-system -l k8s-app=nvidia-device-plugin -o wide > "$BUNDLE/gpu-plugin.txt" 2>&1 || true

# Failed pod logs
for pod in $(kubectl get pods --field-selector=status.phase=Failed -o name 2>/dev/null); do
  kubectl logs "$pod" --tail=200 > "$BUNDLE/$(basename "$pod")-logs.txt" 2>&1 || true
done

# Rate limit headers
curl -s -D "$BUNDLE/rate-headers.txt" -o /dev/null \
  -H "Authorization: Bearer ${COREWEAVE_API_KEY}" \
  https://api.coreweave.com/v1/namespaces 2>/dev/null || true

tar -czf "$BUNDLE.tar.gz" "$BUNDLE" && rm -rf "$BUNDLE"
echo "Bundle: $BUNDLE.tar.gz"
```

## Analyzing the Bundle

```bash
tar -xzf debug-coreweave-*.tar.gz
cat debug-coreweave-*/summary.txt          # API + env status at a glance
grep -i "error\|fail\|oom" debug-coreweave-*/events.txt  # Critical events
cat debug-coreweave-*/gpu-allocation.txt   # GPU resource pressure
```

## Common Issues

| Symptom | Check in Bundle | Fix |
|---------|----------------|-----|
| GPU pods stuck Pending | `gpu-allocation.txt` shows 0 allocatable GPUs | Request quota increase or switch to available GPU type |
| OOMKilled on inference pod | `events.txt` for OOMKilled entries | Increase memory limits in pod spec; check model size vs allocated RAM |
| Node NotReady | `nodes.txt` status column | Check `events.txt` for kubelet issues; contact CoreWeave if persistent |
| API returns 401 | `summary.txt` shows HTTP 401 | Regenerate API key at CoreWeave dashboard; verify `COREWEAVE_API_KEY` is set |
| NVIDIA device plugin missing | `gpu-plugin.txt` empty or error | Verify namespace `kube-system` has device plugin DaemonSet; redeploy if missing |

## Output

- A scope-limited, redacted diagnostic archive with cluster state, relevant events,
  GPU allocation, and bounded failure logs.
- A reproducible incident receipt identifying collection time, scope, owner, and
  approved storage location without embedding credentials.

## Error Handling

| Condition | Safe response |
|---|---|
| Bundle contains a secret or customer data | Stop distribution, delete the local archive, rotate exposed credentials, and recollect with stronger redaction. |
| Collection command is denied | Request temporary read-only incident access; do not use another user's kubeconfig. |
| Archive is too large | Restrict it to the affected namespace and reduce log tails; do not omit events or security review. |
| API probe fails | Record the status and request ID only; do not paste authorization headers into the bundle. |

## Examples

For an OOM incident, collect only the affected namespace and verify that the archive
does not contain secret values before upload:

```bash
INCIDENT=inc-2026-08-26
./collect-coreweave-debug.sh --namespace inference --incident "$INCIDENT"
tar -tzf "debug-coreweave-${INCIDENT}.tar.gz"
```

Have a second authorized responder review the archive manifest, then store it in the
approved incident system. Delete the local copy only after the upload is verified.

## Automated Health Check

```typescript
async function checkCoreWeave(): Promise<void> {
  const key = process.env.COREWEAVE_API_KEY;
  if (!key) { console.error("[FAIL] COREWEAVE_API_KEY not set"); return; }

  const res = await fetch("https://api.coreweave.com/v1/namespaces", {
    headers: { Authorization: `Bearer ${key}` },
  });
  console.log(`[${res.ok ? "OK" : "FAIL"}] API: HTTP ${res.status}`);

  const limit = res.headers.get("x-ratelimit-remaining");
  if (limit) console.log(`[INFO] Rate limit remaining: ${limit}`);
}
checkCoreWeave();
```

## Resources

- [CoreWeave Status](https://status.coreweave.com)

## Next Steps

See `coreweave-common-errors` for GPU scheduling and Kubernetes troubleshooting patterns.

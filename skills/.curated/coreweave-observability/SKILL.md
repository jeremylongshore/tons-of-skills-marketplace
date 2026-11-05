---
name: coreweave-observability
description: 'Set up GPU monitoring and observability for CoreWeave workloads.

  Use when implementing GPU metrics dashboards, configuring alerts,

  or tracking inference latency and throughput.

  Trigger with phrases like "coreweave monitoring", "coreweave observability",

  "coreweave gpu metrics", "coreweave grafana".

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
# CoreWeave Observability

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

CoreWeave runs GPU-intensive workloads on Kubernetes where hardware failures, memory exhaustion, and underutilization directly impact cost and reliability. Observability must cover DCGM GPU metrics, Kubernetes pod health, inference latency, and job completion rates. Proactive monitoring prevents wasted spend on idle GPUs and catches OOM conditions before they cascade.

## Prerequisites

- A metrics backend receiving Kubernetes and DCGM exporter metrics.
- A named dashboard and on-call owner for the namespace or service.
- Log and trace redaction rules that exclude prompts, model outputs, tokens, and credentials.

## Instructions

1. Tag metrics with bounded values such as namespace, model family, and status; do
   not use request IDs, prompts, or user identifiers as labels.
2. Build dashboards for utilization, memory, queue depth, latency, error rate, and
   restart rate, then set alert thresholds from a measured baseline.
3. Route critical alerts to the responsible on-call team and link a runbook that
   includes a safe scale-down or rollback action.
4. Test one alert in a non-production namespace and verify that the receipt contains
   only operational metadata, not workload data.

## Key Metrics

| Metric | Type | Target | Alert Threshold |
|--------|------|--------|-----------------|
| GPU utilization | Gauge | > 60% | < 20% for 30m |
| GPU memory usage | Gauge | < 85% | > 95% for 5m |
| Inference latency p99 | Histogram | < 200ms | > 500ms |
| Job completion rate | Counter | > 99% | < 95% per hour |
| Pod restart count | Counter | 0 | > 3 in 15m |
| Node GPU temperature | Gauge | < 80C | > 85C for 10m |

## Instrumentation

```typescript
async function trackInference(model: string, fn: () => Promise<any>) {
  const start = Date.now();
  try {
    const result = await fn();
    metrics.record('coreweave.inference.latency', Date.now() - start, { model, status: 'ok' });
    metrics.increment('coreweave.inference.completed', { model });
    return result;
  } catch (err) {
    metrics.increment('coreweave.inference.errors', { model, error: err.code });
    throw err;
  }
}
```

## Health Check Dashboard

```typescript
async function coreweaveHealth(): Promise<Record<string, string>> {
  const gpu = await queryPrometheus('avg(DCGM_FI_DEV_GPU_UTIL)');
  const mem = await queryPrometheus('avg(DCGM_FI_DEV_FB_USED/(DCGM_FI_DEV_FB_USED+DCGM_FI_DEV_FB_FREE))');
  const pods = await queryPrometheus('kube_deployment_status_replicas_available{namespace="inference"}');
  return {
    gpu_utilization: gpu > 20 ? 'healthy' : 'underutilized',
    gpu_memory: mem < 0.9 ? 'healthy' : 'critical',
    inference_pods: pods > 0 ? 'healthy' : 'down',
  };
}
```

## Alerting Rules

```typescript
const alerts = [
  { metric: 'DCGM_FI_DEV_GPU_UTIL', condition: 'avg < 20', window: '30m', severity: 'warning' },
  { metric: 'gpu_memory_pct', condition: '> 0.95', window: '5m', severity: 'critical' },
  { metric: 'inference_latency_p99', condition: '> 500ms', window: '10m', severity: 'warning' },
  { metric: 'pod_restart_count', condition: '> 3', window: '15m', severity: 'critical' },
];
```

## Structured Logging

```typescript
function logGpuEvent(event: string, node: string, data: Record<string, any>) {
  console.log(JSON.stringify({
    service: 'coreweave', event, node,
    gpu_model: data.gpu_model, utilization: data.util,
    memory_pct: data.memPct, temperature: data.temp,
    timestamp: new Date().toISOString(),
  }));
}
```

## Error Handling

| Signal | Meaning | Action |
|--------|---------|--------|
| GPU util < 20% sustained | Idle GPUs burning cost | Scale down or reassign workload |
| GPU memory > 95% | OOM imminent | Reduce batch size or add nodes |
| Pod CrashLoopBackOff | Driver or config failure | Check DCGM logs, restart node |
| Inference latency spike | Contention or throttling | Review GPU temp and queue depth |
| Node NotReady | Hardware or network issue | Cordon node, migrate pods |

## Output

- A bounded-label GPU and workload dashboard with actionable alert rules.
- A redacted event trail linking an alert to the namespace, model family, severity,
  and response owner.
- A tested incident path for capacity, memory, latency, and node-health failures.

## Examples

Use a non-production workload to verify the alert route without disrupting a live
service:

```bash
kubectl -n inference-staging scale deployment/summarizer --replicas=0
kubectl -n inference-staging get pods --watch
# Confirm the unavailable-replica alert reaches the test route, then restore it.
kubectl -n inference-staging scale deployment/summarizer --replicas=1
```

Record the alert ID and restoration time, not request or model content. Escalate a
node or memory alert through the runbook before deleting pods or changing quotas.

## Resources

- [CoreWeave Observability](https://www.coreweave.com/observability)

## Next Steps

For incident response, see `coreweave-incident-runbook`.

# GPU workload evidence boundaries

Community-contributed; not affiliated with CoreWeave.

Pod readiness, requested GPUs, allocated devices and observed activity are different
facts. Preserve the Pod UID, Node, GPU UUID and sample timestamp across the join.
A reused Pod name cannot establish device ownership. Empty/stale metrics are unknown;
zero utilization can be a healthy idle phase and is not automatically a fault.

The helper accepts full-GPU integer limits and supplied device-to-Pod attribution.
MIG, MPS, time-slicing, init-container scheduling and custom resource names require a
reviewed adapter. Positive activity does not establish application correctness,
latency, efficiency, sustained throughput or fabric health. The maximum evidence
age is five minutes; retrospective fixture replay time must be labeled historical.

Never create a benchmark, restart a workload or reset a GPU just to make this
verify-only skill produce a positive result. Request a bounded fresh snapshot from
the authorized operator and preserve an incomplete verdict until it arrives.

Source: [CKS workload scheduling](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling),
reviewed 2026-11-05. No live account evidence is claimed.

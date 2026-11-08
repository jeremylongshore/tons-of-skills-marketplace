# GPU workload evidence boundaries

Community-contributed; not affiliated with CoreWeave.

Pod readiness, requested GPUs, allocated devices and observed activity are different
facts. Preserve the Pod UID, Node, GPU UUID and sample timestamp across the join.
A reused Pod name cannot establish device ownership. Empty/stale metrics are unknown;
zero utilization can be a healthy idle phase and is not automatically a fault.

The helper accepts full-GPU nonnegative integer limits and plain ASCII decimal
strings such as `"1"`, bounded by the Kubernetes signed 64-bit quantity maximum.
Booleans, fractions and other quantity forms are outside this adapter. Valid
Kubernetes forms such as `3Ki` or `3000m` must be normalized to whole units by an
operator; rejection here is not a claim that Kubernetes rejects those forms.
Device-to-Pod attribution remains supplied evidence.
MIG, MPS, time-slicing, init-container scheduling and custom resource names require a
reviewed adapter. Positive activity does not establish application correctness,
latency, efficiency, sustained throughput or fabric health. The maximum evidence
age is five minutes at evaluation, not five minutes relative to another aged
snapshot. Samples later than the capture timestamp are inconsistent and cannot
establish activity. Retrospective replay time must be labeled historical.
A non-null deletion timestamp makes readiness incomplete even if the Pod still
reports Ready. The report keeps the observed Ready condition separate from that
qualified readiness result, and records per-device ages relative to `evaluated_at`.

Never create a benchmark, restart a workload or reset a GPU just to make this
verify-only skill produce a positive result. Request a bounded fresh snapshot from
the authorized operator and preserve an incomplete verdict until it arrives.

Source: [CKS workload scheduling](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling),
reviewed 2026-11-05. No live account evidence is claimed.

## Source register and claim boundaries

| ID / evidence state | Contract | Source / review |
| --- | --- | --- |
| SRC-CW-S26-1 / verified | Kubernetes quantities serialize as strings; full quantity syntax is broader than this adapter. | [Quantity API](https://kubernetes.io/docs/reference/kubernetes-api/definitions/quantity-resource/), inspected 2026-11-07 |
| SRC-CW-S26-2 / verified | Extended resources require whole numbers; some suffix forms still represent whole units. | [Resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#consuming-extended-resources), inspected 2026-11-07 |
| SRC-CW-S26-3 / verified | A deletion timestamp records requested deletion and can remain present while finalization is pending. | [ObjectMeta API](https://kubernetes.io/docs/reference/kubernetes-api/definitions/object-meta-v1-meta/), inspected 2026-11-07 |
| DEC-CW-S26-1 / derived | Treat terminating Pods as incomplete and use evaluation time for sample freshness. | Maintainer safety policy implemented by this offline adapter, not a vendor health certification |
| LIM-CW-S26-1 / unknown | Actual account state, device ownership and application correctness. | Supplied snapshots and positive GPU utilization cannot establish these facts |

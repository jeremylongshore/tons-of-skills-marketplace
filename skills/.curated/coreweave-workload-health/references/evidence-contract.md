# Evidence contract: Workload and GPU health evidence

Community-contributed; not affiliated with CoreWeave.

Supply the Kubernetes `pod` JSON object, `gpu_allocations` mapping Pod UID to GPU UUID, and `gpu_samples` with uuid/pod_uid/at/utilization_percent. Allocation evidence must come from the approved device/Pod mapping; do not join only on a reused Pod name. Samples must be finite, in 0..100 and within five minutes of capture. Positive utilization shows activity in that window, not model correctness, sustained efficiency, all GPU architectures or application health. Idle but healthy batch workloads can return incomplete activity evidence. MIG/MPS/time-slicing need an explicit adapter; do not pretend full-GPU UUID semantics prove those allocations.

## Input and review boundary

The packaged `tests/fixtures/example.json` is the complete normalized input example.
`cases.json` includes specific negative outcomes as well as stale, wrong-scope and
injected-instruction variants. Inputs are supplied observations, not authenticated
proof. Review the source of every boolean assertion. The common envelope records
intended and observed scope plus a timezone-aware capture timestamp. Output includes
the SHA-256 of the actual bytes read, never a token or raw log excerpt.

Read-only collection commands and upload/deploy commands belong to the human-approved
operator workflow. Helper parsing is intentionally independent of credentials and
network availability. Unknown nested platform formats fail closed; add a reviewed
fixture before extending an adapter.

## Source and review

Primary source: https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling

Contract reviewed 2026-11-05. Repository examples are original. Vendor version and
account-specific availability must be confirmed separately; no live operation was
performed for this pack. See the blueprint for requirements and release boundaries.

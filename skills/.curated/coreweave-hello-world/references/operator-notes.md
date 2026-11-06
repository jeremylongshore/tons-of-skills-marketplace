# GPU smoke-test review: evidence and failure boundaries

## Review details

OOMKilled is a container memory-limit event; a CUDA out-of-memory exception is a different GPU-memory signal. Inspect the exact termination state.

A timeout is inconclusive until Failed conditions and scheduling events are checked. Neither a test receipt nor available GPU quota guarantees future capacity.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling)
- [Primary reference 2](https://kubernetes.io/docs/reference/kubectl/)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.

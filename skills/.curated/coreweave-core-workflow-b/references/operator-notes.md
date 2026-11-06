# Training launch and recovery review: evidence and failure boundaries

## Review details

NCCL timeout can have rank, rendezvous, storage or transport causes. Do not assume NVLink or a GPU upgrade fixes every timeout.

If any checkpoint shard is missing or mismatched, stop resume and retain the prior complete checkpoint. Do not prune the last recovery point.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling)
- [Primary reference 2](https://docs.coreweave.com/products/storage/distributed-file-storage/create-volumes)
- [Primary reference 3](https://github.com/coreweave/nccl-tests)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.

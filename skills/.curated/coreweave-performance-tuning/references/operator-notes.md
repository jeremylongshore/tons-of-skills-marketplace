# Measured performance experiments: evidence and failure boundaries

## Review details

Low GPU utilization can reflect checkpointing, data stalls, low request volume or metric sampling. It is not automatically waste or a faulty GPU.

A GPU-memory target or batching flag may increase OOM/error rates. Report both successful throughput and dropped/failed requests.

## Source contract

Sources checked 2026-11-05. Read the current API/tool contract before adapting examples; tenant access and rollout state were not tested against a live CoreWeave account.

- [Primary reference 1](https://docs.coreweave.com/products/inference/scaling)
- [Primary reference 2](https://docs.coreweave.com/observability/usage-monitoring)
- [Primary reference 3](https://docs.vllm.ai/en/latest/)

## Receipt fields

Record context/namespace identifiers only in the approved private incident system, UTC collection time, selected resource names, command exit status, missing permissions, and any review decision. Separate observed state, inferred cause and proposed change. A denied or incomplete check remains unknown, never a clean bill of health.

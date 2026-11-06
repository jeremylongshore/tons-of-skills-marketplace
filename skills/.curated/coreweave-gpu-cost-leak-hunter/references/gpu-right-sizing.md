# Right-sizing evidence

Use current contracted rates, workload quality, batch/concurrency distribution, precision, KV-cache/model memory, interconnect, availability and measured throughput. A parameter count is not a GPU allocation rule. Do not assert that L40S always beats H100/H200 per token or that a particular model repository or precision mode exists without checking it.

Run only an owner-approved bounded canary. Compare cost per successful unit at the same latency and quality target; include cold starts and failure rates. Label any unmeasured equivalent-throughput assumption as estimated. Retain the known-good image/model/manifest for rollback.

Sources: https://docs.coreweave.com/products/inference/billing and https://docs.coreweave.com/products/inference/scaling

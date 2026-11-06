# Comparable bandwidth evidence

Record GPU model/count, number of Nodes, topology, message size, image, driver/NCCL version and cache/warmup conditions. Compare the same all_reduce_perf columns (algbw versus busbw) and repeat the run enough to characterize variance. No absolute bandwidth threshold or slowdown multiplier is established by this package.

The offline script echoes an observed summary; it does not launch a benchmark, validate all table rows, or compare against a stored performance result. The CoreWeave example repository is reference material, not a measured baseline for this account.

Source: https://github.com/coreweave/nccl-tests

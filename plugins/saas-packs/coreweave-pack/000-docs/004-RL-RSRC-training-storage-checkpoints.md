<!-- doc-class: record -->

**Status:** Research material only; not adopted policy, implementation, certification, or operational authorization.
**Access date:** 2026-10-22 UTC. **Historical boundary:** The original four-domain July 2 research records were not recovered. These are new current-source observations. Existing July-dated PRD pain anchors are preserved where present; a PRD assertion alone is not corroboration.

# Distributed training launch, storage and checkpointing

## Immutable pack-source context

Pack source: `8d38bb77c016b1adfdc7b6e0afcc25638682e2b3`. The [manifest](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/.claude-plugin/plugin.json) declares Jeremy Longshore authorship, MIT licensing and community/non-affiliation status; the [README](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/README.md) describes the pack. Historical pain anchors are in the [GPU PRD](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/skills/coreweave-gpu-node-forensics/PRD.md), [fabric PRD](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/skills/coreweave-fabric-diagnostics/PRD.md) and [cost PRD](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/skills/coreweave-gpu-cost-leak-hunter/PRD.md). These are immutable context, not recovered July research receipts or independent proof of their assertions.

## Historical context

No original July training-domain record or training-specific Dxx list was recovered. The identifiers below are newly proposed current research anchors.

## Bounded pain catalog

- **D-CW-TRAIN-01 — A launcher recipe depends on orchestration and transport.** CoreWeave maintains distinct NCCL examples for MPI Operator and Slurm and describes their interaction with distributed frameworks. Inference: copying one launcher into another environment without checking rank/topology/transport is a reproducibility risk. [Pinned NCCL README](https://github.com/coreweave/nccl-tests/blob/ab7a928135c7aa04f151d993de3d36fffdd3d034/README.md).
- **D-CW-TRAIN-02 — Shared storage requires the right PVC contract.** Current CKS DFS guidance specifies ReadWriteMany, shared-vast and namespace-scoped claims. Inference: wrong access/storage-class/namespace assumptions can prevent shared checkpoint paths from being mounted. [Create DFS volumes](https://docs.coreweave.com/products/storage/distributed-file-storage/create-volumes).
- **D-CW-TRAIN-03 — Cold reads and checkpoint restores have cache state.** CoreWeave documents HeadObject-based pre-staging of complete objects into LOTA. Inference: warm/cold cache must be recorded when comparing startup or restore times; the service's performance examples are not measurements of this pack or a particular training job. [Pre-stage LOTA](https://docs.coreweave.com/products/storage/object-storage/improving-performance/prestage-cache).
- **D-CW-TRAIN-04 — Low GPU activity is not automatically wasted allocation.** CoreWeave's Slurm dashboard separates GPU efficiency, node conditions and NFS read/write signals; its stated efficiency estimate excludes restart/checkpoint periods and is not MFU. Inference: correlate checkpoint/storage phases before labeling idle-looking intervals a leak. [Slurm job metrics](https://docs.coreweave.com/observability/managed-grafana/sunk/slurm-job-metrics).

## Could not verify

Original July research; checkpoint atomicity/completeness for any framework; safe application-specific resume; optimal checkpoint interval; recovery-point/time guarantees; exact storage throughput; checkpoint serialization compatibility; universal launcher or world-size-rescaling support. Shared storage and warm cache do not prove a valid checkpoint. No workload, volume, object request, cache warm-up, benchmark or restore was executed.

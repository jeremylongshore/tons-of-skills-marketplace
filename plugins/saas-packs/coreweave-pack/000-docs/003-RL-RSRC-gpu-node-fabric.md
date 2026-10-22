<!-- doc-class: record -->

**Status:** Research material only; not adopted policy, implementation, certification, or operational authorization.
**Access date:** 2026-10-22 UTC. **Historical boundary:** The original four-domain July 2 research records were not recovered. These are new current-source observations. Existing July-dated PRD pain anchors are preserved where present; a PRD assertion alone is not corroboration.

# GPU node forensics and fabric

## Immutable pack-source context

Pack source: `8d38bb77c016b1adfdc7b6e0afcc25638682e2b3`. The [manifest](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/.claude-plugin/plugin.json) declares Jeremy Longshore authorship, MIT licensing and community/non-affiliation status; the [README](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/README.md) describes the pack. Historical pain anchors are in the [GPU PRD](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/skills/coreweave-gpu-node-forensics/PRD.md), [fabric PRD](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/skills/coreweave-fabric-diagnostics/PRD.md) and [cost PRD](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/skills/coreweave-gpu-cost-leak-hunter/PRD.md). These are immutable context, not recovered July research receipts or independent proof of their assertions.

## Historical anchors

Existing coreweave-gpu-node-forensics/PRD.md names D-CW-GPU-01 through04; coreweave-fabric-diagnostics/PRD.md names CW-F1 through4. Preserve those IDs. The following narrows what current primary sources support; it does not rewrite the PRDs.

## Bounded pain catalog

- **D-CW-GPU-01 / D-CW-GPU-04 — Node remediation can interrupt workloads and is controller-owned.** CoreWeave documents lifecycle transitions including cordon, reboot and triage, with pending/immediate states and workload-dependent timing. Inference: operators must inspect lifecycle state before changing scheduling; this is not authorization to reset or uncordon. [Node transitions](https://docs.coreweave.com/platform/fleet-management/node-lifecycle/state-transitions).
- **D-CW-GPU-02 — Contained and uncontained memory events differ.** NVIDIA DCGM distinguishes Xid94 contained memory errors and Xid95 uncontained errors. Architecture, driver and surrounding diagnostics still matter; these labels alone do not establish a universal reset/reboot/RMA action. [NVIDIA DCGM health monitoring](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/health-monitoring.html).
- **CW-F1 / CW-F2 / CW-F3 — RDMA requires matching platform and pod setup.** CoreWeave documents InfiniBand-capable nodes, NCCL/OFED userspace and pod device/environment configuration. Crucial correction: Kubernetes can default requests from limits; the historical absolute claim that both fields must independently be supplied is too strong. Missing transport prerequisites are a diagnostic hypothesis, not proof of any specific slowdown multiplier. [GPUDirect RDMA](https://docs.coreweave.com/products/networking/hpc-interconnect/use-gpudirect-rdma).
- **CW-F4 — A benchmark must be interpreted with topology and transport context.** CoreWeave's pinned NCCL examples cover MPI Operator and Slurm and multiple GPU/network arrangements. Inference: one universal bandwidth threshold cannot be inferred from a sample job. [Pinned NCCL README](https://github.com/coreweave/nccl-tests/blob/ab7a928135c7aa04f151d993de3d36fffdd3d034/README.md).

## Could not verify

Historical claimed5–20x slowdown; any customer's measured bandwidth; exact GPU failure frequency; universal application-only attribution for Xids13/31/43/45; blanket94/95 remediation; healthy-card RMA rate; exact lost GPU-hours or dollars. D-CW-GPU-03 remains a useful triage question, not an established cost estimate. No node access, hardware diagnostics, cordon/reset or NCCL job was run.

<!-- doc-class: record -->

**Status:** Research material only; not adopted policy, implementation, certification, or operational authorization.
**Access date:** 2026-10-22 UTC. **Historical boundary:** The original four-domain July 2 research records were not recovered. These are new current-source observations. Existing July-dated PRD pain anchors are preserved where present; a PRD assertion alone is not corroboration.

# Inference cold start, cost, capacity and observability

## Immutable pack-source context

Pack source: `8d38bb77c016b1adfdc7b6e0afcc25638682e2b3`. The [manifest](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/.claude-plugin/plugin.json) declares Jeremy Longshore authorship, MIT licensing and community/non-affiliation status; the [README](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/README.md) describes the pack. Historical pain anchors are in the [GPU PRD](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/skills/coreweave-gpu-node-forensics/PRD.md), [fabric PRD](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/skills/coreweave-fabric-diagnostics/PRD.md) and [cost PRD](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/skills/coreweave-gpu-cost-leak-hunter/PRD.md). These are immutable context, not recovered July research receipts or independent proof of their assertions.

## Historical anchors

Existing cost-leak PRD names CW-C1 idle reserved, CW-C2 wrong GPU, CW-C3 allocated idle, CW-C4 commitment gap. These survive as historical trace anchors; they are not automatically current billing facts. New D-CW-INF identifiers below distinguish current observations.

## Bounded pain catalog

- **D-CW-INF-01 — Model loading contributes to cold start.** Tensorizer describes streaming tensor loading from remote endpoints and exposes format/API trade-offs. Inference: measure loading separately from scheduling/image/runtime warm-up; a repository benchmark is not a guaranteed end-to-end startup SLA. [Pinned Tensorizer README](https://github.com/coreweave/tensorizer/blob/652d3c016c84836bba97153e108821c11428ac40/README.md).
- **CW-C1 / CW-C4 — Capacity models have materially different commitments.** Current CKS plans distinguish RI, Flex, Spot and On-Demand. RI is billed through idle periods; Flex has holding and active-usage components; Spot is reclaimable and On-Demand lacks a capacity guarantee. Inference: a single take-or-pay formula cannot represent every plan. [Capacity plans](https://docs.coreweave.com/platform/capacity-plans).
- **CW-C2 / D-CW-INF-02 — Right-sizing is workload- and product-specific.** Dedicated Inference guidance recommends sizing to memory/throughput needs and aligning replica minima with latency needs. It distinguishes reserved-node and GPU-hour billing from Serverless per-token billing. This does not establish that L40S always beats H100/H200 per token. [Inference billing](https://docs.coreweave.com/products/inference/billing).
- **CW-C3 / D-CW-INF-03 — Metering and billing are different measures.** CoreWeave's usage guidance describes On-Demand usage-based cost estimates; actual billed amounts depend on contract terms, discounts and taxes. Inference: usage telemetry alone is not a final invoice or proven savings. [Cost and usage monitoring](https://docs.coreweave.com/observability/usage-monitoring).

## Could not verify

Historical July receipts; universal GPU price rankings; contracted rates/credits; claimed percentage savings; any customer's idle threshold; per-model latency or cost/token; guaranteed cold-start bounds; actual capacity availability. No credential, billing API, inference call, model download, deployment, scheduling or spend-producing operation was performed.

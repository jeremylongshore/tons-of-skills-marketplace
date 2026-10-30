<!-- doc-class: record -->

**Status:** Research material only; not adopted policy, implementation, certification, or operational authorization.
**Access date:** 2026-10-22 UTC. **Historical boundary:** The original four-domain July 2 research records were not recovered. These are new current-source observations. Existing July-dated PRD pain anchors are preserved where present; a PRD assertion alone is not corroboration.

# Platform, API, authentication and official OSS

## Immutable pack-source context

Pack source: `8d38bb77c016b1adfdc7b6e0afcc25638682e2b3`. The [manifest](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/.claude-plugin/plugin.json) declares Jeremy Longshore authorship, MIT licensing and community/non-affiliation status; the [README](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/README.md) describes the pack. Historical pain anchors are in the [GPU PRD](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/skills/coreweave-gpu-node-forensics/PRD.md), [fabric PRD](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/skills/coreweave-fabric-diagnostics/PRD.md) and [cost PRD](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/8d38bb77c016b1adfdc7b6e0afcc25638682e2b3/plugins/saas-packs/coreweave-pack/skills/coreweave-gpu-cost-leak-hunter/PRD.md). These are immutable context, not recovered July research receipts or independent proof of their assertions.

## Ownership and historical context

The marketplace pack is first-party Jeremy Longshore/MIT with an explicit community/non-affiliation disclaimer. It has no sources.yaml entry or .source.json marker. The three existing July PRDs do not recover the original platform research record. IDs below are newly proposed, not claimed July identifiers.

## Bounded pain catalog

- **D-CW-PLAT-01 — Credential material is a recovery/security boundary.** CoreWeave documents API tokens, expiration, cluster-specific kubeconfig download, one-time display of secret values and permissions-managed access. Inference: losing token material or assuming a kubeconfig is harmless can block access or expose credentials. No credentials were accessed. [Token/kubeconfig documentation](https://docs.coreweave.com/docs/products/cks/auth-access/manage-api-access-tokens).
- **D-CW-PLAT-02 — Tooling must reflect the actual control surface.** An official Mission Control MCP tool reference now exists. The parent task's July assertion of no first-party MCP tooling cannot be repeated as a current fact. Availability and safe tool selection need product/permission review, not a newly invented API wrapper. [Official MCP tools](https://docs.coreweave.com/observability/mission-control-mcp/reference/tools).
- **D-CW-PLAT-03 — IaC examples are not permission to provision.** CoreWeave maintains a Terraform provider; its README distinguishes development/debugging and real acceptance-test configuration. Inference: confusing documentation/development examples with approved live changes risks resource creation. [Pinned provider README](https://github.com/coreweave/terraform-provider-coreweave/blob/4e41acdb33dfdf0922173fe4c474466d2e176ea0/README.md).
- **D-CW-PLAT-04 — OSS reuse needs per-repository proof.** Tensorizer and the Terraform provider advertise MIT licenses at inspected pins. The inspected root trees of nccl-tests and kubernetes-cloud contain no root LICENSE/NOTICE/COPYING entry; their GitHub license metadata was null. This is insufficient to endorse the parent claim that every listed repository is MIT/Apache. Cite ideas without copying code until licensing is resolved. [Tensorizer](https://github.com/coreweave/tensorizer/tree/652d3c016c84836bba97153e108821c11428ac40), [provider](https://github.com/coreweave/terraform-provider-coreweave/tree/4e41acdb33dfdf0922173fe4c474466d2e176ea0), [nccl-tests](https://github.com/coreweave/nccl-tests/tree/ab7a928135c7aa04f151d993de3d36fffdd3d034), [kubernetes-cloud](https://github.com/coreweave/kubernetes-cloud/tree/3005605371d85eced85ab78191f962285914fd14).

## Could not verify

Original July source receipts; customer-specific token scopes/availability; live MCP behavior or permissions; exhaustive absence/presence of all official agent integrations; complete license coverage of every subdirectory/transitive dependency. No API, Terraform, MCP, provider test or compute operation was executed.

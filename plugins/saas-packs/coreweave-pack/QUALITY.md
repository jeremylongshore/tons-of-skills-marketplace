# CoreWeave community pack: evidence and limits

**Review date:** 2026-11-05. **Scope:** all 23 shipped skill guides, three scripts, their requirements/architecture/reference/eval records, package metadata and generated distribution copies.

## Observed offline results

- 64 focused operator regressions passed on Python 3.12.3 and 3.14.0, with zero failures, errors or skips.
- All three script self-tests passed. The retained receipt contains the tested script hashes and output.
- Each scripted skill passed 13 J-Rig package-integrity checks, with no package warnings or errors. This command does not run a model.
- All 23 skills passed the marketplace schema/rubric with grade A and no schema errors. Scores and remaining advisory warnings are retained individually.

See [offline-results.json](offline-results.json) for the actual results, test-source hash and script hashes. The receipt is an unsigned local result, not an independent certification or a live-account attestation. Use the exact source revision when reproducing it.

## Behavioral corrections covered by fixtures

RDMA limits-only defaulting and explicit mismatches; per-container resource separation; transport warning versus positive selection; GPU-direct evidence separate from IB; Inactive ports; unknown/multi-GPU Xid evidence; same-device remap correlation; no remap downgrade of a PCIe failure; invalid/ambiguous CLI flags; non-finite, missing and malformed financial data; confidence default and billing-reference requirements; conflicting discount/repricing scenarios; report escaping and preservation of a prior report on invalid input; and private CI credential-file cleanup after a failed mocked rollout.

## Documentation and integration corrections

Removed unsourced billing-API absence, universal performance/savings claims, fabricated benchmark tables, legacy scheduling/storage recipes, invented webhook signatures, unsafe generated-source interpolation, incorrect SDK calls, and a restart mislabeled as rollback. Current guides use explicit contexts/namespaces and owner-reviewed changes. A Pod/container memory OOM is distinguished from a CUDA allocation error. Quotas, RBAC, Pod creation and storage mounts are separate security boundaries.

The read-only Mission Control MCP FOCUS tool returns usage, not dollar amounts; pagination, data_as_of, quantity units and current capacity plans matter. Existing research records from October 22 remain dated historical records. The updated skill requirements and architecture describe the corrected implementation, preserving their original pain anchors.

The community pack points provisioning users to CoreWeave’s official skill distribution and does not copy that proprietary code. Community authorship, MIT licensing and non-affiliation remain explicit; the requested unofficial CI title is preserved.

## Not established

No live CoreWeave account, GPU workload, benchmark, billing invoice, hardware recovery, capacity reservation or real deployment was exercised. No provider-backed behavioral evaluation, baseline value comparison, trigger-quality measurement, model-variance result or production certification is claimed. Eval specifications were corrected and package-checked; they are not passing eval results.

Before live use, the authorized owner must validate credentials, resource/contract scope, current platform semantics, workload correctness, cost budget and recovery in a bounded non-production environment. Keep model/provider evaluation and live compute separate from this offline evidence.

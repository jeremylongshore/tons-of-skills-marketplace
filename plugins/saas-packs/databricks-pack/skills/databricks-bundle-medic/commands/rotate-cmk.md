---
name: rotate-cmk
description: Run the CMK rotation runbook - drain all Databricks compute, rotate, resume
aliases: [cmk-rotation, drain-and-rotate]
---

# /rotate-cmk

Drives a customer-managed-key (CMK) rotation (pain D8) for a Databricks workspace via
the `databricks-bundle-medic` skill. CMK rotation requires every cluster, instance
pool, and SQL warehouse to be terminated first — this runbook makes that drain
deterministic and reversible.

## Usage

```text
/rotate-cmk [--cloud aws|azure|gcp]
```

## What it does

1. Inventories the running clusters, instance pools, and SQL warehouses.
2. Runs `scripts/drain-workspace.py` in **dry-run** first — shows exactly what will be
   terminated (already-stopped resources are skipped; the drain is idempotent).
3. On approval, executes the drain and writes a resume manifest recording only what it
   stopped.
4. Walks the per-cloud key rotation from `references/cmk-rotation-by-cloud.md`
   (AWS KMS / Azure Key Vault / GCP Cloud KMS via the Account API).
5. Resumes from the manifest — restarting only the resources it drained, never waking
   something that was already stopped before the window.

Dry-run by default; nothing is terminated until you approve the plan.

---
name: audit-photon-fallback
description: Find Databricks queries that fall back to Spark despite Photon's premium
aliases: [photon-audit, photon-fallback]
---

# /audit-photon-fallback

Audits whether Photon is earning its ~2x DBU premium or silently falling back to
Spark (pain D02).

## Usage

```
/audit-photon-fallback
```

## What it does

1. Reads recent `system.query.history` via the CLI Statement Execution API
   (needs `DATABRICKS_WAREHOUSE_ID` + the `system.query` grant chain) to find the
   slowest recent statements.
2. Inspects their physical plans for the "Photon does not support" seam and the
   `ColumnarToRow` / `RowToColumnar` boundaries that mark a fallback.
3. Confirms the cluster is Photon (`runtime_engine` via `clusters_get`).
4. Reports the queries paying the premium without the speedup and the fix — per
   `references/photon-eligibility-and-fallback.md`, usually rewriting a UDF as a
   native SQL expression so Photon engages, or turning Photon off for that workload.

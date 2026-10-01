---
name: dbr-upgrade-check
description: Scan a job's code and JARs for known Databricks Runtime upgrade landmines
aliases: [dbr-check, runtime-upgrade-check]
---

# /dbr-upgrade-check

Runs the pre-upgrade detectors for a Databricks Runtime bump (pains D03/D04/D05).

## Usage

```
/dbr-upgrade-check <path-to-job> [--from 13.3 --to 15.4]
```

## What it does

1. **CWD writes (D03)** — `scripts/find-cwd-writes.py --risk-only <path>` flags
   Python writes to relative/CWD paths that the DBR 14.x ~500 MB
   workspace-filesystem cap silently breaks.
2. **JDK target (D04)** — `scripts/scan-jar-jdk.sh <path>` flags JARs built for a
   pre-17 JDK that DBR 15.1's JDK 17 may reject at runtime.
3. Cross-references each hop's breaking changes (14.x CWD cap, 15.1 DBFS-root
   library + JDK-11 removals, 15.4 JDBC calendar flip) from
   `references/dbr-upgrade-paths.md`, scoped to the `--from`/`--to` range.

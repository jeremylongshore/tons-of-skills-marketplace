---
name: investigate-cluster
description: Triage a failed or slow Databricks cluster via parallel root-cause threads
aliases: [cluster-triage, why-cluster-failed]
---

# /investigate-cluster

Diagnoses one broken or anomalous Databricks cluster by invoking the
`cluster-event-investigator` subagent.

## Usage

```
/investigate-cluster <cluster_id> [symptom]
```

- `<cluster_id>` — the cluster to triage.
- `[symptom]` — optional, e.g. "never started", "died at 12 min", "randomly slow".

## What it does

Pulls the cluster's spec + event stream (`databricks-workspace-mcp` `clusters_get`
/ `clusters_events`, or a pasted `clusters.events` JSON in advisory mode), then runs
parallel investigation threads — provisioning, network/NPIP, init-script, driver,
spot/shuffle — and aggregates to the most-likely cause. It names the failure with
its actual `termination_reason.code` and cites the disambiguating check from
`references/termination-codes.md`. Read-only: it diagnoses, never restarts the cluster.

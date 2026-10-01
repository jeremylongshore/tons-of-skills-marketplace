---
name: databricks-bundle-medic
description: |
  Fix the deploy-time foot-guns of Databricks Asset Bundles (DAB) and the
  infrastructure operations around them: the bundle-bind gap for UC catalogs and
  external locations, the "unexpected EOF reading terraform.tfstate" redeploy failure,
  the schema-GRANT-ordering bug that fails the first deploy, customer-managed-key (CMK)
  rotation that requires draining the whole workspace, and the PrivateLink cost leak
  where S3/STS/Kinesis still traverse the NAT. Includes a PreToolUse hook that backs up
  and validates the bundle's terraform state before every deploy, and a PostToolUse
  hook that recognises the transient GRANT-ordering failure and recommends a single
  retry. Use when a databricks bundle deploy fails, before rotating a CMK, when a UC
  resource cannot be bound to a bundle, or when auditing PrivateLink networking cost.
  Trigger with "bundle deploy failed", "unexpected EOF terraform.tfstate", "bundle bind
  external location", "User does not have CREATE TABLE on Schema", "rotate CMK",
  "privatelink still using NAT".
allowed-tools: Read, Write, Edit, Bash(databricks:*), Bash(terraform:*), Bash(jq:*), Bash(python3:*), Bash(bash:*), Glob, mcp__databricks-workspace-mcp__external_locations_list, mcp__databricks-workspace-mcp__storage_credentials_list
version: 2.28.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, databricks, asset-bundles, deploy, infrastructure]
---

# Databricks Bundle Medic

The deploy + infrastructure spine of the pack. Databricks Asset Bundles (DAB) is
immature tooling — the replacement for the deprecated `dbx`, with a moving bug list
across CLI versions — and the infrastructure operations around a deploy (encryption
keys, networking, workspace config) bite production platform teams hardest. This skill
turns the five worst deploy-time foot-guns into deterministic, reversible operations.

## Overview

Five pains, all from the pack's deploy-ops research:

**Asset Bundles (DAB).** D4 — `databricks bundle bind` does NOT yet support UC catalogs
or external locations (databricks/cli#4842), so existing UC resources cannot come under
bundle management without hand-editing `terraform.tfstate` (hostile) or
destroy-and-recreate (impossible with dependent tables). D5 — "unexpected EOF reading
terraform.tfstate" on every redeploy after the first (databricks/cli#4986), which bricks
the bundle until you switch to `DATABRICKS_BUNDLE_ENGINE=direct`. D6 — the schema
GRANT-ordering bug (databricks/cli#4573): the first deploy to a fresh workspace fails
with "User does not have CREATE TABLE on Schema", but the second succeeds because the
first applied the grants before dying.

**Deploy-time infrastructure.** D8 — rotating a workspace's customer-managed key (CMK)
requires terminating every cluster, instance pool, and SQL warehouse first: a hard
maintenance window. D9 — the PrivateLink trap: enabling PrivateLink for the control
plane is mistaken for "all traffic is private," but the data plane's S3 / STS / Kinesis
calls still traverse the NAT, billing NAT-processing + cross-AZ transfer until each gets
its own VPC endpoint.

**The two hooks (this is the pack's only two-hook skill).** A `PreToolUse` hook
(`hooks/bundle-deploy-guard.py`) runs before every `databricks bundle deploy`: it
validates the bundle's local terraform state parses as JSON, caches a timestamped
known-good backup as a recovery escape hatch, and warns loudly if the state is corrupt
or has shrunk (the D5 signature). A `PostToolUse` hook (`hooks/bundle-grant-retry.py`)
watches a deploy's output and — ONLY on the exact D6 "does not have … on Schema"
signature — adds context recommending one retry, with the reason. Both are advisory:
the pre-hook never blocks a deploy, and the post-hook never masks a real error — it
surfaces the diagnosis and stops recommending retries if the same failure persists.

Deterministic work lives in `scripts/`; deep knowledge in `references/`. The
`import-uc-resource-to-bundle.py` D4 workaround is **self-deprecating** — it exists only
until #4842 closes and says so. Control-plane state comes from the
`databricks-workspace-mcp` server (`external_locations_list`, `storage_credentials_list`)
or the CLI; advisory-mode fallback accepts pasted input.

## Prerequisites

- **Databricks CLI** authenticated, plus `terraform` and `jq` on PATH — for the bundle,
  import, and state operations.
- **`databricks-workspace-mcp` registered** (optional) — for `external_locations_list`
  and `storage_credentials_list`. Absent → the CLI (`databricks external-locations
  list`) or advisory mode on pasted input.
- **Account-level OAuth M2M** (service principal) for CMK rotation — the D8 operations
  are account-scoped; a workspace PAT is insufficient. AWS/Azure/GCP CLI for the
  cloud-side key + VPC-endpoint work.
- **The two hooks are plugin-level** — installed with the pack. The pre-hook is silent
  unless a state looks corrupt; the post-hook is silent unless the exact D6 error fires.

## Instructions

Pick the flow by symptom. **Always name the exact error string / issue id** —
`unexpected EOF reading terraform.tfstate` (#4986), `does not have CREATE TABLE on
Schema` (#4573), the `bundle bind` UC gap (#4842) — an operator greps for those.

### Step 1: A bundle deploy that fails on state (D5)

"unexpected EOF reading terraform.tfstate" after the first deploy is #4986. The
`bundle-deploy-guard` PreToolUse hook already cached a known-good backup; restore it,
or switch engines:

```bash
DATABRICKS_BUNDLE_ENGINE=direct databricks bundle deploy -t "$TARGET"
```

Engine tradeoffs + the migration steps:
[`${CLAUDE_SKILL_DIR}/references/bundle-engine-tradeoffs.md`](references/bundle-engine-tradeoffs.md).

### Step 2: First deploy fails "does not have CREATE TABLE on Schema" (D6)

This is the transient GRANT-ordering bug (#4573). The `bundle-grant-retry` PostToolUse
hook flags it; re-run the SAME deploy **exactly once** — the failed first pass already
applied the grants. If the identical error persists after one retry, it is NOT this
transient — treat it as a real missing privilege and stop retrying.

### Step 3: A UC resource that will not bind (D4)

`databricks bundle bind` cannot take a UC catalog or external location yet (#4842).
Generate a review-first Terraform import plan (never hand-edit state):

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/import-uc-resource-to-bundle.py" \
  --type external_location --name raw_zone --resource-key raw_zone_loc
```

The three workarounds, ranked by risk:
[`${CLAUDE_SKILL_DIR}/references/uc-resource-binding-workarounds.md`](references/uc-resource-binding-workarounds.md).

### Step 4: Rotate a customer-managed key (D8)

CMK rotation needs the whole workspace drained. Inventory the running compute (via
`external_locations_list` / the CLI), then plan the drain — dry-run by default:

```bash
databricks clusters list --output json > /tmp/inv-clusters.json   # + warehouses, pools
python3 "${CLAUDE_SKILL_DIR}/scripts/drain-workspace.py" --inventory inv.json          # dry-run
python3 "${CLAUDE_SKILL_DIR}/scripts/drain-workspace.py" --inventory inv.json --execute --manifest drain.json
# ... rotate the CMK per cloud, then:
python3 "${CLAUDE_SKILL_DIR}/scripts/drain-workspace.py" --resume drain.json
```

Per-cloud playbooks (AWS/Azure/GCP):
[`${CLAUDE_SKILL_DIR}/references/cmk-rotation-by-cloud.md`](references/cmk-rotation-by-cloud.md).

### Step 5: Audit the PrivateLink cost leak (D9)

PrivateLink covers the control plane only. Audit the data-plane VPC for the S3/STS/Kinesis
endpoints and emit remediation Terraform for any that are missing:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/audit-vpc-endpoints.py" \
  --present s3 --vpc-id vpc-abc --region us-east-1 --emit-terraform
```

The full per-service leak/fix map:
[`${CLAUDE_SKILL_DIR}/references/cost-leak-map.md`](references/cost-leak-map.md).

## Output

- **A hook backup + advisory** — before each deploy, a validated known-good state
  backup and, if the state is corrupt/shrunk, the #4986 recovery message.
- **A retry recommendation** — on the exact D6 signature, a one-retry recommendation
  with the reason (never a masked error).
- **A UC import plan** — the `resources:` YAML + Terraform `import` block/command to
  adopt an existing UC resource, with the self-deprecation notice.
- **A drain / resume plan** — the idempotent list of compute to terminate for CMK
  rotation and the manifest to resume exactly what was drained.
- **A VPC-endpoint verdict** — SAFE or a COST LEAK finding naming the missing
  S3/STS/Kinesis endpoints, with remediation Terraform.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `unexpected EOF reading terraform.tfstate` | Terraform-engine state read bug on redeploy (D5, #4986) | Restore the guard's cached backup, or `DATABRICKS_BUNDLE_ENGINE=direct`. |
| `User does not have CREATE TABLE on Schema '…'` | DAB GRANT-ordering (D6, #4573) | Re-run the deploy once; grants were applied by the failed pass. Persists after one retry → real missing grant. |
| `bundle bind` rejects a UC catalog / external location | Unsupported in the CLI (D4, #4842) | Use `import-uc-resource-to-bundle.py` to generate a Terraform import plan; never hand-edit state. |
| CMK rotation rejected — compute still running | CMK update requires a drained workspace (D8) | `drain-workspace.py --execute`, rotate, then `--resume`. |
| High NAT / cross-AZ cost after PrivateLink | S3/STS/Kinesis have no VPC endpoint (D9) | `audit-vpc-endpoints.py --emit-terraform`; add Gateway (S3) + Interface (STS/Kinesis) endpoints. |

## Examples

### Example 1: "My second `bundle deploy` fails with unexpected EOF reading terraform.tfstate."

D5 (#4986). The `bundle-deploy-guard` hook already cached a known-good state before the
deploy — restore it, then redeploy with `DATABRICKS_BUNDLE_ENGINE=direct` (the direct
engine never reads the state file, so the EOF class cannot fire).

### Example 2: "First deploy to a fresh workspace: User does not have CREATE TABLE on Schema."

D6 (#4573). The `bundle-grant-retry` hook recognises the exact signature and recommends
one retry — the failed first deploy applied the schema grants, so the second succeeds.

### Example 3: "I need to bring an existing external location under my bundle."

D4 (#4842) — `bundle bind` can't. `import-uc-resource-to-bundle.py --type
external_location` emits the `resources:` YAML plus a Terraform `import` block to adopt
it without recreating it or hand-editing state. The script self-deprecates when #4842 closes.

### Example 4: "We turned on PrivateLink but the NAT bill went up."

D9. `audit-vpc-endpoints.py --present s3` finds STS and Kinesis have no Interface
endpoint, so credential-vending and log traffic still cross the NAT — it emits the
remediation Terraform for both.

## Resources

- [`${CLAUDE_SKILL_DIR}/references/uc-resource-binding-workarounds.md`](references/uc-resource-binding-workarounds.md) — the D4 `bundle bind` gap + 3 ranked workarounds (#4842).
- [`${CLAUDE_SKILL_DIR}/references/bundle-engine-tradeoffs.md`](references/bundle-engine-tradeoffs.md) — Terraform vs direct engine, the D5 EOF bug (#4986).
- [`${CLAUDE_SKILL_DIR}/references/cmk-rotation-by-cloud.md`](references/cmk-rotation-by-cloud.md) — AWS/Azure/GCP CMK rotation playbooks + the drain requirement (D8).
- [`${CLAUDE_SKILL_DIR}/references/cost-leak-map.md`](references/cost-leak-map.md) — the PrivateLink S3/STS/Kinesis NAT cost leak + fix map (D9).
- [`${CLAUDE_SKILL_DIR}/scripts/import-uc-resource-to-bundle.py`](scripts/import-uc-resource-to-bundle.py) — self-deprecating UC-resource import-plan generator (D4).
- [`${CLAUDE_SKILL_DIR}/scripts/drain-workspace.py`](scripts/drain-workspace.py) — idempotent drain + resume for CMK rotation (D8).
- [`${CLAUDE_SKILL_DIR}/scripts/audit-vpc-endpoints.py`](scripts/audit-vpc-endpoints.py) — VPC-endpoint audit + remediation Terraform (D9).
- [`${CLAUDE_SKILL_DIR}/hooks/bundle-deploy-guard.py`](hooks/bundle-deploy-guard.py) — PreToolUse state backup + validation (D5).
- [`${CLAUDE_SKILL_DIR}/hooks/bundle-grant-retry.py`](hooks/bundle-grant-retry.py) — PostToolUse D6 retry recommendation (D6).
- [Databricks Asset Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/) · [Customer-managed keys](https://docs.databricks.com/aws/en/security/keys/customer-managed-keys) · [PrivateLink](https://docs.databricks.com/aws/en/security/network/classic/privatelink)

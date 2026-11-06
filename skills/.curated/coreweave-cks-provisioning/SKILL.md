---
name: coreweave-cks-provisioning
description: Review original Terraform CKS cluster, VPC and node-pool plans for cost,
  ownership and replacement risks. Use when reviewing CoreWeave cks provisioning or
  checking supplied operational evidence. Trigger with "coreweave cks provisioning".
allowed-tools: Read, Write, Edit, Bash(python3:*), Grep
version: 1.14.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Portable local Python 3.12+ fixture workflow; optional platform commands
  require separately approved credentials.
tags:
- coreweave
- gpu-cloud
- operations
- offline
---
# CKS infrastructure plan review

> Community-contributed; not affiliated with, endorsed by, or sponsored by CoreWeave, Inc.

## Overview

Review original Terraform CKS cluster, VPC and node-pool plans for cost, ownership and replacement risks.
Use Read for supplied evidence and references, Write for a local report, Edit for a proposed local plan, and Grep for relevant log excerpts. Bash is restricted to Python helpers; no helper makes account calls.

## Prerequisites

- Python 3.12+, the supplied evidence contract and explicit intended context/namespace.
- An owner-reviewed resource scope, timestamps, model provenance and applicable platform versions.
- Redacted local inputs; no kubeconfig, token or customer payload in fixtures or reports.

## Cost and safety gate

Before creating or uploading anything, complete the [mandatory cost gate](references/cost-gate.md).
Show the exact resources, GPU type/count and supplied hourly rate, all other costs,
expiry and teardown. Obtain explicit user confirmation for the reviewed artifact.
Default to local review; neither this helper nor a JSON receipt authorizes execution.

## Instructions

1. Read the evidence contract and classify missing inputs before reviewing a result.
2. Inspect the supplied scope and timestamps. Never fall back to a current context.
3. Run the local helper and preserve the full status, findings and input digest.
4. Resolve blockers and collect missing evidence through an authorized operator.
5. Verify the outcome against the acceptance criteria; distinguish supplied evidence from live observation.

## Examples

Use the fixture replay below before processing redacted operator evidence.

## Output

A JSON report with status, findings, observations, input SHA-256 and evidence boundary.

## Error Handling

| Condition | Response |
| --- | --- |
| Invalid or mismatched input | Stop with a blocker and request corrected evidence. |
| Stale or missing observations | Return incomplete; do not infer healthy or zero cost. |
| Unsupported platform shape | Use a reviewed adapter before claiming compatibility. |

## Resources

- [Primary platform reference](https://registry.terraform.io/providers/coreweave/coreweave/0.26.0/docs)
- [CoreWeave official skills](https://github.com/coreweave/skills) for vendor-maintained workflows.

## Offline verification

Supply `plan` from a redacted Terraform JSON plan, `owned_state` and `cost_gate_reviewed`. Reviewers enumerate exact resource addresses and reject updates/replacements/deletes in this initial create-only workflow. Unknown computed IDs are distinct from unresolved desired configuration. CoreWeave provider 0.26.0 defines VPC and CKS cluster resources; node pools use the Kubernetes provider and NodePool CRD in a separate stage after cluster readiness. This avoids planning a CRD against an API server that does not yet exist. Do not enable prefill or autoscaling without budgeting the extra capacity. Terraform state and plan files can contain credentials and must remain private.

From this skill directory, replay the synthetic example (its timestamp is intentionally
fixed; it contains no account data):

```bash
python3 scripts/review-plan.py --input tests/fixtures/example.json --as-of 2026-11-05T12:01:00Z
```

For current evidence, omit `--as-of`; it defaults to current UTC. Required common
fields: `schema: coreweave-evidence/v1`, `captured_at`, `context`, `namespace`,
`expected_context`, `expected_namespace`. The scope must agree and evidence must
be at most five minutes old. Explicit replay time is for testing historical fixtures,
not a way to make stale production evidence current.

Exit 0 / `reviewed` means the supplied assertions satisfy this bounded contract;
2 / `blocked` requires correction; 3 / `incomplete` requires more evidence. Read the
findings rather than relying only on exit status. Scripts never execute text from
inputs, call a cloud API or authorize a change. Fixture and package checks are
separate from model behavior and live compatibility.

- [Input contract and limitations](references/evidence-contract.md)
- [Skill blueprint and acceptance](docs/BLUEPRINT.md)

## Provisioning procedure after owner approval

The original assets use separate Terraform roots: `assets/terraform/` for a new VPC
and private CKS cluster, and `assets/terraform/node-pool/` for the NodePool CRD.
Use separate owned state and pinned providers. Confirm a private API access route,
least-privilege kubeconfig, available zone/instance type, GPUs per node, supported
Kubernetes version and non-overlapping CIDRs before proposing creation.

1. Supply all variables explicitly. The cluster root defaults to a private API;
   establish the supported authentication/access route with the platform owner.
   Provider authentication uses the approved environment, never committed tfvars.
2. Review a saved plan and its JSON with `scripts/review-plan.py`. The helper accepts
   a redacted plan inside the evidence envelope; it does not produce or apply plans.
   Show exact resources and costs through the cost gate, then obtain confirmation.
3. Apply only that saved plan after checking its digest again. Wait for the cluster
   to be usable before planning the separate node-pool root. Its Kubernetes
   provider must discover the existing NodePool CRD; do not combine both stages
   into one first-create plan.
4. Repeat the cost gate for the pool, including node count × GPUs per node, capacity
   terms and retention. Autoscaling and prefill are explicitly disabled. GPU driver
   changes and rack-sized pools require a separate reviewed design.
5. Verify owner-supplied cluster status, pool desired/ready counts and allocatable
   GPUs, then run the verify-only workload-health skill on a supplied snapshot.
   Terraform apply success is not proof of workload readiness.

```bash
# Operator-only commands; not run by offline tests. Work inside the reviewed root.
terraform plan -out=reviewed.tfplan
terraform show -json reviewed.tfplan > reviewed-plan.private.json
# STOP: inspect, redact for sharing, hash the artifact and confirm exact cost/scope.
terraform apply reviewed.tfplan
# Teardown proposal for this dedicated state, never a shared state:
terraform plan -destroy -out=reviewed-destroy.tfplan
# STOP: review ownership and retention again before applying a destruction plan.
```

Both resources use `prevent_destroy`; a destroy plan intentionally refuses until
its removal has been separately reviewed for the owned resources. Never route
around it with targeted destruction. Keep state, plans and provider credentials
private. [Provisioning contract](references/provisioning-contract.md) describes
mock validation and the unresolved live-account boundary.

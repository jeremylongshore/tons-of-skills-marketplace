---
name: coreweave-core-workflow-a
description: 'Review a CoreWeave self-managed inference release, readiness and GPU scheduling. Use when deploying a model on CKS, checking KServe prerequisites, or diagnosing an inference rollout. Trigger with coreweave inference service, coreweave model serving, or coreweave kserve.'
allowed-tools: Read, Write, Edit, Bash(kubectl:*), Bash(python3:*), Grep
version: 1.13.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- gpu-cloud
- kubernetes
- inference
- coreweave
compatibility: Designed for Claude Code
---
# CoreWeave Inference deployment preflight

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Review a self-managed CKS inference release and verify readiness before traffic.
Use Read to inspect the approved input files, Write the evidence report, and Edit only the proposed local artifact before review.
These procedures complement [CoreWeave’s official skills](https://github.com/coreweave/skills); they do not redistribute or replace that upstream distribution.

## Prerequisites

- The owner-approved organization, cluster context, namespace and resource names.
- A trusted kubeconfig from the approved secret location; no raw credentials in source, logs or terminal history.
- Installed kubectl compatible with the cluster, and authority for each proposed read or change.
- An agreed success criterion, resource budget, evidence destination and recovery owner.

## Cost and safety gate

Before any billable action, follow the [mandatory cost gate](references/cost-gate.md).
Use the local `scripts/review-cost-plan.py` helper to inspect the exact plan;
then obtain explicit user confirmation through the trusted approval channel.
No plan, missing price, changed digest or expired approval means no execution.
Default to offline inspection; server dry-run and Terraform plan are account calls.

## Instructions

1. Use CoreWeave official skills for creating the cluster/Node Pool and deploying a self-managed vLLM service. Choose explicitly between self-managed CKS, Dedicated Inference and Serverless Inference.

2. For self-managed CKS, inspect the reviewed Deployment and Service. Require an immutable image, approved model/version/license, secret references, measured host/GPU memory budget and health/startup/readiness probes.

3. Do not assume KServe or Knative is bundled with every CKS cluster. If a KServe design is requested, first verify the installed CRDs, controller versions and supported autoscaler configuration.

4. Run server dry-run and inspect the diff before an approved staging rollout. Bound replicas and GPU capacity; ensure readiness verifies the loaded model rather than only a process listening on a port.

5. Test through the approved private route with non-sensitive input. Compare correctness, latency, error rate and cold-start behavior before production approval; scaling Pods to zero does not necessarily remove reserved capacity charges.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get "deployment/$CW_DEPLOYMENT" "service/$CW_SERVICE"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" apply --dry-run=server -f inference-reviewed.yaml
# After approval of the reviewed staging change:
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" apply -f inference-reviewed.yaml
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" rollout status "deployment/$CW_DEPLOYMENT" --timeout=15m
```

These are operator examples, not commands run by this package’s offline tests. Mutating examples require approval for the exact manifest, environment and budget before execution.

## Output

- A UTC-stamped review identifying the observed state, evidence coverage and unresolved assumptions.
- A specific proposed next step, the owner who can authorize it, and a measurable acceptance or recovery check.
- A clear incomplete result when credentials, capacity, metrics or live validation are unavailable.

## Error Handling

| Condition | Response |
|---|---|
| Authentication or authorization denied | Stop; verify the intended identity and scope without escalating permissions automatically. |
| Empty or stale evidence | Record unknown and collect a bounded fresh sample; never substitute zero or healthy. |
| Admission, rollout or acceptance failure | Preserve the sanitized error and use the reviewed recovery path with its owner. |
| Output may contain a secret or workload data | Restrict sharing and review/redact before retaining or uploading it. |

## Resources

- [Operator details and evidence boundaries](references/operator-notes.md)
- [Primary reference 1](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling)
- [Primary reference 2](https://docs.coreweave.com/products/cks/deploy-model)
- [Primary reference 3](https://docs.coreweave.com/products/inference/scaling)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.

## Offline verification

The helper consumes an InferenceService object in `manifest`, CRD names in `crds`, `controller_version`, `model_provenance` (license_reviewed and SHA-256), `expected_model`, and a supplied `endpoint_result` (status_code, model, accepted). It checks observedGeneration against metadata.generation, GPU limits, bounded replicas and the model response independently. It supports the KServe model predictor shape in the fixture, not every custom predictor. Do not substitute Deployment readiness for endpoint acceptance. A source digest is not proof of the served weights unless the endpoint acceptance procedure binds that digest.

From this skill directory, replay the synthetic example (its timestamp is intentionally
fixed; it contains no account data):

```bash
python3 scripts/review-inference.py --input tests/fixtures/example.json --as-of 2026-11-05T12:01:00Z
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

---
name: coreweave-enterprise-rbac
description: 'Configure RBAC and namespace isolation for CoreWeave multi-team GPU
  access.

  Use when managing team permissions, isolating GPU quotas,

  or implementing namespace-level access control.

  Trigger with phrases like "coreweave rbac", "coreweave permissions",

  "coreweave namespace isolation", "coreweave team access".

  '
allowed-tools: Read, Write, Edit, Bash(kubectl:*), Bash(python3:*), Grep
version: 1.15.0
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
# CoreWeave Access-boundary review

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Review organization permissions, Kubernetes RBAC and workload isolation independently.
Use Read to inspect the approved input files, Write the evidence report, and Edit only the proposed local artifact before review.
These procedures complement [CoreWeave’s official skills](https://github.com/coreweave/skills); they do not redistribute or replace that upstream distribution.

## Prerequisites

- The owner-approved organization, cluster context, namespace and resource names.
- A trusted kubeconfig from the approved secret location; no raw credentials in source, logs or terminal history.
- Installed kubectl compatible with the cluster, and authority for each proposed read or change.
- An agreed success criterion, resource budget, evidence destination and recovery owner.

## Instructions

1. Distinguish CoreWeave organization/token permissions from Kubernetes Roles, RoleBindings and service accounts. There is no universal built-in “Team Lead” role with every permission listed by this pack.

2. Have the organization and cluster owners approve the exact identity, namespace, verbs and resources. Prefer scoped group bindings and dedicated workload identities; avoid granting edit/admin solely to fix a denied diagnostic command.

3. Use kubectl auth can-i for the current identity. Impersonation checks require explicit impersonation privilege; do not claim a denied impersonation attempt proves the target user is denied.

4. Review cross-namespace and escalation paths, including Pod creation, Secrets, RoleBindings and service-account token creation. Quotas constrain resource consumption, not access to another tenant’s data.

5. Test both allowed and denied cases with the authorized identity in staging. Keep revocation, token expiry and audit ownership explicit. Namespace isolation alone does not establish regulatory compliance.

## Examples

Set `CW_CONTEXT` and `CW_NAMESPACE` from the approved access request. Set each referenced resource variable to the exact owner-selected resource, not a wildcard or the first matching Pod.

```bash
: "${CW_CONTEXT:?approved context required}" "${CW_NAMESPACE:?approved namespace required}"
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" auth can-i create jobs.batch
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" auth can-i get secrets
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" auth can-i create rolebindings.rbac.authorization.k8s.io
kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" get rolebinding,serviceaccount,resourcequota
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
- [Primary reference 1](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Primary reference 2](https://docs.coreweave.com/products/cks/auth-access/managed-auth/kubeconfig)
- [Primary reference 3](https://docs.coreweave.com/products/cks/clusters/scheduling/workload-scheduling)

## Evidence status

Source-reviewed guidance with offline repository checks. No live CoreWeave account, paid GPU workload or provider-backed behavioral evaluation was used to validate this guide. Record live results separately before claiming workload success.

## Offline verification

Input contains Kubernetes `roles` and `bindings`, an exact `subject` (kind/name/namespace), and `snapshot_complete`. Roles use their Kubernetes kind, metadata and rules; roleRef resolution preserves Role namespace versus ClusterRole scope. The helper detects direct matching subjects, wildcard access, sensitive credential access and workload/impersonation/escalation paths. It does not expand group membership, aggregated ClusterRoles, admission policy or external identity systems. If any is relevant, completeness is false and a broader authorized access audit is required. The report does not claim a definitive authorization decision.

From this skill directory, replay the synthetic example (its timestamp is intentionally
fixed; it contains no account data):

```bash
python3 scripts/review-access.py --input tests/fixtures/example.json --as-of 2026-11-05T12:01:00Z
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

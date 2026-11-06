# Evidence contract: Effective access review

Community-contributed; not affiliated with CoreWeave.

Input contains Kubernetes `roles` and `bindings`, an exact `subject` (kind/name/namespace), and `snapshot_complete`. Roles use their Kubernetes kind, metadata and rules; roleRef resolution preserves Role namespace versus ClusterRole scope. The helper detects direct matching subjects, wildcard access, sensitive credential access and workload/impersonation/escalation paths. It does not expand group membership, aggregated ClusterRoles, admission policy or external identity systems. If any is relevant, completeness is false and a broader authorized access audit is required. The report does not claim a definitive authorization decision.

## Input and review boundary

The packaged `tests/fixtures/example.json` is the complete normalized input example.
`cases.json` includes specific negative outcomes as well as stale, wrong-scope and
injected-instruction variants. Inputs are supplied observations, not authenticated
proof. Review the source of every boolean assertion. The common envelope records
intended and observed scope plus a timezone-aware capture timestamp. Output includes
the SHA-256 of the actual bytes read, never a token or raw log excerpt.

Read-only collection commands and upload/deploy commands belong to the human-approved
operator workflow. Helper parsing is intentionally independent of credentials and
network availability. Unknown nested platform formats fail closed; add a reviewed
fixture before extending an adapter.

## Source and review

Primary source: https://kubernetes.io/docs/reference/access-authn-authz/rbac/

Contract reviewed 2026-11-05. Repository examples are original. Vendor version and
account-specific availability must be confirmed separately; no live operation was
performed for this pack. See the blueprint for requirements and release boundaries.

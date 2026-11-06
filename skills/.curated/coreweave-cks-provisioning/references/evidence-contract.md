# Evidence contract: CKS infrastructure plan review

Community-contributed; not affiliated with CoreWeave.

Supply `plan` from a redacted Terraform JSON plan, `owned_state` and `cost_gate_reviewed`. Reviewers enumerate exact resource addresses and reject updates/replacements/deletes in this initial create-only workflow. Unknown computed IDs are distinct from unresolved desired configuration. CoreWeave provider 0.26.0 defines VPC and CKS cluster resources; node pools use the Kubernetes provider and NodePool CRD in a separate stage after cluster readiness. This avoids planning a CRD against an API server that does not yet exist. Do not enable prefill or autoscaling without budgeting the extra capacity. Terraform state and plan files can contain credentials and must remain private.

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

Primary source: https://registry.terraform.io/providers/coreweave/coreweave/0.26.0/docs

Contract reviewed 2026-11-05. Repository examples are original. Vendor version and
account-specific availability must be confirmed separately; no live operation was
performed for this pack. See the blueprint for requirements and release boundaries.

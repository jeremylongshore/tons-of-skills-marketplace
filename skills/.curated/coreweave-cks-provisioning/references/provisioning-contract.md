# Original CKS Terraform contract

Community-contributed; not affiliated with CoreWeave.

The cluster root uses CoreWeave provider 0.26.0. Its documented resource schemas
cover `coreweave_networking_vpc` and `coreweave_cks_cluster`. The node-pool root uses
HashiCorp Kubernetes provider 2.38.0 with `kubernetes_manifest` for the documented
`compute.coreweave.com/v1alpha1` NodePool. No proprietary official skill code is
included. The roots, variables and mock assertions were authored for this pack.

Sources inspected 2026-11-05:

- [Pinned CoreWeave provider schemas](https://github.com/coreweave/terraform-provider-coreweave/tree/v0.26.0/docs)
- [Node Pool API](https://docs.coreweave.com/products/cks/reference/node-pool)
- [Node Pool management](https://docs.coreweave.com/products/cks/nodes/manage)

Terraform 1.7+ mock providers support the packaged `tests/offline.tftest.hcl`
files. After dependency installation, `terraform test` in each root uses the mock
provider and never creates cloud resources. Normal `terraform plan`, including
`-refresh=false`, is not a substitute for mock tests: provider planning can contact
an API. Run tests with account credentials absent. Tests demonstrate template
invariants, not provider authentication, zone capacity, CRD installation or service
availability. Provider lockfiles pin downloaded dependency hashes.

New private clusters need an approved access route and authentication arrangement.
Review all CIDRs for overlap and zone constraints; syntactically valid CIDRs alone
are insufficient. Node pools can cause replacement/prefill capacity beyond the
steady-state target; this template disables prefill and autoscaling until separately
budgeted. `prevent_destroy` is deliberate. Retained volumes, capacity agreements
and state backups need their own cost/retention decisions.

The offline plan adapter resolves computed `vpc_id` only through a direct root-module
reference to exactly one reviewed VPC in the same plan. Module, indexed, conditional
and external references require separate operator review; unresolved settings remain blocked.

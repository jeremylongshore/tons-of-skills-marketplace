# Validation and execution

Select checks that answer a concrete question. Record their tool/version, target,
command, exit status and limits. A generated artifact is not a passed check.

## Validation levels

| Level                | Evidence and limits                                                                                                                          |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Static review        | Check syntax, variable references, permissions and repository conventions; no runtime health claim.                                          |
| Tool validation      | Run only available, authorized format/schema/config checks. Record required downloads and execution rather than calling every check offline. |
| Environment plan     | Bind account/project/region/workspace/cluster and inputs. Inspect intended effects and unresolved values. A plan is not a deployment.        |
| Deployment           | Run the authorized reviewed operation; capture actual resource/operation IDs and failures.                                                   |
| Runtime verification | Check resource readiness, workload behavior and requested integrations; report untested failure and recovery paths.                          |

## Terraform

- `terraform fmt -check` checks formatting. It does not validate architecture or deployment.
- Initialization can access backends/registries and install provider plugins/modules.
  Review the selected source and versions; do not initialize arbitrary downloaded
  code solely to inspect it. `-backend=false` avoids backend initialization, but
  does not turn initialization into a no-network or no-execution sandbox.
- `terraform validate` checks configuration consistency after required dependencies
  are available. It does not establish that a live account can deploy the plan.
- A plan can read remote state and provider APIs, acquire a state lock, and execute
  provider/data-source logic. Review source and target before running it. Preserve
  the relevant plan and source/input binding for an authorized apply.
- Applying a saved plan executes without Terraform's interactive approval prompt.
  Do not rely on the CLI prompt as the authorization boundary.
- Plans and state may contain secrets even when terminal fields say sensitive.
  Store them in protected locations with appropriate access and retention. Do not
  commit them, publish their JSON, or paste full contents into a report.
- Destroying resources is not a universal rollback. Document state migration,
  backup/restore and data-loss consequences for the actual resource changes.

## Containers and Kubernetes

- A Docker build executes build instructions and may download dependencies. A
  successful build is not a live health or vulnerability assessment. Starting
  Compose services can expose ports, mount paths and create persistent data.
- Bind kubectl operations to the selected context/namespace. Server-side dry runs
  contact the cluster; do not equate dry-run wording with no remote interaction.
  Record the actual command/mode and what it checked.
- Do not apply manifests, enable a generated deployment workflow, create cloud
  resources or roll back a live workload beyond the task's authorization. Preserve
  authorization already given rather than repeating approval requests.

## Evidence and control claims

Cost estimates require rates, units and workload assumptions; identify omitted
storage, network, support or tax items where relevant. A small estimate is not a
provider-enforced spending cap.

For regulated workloads, list the identified technical controls and missing owner
or legal evidence. For example, HHS cloud guidance discusses responsibilities,
risk assessment and applicable business-associate agreements; a generated storage
configuration is not evidence of HIPAA compliance. Do not assert a universal
"HIPAA requires dedicated tenancy" rule.

## Primary references

Checked 2026-10-25; consult the selected provider/tool version before execution.

- [Terraform initialization](https://developer.hashicorp.com/terraform/cli/commands/init)
- [Terraform validation](https://developer.hashicorp.com/terraform/cli/commands/validate)
- [kubectl apply modes](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_apply/)
- [Terraform plan reference](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [Saved-plan application and sensitive values](https://developer.hashicorp.com/terraform/tutorials/cli/plan)
- [Terraform backend configuration](https://developer.hashicorp.com/terraform/language/backend)
- [HHS guidance on HIPAA and cloud computing](https://www.hhs.gov/hipaa/for-professionals/special-topics/health-information-technology/cloud-computing/index.html)

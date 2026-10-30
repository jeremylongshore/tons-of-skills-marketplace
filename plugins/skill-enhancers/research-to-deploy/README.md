# Research to Deploy

Research current infrastructure documentation, generate reviewable configurations
and runbooks, and execute scoped deployments when authorized.

## Installation

```text
/plugin install research-to-deploy@claude-code-plugins-plus
```

## Usage

- "Research Cloud Run options and generate Terraform for this API."
- "Prepare a Fargate staging deployment using our existing IaC."
- "Draft AKS manifests and a runbook without accessing a cluster."

The skill reads application and infrastructure context, checks primary provider
sources, explains architecture choices and produces the artifacts the task needs.
It can use Terraform, containers or Kubernetes within the user's authorized scope.
There is no bundled cloud deployment service or separate cloud account provisioning.

## Deliverables

Research notes, configuration files, a cost model when inputs support it, optional
CI/CD configuration, and a validation/deployment/recovery runbook. Evidence reports
which checks ran and whether anything was actually deployed. Missing tools or
credentials are recorded as limitations; generation does not require cloud login.

Generated files do not establish production readiness, compliance, a spending cap
or an SLA. Deployment depends on the selected environment, toolchain, authorization
and actual validation results.

## License

MIT. See [LICENSE](LICENSE).

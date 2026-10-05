# DevOps Infrastructure Plugins

A comprehensive collection of 25 DevOps infrastructure plugins for Claude Code, covering the entire DevOps lifecycle.

## Plugin Collection Overview

### Container Orchestration (4 plugins)

- **docker-compose-generator** - Generate Docker Compose configurations with best practices
- **kubernetes-deployment-creator** - Create K8s deployments, services, and configurations
- **helm-chart-generator** - Generate Helm charts for Kubernetes applications
- **container-registry-manager** - Manage container registries (ECR, GCR, Harbor)

### CI/CD & Deployment (5 plugins)

- **ci-cd-pipeline-builder** - Build pipelines for GitHub Actions, GitLab CI, Jenkins
- **deployment-pipeline-orchestrator** - Orchestrate multi-stage deployment pipelines
- **deployment-rollback-manager** - Manage deployment rollbacks with safety checks
- **gitops-workflow-builder** - Build GitOps workflows with ArgoCD and Flux
- **infrastructure-drift-detector** - Detect infrastructure drift from desired state

### ️ Infrastructure as Code (3 plugins)

- **infrastructure-as-code-generator** - Generate Terraform, CloudFormation, Pulumi code
- **terraform-module-builder** - Build reusable Terraform modules
- **ansible-playbook-creator** - Create Ansible playbooks for configuration management

### Security & Compliance (3 plugins)

- **container-security-scanner** - Scan containers with Trivy, Snyk
- **compliance-checker** - Check SOC2, HIPAA, PCI-DSS compliance
- **secrets-manager-integrator** - Integrate Vault, AWS Secrets Manager

### ️ Configuration & Scaling (4 plugins)

- **environment-config-manager** - Manage environment configurations and secrets
- **auto-scaling-configurator** - Configure HPA and auto-scaling policies
- **load-balancer-configurator** - Configure ALB, NLB, Nginx, HAProxy
- **network-policy-manager** - Manage K8s network policies and firewall rules

### Monitoring & Observability (2 plugins)

- **monitoring-stack-deployer** - Deploy Prometheus, Grafana, Datadog
- **log-aggregation-setup** - Set up ELK, Loki, Splunk logging

### Service Management (2 plugins)

- **service-mesh-configurator** - Configure Istio, Linkerd for microservices
- **cloud-cost-optimizer** - Optimize cloud costs with FinOps practices

### Backup & Recovery (2 plugins)

- **backup-strategy-implementor** - Implement database and application backups
- **disaster-recovery-planner** - Plan and implement disaster recovery procedures

## Installation

### Install Individual Plugins

```bash
# Container orchestration
/plugin install docker-compose-generator@claude-code-plugins-plus
/plugin install kubernetes-deployment-creator@claude-code-plugins-plus

# CI/CD
/plugin install ci-cd-pipeline-builder@claude-code-plugins-plus
/plugin install deployment-pipeline-orchestrator@claude-code-plugins-plus

# Infrastructure as Code
/plugin install infrastructure-as-code-generator@claude-code-plugins-plus
/plugin install terraform-module-builder@claude-code-plugins-plus

# Security
/plugin install container-security-scanner@claude-code-plugins-plus
/plugin install compliance-checker@claude-code-plugins-plus

# And more... (see full list above)
```

### Install All DevOps Plugins at Once

```bash
# Install the complete DevOps Automation Pack
/plugin install devops-automation-pack@claude-code-plugins-plus
```

## Usage Examples

### Docker Compose

```bash
/docker-compose
# Generates production-ready Docker Compose configurations
```

### Kubernetes

```bash
/k8s-deploy
# Creates complete K8s manifests with deployments, services, ingress
```

### CI/CD

```bash
/ci-cd-build
# Builds GitHub Actions, GitLab CI, or Jenkins pipelines
```

### Infrastructure as Code

```bash
/iac-generate
# Generates Terraform, CloudFormation, or Pulumi code
```

### Container Security

```bash
/container-scan
# Scans containers for vulnerabilities using Trivy
```

## Key Features Across All Plugins

- **Production-Ready**: All configurations follow industry best practices
- **Multi-Platform**: Support for AWS, GCP, Azure, and on-premises
- **Security-First**: Built-in security configurations and compliance checks
- **Scalable**: Auto-scaling and high-availability patterns included
- **Well-Documented**: Comprehensive examples and inline documentation
- **Modular**: Mix and match plugins based on your needs

## Plugin Categories

### Featured Plugins

These plugins are marked as featured in the marketplace:

- docker-compose-generator
- kubernetes-deployment-creator
- ci-cd-pipeline-builder
- infrastructure-as-code-generator

### Complete DevOps Workflow

1. **Development**: Use docker-compose-generator for local environments
2. **Infrastructure**: Generate IaC with infrastructure-as-code-generator
3. **CI/CD**: Build pipelines with ci-cd-pipeline-builder
4. **Security**: Scan with container-security-scanner
5. **Deployment**: Deploy with kubernetes-deployment-creator
6. **Monitoring**: Set up with monitoring-stack-deployer
7. **Operations**: Manage with deployment-rollback-manager
8. **Optimization**: Optimize with cloud-cost-optimizer

## Technologies Supported

### Container Platforms

- Docker & Docker Compose
- Kubernetes (K8s)
- Amazon ECS/EKS
- Google GKE
- Azure AKS

### CI/CD Platforms

- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI
- Travis CI

### Infrastructure as Code

- Terraform
- CloudFormation
- Pulumi
- ARM Templates
- CDK (AWS/Terraform)

### Cloud Providers

- Amazon Web Services (AWS)
- Google Cloud Platform (GCP)
- Microsoft Azure
- DigitalOcean
- On-premises/Hybrid

### Security Tools

- Trivy
- Snyk
- Vault
- AWS Secrets Manager
- SOPS

### Monitoring & Logging

- Prometheus
- Grafana
- Datadog
- ELK Stack
- Loki
- Splunk

### Service Mesh

- Istio
- Linkerd
- Consul

### GitOps Tools

- ArgoCD
- Flux
- Jenkins X

## Contributing

Found a bug or want to add a feature to a plugin? See our [Contributing Guide](../../000-docs/007-DR-GUID-contributing.md).

## License

All plugins are licensed under MIT License. See individual plugin directories for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/jeremylongshore/claude-code-plugins/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jeremylongshore/claude-code-plugins/discussions)

---

**Total Plugins**: 25
**Category**: DevOps Infrastructure
**Maintainer**: Jeremy Longshore ([@jeremylongshore](https://github.com/jeremylongshore))
**Last Updated**: October 2025

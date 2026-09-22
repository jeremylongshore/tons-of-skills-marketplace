# CodeRabbit Skill Pack

Twenty-four evidence-backed operator workflows for current CodeRabbit reviews,
configuration, CLI use, organization governance, security, reporting, REST API
integration, and incident response.

## Installation

```bash
/plugin install coderabbit-pack@claude-code-plugins-plus
```

## Operating model

- Every workflow links to dated first-party CodeRabbit documentation.
- Git-provider behavior is distinguished from CodeRabbit behavior.
- Live repository, organization, billing, role, API, and merge-policy changes
  stop at explicit human approval boundaries.
- Current plan prices, limits, permissions, schema fields, and feature
  availability are re-verified before execution.
- CodeRabbit supplements independent tests, security scanning, and human review.

## Skills

### Review and configuration

| Skill | Operator job |
|---|---|
| `coderabbit-hello-world` | Prove one bounded first review and clean up |
| `coderabbit-core-workflow-a` | Run a PR review and disposition findings |
| `coderabbit-core-workflow-b` | Tune learnings, guidelines, and path guidance |
| `coderabbit-common-errors` | Triage skipped, noisy, or misconfigured reviews |
| `coderabbit-multi-env-setup` | Govern target-branch review eligibility |
| `coderabbit-performance-tuning` | Tune measured scope, signal, cache, and review behavior |
| `coderabbit-upgrade-migration` | Upgrade configuration through schema validation |

### Installation and delivery

| Skill | Operator job |
|---|---|
| `coderabbit-install-auth` | Install by platform and authenticate the CLI safely |
| `coderabbit-local-dev-loop` | Run bounded local CLI review and fix loops |
| `coderabbit-ci-integration` | Design review-state and provider-check merge policy |
| `coderabbit-deploy-integration` | Roll out central configuration in cohorts |
| `coderabbit-prod-checklist` | Decide production readiness with evidence |
| `coderabbit-migration-deep-dive` | Migrate from an existing review process safely |
| `coderabbit-reference-architecture` | Map control, data, identity, and review boundaries |

### Governance, data, and operations

| Skill | Operator job |
|---|---|
| `coderabbit-enterprise-rbac` | Audit native roles, custom roles, seats, and API access |
| `coderabbit-cost-tuning` | Analyze current plans, seats, limits, and credits |
| `coderabbit-data-handling` | Govern cache, retention, exports, and sensitive paths |
| `coderabbit-security-basics` | Layer CodeRabbit security capabilities with independent gates |
| `coderabbit-observability` | Measure reviews from documented metrics and exports |
| `coderabbit-rate-limits` | Diagnose current PR, IDE, and CLI allowances |
| `coderabbit-debug-bundle` | Produce a minimal redacted diagnostic package |
| `coderabbit-incident-runbook` | Contain incidents without silently bypassing safeguards |
| `coderabbit-webhooks-events` | Automate verified Git-provider review events |
| `coderabbit-sdk-patterns` | Build a thin adapter for documented REST API operations |

## Important contract corrections

- Repository YAML is read from the feature branch under review; target-branch
  eligibility is controlled by `reviews.auto_review.base_branches`.
- CodeRabbit review state, GitHub Checks ingestion, and branch protection are
  separate contracts. Never guess a required-check name.
- CodeRabbit now documents native roles and an authenticated REST API for
  eligible plans and permissions.
- Normal PR-review automation uses Git-provider events; this pack does not
  invent a separate outgoing CodeRabbit webhook or signing secret.
- Prices, limits, and review timings are not frozen into these skills.

## License

MIT

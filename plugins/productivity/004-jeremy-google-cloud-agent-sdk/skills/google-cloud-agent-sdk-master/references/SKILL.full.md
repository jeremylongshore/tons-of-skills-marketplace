# Google agents-cli Lifecycle Reference

Source baseline: [`google/agents-cli`](https://github.com/google/agents-cli),
verified 2026-09-09. Always prefer the installed command's `--help` when a flag
or target differs from this reference.

## Product Boundary

`agents-cli` is a lifecycle tool for applications built with Google ADK. It is
not itself a coding agent and it is not a replacement for Claude Code, Codex, or
Antigravity. It provides commands and Agent Skills that help those coding agents
build, evaluate, deploy, publish, and observe ADK applications.

Agent Starter Pack is in maintenance mode. New projects should use
`google-agents-cli`; existing Starter Pack projects should migrate rather than
accumulate new template-specific work.

## Installation and Discovery

Check prerequisites before modifying the machine:

```bash
python --version
uvx --version
node --version
```

The maintained setup entry point is:

```bash
uvx google-agents-cli setup
```

For skills only, Google's repository documents:

```bash
npx skills add google/agents-cli
```

Inspect commands rather than guessing flags:

```bash
uvx google-agents-cli --help
agents-cli --help
agents-cli info
```

## Scaffold

Create a new project:

```bash
agents-cli create PROJECT_NAME
```

Enhance or upgrade an existing project:

```bash
agents-cli scaffold enhance
agents-cli scaffold upgrade
```

Before running a scaffold command:

1. Confirm the absolute destination.
2. Inspect existing files and repository instructions.
3. Record the CLI version.
4. Show the exact command and expected write scope.
5. Require approval if files will be created or overwritten.

Do not preserve old Agent Starter Pack template names as if they were current
`agents-cli` choices. Ask `agents-cli create --help` for the installed release's
supported languages, frameworks, and flags.

## Develop

Current command families include:

```bash
agents-cli install
agents-cli run "PROMPT"
agents-cli lint
```

Use the generated project's configuration and tests as authoritative. Define:

- agent purpose and instruction contract
- tool and user-visible description
- model selection rationale
- tool input, output, timeout, and error behavior
- session state and persistence boundaries
- callbacks and policy checks
- unit, integration, and evaluation cases

Never store an AI Studio key, service-account JSON, access token, or generated
credential in tracked files.

## Evaluate

The maintained CLI separates generation, grading, comparison, analysis, and
optimization:

```bash
agents-cli eval run
agents-cli eval generate
agents-cli eval grade
agents-cli eval compare
agents-cli eval analyze
agents-cli eval metric list
agents-cli eval dataset synthesize
agents-cli eval optimize
```

An evaluation receipt should identify the dataset, metric configuration, model,
CLI version, environment, result artifact, and exit status. Treat LLM-as-judge
scores as measured evidence with variance, not deterministic proof.

## Deploy

Google's current skills cover Agent Runtime, Cloud Run, and GKE deployment.
Resolve available targets and flags from:

```bash
agents-cli deploy --help
agents-cli infra --help
```

Before deployment, state:

- Google Cloud project and region
- runtime and why it fits
- identity and least-privilege IAM plan
- secret storage and injection path
- APIs and quotas required
- network exposure and authentication
- observability and rollback checks
- pricing pages that must be reviewed

The CLI also exposes infrastructure workflows including `infra single-project`
and `infra cicd`. These provision external resources; require explicit approval
for the exact project and target.

## Publish

Gemini Enterprise registration is a separate external mutation:

```bash
agents-cli publish gemini-enterprise --help
```

Do not equate a successful cloud deployment with successful publication. Report
the deployed service and the registered Gemini Enterprise resource separately.

## Observe and Operate

Verify the generated project's logging and tracing configuration. For each live
deployment capture:

- health and readiness result
- one successful smoke invocation
- one expected failure path
- trace or log correlation identifier
- rollback command or prior revision
- quota and billing-alert ownership

Avoid absolute security claims. Cloud deployment inherits the security of its
IAM, network, tool, data, and secret configuration.

## Agent Starter Pack Migration

Use Google's current migration guide. A migration should preserve agent code,
tests, Terraform, and CI/CD where supported, then replace obsolete Makefile and
Starter Pack CLI instructions with the corresponding `agents-cli` workflow.

Inventory before changing:

```text
agent code
evaluation datasets and metrics
deployment configuration
Terraform state and modules
CI/CD identities and secrets
observability configuration
environment-specific variables
```

Run the upgraded lint, local smoke, evaluation, and infrastructure plan before
any deployment. Keep the old deployment available until the new health and
rollback checks pass.

## Current Primary Sources

- https://github.com/google/agents-cli
- https://google.github.io/agents-cli/
- https://google.github.io/agents-cli/reference/from-agent-starter-pack/
- https://google.github.io/adk-docs/
- https://cloud.google.com/run/pricing
- https://cloud.google.com/kubernetes-engine/pricing
- https://cloud.google.com/vertex-ai/generative-ai/pricing

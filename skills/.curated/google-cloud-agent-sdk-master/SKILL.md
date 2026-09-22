---
name: google-cloud-agent-sdk-master
description: >-
  Build, evaluate, deploy, publish, or modernize Google ADK agent applications
  with Google's maintained agents-cli workflow. Use when a request mentions
  Google Agent Development Kit, agents-cli, Gemini Enterprise Agent Platform,
  Agent Runtime, Cloud Run or GKE agent deployment, or migration from Agent
  Starter Pack. For Claude Code agents/*.md definitions, use agent-creator
  instead. Trigger with "build a Google ADK agent", "deploy this ADK app", or
  "migrate Agent Starter Pack".
argument-hint: "<build|enhance|evaluate|deploy|publish|migrate> [project-path]"
allowed-tools: Read,Glob,Grep,WebFetch,WebSearch
version: 2.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- google-cloud
- adk
- agents-cli
- agent-platform
model: inherit
effort: high
compatibility: Designed for Claude Code and other Agent Skills clients; commands require Python 3.11+, uv, and Node.js
---
# Google Cloud ADK Application Workflow

## Overview

Guide a Google ADK application through its current lifecycle: inspect, scaffold,
run, evaluate, deploy, publish, and observe. Prefer Google's actively maintained
[`agents-cli`](https://github.com/google/agents-cli). Agent Starter Pack is in
maintenance mode and should be treated as a migration source, not the default
for new work.

This skill creates Google-hosted agent applications. It does not create Claude
Code subagent definition files; route those requests to `agent-creator`.

## Prerequisites

- Identify whether the target is new, an existing ADK app, or an Agent Starter
  Pack project that needs migration.
- Confirm the local project path and read its instructions.
- For current-version questions, use `WebFetch` on official Google documentation
  or `WebSearch` restricted to official Google domains.
- For existing code, use `Glob`, `Grep`, and `Read` to establish its actual
  framework, configuration, tests, and deployment lane before recommending work.
- Do not require Google Cloud for local development; AI Studio credentials may
  support a local-only workflow. Cloud deployment does require a Google project.

## Instructions

1. Classify the request as build, enhance, evaluate, deploy, publish, observe, or
   migrate. State which lifecycle stage is in scope.
2. Inspect the local repository before proposing changes. Preserve working agent
   code, evaluation datasets, Terraform, and CI/CD during migrations.
3. Verify current CLI syntax from the installed command or official docs. Start
   from these maintained entry points:

   ```bash
   uvx google-agents-cli setup
   agents-cli create PROJECT_NAME
   agents-cli scaffold enhance
   agents-cli scaffold upgrade
   ```

4. For implementation guidance, define the ADK agent, tools, state, callbacks,
   error contracts, and tests before selecting infrastructure. Use the detailed
   [lifecycle reference](references/SKILL.full.md) for current command families.
5. Validate locally with the generated project's own commands. Current
   `agents-cli` releases expose `install`, `lint`, `run`, and the `eval` command
   group. Do not claim success without the actual command receipt.
6. For deployment, distinguish Agent Runtime, Cloud Run, and GKE. Inspect
   `agents-cli deploy --help` for the installed version and present project,
   region, identity, secrets, APIs, quotas, and rollback before any mutation.
7. For Gemini Enterprise registration, use the current `publish
   gemini-enterprise` workflow and require a separate approval.
8. For Agent Starter Pack projects, follow Google's migration guide. Do not
   recreate removed templates or old Makefile commands.

## Output

- Lifecycle stage and selected architecture
- Source evidence: inspected files and official documentation version/date
- Exact commands proposed or run
- Tool, state, authentication, and secret contracts
- Verification results from lint, smoke tests, evaluations, and deployment checks
- Remaining risks, costs to verify, and the next approval boundary

## Error Handling

| Failure | Response |
|---|---|
| Request is for a Claude Code subagent file | Route to `agent-creator`; do not scaffold a Google app |
| CLI syntax conflicts with this skill | Trust installed `--help` and current official docs, then report the drift |
| Agent Starter Pack command is encountered | Treat it as legacy and use the migration guide |
| Authentication is absent | Keep work local; explain the needed login or credential without handling secrets |
| Region, runtime, or feature is unavailable | Cite the failed target and offer a documented supported alternative |
| Evaluation or smoke test fails | Stop before deployment and preserve the failing receipt |
| Pricing is requested | Link current Google pricing; do not repeat cached fixed prices |

## Examples

- **"Create a new Google ADK support agent."** Inspect prerequisites, propose
  `agents-cli create`, define the tool and evaluation contract, and wait before
  scaffolding.
- **"Modernize this Agent Starter Pack project."** Inventory the project, follow
  the official migration path, preserve code and infrastructure, then run the
  upgraded verification lane.
- **"Deploy this ADK app."** Verify local tests and evals, compare supported
  runtimes, show the exact deployment plan, and wait for approval.

## Resources

- [Lifecycle and command reference](references/SKILL.full.md)
- [Reference index](references/README.md)
- [Google agents-cli](https://github.com/google/agents-cli)
- [Google agents-cli documentation](https://google.github.io/agents-cli/)
- [Google ADK documentation](https://google.github.io/adk-docs/)
- [Agent Starter Pack migration guide](https://google.github.io/agents-cli/reference/from-agent-starter-pack/)

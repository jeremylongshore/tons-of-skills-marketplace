# Hyperflow

**A local workflow planner and execution runner for coding agents.** Hyperflow keeps plans readable, validates static workflows, delegates bounded tasks through an available provider adapter, and records durable execution state locally.

[![version v8.0.0](https://img.shields.io/badge/version-v8.0.0-blueviolet?style=flat-square)](CHANGELOG.md)
[![validation](https://img.shields.io/github/actions/workflow/status/Mohammed-Abdelhady/hyperflow/plugin-validation.yml?style=flat-square&label=validation)](https://github.com/Mohammed-Abdelhady/hyperflow/actions)
[![MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

## Four public skills

| Skill | Responsibility |
|---|---|
| `/hyperflow-plan` | Inspect, ask consequential questions, record answers, and compile a workflow. It stops before execution. |
| `/hyperflow-smash` | Execute an approved workflow through isolated tasks, independent review, scoped repair, and verification, then one final consolidated security review before anything touches your checkout. Status, graph, stop, resume, sessions, rename, and messages are subcommands. |
| `/hyperflow-crash` | Review a pinned pull request or Git range in fresh read-only sessions. |
| `/hyperflow-agents-skill` | Inspect or update validated primary, general, and lightweight model roles. |

Smash runs unattended with full-access writing delegates, automatic checks and repairs, and read-only reviewers. It records blockers and continues independent tasks without asking questions.

## Lanes and review routing

Every task carries actual details, a difficulty (`routine`, `complex`, or `security`), and an explicit effort (`low`, `medium`, or `high`). Routine work routes to the lightweight role; complex and security work routes to the general role. Correctness review is always performed by the primary role in a fresh, isolated read-only lane. One consolidated security review by the general role runs once, after all other phases finish, before changes reach the user checkout. Its findings are implemented in a new general fix lane, and fixes rerun affected checks, primary correctness review, and security revalidation.

The skills invoke `node <plugin-root>/runtime/cli.mjs`. Installation does not execute a workflow or modify provider credentials. No daemon or cloud service is required.

## Models

Default profiles are preferences: native Codex `gpt-6.1-sol` for primary, `zai/glm-5.3` for general, and `zai/glm-5.3-flash` for lightweight. Each role can select an available delegate harness and model. Hyperflow resolves preferences against actual configuration before dispatch and never changes the active host coordinator. Effort is assigned per task during planning and shown in the workflow.

## Local state

Readable plans and approved knowledge stay in Markdown under `.hyperflow/`. The local runtime store keeps execution leases, attempts, run IDs, stop generations, messages, and evidence references. Existing `.hyperflow` data, credentials, shared skills, and foreign host registrations are preserved during installation and migration.

The workflow file is a static JSON-compatible declaration parsed without evaluating JavaScript. Tasks declare dependencies, read/write ownership, acceptance criteria, registered checks, and resource needs. Task creation writes planning, task, implementation, correctness-review, security-review, and conditional security-fix files under `.hyperflow/workflows/<slug>/`, with planned agents and effort. Compilation records validated model bindings and binds the workflow and phase-file digests into the approval receipt. Missing or edited approved phase files block execution.

## Install

Use the native plugin installation flow for the host you use. The source installer registers skills in detected Claude Code, Codex, Antigravity, Cursor, OpenCode, and Pi skill directories. Codex receives owned copies for native discovery; other hosts receive source links. It registers four native command files only for OpenCode and preserves unrelated config:

```bash
./install.sh
```

Installation never runs plans or contacts model providers. Use `node <plugin-root>/runtime/cli.mjs setup-delegates` only when you explicitly want the pinned upstream relay. See [installation](docs/installation.md) and [getting started](docs/getting-started.md).

## Host compatibility

Host command discovery and runtime execution are separate checks. This repository does not treat a manifest, skill directory, or static validation as host certification. See [host compatibility evidence](docs/installation.md#host-compatibility-evidence).

## Documentation

- [Orchestration contract](docs/orchestration.md)
- [Privacy](PRIVACY.md)
- [Releasing](RELEASING.md)
- [Changelog](CHANGELOG.md)

## License

Copyright (c) 2026 Mohammed Abdelhady. Released under the [MIT License](LICENSE).

---
name: adk-agent-builder
description: |
  Scaffold production-ready AI agents on Google's Agent Development Kit (ADK):
  ReAct-style single agents, multi-agent orchestration (Sequential/Parallel/Loop),
  tool wiring, evaluation, and optional Vertex AI Agent Engine deployment.
  Use when building, scaffolding, or deploying ADK agents on Google Cloud, or
  when wiring ADK tools and orchestration patterns. Trigger with "build an ADK
  agent", "scaffold an agent on ADK", or "deploy to Agent Engine".
allowed-tools: Read, Write, Edit, Grep, Bash(cmd:*)
version: 2.3.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- google-adk
- react
- adk-agent
compatibility: Designed for Claude Code
---
# ADK Agent Builder

Build production-ready agents with Google’s Agent Development Kit (ADK): scaffolding, tool wiring, orchestration patterns, testing, and optional deployment to Vertex AI Agent Engine.

## Overview

- Creates a minimal, production-oriented ADK scaffold (agent entrypoint, tool registry, config, and tests).
- Supports single-agent ReAct-style workflows and multi-agent orchestration (Sequential/Parallel/Loop).
- Produces a validation checklist suitable for CI (lint/tests/smoke prompts) and optional Agent Engine deployment verification.

## Prerequisites

- Python runtime compatible with your project (often Python 3.10+)
- `google-adk` installed and importable
- If deploying: access to a Google Cloud project with Vertex AI enabled and permissions to deploy Agent Engine runtimes
- Secrets available via environment variables or a secret manager (never hardcoded)

## Instructions

1. Confirm scope: local-only agent scaffold vs Vertex AI Agent Engine deployment.
2. Choose an architecture:
   - Single agent (ReAct) for adaptive tool-driven tasks
   - Multi-agent system (specialists + orchestrator) for complex, multi-step workflows
3. Define the tool surface (built-in ADK tools + any custom tools you need) and required credentials.
4. Scaffold the project:
   - `src/agents/`, `src/tools/`, `tests/`, and a dependency file (`pyproject.toml` or `requirements.txt`)
5. Implement the minimum viable agent and a smoke test prompt; add regression tests for tool failures.
6. If deploying, produce an `adk deploy ...` command and a post-deploy validation checklist (AgentCard/task endpoints, permissions, logs).

## Output

- A repo-ready ADK scaffold (files and directories) plus starter agent code
- Tool stubs and wiring points (where to add new tools safely)
- A test + validation plan (unit tests and a minimal smoke prompt)
- Optional: deployment commands and verification steps for Agent Engine

## Error Handling

- Dependency/runtime issues: provide pinned install commands and validate imports.
- Auth/permission failures: identify the missing role/API and propose least-privilege fixes.
- Tool failures/rate limits: add retries/backoff guidance and a regression test to prevent recurrence.

## Examples

**Example: Scaffold a single ReAct agent**

- Request: “Create an ADK agent that summarizes PRs and proposes test updates.”
- Result: agent entrypoint + tool registry + a smoke test command for local verification.

**Example: Multi-agent orchestrator**

- Request: “Build a supervisor + deployer + verifier team and deploy to Agent Engine.”
- Result: orchestrator skeleton, per-agent responsibilities, and `adk deploy ...` + post-deploy health checks.

## Resources

- Implementation patterns (scaffolds, tool wiring, orchestration): [`references/implementation.md`](references/implementation.md)
- Worked examples (single-agent + multi-agent): [`references/examples.md`](references/examples.md)
- Error-handling and recovery patterns: [`references/errors.md`](references/errors.md)
- Product / architecture context: [`PRD.md`](PRD.md), [`ARD.md`](ARD.md)
- ADK / Agent Engine docs:

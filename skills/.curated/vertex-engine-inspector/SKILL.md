---
name: vertex-engine-inspector
description: 'Inspect and validate Vertex AI Agent Engine deployments including Code
  Execution Sandbox, Memory Bank, A2A protocol compliance, and security posture. Generates
  production readiness scores. Use when asked to inspect, validate, or audit an Agent
  Engine deployment. Trigger with "inspect agent engine", "validate agent engine deployment",
  "check agent engine config", "audit agent engine security", "agent engine readiness
  check", "vertex engine health", or "reasoning engine status".

  '
allowed-tools: Read, Grep, Glob, Bash(cmd:*)
version: 2.32.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
argument-hint: <project-id> <agent-engine-id> [location]
effort: high
tags:
- ai
- deployment
- security
- compliance
compatibility: Designed for Claude Code
---
# Vertex Engine Inspector

## Overview

Inspect and validate Vertex AI Agent Engine deployments across seven categories: runtime configuration, Code Execution Sandbox, Memory Bank, A2A protocol compliance, security posture, performance metrics, and monitoring observability. This skill generates weighted production-readiness scores (0-100%) with actionable recommendations for each deployment.

## Prerequisites

- `google-cloud-aiplatform[agent_engines]>=1.120.0` Python SDK installed
- `gcloud` CLI authenticated (for IAM and monitoring queries — **not** for Agent Engine CRUD)
- IAM roles: `roles/aiplatform.user` and `roles/monitoring.viewer` granted on the target project
- Access to the target Google Cloud project hosting the Agent Engine deployment
- `curl` for A2A protocol endpoint testing (AgentCard, Task API, Status API)
- Cloud Monitoring API enabled for performance metrics retrieval
- Familiarity with Vertex AI Agent Engine concepts: Code Execution Sandbox, Memory Bank, Model Armor

**Important**: There is no `gcloud` CLI surface for Agent Engine (no `gcloud ai agents`, `gcloud ai reasoning-engines`, or `gcloud alpha ai agent-engines` commands exist). All Agent Engine operations use the Python SDK via `vertexai.Client()` or `vertexai.preview.reasoning_engines`.

## Instructions

1. Connect to the Agent Engine deployment by retrieving agent metadata via the Python SDK (`client.agent_engines.get(name=...)`)
2. Parse the runtime configuration: model selection (Gemini 2.5 Pro/Flash), tools enabled, VPC settings, and scaling policies
3. Validate Code Execution Sandbox settings: confirm state TTL is 7-14 days, sandbox type is `SECURE_ISOLATED`, and IAM permissions are scoped to required GCP services only
4. Check Memory Bank configuration: verify enabled status, retention policy (min 100 memories), Firestore encryption, indexing enabled, and auto-cleanup active
5. Test A2A protocol compliance by probing `/.well-known/agent-card`, `POST /v1/tasks:send`, and `GET /v1/tasks/<task-id>` endpoints for correct responses
6. Audit security posture: validate IAM least-privilege roles, VPC Service Controls perimeter, Model Armor activation, encryption at rest and in transit, and absence of hardcoded credentials
7. Query Cloud Monitoring for performance metrics: request count, error rate (target < 5%), latency percentiles (p50/p95/p99), token usage, and cost estimates over the last 24 hours
8. Assess monitoring and observability: confirm Cloud Monitoring dashboards, alerting policies, structured logging, OpenTelemetry tracing, and Cloud Error Reporting are configured
9. Calculate weighted scores across all categories and determine overall production readiness status
10. Generate a prioritized list of recommendations with estimated score improvement per remediation

See [`references/inspection-workflow.md`](references/inspection-workflow.md) for the phased inspection process and [`references/inspection-categories.md`](references/inspection-categories.md) for detailed check criteria.

## Output

- Inspection report in YAML format with per-category scores and overall readiness percentage
- Runtime configuration summary: model, tools, VPC, scaling settings
- A2A protocol compliance matrix: pass/fail for AgentCard, Task API, Status API
- Security posture score with breakdown: IAM, VPC-SC, Model Armor, encryption, secrets
- Performance metrics dashboard: error rate, latency percentiles, token usage, daily cost estimate
- Prioritized recommendations with estimated score improvement per item

See [`references/example-inspection-report.md`](references/example-inspection-report.md) for a complete sample report.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Agent metadata not accessible | Insufficient IAM permissions or incorrect agent ID | Verify `roles/aiplatform.user` granted; confirm agent ID with `client.agent_engines.list()` via Python SDK |
| A2A AgentCard endpoint 404 | Agent not configured for A2A protocol or endpoint path incorrect | Check agent configuration for A2A enablement; verify `/.well-known/agent-card` path |
| Cloud Monitoring metrics empty | Monitoring API not enabled or no recent traffic | Run `gcloud services enable monitoring.googleapis.com`; generate test traffic first |
| VPC-SC perimeter blocking access | Inspector running outside VPC Service Controls perimeter | Add inspector service account to access level; use VPC-SC bridge or access policy |
| Code Execution TTL out of range | State TTL set below 1 day or above 14 days | Adjust TTL to 7-14 days for production; values above 14 days are rejected by Agent Engine |

See [`references/errors.md`](references/errors.md) for additional error scenarios.

## Examples

**Scenario 1: Pre-Production Readiness Check** -- Inspect a newly deployed ADK agent before production launch. Run all 28 checklist items across security, performance, monitoring, compliance, and reliability. Target: overall score above 85% before approving production traffic.

**Scenario 2: Security Audit After IAM Change** -- Re-inspect security posture after modifying service account roles. Validate that least-privilege is maintained (target: IAM score 95%+), VPC-SC perimeter is intact, and Model Armor remains active.

**Scenario 3: Performance Degradation Investigation** -- Inspect an agent showing elevated error rates. Query 24-hour performance metrics, identify latency spikes at p95/p99, check auto-scaling behavior, and correlate with token usage patterns to isolate the root cause.

## Resources

- Vertex AI Agent Engine Documentation -- deployment and configuration
- A2A Protocol Specification -- AgentCard, Task API, protocol compliance
- [Cloud Monitoring API](https://cloud.google.com/monitoring/api/v3) -- metrics queries and dashboard configuration
- [VPC Service Controls](https://cloud.google.com/vpc-service-controls/docs) -- perimeter setup and access policies
- Model Armor -- prompt injection protection configuration

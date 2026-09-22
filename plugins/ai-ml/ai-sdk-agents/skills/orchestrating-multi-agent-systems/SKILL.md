---
name: orchestrating-multi-agent-systems
description: 'Execute orchestrate multi-agent systems with handoffs, routing, and
  workflows across AI providers.

  Use when building complex AI systems requiring agent collaboration, task delegation,
  or workflow coordination.

  Trigger with phrases like "create multi-agent system", "orchestrate agents", or
  "coordinate agent workflows".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(npm:*)
version: 1.37.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- ai
- workflow
- agent-orchestration
compatibility: Designed for Claude Code
---
# Orchestrating Multi-Agent Systems

## Overview

Design and implement multi-agent systems using AI SDK v5 with structured handoffs, intelligent routing, and coordinated workflows across AI providers. This skill covers agent role definition, tool scoping, inter-agent delegation via handoff rules, and workflow orchestration patterns including coordinator-worker and supervisor topologies.

## Prerequisites

- Node.js 18+ and TypeScript 5.0+ runtime
- AI SDK v5 (`npm install ai @ai-sdk/openai @ai-sdk/anthropic @ai-sdk/google`)
- API keys for target providers set in environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_GENERATIVE_AI_API_KEY`)
- Zod for input/output schema validation (`npm install zod`)
- Familiarity with agent-based architecture patterns (coordinator, pipeline, broadcast)

## Instructions

1. Initialize a TypeScript project with `tsconfig.json` targeting ES2022 and moduleResolution `bundler`
2. Install AI SDK v5 core and provider packages for each model backend required
3. Define agent roles by creating separate modules per agent, each with a system prompt, model binding, and scoped tool set
4. Implement tool functions using `ai.tool()` with Zod input/output schemas for type-safe execution
5. Configure handoff rules using `ai.handoff()` to delegate tasks between agents with clear trigger conditions and context passing
6. Build routing logic that classifies incoming requests by topic or intent and dispatches to the appropriate specialist agent
7. Wire agents into a workflow using sequential, parallel, or conditional orchestration patterns
8. Add state management to persist context across multi-step workflows using a shared context object or external store
9. Implement circuit breakers and timeout guards to prevent workflow deadlocks
10. Test each agent in isolation, then validate end-to-end handoff chains with representative inputs

See `${CLAUDE_SKILL_DIR}/references/implementation.md` for the detailed implementation guide.

## Output

- TypeScript agent modules with AI SDK v5 provider bindings and system prompts
- Tool definitions with Zod-validated input/output schemas
- Handoff configuration mapping agent-to-agent delegation triggers
- Workflow orchestration files defining sequential, parallel, and conditional execution paths
- Routing classifier that maps user intents to specialist agents
- Integration test suite covering handoff chains and fallback paths

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Provider configuration invalid | Missing or malformed API key in environment | Verify `process.env.*_API_KEY` values; check provider SDK version compatibility |
| Circular handoff detected | Agent A hands off to B which hands back to A | Implement handoff depth counter; set `maxHandoffDepth` and add a fallback terminal agent |
| Task routed to no agent | Routing classifier returned no match for input | Add a default catch-all route; improve classifier training data or keyword coverage |
| Tool access violation | Agent invoked a tool outside its scoped permission set | Review `tools` array per agent; ensure tool names match registered definitions exactly |
| Workflow timeout | Multi-step workflow exceeded deadline without completion | Set per-step timeouts with `AbortController`; add workflow-level deadline and partial-result handling |

See `${CLAUDE_SKILL_DIR}/references/errors.md` for the full error reference.

## Examples

**Scenario 1: Customer Support Triage** -- A coordinator agent classifies incoming tickets as billing, technical, or general. Billing queries hand off to a specialist agent with access to Stripe tools. Technical queries route to a code-analysis agent with filesystem read tools. Resolution rate target: 85% automated within 3 handoff steps.

**Scenario 2: Research Pipeline** -- A sequential workflow chains a web-search agent, a summarization agent, and a report-writer agent. Each agent produces structured JSON output consumed by the next. The pipeline processes 50 research queries per batch with a p95 latency under 30 seconds per query.

**Scenario 3: Code Review Multi-Agent** -- A supervisor agent distributes pull request diffs to specialized reviewers (security, performance, style). Each reviewer returns findings with severity scores. The supervisor aggregates results into a unified review with prioritized action items.

See `${CLAUDE_SKILL_DIR}/references/examples.md` for additional examples.

## Resources

- [AI SDK v5 Documentation](https://sdk.vercel.ai/docs) -- agent creation, tool definitions, handoffs
- [Zod Schema Library](https://zod.dev) -- input/output validation for tools and flows
- Provider integration guides: OpenAI, Anthropic, Google Gemini
- Coordinator-worker and supervisor orchestration pattern references
- OpenTelemetry tracing for multi-agent observability

---
name: mistral-migration-deep-dive
description: >-
  Migrate an existing model workload to Mistral through semantic mapping, dual-run evaluation, bounded canary, and provider rollback. Use when re-platforming from another provider. Trigger with "migrate to Mistral", "move from OpenAI to Mistral", or "compare a workload with Mistral".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<source-provider> <workload> <migration-window>"
version: 1.14.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, mistral, provider-migration]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Mistral actions require network access and explicit approval"
---
# Cross-Provider Migration to Mistral

## Overview

Treat migration as behavior and operations redesign, not field renaming. Preserve the application contract while re-evaluating models, prompts, streams, tools, safety, state, data, spend, and incidents.

## Prerequisites

- A source workload inventory and application-owned adapter.
- Golden/adversarial evaluation sets with governed data.
- Current Mistral access, dual-run budget, canary, rollback, and exit owners.

## Current Contract

Chat, embeddings, classifiers, files/OCR, audio, batch, Workflows, and Public Preview stateful APIs are provider-specific. No source feature, model, tool, safety result, or state object is automatically equivalent.

## Authentication

Keep source and Mistral credentials in separate secret references with independent owners. Dual-run data must be approved for both providers.

## Instructions

1. Inventory source messages, streams, tools, structure, embeddings, files, state, retry, usage, and safety.
2. Define the stable app contract and identify source-specific behavior to adapt or retire.
3. Map workloads to current Mistral surfaces; reject unsupported or unacceptable preview substitutions.
4. Build target adapter and run offline characterization against shared normalized fixtures.
5. Run approved dual evaluation for correctness, safety, latency, usage, failure, and governance.
6. Canary bounded traffic with kill switch; reconcile state, cut over, and retain rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, locks, configuration, tests, and evidence. Use Write and Edit only for approved repository changes. Invocation alone does not authorize network calls, paid usage, uploads, stateful resources, admin mutations, deployments, or deletion.

## Approval Boundaries

Dual submission, customer data, new spend, preview APIs, production routing, state copying, source shutdown, or credential deletion require approval.

## Error Handling

- Equivalent parameter names can differ in defaults/semantics.
- Dual-run doubles exposure and spend unless bounded.
- Rollback fails when new provider state lacks reconciliation.

## Output

Return source/target contract matrix, gaps, evaluation, data/spend delta, canary, reconciliation, cutover, rollback, and source exit.

## Examples

- Preserve app tool authorization while adapting provider call shape.
- Reject stateful agent migration until preview and rollback risks are accepted.

## Validation

Run identical golden, adversarial, timeout, stream, tool, tenant, and outage cases; verify cutover and rollback.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable endpoints, models, limits, prices, preview status, or retention.
- Record live account observations as environment-specific evidence, not universal Mistral guarantees.

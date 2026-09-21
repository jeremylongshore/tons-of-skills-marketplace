---
name: castai-local-dev-loop
description: 'Build an offline-first local loop for CAST AI Terraform, Helm, policy, and workload configuration before touching a sandbox cluster. Use when developing infrastructure modules, annotations, or CI checks. Trigger with: "develop CAST AI locally", "test CAST AI configuration", "make a CAST AI dev loop".'
allowed-tools: Read, Grep, Write, Edit, Bash(terraform:*), Bash(helm:*), Bash(kubectl:*), Bash(castctl:*)
version: 2.0.0
argument-hint: '[infrastructure-or-manifest-root]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - local-development
  - testing
compatibility: 'Requires locally pinned infrastructure tools; optional sandbox checks require an explicitly selected non-production kube context'
---

# CAST AI Offline-First Development Loop

## Overview

Make configuration feedback fast without treating a live cluster as a test fixture. Render, validate, diff, and policy-check locally; use a sandbox only for the behavior that cannot be proven offline.

## Prerequisites

- Repository-owned Terraform, Helm values, policy, or workload manifests
- Pinned tool and provider versions
- Sanitized fixtures for cluster identity, policies, and API failures
- Optional sandbox with a distinct kube context and budget owner

## Instructions

### Step 1: Map inputs and ownership

Use Read and Grep to locate provider constraints, chart versions, values, annotations, policy definitions, generated files, and secret references. Identify which files are authoritative and which are derived.

### Step 2: Establish local gates

Use Bash(terraform:_) to format and validate without applying. Use Bash(helm:_) to lint and render pinned charts. Use Bash(kubectl:\*) only for client-side schema checks against rendered objects. Add deterministic tests for region, organization, policy bounds, automation state, HPA ownership, and prohibited secrets.

### Step 3: Model negative paths

Use Write or Edit to add sanitized fixtures for missing identity, wrong region, permission denial, malformed configuration, conflicting controllers, unavailable metrics, PDB denial, and unsatisfied node constraints. Assert fail-closed behavior.

### Step 4: Preview sandbox connection

When installation behavior must be checked, use Bash(castctl:\*) with the documented dry-run against the named sandbox context. Compare detected identity and proposed changes to approved fixtures before any connection.

### Step 5: Run one bounded sandbox experiment

Use a reviewed plan and one disposable workload or policy assignment. Observe only the intended behavior, never production data. Do not use a personal API key or console edits that bypass the repository source of truth.

### Step 6: Capture reproducibility

Record commit, tool versions, rendered artifact hashes, plan summary, sandbox context, start/end time, cleanup, and remaining untested behavior. Return the sandbox to its declared baseline.

## Tool Discipline

Use Read and Grep for source discovery. Use Write and Edit for fixtures and checks. Use Bash(terraform:_), Bash(helm:_), and Bash(kubectl:_) for offline validation; use Bash(castctl:_) only for a documented dry-run or approved sandbox action.

## Output

- Reproducible local validation commands
- Sanitized success and failure fixtures
- Rendered and planned artifact receipts
- Optional bounded sandbox result and cleanup evidence

## Examples

A policy change is tested against fixture assertions and a rendered workload annotation before one Deferred-mode sandbox canary. Production credentials and clusters never enter the local loop.

## Error Handling

| Failure                          | Response                                |
| -------------------------------- | --------------------------------------- |
| Tool versions float              | Pin them before comparing results       |
| Render needs a real secret       | Replace it with a reference or sentinel |
| Sandbox context is ambiguous     | Stop before any cluster command         |
| Test requires production traffic | Redesign it around sanitized fixtures   |

## Resources

- [Development evidence and source notes](references/official-docs.md)
- [Workload Autoscaler configuration](https://docs.cast.ai/docs/workload-autoscaling-configuration)
- [Connect with castctl](https://docs.cast.ai/docs/connect-with-castctl)
- [Autoscaler settings](https://docs.cast.ai/docs/autoscaler-settings)

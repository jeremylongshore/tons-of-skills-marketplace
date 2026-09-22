---
name: castai-performance-tuning
description: 'Tune CAST AI node and workload autoscaling against application SLOs, scheduling constraints, and recommendation confidence. Use when optimization causes latency, disruption, slow provisioning, or unstable replica and resource behavior. Trigger with: "tune CAST AI performance", "stabilize CAST AI autoscaling", "fix CAST AI scaling latency".'
allowed-tools: Read, Grep, Write, Edit, Bash(kubectl:*)
version: 2.0.0
argument-hint: '[cluster-and-workload]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - performance
  - autoscaling
compatibility: 'Requires workload telemetry, SLOs, and read access to effective CAST AI and Kubernetes scaling configuration'
---

# CAST AI Performance Guardrail Tuning

## Overview

Tune from evidence across workload demand, requests, replicas, scheduling, and nodes. Keep vertical, horizontal, and node changes separate so a lower bill never hides degraded service.

## Prerequisites

- Workload SLOs, error budget, traffic profile, and representative observation window
- Effective scaling policy, annotations, HPA, PDB, node templates, and cluster limits
- Metrics-server and healthy CAST AI components

## Instructions

### Step 1: Build the timeline

Use Read and Grep to align request rate, latency, errors, pod requests, replicas, pending time, evictions, node provisioning, and policy changes. Identify whether the symptom precedes or follows CAST AI action.

### Step 2: Inspect effective workload policy

Check policy assignment, recommendation percentile, overhead, optimization threshold, minimum and maximum resources, confidence, and automation state. Invalid annotation YAML is ignored; an invalid policy name can fall back to a system policy, so verify effective state rather than intended text.

### Step 3: Choose application mode

Use Immediate mode only when evictions are acceptable and PDB behavior is proven. Use Deferred mode when recommendations should apply at natural recreation. Account for recommendation confidence and gradual behavior on newly onboarded clusters.

### Step 4: Reconcile horizontal scaling

Inspect the native `autoscaling/v2` HPA, metric targets, replica bounds, stabilization, and ownership. Avoid competing HPA controllers. When CAST AI takes ownership, treat that as a configuration migration with explicit rollback.

### Step 5: Reconcile node capacity

Use Bash(kubectl:\*) to examine pending reasons, affinities, topology, taints, resource shape, and scheduling events. Review node templates and maximum CPU limits. More permissive capacity is not automatically safer or cheaper.

### Step 6: Change one variable

Use Write or Edit to record one hypothesis, one configuration change, performance and cost guardrails, observation window, and rollback. Compare the same traffic class and retain SLO evidence before expanding.

## Tool Discipline

Use Read and Grep for metrics, policy, and configuration evidence. Use Write and Edit for the tuning experiment and decision. Use Bash(kubectl:\*) for bounded, non-secret inspection of workloads, HPAs, PDBs, events, and nodes.

## Output

- Joined performance and scaling timeline
- Effective vertical, horizontal, and node control map
- One-variable experiment with SLO and cost guardrails
- Expand, hold, or rollback decision

## Examples

A workload oscillates because replica stabilization and vertical requests changed together. The team freezes vertical automation, tunes the managed HPA in a canary, and restores rightsizing only after replica behavior is stable.

## Error Handling

| Failure                                  | Response                                                 |
| ---------------------------------------- | -------------------------------------------------------- |
| Metrics are missing or misaligned        | Stop tuning and repair observability                     |
| Effective policy differs from annotation | Correct YAML or policy assignment before experimentation |
| PDB blocks needed replacement            | Prefer Deferred mode or review disruption with the owner |
| SLO regresses                            | Roll back immediately even if cost improves              |

## Resources

- [Performance evidence and source notes](references/official-docs.md)
- [Workload Autoscaler overview](https://docs.cast.ai/docs/workload-autoscaling-overview)
- [Scaling policies](https://docs.cast.ai/docs/woop-scaling-policies)
- [Horizontal Pod Autoscaling](https://docs.cast.ai/docs/horizontal-pod-autoscaling)

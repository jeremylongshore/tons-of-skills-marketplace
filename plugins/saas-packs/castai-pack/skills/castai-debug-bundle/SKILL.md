---
name: castai-debug-bundle
description: 'Create a bounded, redacted CAST AI diagnostic bundle that preserves component, policy, and Kubernetes evidence for escalation. Use when triage must be handed to platform engineering, a cloud owner, or CAST AI support. Trigger with: "collect CAST AI diagnostics", "make a CAST AI support bundle", "capture CAST AI evidence".'
allowed-tools: Read, Grep, Write, Bash(kubectl:*), Bash(helm:*), Bash(castctl:*)
version: 2.0.0
argument-hint: '[kube-context-and-time-window]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - kubernetes
  - cast-ai
  - diagnostics
  - support
compatibility: 'Requires read-only access to the selected cluster; collection must follow local data-handling and support-sharing policy'
---

# CAST AI Redacted Diagnostic Bundle

## Overview

Capture enough evidence to reproduce a CAST AI failure without exporting credentials, Secret payloads, broad cluster inventory, application data, or unbounded logs.

## Prerequisites

- Exact kube context, cluster identifier, CAST AI region, incident window, and symptom
- Approved local destination with retention and audience
- Redaction rules for names, labels, annotations, IPs, account data, and credentials

## Instructions

### Step 1: Declare the bundle contract

Use Write to record incident ID, collector, start and end time, selected namespaces, commands, excluded data classes, redaction method, checksum method, retention, and recipients.

### Step 2: Inventory component versions

Use Bash(castctl:_) for version information, Bash(helm:_) for release metadata and redacted values, and Bash(kubectl:\*) for component images and readiness. Do not collect Helm secrets, rendered Secret objects, service-account tokens, or kubeconfig contents.

### Step 3: Capture bounded health evidence

Collect status, restart counts, recent warning events, selected resource descriptions, and logs constrained by component, time, and line count. Include metrics-server status when workload recommendations are involved and pending-pod reasons when node capacity is involved.

### Step 4: Capture declared policy context

Use Read and Grep on repository-owned Terraform, Helm values, annotations, node templates, PDBs, and HPAs. Record source paths and commit identifiers. Prefer diffs and normalized summaries over raw state files.

### Step 5: Redact and verify

Scan the bundle for API keys, authorization headers, tokens, Secret data, cloud account identifiers, email addresses, private endpoints, and application payloads. Replace values consistently so relationships remain debuggable.

### Step 6: Seal the handoff

Write a manifest of included files, omitted evidence, timestamps, tool versions, hashes, and known gaps. Open the sanitized files before sharing and require a second-person review for external support transfer.

## Tool Discipline

Use Read and Grep for source and redaction review. Use Write only for sanitized bundle artifacts and the manifest. Use Bash(kubectl:_), Bash(helm:_), and Bash(castctl:\*) for non-mutating, bounded inspection; never request Secret contents or stream logs indefinitely.

## Output

- Sanitized component and cluster-health evidence
- Policy/source-of-truth references
- Redaction report and file manifest
- Checksums, retention, audience, and escalation question

## Examples

A workload-autoscaler incident includes component versions, a 15-minute warning-event window, PDB status, policy name, and sanitized logs. It excludes Secret objects, all-namespace inventory, Terraform state, and unrelated application logs.

## Error Handling

| Failure                           | Response                                                            |
| --------------------------------- | ------------------------------------------------------------------- |
| Context or time window is unknown | Stop and resolve scope before collection                            |
| A command would reveal a Secret   | Omit it and document the evidence gap                               |
| Redaction cannot preserve safety  | Keep the bundle local and share a summary                           |
| Bundle exceeds approved scope     | Delete the excess from the exact bundle and regenerate its manifest |

## Resources

- [Bundle evidence and source notes](references/official-docs.md)
- [Workload Autoscaler overview](https://docs.cast.ai/docs/workload-autoscaling-overview)
- [Node Autoscaling](https://docs.cast.ai/docs/autoscaler)
- [Connect with castctl](https://docs.cast.ai/docs/connect-with-castctl)

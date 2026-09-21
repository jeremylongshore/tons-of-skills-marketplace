---
name: vastai-common-errors
description: >-
  Classify Vast.ai authentication, offer, instance-state, SSH, image, credit, and API failures before choosing a recovery action. Use when automation is stuck or a GPU workload cannot start. Trigger with: "diagnose Vast.ai", "why is my instance scheduling", "fix a Vast.ai CLI error".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[command-instance-id-and-redacted-error]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - troubleshooting
  - instances
  - diagnostics
compatibility: 'Requires the Vast.ai CLI, redacted structured output, and access to the affected account or instance.'
---

# Vast.ai Failure Classifier

## Overview

Diagnose from provider state and error evidence instead of retrying every failure. Separate identity and permission errors, marketplace scarcity, transient startup, terminal host states, billing stops, SSH configuration, and workload exits.

## Prerequisites

- Exact command, non-secret arguments, exit status, timestamp, and redacted response
- Affected account context, instance ID, image identity, and expected state
- Authority to inspect but not automatically destroy or fund resources

## Instructions

### Step 1: Capture structured evidence

Run the failing command with `--raw` where supported and record CLI version. For request diagnosis, use `--explain` or `--curl` only after ensuring generated output cannot expose the key.

### Step 2: Classify control-plane failure

Treat 401 as credential failure, 403 as missing scoped permission, 429 as endpoint/identity rate limiting, and insufficient credit or spend-rate errors as billing policy—not host failure.

### Step 3: Classify instance state

Loading may reflect an image pull; scheduling after a stop may wait indefinitely for the original GPU; exited is a workload/container failure; unknown or offline indicates missing host heartbeat.

### Step 4: Check SSH and network facts

Wait for `running`, resolve the current SSH URL, verify the registered public key and selected private key, and do not disable host verification as a blanket fix.

### Step 5: Choose reversible recovery

Relax offer filters explicitly, repair permissions, change host, restore credit through the approved owner, or resume from checkpoint according to the class.

### Step 6: Close or escalate

Preserve identifiers and redacted evidence, confirm any replacement or cleanup, and escalate host or billing cases without speculative retries.

## Authentication

Do not paste API keys into diagnostic commands. A scoped read key is usually sufficient for user, instance, logs, offers, and audit evidence; request additional authority only for the selected recovery.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Failure class and evidence timeline
- Ranked recovery action with mutation boundary
- Redacted resolution or escalation receipt

Return command, CLI version, resource ID, observed status/error class, chosen response, outcome, and remaining billing risk.

## Examples

An instance stuck in `scheduling` after being stopped is classified as GPU reacquisition, not image failure; the operator copies recoverable data or creates a new instance instead of waiting without a deadline.

## Error Handling

| Failure | Response |
| --- | --- |
| Evidence contains a credential | Stop, redact, rotate if exposed, and recollect safely. |
| Error shape is inconsistent | Preserve HTTP status plus `msg` or `message` and classify conservatively. |
| Host is offline | Do not attempt repair on the host; preserve the instance ID and use external checkpoints. |
| Balance is zero | Escalate to the billing owner because resources and data may be at risk. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Troubleshooting](https://docs.vast.ai/guides/reference/troubleshooting)
- [Manage instances](https://docs.vast.ai/guides/instances/manage-instances)
- [CLI rate limits and errors](https://docs.vast.ai/cli/rate-limits)

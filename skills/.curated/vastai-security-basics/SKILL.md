---
name: vastai-security-basics
description: >-
  Harden Vast.ai renter access across scoped API keys, SSH, images, hosts, data, and teardown. Use when reviewing security before placing workloads on marketplace hardware. Trigger with: "secure Vast.ai", "review Vast.ai credentials", "protect data on a rented GPU".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[workload-sensitivity-and-required-resources]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - vastai
  - security
  - least-privilege
  - data-protection
compatibility: 'Requires a classified workload, approved secrets and image registries, SSH key management, and a verified-datacenter policy.'
---

# Vast.ai Renter Security Boundary

## Overview

A Vast.ai renter controls credentials and workload configuration but does not own the physical host. Apply least privilege, prefer verified datacenters for sensitive data, encrypt critical material, and assume destroyed local storage is not a substitute for external recovery.

## Prerequisites

- Data classification and decision on whether shared marketplace hardware is permitted
- Scoped API-key and dedicated SSH-key owners
- Approved image provenance, secret injection, network exposure, and checkpoint controls

## Instructions

### Step 1: Constrain the control plane

Create named scoped keys with only needed permission categories and endpoint constraints. Separate human, CI, monitoring, and deployment identities.

### Step 2: Establish SSH trust

Register a dedicated public key before creation, protect the private key, resolve the current connection endpoint, and validate host identity according to policy.

### Step 3: Verify workload provenance

Use an immutable image digest, scan it, document its entrypoint, and keep registry, model, and storage credentials out of image layers and startup text.

### Step 4: Limit host and network exposure

Prefer verified datacenters for sensitive workloads, expose only required ports, and avoid placing secrets or regulated plaintext on untrusted hosts.

### Step 5: Protect recoverability

Encrypt critical data, scope storage credentials to a run prefix, and checkpoint externally before stop, expiry, host failure, or destroy.

### Step 6: Rotate and close

Revoke temporary keys, remove obsolete SSH keys and environment variables, verify resource destruction, and retain a redacted audit receipt.

## Authentication

API keys are password-equivalent and do not expire by default. Environment injection is appropriate for CI, but logs, shell traces, generated curl commands, and debug bundles must remain secret-free.

## Tool Discipline

Use Read and Grep to inspect manifests, configuration, provider output, and existing tests before proposing a mutation. Use Write or Edit only for the approved plan, implementation, test, or redacted receipt; do not create, update, destroy, or fund Vast.ai resources without explicit operator approval.

## Output

- Threat and data-placement decision
- Credential, SSH, image, host, network, and storage controls
- Positive/negative access tests plus teardown receipt

Return workload class, selected host trust tier, key IDs/scopes, image digest, exposed ports, checkpoint destination, and cleanup outcome.

## Examples

A sensitive training canary uses a verified datacenter, immutable image digest, constrained instance key, dedicated SSH key, encrypted dataset, prefix-scoped checkpoint credential, and confirmed credential revocation after teardown.

## Error Handling

| Failure | Response |
| --- | --- |
| Workload is not allowed on shared hardware | Stop before provisioning and choose an approved environment. |
| Image identity is mutable | Pin a digest and repeat security review. |
| Secret appears in a trace or image | Revoke it, scrub artifacts, rebuild the image, and investigate exposure. |
| External checkpoint is missing | Do not destroy until recovery evidence exists, unless incident containment requires it. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Manage API keys](https://docs.vast.ai/guides/reference/api-keys)
- [CLI permissions](https://docs.vast.ai/cli/permissions)
- [Manage instances security notes](https://docs.vast.ai/guides/instances/manage-instances)

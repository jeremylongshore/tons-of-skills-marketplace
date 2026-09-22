---
name: brightdata-security-basics
description: 'Review a Bright Data integration for least privilege, public-data authorization, secret containment, and controlled use. Use when approving a target, adding a zone, rotating access, or preparing a security review. Trigger with: "security review Bright Data", "approve a Bright Data target", "audit Bright Data credentials".'
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: "[integration-inventory]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- web-data
- bright-data
- security-basics
- operations
compatibility: 'Requires an approved Bright Data account or offline fixtures, current Bright Data documentation, and an authorized public-data collection purpose'
---
# Bright Data Security and Use Review

## Overview

Treat legal purpose, public-data scope, account roles, zone isolation, and application controls as one authorization chain. Provider access does not replace the customer's duty to restrict targets, fields, retention, and downstream use.

## Prerequisites

- An integration inventory and named business and data owner
- The Bright Data acceptable-use and account-role documentation
- Secret-manager, egress, retention, and incident-response controls

## Instructions

### Step 1: Approve purpose and targets

Read the use case and Grep manifests for authenticated pages, personal or sensitive fields, messaging, purchases, account creation, or other prohibited activity. Refuse nonpublic information behind login.

### Step 2: Minimize identity

Choose named-user API keys or product-specific zone credentials, apply the least account role, isolate environments, and document revocation. Never encode secret values in configuration examples.

### Step 3: Enforce in the application

Write target and field allowlists, maximum records and bytes, retention, rate and cost ceilings, redirect rules, and fail-closed policy handling. Provider denial cannot trigger automatic evasion.

### Step 4: Test and review

Edit tests to cover disallowed hosts, login redirects, secret redaction, oversized results, policy errors, and revoked access. Record owner approval and the next review condition.

## Tool Discipline

Use Read and Grep to inspect policy, roles, configuration, and tests. Use Write and Edit only for approved manifests, controls, tests, and the security receipt. This skill grants no live collection or account-administration authority.

## Output

- Purpose, target, and data authorization matrix
- Least-privilege identity and revocation plan
- Application guardrails, negative tests, and review receipt

## Examples

Authorize a public product-price dataset with named fields and short retention. Deny login redirects and free-form URLs, bind one production zone to one worker role, and make every policy 403 a hard stop.

## Error Handling

| Failure | Meaning | Response |
|---------|---------|----------|
| Target ownership or purpose is missing | Authorization chain is incomplete | Stop before provisioning credentials |
| Account-wide key is shared broadly | Blast radius is excessive | Issue named-user access or a narrower zone credential |
| Collected fields exceed the manifest | Application guardrail failed | Quarantine output and open an incident |

## Resources

- [Acceptable use policy](https://docs.brightdata.com/general/policy/acceptable-use-policy)
- [Users management](https://docs.brightdata.com/general/account/users-management)
- [Authentication and API keys](https://docs.brightdata.com/api-reference/authentication)
- [Proxy error catalog](https://docs.brightdata.com/proxy-networks/errorCatalog)

---
name: procore-multi-env-setup
description: >-
  Configure Procore Developer, On-Demand, Monthly, and production environments without mixing app keys, OAuth credentials, hosts, company IDs, or reset assumptions. Use when building an environment matrix or onboarding customer testing. Trigger with: "configure Procore environments", "set up Procore sandbox", "fix Procore sandbox credentials".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[environment-and-test-purpose]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - environments
  - sandbox
compatibility: 'Requires a Procore app and the administrator access applicable to the selected sandbox or production company.'
---

# Procore Environment Isolation Matrix

## Overview

Choose the environment from the test purpose and configure its actual installation and runtime contract. Developer, On-Demand, and Monthly sandboxes differ in credentials, hosts, app version keys, refresh behavior, and customer eligibility.

## Prerequisites

- Test objective, data sensitivity, customer involvement, and refresh requirement
- App version, sandbox or production keys, OAuth credential aliases, and company IDs
- Named administrator and post-refresh or post-install verification owner

## Instructions

### Step 1: Select the environment

Use a Developer Sandbox for isolated app building, On-Demand Sandbox for customer-controlled testing on copied data, and Monthly Sandbox for a periodically refreshed customer snapshot. Use production only for approved live operation.

### Step 2: Build an explicit matrix

Record authentication host, API host, browser host, app version key type, OAuth credential type, company ID, refresh behavior, and installation owner for each environment.

### Step 3: Enforce isolation

Store configurations separately and add guards that reject mismatched host, credential alias, and environment. Never infer environment from a company name.

### Step 4: Install correctly

Use the Sandbox App Version Key only for the Developer Sandbox. Customer On-Demand and Monthly sandboxes use the production app version key and must be installed or surfaced according to their documented lifecycle.

### Step 5: Plan data reset

Do not assume Developer Sandboxes refresh. Treat On-Demand lifecycle as customer-controlled and Monthly Sandbox changes as disposable at refresh.

### Step 6: Verify after change

After install, recreation, or refresh, obtain a token and run the read-only connection proof against the expected company and project boundary.

## Authentication

Developer Sandbox uses sandbox OAuth credentials and sandbox hosts. On-Demand uses production OAuth credentials and production endpoints; Monthly uses production credentials with its monthly-sandbox hosts. Tokens are never interchangeable across configured environments.

## Tool Discipline

Use Read and Grep to inspect environment matrices, app configuration, and guards. Use Write or Edit only for the approved configuration, test, runbook, or redacted receipt; installation changes require the proper Procore administrator.

## Output

- Environment selection and complete connection matrix
- Host, key, credential, company, and reset guards
- Installation or refresh verification receipt

Return the environment, configuration aliases, expected data lifecycle, verification outcome, and owner.

## Examples

A developer builds against a seeded Developer Sandbox with sandbox credentials. A customer trial uses an On-Demand Sandbox installed with the production app key, but its distinct company ID keeps the trial isolated from the customer's production company.

## Error Handling

| Failure | Response |
| --- | --- |
| Token rejected | Verify the credential and login host belong to the same environment. |
| App absent after Monthly refresh | Check production installation timing and rerun post-refresh verification. |
| Developer Sandbox needs reset | Register a deliberate replacement app and migrate configuration; do not assume refresh. |
| Company ID differs after recreation | Update the explicit environment matrix and rerun scope assertions. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Procore sandboxes](https://developers.procore.com/documentation/development-environments)
- [Install a version in Developer Sandbox](https://developers.procore.com/documentation/install-version-sandbox)
- [OAuth endpoints](https://developers.procore.com/documentation/oauth-endpoints)

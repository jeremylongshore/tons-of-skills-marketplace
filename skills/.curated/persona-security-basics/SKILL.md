---
name: persona-security-basics
description: >-
  Harden Persona API keys, identity data, inquiry sessions, webhook verification, and destructive redaction. Use when conducting a security review. Trigger with: "secure Persona integration", "Persona PII controls", "audit Persona webhook security".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[service-and-environment]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - security
  - pii
  - webhooks
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Persona PII, Key, Session, and Webhook Controls

## Overview

Treat the integration as a high-sensitivity identity boundary. Separate server API keys, short-lived inquiry session tokens, and webhook secrets; minimize collected PII; authenticate every event; and make destructive redaction an explicit governed operation.

## Prerequisites

- Data-flow and threat model for the Persona integration
- Owners for credentials, privacy, incidents, retention, and redaction
- Approved environment, template, webhook, and access-control inventory

## Instructions

### Step 1: Classify secrets and data

Inventory bearer keys, webhook secrets, session tokens, identity attributes, documents, images, logs, and derived decisions with owners and retention.

### Step 2: Enforce environment isolation

Use distinct secret scopes, endpoints, templates, and access policies for sandbox and production. Deny production data in developer fixtures.

### Step 3: Minimize privilege and exposure

Restrict keys and operator roles, keep Persona calls server-side, redact headers and bodies, and prevent session tokens from analytics or URLs.

### Step 4: Authenticate raw events

Parse `Persona-Signature`, compute SHA-256 HMAC over `timestamp + '.' + rawBody`, compare all `v1` candidates in constant time, and enforce a reviewed timestamp tolerance.

### Step 5: Make processing replay-safe

Deduplicate event IDs and order business transitions by provider `created-at`, because deliveries may repeat or arrive out of order.

### Step 6: Govern redaction

Require subject, resource, authorization, impact preview, child-resource expectations, and evidence before invoking redaction. It cannot be undone and child redaction is asynchronous.

## Authentication

REST uses an environment bearer API key; event intake uses the endpoint webhook secret; browser flows receive only the intended inquiry session token. These credentials are not interchangeable.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Credential and sensitive-data inventory
- Webhook authenticity and replay-control design
- Retention, redaction, rotation, incident, and rollback controls

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

During secret rotation the endpoint accepts both current signing candidates, verifies every candidate against the raw body in constant time, records only the matching-secret generation, and removes the retired secret after the overlap window.

## Error Handling

| Failure | Response |
| --- | --- |
| Signature valid only after JSON serialization | Reject it: verification must use the exact raw bytes received. |
| Secret or token in telemetry | Revoke or rotate as appropriate, contain access, and follow the incident plan. |
| Redaction target ambiguous | Stop; resolve the exact inquiry and child-resource impact before any destructive call. |

## Validation

Verify the result against the linked first-party evidence, the pinned API version, redacted contract fixtures, an expected failure path, and the documented rollback or manual-disposition path. A successful request is not proof of a successful identity decision.

## Resources

- [First-party source notes](references/official-docs.md)
- [API introduction](https://docs.withpersona.com/api-introduction)
- [API quickstart](https://docs.withpersona.com/api-quickstart-tutorial)
- [API keys](https://docs.withpersona.com/api-keys)
- [Rate limits](https://docs.withpersona.com/rate-limiting)
- [Webhook best practices](https://docs.withpersona.com/webhooks-best-practices)
- [Request idempotence](https://docs.withpersona.com/idempotence)

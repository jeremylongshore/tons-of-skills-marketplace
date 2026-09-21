---
name: palantir-install-auth
description: >-
  Select and configure a Palantir OSDK or Platform SDK with the correct Developer Console OAuth grant and restrictions. Use when bootstrapping a user application, backend service, or direct platform API client. Trigger with "install Palantir SDK" or "Foundry OAuth".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[application-and-language]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, installation, oauth]
---
# Palantir SDK Selection and OAuth Setup

## Overview

Choose the SDK from the job: a generated OSDK for application-specific Ontology access, or the Platform SDK for broader Foundry/AIP REST APIs. Then configure OAuth through Developer Console with the minimum grant, scope, resources, and operations.

## Prerequisites

- Identify the application type, language, Foundry environment, acting user or service user, required APIs, and accountable owner.
- List the minimum Ontology entities or Platform API operations before creating credentials.
- Read `references/official-docs.md` and use Developer Console's generated Start developing instructions for the target application.
- Prepare an approved secret store and non-production verification resource.

## Current Contract

- Foundry APIs use OAuth 2.0 bearer tokens.
- Authorization Code grant is for applications acting on behalf of users; Client Credentials grant is for backend services acting as a service user.
- Developer Console application restrictions limit available Ontology resources or Platform SDK operations in addition to requested scopes and principal permissions.
- Temporary user API tokens may support development, but production applications should use the appropriate OAuth grant.

## Authentication

Never ask for, print, or commit a bearer token, client secret, authorization code, or refresh token. Store secrets only in an approved manager. Record the client ID only where allowed, and inventory grant type, redirect URLs, requested scopes, application restrictions, service-user permissions, owners, and rotation.

## Instructions

1. Choose generated OSDK or Platform SDK and document why the other surface is insufficient or unnecessary.

2. Create or select the Developer Console application and configure the user-delegated or backend-service grant.

3. Restrict the client to the required Ontology entities or Platform SDK operations and request the minimum scopes.

4. Install and pin the generated/package SDK plus its compatible client using the application-specific instructions.

5. Verify a bounded read in the target environment, test denial outside the intended restriction, and record secret rotation and revocation.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

The application owner approves the OAuth client and redirect behavior; the Ontology or platform owner approves resource restrictions; the security owner approves secret storage; the data owner approves the verification read.

## Output

An SDK decision, pinned dependency set, Developer Console configuration inventory, grant and principal, scope/restriction matrix, secret-store references, positive/negative verification, and rotation/revocation ownership.

## Error Handling

| Condition | Response |
|---|---|
| A token works outside intended resources | Tighten application restrictions and principal permissions, revoke affected credentials, and retest. |
| A client-credentials request is forbidden | Check service-user permissions, scopes, and application restrictions independently. |
| Generated code disagrees with a copied example | Use the target application's generated instructions and current SDK package as authoritative. |
| A secret appears in source or logs | Revoke and rotate it immediately, remove it from history, and regenerate sanitized evidence. |

## Examples

### Example 1

Bootstrap a TypeScript OSDK user application with Authorization Code grant, one selected object type, one Action, explicit redirect URLs, and a negative test for an unselected resource.

### Example 2

Configure a Python Platform SDK backend service with Client Credentials grant, only the required operation restrictions and scopes, a secret-manager reference, and a bounded read verification.

## Validation

- The chosen SDK corresponds to the required API surface.
- Grant type and acting principal match the application architecture.
- Scopes, application restrictions, and Foundry permissions are all minimum and separately documented.
- Dependencies are pinned to the generated/current compatible versions.
- Revocation, rotation, and negative-access tests succeed.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.

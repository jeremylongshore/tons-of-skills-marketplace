---
name: lucidchart-install-auth
description: 'Choose and configure the correct Lucid authentication model: API key, OAuth user token, or OAuth account token. Use when bootstrapping or repairing Lucid REST access. Trigger with "configure Lucid auth".'
argument-hint: "[project-path] [auth-mode]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, lucidchart, authentication, oauth, api-key]
model: inherit
effort: medium
compatibility: Designed for Claude Code; credential creation, OAuth registration, consent, and account-token grants require administrator or resource-owner approval
---
# Lucid Installation and Authentication

## Overview

Select the least-privilege credential class for the operation, configure a secretless local contract, and verify identity and scope without exposing credentials.

## Prerequisites

- The exact Lucid operation, resource owner, environment, and required scopes
- A registered OAuth application when user or account OAuth is selected
- An approved secret store and rotation owner

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect configuration templates, `WebFetch` for current auth and scope contracts, and `Write` or `Edit` only for secretless examples or redacted receipts.

## Current Contract

Lucid documents API keys, OAuth user tokens, and OAuth account tokens. OAuth applications use Authorization Code Flow. REST credentials are normally sent as `Authorization: Bearer ...`; an operation may also require a resource-specific `Lucid-Api-Version` header.

## Authentication

- Use an API key only where the current operation supports it and personal ownership is acceptable.
- Use OAuth user tokens for delegated user access and consented scopes.
- Use OAuth account tokens only for documented account-level use with administrator authorization.
- Never substitute a fabricated `Lucid-Api-Key` header or log authorization values.

## Instructions

1. Re-fetch authentication methods, the exact operation, access scopes, and headers.
2. Create an auth decision record: credential class, principal, resources, scopes, expiration, rotation, and revocation.
3. Inspect the project for hard-coded tokens, unsafe redirects, committed environment files, and mixed credential classes.
4. Define environment-variable names and a secret-provider interface without writing values.
5. For OAuth, validate exact redirect URIs, state handling, authorization-code exchange, secure token storage, refresh behavior, and revocation.
6. Present any app registration, consent, account grant, or secret creation for explicit approval.
7. After credentials are provisioned outside the transcript, perform the smallest documented read-only verification and capture only status, principal class, scopes, and safe request identifiers.

## Approval Boundaries

Do not create keys, register or modify OAuth apps, authorize accounts, broaden scopes, or rotate/revoke credentials without the relevant owner.

## Output

Return auth decision, required scopes and headers, secretless configuration, verification receipt, rotation/revocation owner, and unresolved access gaps.

## Error Handling

| Condition | Response |
|---|---|
| Operation rejects a credential class | Re-check the operation-specific auth table; do not try random headers. |
| OAuth redirect or state validation fails | Stop the exchange and repair the application configuration. |
| Scope is insufficient | Request the narrow documented scope; never silently broaden consent. |

## Example

```text
mode=oauth-user; principal=user-delegated; scopes=verified-current-docs; token-output=redacted; smoke=pass
```

## Resources

- [Official documentation map](references/official-docs.md)

## Next Steps

Test revocation and rotation in a non-production environment before depending on the credential operationally.

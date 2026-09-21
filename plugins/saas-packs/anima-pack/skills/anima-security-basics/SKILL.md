---
name: anima-security-basics
description: 'Audit and harden Anima and Figma tokens for design-to-code pipelines.

  Use when protecting API credentials, restricting Figma access scope,

  or hardening CI/CD design automation pipelines.

  Trigger with: "anima security", "anima token safety", "figma token security".

  '
allowed-tools: Read, Write, Edit, Grep
version: 2.0.0
argument-hint: "[pipeline-or-environment]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- security
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Security Basics

## Overview

This workflow protects the Anima and Figma credentials used by a
design-to-code pipeline while keeping generated output reviewable. It applies
least privilege to the design source, keeps tokens on the server, and makes
secret exposure or unexpected file access a fail-closed condition.

## Prerequisites

- A managed secret store and separate development, staging, and production
  bindings for `ANIMA_TOKEN` and `FIGMA_TOKEN`.
- An allowlist of Figma file keys and component node IDs, with an owner for
  each design source and a documented rotation/revocation contact.
- A non-production fixture and a disposable staging workspace for testing
  token scope, generated artifacts, and rollback behavior.
- Repository secret scanning and a deterministic generated-code directory;
  never use real customer or personal design data as the test fixture.

## Security Checklist

- [ ] Anima token stored in secret manager (not .env in prod)
- [ ] Figma token uses only the endpoint-required granular read scopes
- [ ] SDK runs server-side only (never ship tokens to browser)
- [ ] `.env` files gitignored and chmod 600
- [ ] CI secrets stored in GitHub Secrets, not workflow files
- [ ] Generated code reviewed before committing (no embedded tokens)

## Instructions

### Step 1: Figma Token Scope Restriction

```bash
# When creating a Figma Personal Access Token:
# - Start with file_content:read for file/node content.
# - Add file_metadata:read, file_versions:read, or library read scopes only
#   when the selected endpoint requires them.
# - Do not use the deprecated broad files:read scope for new integrations.
# - Set an organization-approved expiration date.
# - Create separate tokens for dev vs CI environments
```

### Step 2: Server-Side Only Enforcement

```typescript
// src/anima/safety.ts
// Anima SDK is designed for server-side use only

function validateEnvironment(): void {
  if (typeof window !== 'undefined') {
    throw new Error('Anima SDK must run server-side only — never import in browser code');
  }
  if (!process.env.ANIMA_TOKEN) throw new Error('ANIMA_TOKEN not set');
  if (!process.env.FIGMA_TOKEN) throw new Error('FIGMA_TOKEN not set');
}

// Call this at startup
validateEnvironment();
```

## Error Handling

| Failure | Required response |
|---------|-------------------|
| Secret manager is unavailable or a required token is empty | Abort before any Figma or Anima request; emit only a redacted reason and retry through the deployment system. |
| A browser bundle imports the SDK or contains a token | Fail the build, remove the artifact, and rotate any credential that may have been exposed. |
| Figma returns an authorization or scope error | Stop the run and review the file/node allowlist; do not broaden scopes automatically. |
| A token is expired, over-scoped, or present in logs/artifacts | Revoke and replace it through the managed store, then rerun the leak scan before enabling the pipeline. |
| Generated code contains credentials or unapproved source content | Quarantine the output and block the merge; retain only a sanitized finding and artifact digest. |

All failures should preserve the previous known-good generated revision. Do not
print token values, design content, personal identifiers, or full request
payloads while diagnosing a failure.

### Step 3: Secret Manager Integration

```typescript
// src/anima/secrets.ts
async function loadAnimaSecrets(): Promise<{ animaToken: string; figmaToken: string }> {
  const { SecretManagerServiceClient } = await import('@google-cloud/secret-manager');
  const client = new SecretManagerServiceClient();

  const [animaVersion] = await client.accessSecretVersion({
    name: `projects/${process.env.GCP_PROJECT}/secrets/anima-token/versions/latest`,
  });
  const [figmaVersion] = await client.accessSecretVersion({
    name: `projects/${process.env.GCP_PROJECT}/secrets/figma-token/versions/latest`,
  });

  return {
    animaToken: animaVersion.payload?.data?.toString() || '',
    figmaToken: figmaVersion.payload?.data?.toString() || '',
  };
}
```

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- Figma token with minimal scope (read-only)
- Server-side enforcement preventing browser usage
- Secrets loaded from cloud secret manager

## Examples

Run a staging preflight with an allowlisted synthetic file and verify that the
process can read the managed bindings without revealing their values:

```bash
export FIGMA_FILE_KEY="synthetic-staging-file"
node scripts/anima-preflight.mjs \
  --file-key "$FIGMA_FILE_KEY" \
  --node-id "1:2" \
  --check-token-scope \
  --assert-server-only \
  --redact-output
```

The preflight should fail closed if either secret is absent, the file or node
is not allowlisted, or a generated artifact contains a token. Record only the
environment, source identifier, scope result, artifact digest, and cleanup
result in the receipt; never record the credentials or design contents.

## Resources

- [Figma Access Tokens](https://www.figma.com/developers/api#access-tokens)
- [GCP Secret Manager](https://cloud.google.com/secret-manager)

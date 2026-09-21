---
name: anima-install-auth
description: 'Install the Anima SDK and configure authentication for Figma-to-code
  generation.

  Use when setting up design-to-code automation, configuring Figma token access,

  or initializing the @animaapp/anima-sdk for server-side code generation.

  Trigger with: "install anima", "setup anima", "anima auth", "anima figma token".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 2.0.0
argument-hint: "[backend-project]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- code-generation
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Install & Auth

## Overview

Install the backend-only `@animaapp/anima-sdk`, bind managed Anima and Figma
credentials, and prove one authorized React or HTML generation without exposing
either token.

## Prerequisites

- Node.js 20+ (SDK is server-side only)
- Figma account with API access
- Anima API token (request at [animaapp.com](https://www.animaapp.com))
- Figma Personal Access Token

## Instructions

### Step 1: Install the Anima SDK

```bash
npm install @animaapp/anima-sdk
```

### Step 2: Get Your Tokens

```bash
# 1. Figma Personal Access Token:
#    Figma > Settings > Account > Personal Access Tokens > Generate

# 2. Anima API Token:
#    Request from Anima team (currently limited partner access)
#    https://docs.animaapp.com/docs/anima-api

# Bind ANIMA_TOKEN and FIGMA_TOKEN with the runtime secret manager.
# Check presence without printing values.
test -n "$ANIMA_TOKEN" && test -n "$FIGMA_TOKEN"
```

### Step 3: Initialize and Verify

```typescript
// src/anima-client.ts
import { Anima } from '@animaapp/anima-sdk';

const anima = new Anima({
  auth: {
    token: process.env.ANIMA_TOKEN!,
  },
});

// Verify connection by generating code from a known Figma file
async function verifySetup() {
  try {
    const { files } = await anima.generateCode({
      fileKey: 'your-figma-file-key',     // From Figma URL: figma.com/file/{fileKey}/...
      figmaToken: process.env.FIGMA_TOKEN!,
      nodesId: ['1:2'],                    // Specific node to convert
      settings: {
        language: 'typescript',
        framework: 'react',
        styling: 'tailwind',
      },
    });

    console.log(`Generated ${Object.keys(files).length} files`);
    for (const [fileName, file] of Object.entries(files)) {
      console.log(`  ${fileName} (${file.content.length} chars; binary=${file.isBinary})`);
    }
    return true;
  } catch {
    console.error({ failureClass: 'setup-verification-failed' });
    return false;
  }
}

verifySetup();
```

### Step 4: Get Your Figma File Key

```
Figma URL format:
https://www.figma.com/file/ABC123xyz/My-Design?node-id=1:2

File Key: ABC123xyz
Node ID: 1:2 (from the URL query parameter)
```

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- `@animaapp/anima-sdk` installed
- Anima and Figma tokens bound through the runtime secret manager
- Verified code generation from a Figma design
- Understanding of file key and node ID extraction

## Examples

Create a dedicated staging Figma file with one approved frame and request a
least-privilege Anima token for that file. Store both credentials through the
development secret workflow, run `verifySetup`, and confirm the result names a
small expected set of generated files without printing either token. Keep the
SDK in a server-side module and validate that no credential appears in the
browser build. If token verification, file access, or node lookup fails, stop
and correct the scoped entitlement or reference; do not use a personal token
with broader design access as a workaround.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid Anima token` | Token not provisioned | Request token from Anima team |
| `Invalid Figma token` | PAT expired or wrong | Generate new PAT in Figma Settings |
| `File not found` | Wrong file key | Extract key from Figma URL correctly |
| `Node not found` | Invalid node ID | Use Figma Dev Mode to get node IDs |
| `SDK not for browser` | Used in client-side code | SDK is server-side only |

## Resources

- [Anima API Docs](https://docs.animaapp.com/docs/anima-api)
- [Anima SDK GitHub](https://github.com/AnimaApp/anima-sdk)
- [Figma API Auth](https://www.figma.com/developers/api#access-tokens)
- [Anima npm](https://www.npmjs.com/package/@animaapp/anima-sdk)

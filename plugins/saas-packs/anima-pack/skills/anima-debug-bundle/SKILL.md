---
name: anima-debug-bundle
description: 'Collect Anima SDK debug evidence for support tickets and troubleshooting.

  Use when filing Anima support requests, debugging code generation issues,

  or collecting diagnostic data for the Anima team.

  Trigger with: "anima debug bundle", "anima support ticket", "anima diagnostics".

  '
allowed-tools: Read, Write, Edit, Bash(curl:*), Bash(node:*), Grep
version: 2.0.0
argument-hint: "[failed-job-or-symptom]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- debugging
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Debug Bundle

## Overview

Collect a narrowly scoped, redactable diagnostic artifact for a reproducible
Anima or Figma integration failure. Review the file locally before sharing it:
token-presence indicators are acceptable; credential values, private design
content, and personal identity data are not.

## Prerequisites

- A scoped development credential and a disposable/staging design fixture that
  reproduces the issue without exposing a customer or private production file.
- The expected file/node/settings tuple, timestamp, and sanitized error or
  request ID to correlate the bundle with the reported issue.
- A support-sharing review process and an owner able to rotate credentials if a
  diagnostic artifact is found to contain sensitive material.

## Instructions

Build the bundle locally, inspect its exact fields, run a secret scan, and share
it only after the support owner confirms that every value is safe.

### Step 1: Generate Debug Bundle

```typescript
// src/debug/anima-debug.ts
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);

function errorClass(error: unknown): string {
  return error instanceof Error ? error.name : 'UnknownError';
}

async function generateDebugBundle() {
  const bundle = {
    timestamp: new Date().toISOString(),
    environment: {
      nodeVersion: process.version,
      sdkVersion: require('@animaapp/anima-sdk/package.json').version,
      animaToken: process.env.ANIMA_TOKEN ? 'SET (redacted)' : 'NOT SET',
      figmaToken: process.env.FIGMA_TOKEN ? 'SET (redacted)' : 'NOT SET',
    },
    figmaAccess: await testFigmaAccess(),
    sdkLoad: await testSdkLoad(),
  };

  const outputDir = path.resolve(process.env.DEBUG_OUTPUT_DIR || '.private-debug');
  fs.mkdirSync(outputDir, { recursive: true, mode: 0o700 });
  const filename = path.join(outputDir, `anima-debug-${Date.now()}.json`);
  fs.writeFileSync(filename, JSON.stringify(bundle, null, 2), { mode: 0o600, flag: 'wx' });
  console.log({ debugBundleCreated: true, outputDir });
  return bundle;
}

async function testFigmaAccess() {
  try {
    const res = await fetch('https://api.figma.com/v1/me', {
      headers: { 'X-Figma-Token': process.env.FIGMA_TOKEN! },
    });
    return { status: res.ok ? 'ok' : 'failed', httpStatus: res.status };
  } catch (error: unknown) {
    return { status: 'failed', errorClass: errorClass(error) };
  }
}

async function testSdkLoad() {
  try {
    const { Anima } = await import('@animaapp/anima-sdk');
    new Anima({ auth: { token: process.env.ANIMA_TOKEN! } });
    return { status: 'sdk_loaded', version: 'check package.json' };
  } catch (error: unknown) {
    return { status: 'sdk_failed', errorClass: errorClass(error) };
  }
}

generateDebugBundle().catch(() => {
  console.error({ failureClass: 'debug-bundle-failed' });
  process.exitCode = 1;
});
```

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- JSON debug bundle with SDK version, token status, and connectivity test
- Figma API access verification
- Candidate support artifact pending local field review and secret scan

## Examples

When generation fails against a staging component, run the bundle generator
with scoped credentials and inspect the JSON before attaching it to a support
ticket. Confirm that it contains SDK version, token state, and sanitized
connectivity result—but not token values, the full design payload, or a private
file name. Attach the bundle with the problem timestamp and request ID. If the
review finds sensitive content or the test cannot reproduce safely, do not
upload the file; quarantine it, rotate an exposed credential if needed, reduce
the captured fields, and regenerate the diagnostic.

## Error Handling

| Failure | Response |
|---------|----------|
| Diagnostic credentials are missing or invalid | Stop the run and correct the managed secret binding without printing values. |
| Figma or SDK check fails | Record only status/error category and attach the sanitized context to the incident. |
| Bundle contains sensitive data | Quarantine it, rotate affected credentials, improve redaction, and regenerate. |
| Issue cannot be reproduced in staging | Escalate with minimal non-sensitive metadata rather than collecting production design content. |

## Resources

- [Anima Support](https://support.animaapp.com)
- [Anima SDK GitHub Issues](https://github.com/AnimaApp/anima-sdk/issues)

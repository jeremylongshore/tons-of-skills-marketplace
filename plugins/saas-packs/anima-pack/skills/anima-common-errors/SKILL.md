---
name: anima-common-errors
description: 'Diagnose and fix common Anima SDK design-to-code errors.

  Use when encountering Figma token errors, code generation failures,

  node not found issues, or output quality problems.

  Trigger with: "anima error", "anima not working", "anima debug", "figma to code error".

  '
allowed-tools: Read, Write, Edit, Bash(curl:*), Grep
version: 2.0.0
argument-hint: "[error-or-symptom]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- troubleshooting
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Common Errors

## Overview

Use this guide to diagnose design-to-code failures without widening design-file
access or leaking tokens. Start from a reproducible file/node/settings tuple
and use a least-privilege development credential for all verification.

## Prerequisites

- A sanitized error record with the design file identifier, node identifier,
  selected generation settings, timestamp, and request ID where available.
- Scoped Anima and Figma credentials held in a secret store; never paste a
  personal access token into a ticket, source file, or shared diagnostic log.
- A staging or disposable design fixture so fixes can be reproduced without
  mutating a production design file.

## Instructions

1. Classify the failure as authentication, file/node resolution, generator
   configuration, timeout/rate limit, or rendered-output quality.
2. Reproduce it with the smallest approved frame/component and the diagnostic
   commands, capturing only sanitized results.
3. Correct the matching design input, entitlement, or generation configuration
   and rerun only that fixture.
4. Validate the generated file location, lint/build result, and visual review
   before updating a broader component set.

## Error Reference

### Authentication Errors

| Error | Root Cause | Fix |
|-------|-----------|-----|
| `Invalid Anima token` | Token not provisioned or expired | Request new token from Anima team |
| `Invalid Figma token` | PAT expired or revoked | Generate new PAT: Figma > Settings > Access Tokens |
| `Unauthorized` | Token lacks file access | Ensure Figma PAT has file read permission |

### File & Node Errors

| Error | Root Cause | Fix |
|-------|-----------|-----|
| `File not found` | Wrong file key | Extract from Figma URL: `figma.com/file/{KEY}/...` |
| `Node not found` | Invalid node ID | Copy node link from Figma: right-click > Copy link |
| `No renderable content` | Selected a page or group | Select a frame, component, or component set |
| Empty `files` record | Node is empty or hidden | Unhide layers; ensure node has visible content |

### Code Generation Errors

```typescript
// Classify without printing provider messages, which can contain source details.
async function safeGenerate(anima: Anima, params: Parameters<Anima['generateCode']>[0]) {
  try {
    return await anima.generateCode(params);
  } catch (error: unknown) {
    const status = typeof error === 'object' && error !== null && 'status' in error
      ? Number(error.status)
      : undefined;
    const failureClass = status === 401 || status === 403
      ? 'authentication-or-permission'
      : status === 429
        ? 'rate-limited'
        : status !== undefined && status >= 500
          ? 'provider-transient'
          : 'generation-failed';
    console.error({ failureClass, status });
    return null;
  }
}
```

### Output Quality Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Messy layout | No auto-layout in Figma | Convert frames to auto-layout |
| Wrong colors | Hardcoded hex instead of Figma variables | Use Figma color variables/styles |
| Missing text | Text is inside masked groups | Flatten masks before generating |
| Extra wrappers | Deeply nested groups | Flatten group hierarchy |
| Wrong component names | Unnamed Figma layers | Name layers descriptively |

### Valid Settings Combinations

| Framework | Language | Styling | UI Library |
|-----------|----------|---------|------------|
| `react` | `typescript`, `javascript` | `plain_css`, `tailwind`, `inline_styles` | omit, `mui`, `antd`, `radix`, `shadcn`, `clean_react`, `custom_design_system` |
| `html` | `typescript`, `javascript` | `plain_css`, `tailwind`, `inline_styles` | omit |

## Diagnostic Script

```bash
# Verify Figma token
curl -s "https://api.figma.com/v1/me" \
  -H "X-Figma-Token: ${FIGMA_TOKEN}" | jq '.handle // .err'

# Verify file access
curl -s "https://api.figma.com/v1/files/${FIGMA_FILE_KEY}" \
  -H "X-Figma-Token: ${FIGMA_TOKEN}" | jq '.name // .err'
```

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- Error classified and root cause identified
- Valid settings matrix for reference
- Diagnostic commands for token and file verification

## Examples

When a staging generation returns `Node not found`, compare the copied node ID
with the approved Figma link, then run the file-access diagnostic using a scoped
development token. Regenerate only that small frame after correcting the ID and
confirm files are emitted to the expected generated-code directory. If access
is denied, the node remains hidden, or output is empty, stop the run and ask
the file owner to correct permissions or visibility; do not expand the token’s
scope or substitute a personal token to get past the error.

## Error Handling

| Failure | Response |
|---------|----------|
| Token is invalid, expired, or over-scoped | Stop the diagnostic, replace it through managed secret rotation, and avoid logging the value. |
| File or node cannot be resolved | Verify the approved link and visibility with the design owner before retrying. |
| Generator times out or rate-limits | Use bounded backoff or simplify the fixture; do not fan out uncontrolled retries. |
| Generated output is unsafe or wrong | Keep it out of the main branch, correct source design/settings, and rerun targeted validation. |

## Resources

- [Anima API Docs](https://docs.animaapp.com/docs/anima-api)
- [Figma API Reference](https://www.figma.com/developers/api)

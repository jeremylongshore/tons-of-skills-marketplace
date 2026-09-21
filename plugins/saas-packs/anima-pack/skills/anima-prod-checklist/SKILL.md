---
name: anima-prod-checklist
description: 'Production readiness checklist for Anima design-to-code pipelines.

  Use when deploying automated design-to-code services, preparing CI/CD

  Figma-to-code automation, or validating output quality before production.

  Trigger with: "anima production", "anima go-live", "anima prod checklist".

  '
allowed-tools: Read, Write, Edit, Bash(curl:*), Grep
version: 2.0.0
argument-hint: "[environment]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- production
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Production Checklist

## Overview

Decide whether a React/HTML design-to-code pipeline is safe to launch by checking
source authorization, backend isolation, output quality, review, observability,
and rollback evidence.

## Prerequisites

- Named design, engineering, security, and operations owners who can make a
  go/no-go decision and own the rollback path.
- A staging environment using separate managed Anima/Figma credentials, an
  allowlisted design registry, and a reproducible generated-code fixture.
- Defined output quality gates: source-version traceability, lint/type/build,
  visual/accessibility review, and no secrets in artifacts or logs.

## Instructions

1. Assign an owner and evidence link to every required checklist item.
2. Run the readiness script with the deployment identity in staging and retain
   only its redacted result.
3. Exercise a generation and rollback/disable path with an approved design
   component, then verify downstream code-quality and visual gates.
4. Approve progressive release only when all required checks pass; any failed
   security, credential, output, or fallback control is a no-go condition.

## Authentication & Secrets

- [ ] `ANIMA_TOKEN` stored in the backend secret manager (never in source)
- [ ] Figma token uses only endpoint-required granular read scopes and an approved expiration
- [ ] Separate credentials for development, staging, and production environments
- [ ] Rotation and revocation owners plus tested procedures are documented
- [ ] Tokens excluded from client bundles and build artifacts

## API Integration

- [ ] Pinned SDK uses its documented default API origin unless an approved contract says otherwise
- [ ] Figma rate limiting uses `FigmaRestApi` signals and bounded wait; Anima quotas come from the account contract
- [ ] Generation cache prevents redundant API calls for unchanged screens
- [ ] Figma file version polling detects design changes automatically
- [ ] Optional SDK SSE/job attachment or Figma event queue is authenticated and resumable
- [ ] Component mapping rules are tested for supported React or HTML output

## Error Handling & Resilience

- [ ] Circuit breaker configured for Anima API outages
- [ ] Retry policy distinguishes Figma structured rate limits from bounded transient generation failures
- [ ] Graceful fallback when Figma PAT expires mid-pipeline
- [ ] Generated code validated against ESLint/Prettier before merge
- [ ] Design token mismatches flagged before component output
- [ ] Empty generation results handled (missing layers, unsupported elements)

## Monitoring & Alerting

- [ ] API latency tracked per generation request
- [ ] Error-rate and latency objectives are derived from measured service requirements
- [ ] Generated output tracks build, accessibility, and visual acceptance results
- [ ] Figma sync failures trigger immediate notification
- [ ] Daily digest of generation counts and token usage

## Validation Script

```typescript
async function checkAnimaReadiness(): Promise<void> {
  const checks: { name: string; pass: boolean; detail: string }[] = [];
  const sdkVersion = process.env.APPROVED_ANIMA_VERSION;
  checks.push({
    name: 'Managed bindings',
    pass: Boolean(process.env.ANIMA_TOKEN && process.env.FIGMA_TOKEN && sdkVersion),
    detail: sdkVersion ? `SDK ${sdkVersion}` : 'Pinned SDK version missing',
  });
  // Verify Figma access
  try {
    const res = await fetch('https://api.figma.com/v1/me', {
      headers: { 'X-Figma-Token': process.env.FIGMA_TOKEN! },
    });
    checks.push({ name: 'Figma Access', pass: res.ok, detail: res.ok ? 'Authenticated' : `HTTP ${res.status}` });
  } catch (e: any) { checks.push({ name: 'Figma Access', pass: false, detail: e?.name || 'Request failed' }); }
  for (const c of checks) console.log(`[${c.pass ? 'PASS' : 'FAIL'}] ${c.name}: ${c.detail}`);
}
checkAnimaReadiness();
```

## Error Handling

| Check | Risk if Skipped | Priority |
|-------|----------------|----------|
| API key rotation | Expired keys break entire pipeline | P1 |
| Figma token expiry | Silent sync failure, stale designs | P1 |
| Figma or generation rate limits | Unbounded retries or dropped updates | P2 |
| Component render validation | Broken UI shipped to production | P2 |
| Design token mapping | Visual inconsistencies across app | P3 |

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- Signed-off go/no-go record with owners and redacted readiness evidence
- Verified secret, provider, and Figma access boundaries
- Generated-component validation and source-version traceability receipts
- Tested rollback or generation-disable path for production incidents

## Examples

For a production rehearsal, generate one allowlisted staging component using
the production-shaped secret binding, run the readiness script, and send the
result through lint, type checking, visual review, and the release approval
workflow. Record the Figma version, generated artifact digest, deploy revision,
and rollback owner. If token safety fails, a quality gate is red, or the design
source cannot be traced, declare a no-go, disable generation, and correct the
failed control before rerunning the full checklist.

## Resources

- [Anima API Docs](https://docs.animaapp.com/docs/anima-api)
- [Anima Status](https://status.animaapp.com)

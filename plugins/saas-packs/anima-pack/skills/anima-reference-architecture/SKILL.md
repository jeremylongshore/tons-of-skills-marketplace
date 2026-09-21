---
name: anima-reference-architecture
description: 'Implement reference architecture for Anima design-to-code automation.

  Use when designing a design system automation pipeline, structuring

  a Figma-to-React project, or planning team-scale design handoff.

  Trigger with: "anima architecture", "design-to-code architecture",

  "anima project structure", "figma automation architecture".

  '
allowed-tools: Read, Write, Edit
version: 2.0.0
argument-hint: "[repository-or-service]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- architecture
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Reference Architecture

## Overview

This architecture separates design-source intake, authenticated code generation, deterministic post-processing, and reviewed delivery. It is intended for repeatable Figma-to-code pipelines where each run is bounded to approved files and nodes, produces inspectable artifacts, and can be stopped or rolled back without exposing design content or credentials.

## Prerequisites

- Define the target framework, repository layout, supported Anima/Figma SDK versions, and the owner who approves generated changes. Pin dependencies and create a sandbox Figma file with synthetic components for pipeline tests.
- Obtain Figma and Anima credentials through the deployment secret manager, using least-privilege scopes and short-lived credentials where supported. Validate the configured Figma webhook passcode before accepting events; never commit, print, or place tokens in generated code, cache files, pull requests, or receipts.
- Establish allowlists for Figma file IDs, node IDs, webhook sources, output repositories, and branch names. Define retention and deletion rules for source snapshots, generated output, and logs before enabling automation.
- Prepare a dry-run mode, an artifact-diff gate, a staged canary environment, and a rollback reference to the last approved generated revision. Do not allow a webhook to publish directly to production.

## System Architecture

```
┌────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Figma Design  │────▶│ Figma API    │────▶│ Anima SDK       │
│  (Components)  │     │ (Webhooks)   │     │ (Code Gen)      │
└────────────────┘     └──────────────┘     └────────┬────────┘
                                                      │
                                            ┌─────────▼────────┐
                                            │ Post-Processing   │
                                            │ - Token mapping   │
                                            │ - Normalization   │
                                            │ - Lint/format     │
                                            └─────────┬────────┘
                                                      │
                                            ┌─────────▼────────┐
                                            │ Output            │
                                            │ - React or HTML   │
                                            │ - PR creation     │
                                            │ - Storybook sync  │
└──────────────────┘
```

## Instructions

1. **Ingest and authorize.** Use `Read` to inspect the existing repository conventions and the signed event payload. Check the file/node allowlist, event freshness, source revision, and suppression/deletion rules before requesting any generation.
2. **Generate in isolation.** Run the pinned SDK in a sandbox worker with bounded concurrency and an explicit output directory. Record a request fingerprint and source revision; keep source snapshots and generated files out of logs and clean temporary material after the run.
3. **Normalize and verify.** Use the token mapper and normalizer deterministically, then run formatting, type checks, dependency policy checks, secret scanning, and a generated-file diff. Reject output that writes outside the allowlisted tree or contains credentials, unexpected network calls, or unapproved source data.
4. **Review and deliver.** Use `Write`/`Edit` only within the approved workspace, create a draft change or pull request, and require an owner review before merge. Storybook or preview publishing must target a sandbox first and must not expose private design assets.
5. **Promote and recover.** Promote one canary component or sandbox project, compare aggregate health and visual/regression results, and then roll out in batches. On failure, stop event consumption, restore the prior generated revision, revoke temporary credentials, delete staged artifacts according to retention policy, and record a redacted receipt.

## Error Handling

- Reject unauthenticated, stale, duplicate, or out-of-scope webhook events before any API call. Return a generic status to the sender and keep detailed diagnostics restricted to the operator channel.
- Treat Figma/Anima 401 and 403 responses as configuration or authorization failures; do not retry them automatically. Treat 429 and transient 5xx/network failures with the bounded retry and rate-limit policy, using an idempotency key or request fingerprint to prevent duplicate generation.
- If post-processing, linting, type checking, or secret scanning fails, quarantine the generated tree and do not open or update a production change. Preserve only hashes, rule IDs, counts, and the rollback reference in the receipt.
- If a worker or webhook delivery fails after generation, resume from the last durable stage rather than rerunning the whole pipeline. A rollback must be tested in the sandbox and must restore both repository state and event-consumer state.
- Alert on repeated failures, scope drift, unexpected output paths, retention violations, or canary regressions. A human owner decides whether to retry, repair configuration, or disable the pipeline.

## Examples

For a controlled component update, an event for `file=synthetic-design-system; revision=r42; node=button-primary` passes the allowlist, generates into `generated/canary/`, and produces a draft change containing only normalized component files. The receipt can record `source_revision=r42; output_digest=sha256:opaque; checks=lint,type,secret-scan; canary=pass; production_promoted=false` without storing the design payload or generated source.

For a failed canary, the pipeline records `stage=storybook; reason=visual-regression; rollback=generated/r41; production_promoted=false`, restores revision `r41`, stops further webhook consumption, and removes the staged directory after the retention check. The same sequence is the acceptance test for enabling production promotion.

## Project Structure

```
design-to-code/
├── src/
│   ├── anima/
│   │   ├── client.ts              # Singleton SDK client
│   │   ├── cache.ts               # Generation cache
│   │   ├── retry.ts               # Error recovery
│   │   └── presets.ts             # Framework/styling presets
│   ├── pipeline/
│   │   ├── scanner.ts             # Figma component discovery
│   │   ├── generator.ts           # Batch code generation
│   │   ├── change-detector.ts     # Figma version tracking
│   │   └── runner.ts              # Pipeline orchestrator
│   ├── post-process/
│   │   ├── normalizer.ts          # Output normalization
│   │   ├── token-mapper.ts        # Design token mapping
│   │   └── organizer.ts           # File organization + barrel exports
│   ├── webhooks/
│   │   └── figma-handler.ts       # Figma webhook receiver
│   └── server.ts                  # Express API (optional)
├── scripts/
│   ├── generate-components.ts     # CLI generation script
│   └── compare-presets.ts         # Side-by-side preset comparison
├── fixtures/
│   └── component-map.json         # Figma node ID → component name mapping
├── generated/                     # Output directory (gitignored or committed)
├── .anima-cache/                  # Generation cache (gitignored)
└── package.json
```

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| SDK | `@animaapp/anima-sdk` | Official, server-side, typed |
| Change detection | Figma Webhooks v2 | Event-driven, no polling waste |
| Caching | File-based with MD5 keys | Simple, no external dependencies |
| Post-processing | Custom normalizer | Match project conventions |
| CI integration | GitHub Actions scheduled | Avoid real-time generation costs |
| Output framework | Repository-approved React or HTML settings | Match the pinned SDK and target application |

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- Complete design-to-code pipeline architecture
- Project structure with all components
- Design decision rationale documented

## Resources

- [Anima API](https://docs.animaapp.com/docs/anima-api)
- [Anima SDK GitHub](https://github.com/AnimaApp/anima-sdk)
- [Figma Webhooks](https://www.figma.com/developers/api#webhooks-v2)
- [Anima Figma Plugin](https://www.figma.com/community/plugin/857346721138427857)

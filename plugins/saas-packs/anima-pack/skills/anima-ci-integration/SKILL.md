---
name: anima-ci-integration
description: 'Configure CI/CD pipeline for automated Figma-to-code generation with
  Anima.

  Use when automating design-to-code in GitHub Actions, setting up PR-based

  component generation, or integrating Anima into design handoff workflows.

  Trigger with: "anima CI", "anima GitHub Actions", "anima automated generation".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 2.0.0
argument-hint: "[workflow-file] [figma-file-key]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- ci-cd
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima CI Integration

## Overview

This workflow turns explicitly approved Figma nodes into a reviewable generated
code change. The CI identity receives design credentials only at runtime and
must never merge or deploy generated output without the repository’s normal
quality and ownership controls.

## Prerequisites

- A read-only Anima/Figma integration token stored as CI secrets and limited to
  the intended design file.
- An allowlisted component/node registry, deterministic output directory, and
  generated-code ownership/review policy.
- A branch workflow that validates generated output before any human-approved
  merge; scheduled generation alone is not release authorization.

## Instructions

### Step 1: GitHub Actions Workflow

```yaml
# .github/workflows/design-sync.yml
name: Design-to-Code Sync

on:
  schedule:
    - cron: '0 9 * * 1-5'  # Weekdays at 9am
  workflow_dispatch:         # Manual trigger

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - name: Generate components from Figma
        env:
          ANIMA_TOKEN: ${{ secrets.ANIMA_TOKEN }}
          FIGMA_TOKEN: ${{ secrets.FIGMA_TOKEN }}
          FIGMA_FILE_KEY: ${{ secrets.FIGMA_FILE_KEY }}
        run: npx tsx scripts/generate-components.ts
      - name: Lint generated code
        run: npx eslint src/components/generated/ --fix
      - name: Check for changes
        id: changes
        run: |
          if git diff --quiet src/components/generated/; then
            echo "changed=false" >> $GITHUB_OUTPUT
          else
            echo "changed=true" >> $GITHUB_OUTPUT
          fi
      - name: Create PR with generated components
        if: steps.changes.outputs.changed == 'true'
        run: |
          git checkout -b design-sync/$(date +%Y%m%d)
          git add src/components/generated/
          git commit -m "chore: sync generated components from Figma"
          git push -u origin HEAD
          gh pr create --title "Design sync: updated generated components" \
            --body "Auto-generated from Figma via Anima SDK"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Step 2: Generation Script for CI

```typescript
// scripts/generate-components.ts
import { Anima } from '@animaapp/anima-sdk';
import fs from 'fs';
import path from 'path';

const anima = new Anima({ auth: { token: process.env.ANIMA_TOKEN! } });

const COMPONENTS = [
  { nodeId: '1:2', name: 'Hero' },
  { nodeId: '3:4', name: 'Card' },
  { nodeId: '5:6', name: 'Navigation' },
];

async function main() {
  const outputDir = 'src/components/generated';
  fs.mkdirSync(outputDir, { recursive: true });

  for (const comp of COMPONENTS) {
    const { files } = await anima.generateCode({
      fileKey: process.env.FIGMA_FILE_KEY!,
      figmaToken: process.env.FIGMA_TOKEN!,
      nodesId: [comp.nodeId],
      settings: { language: 'typescript', framework: 'react', styling: 'tailwind', uiLibrary: 'shadcn' },
    });

    for (const [fileName, file] of Object.entries(files)) {
      if (file.isBinary) throw new Error(`Binary output needs asset handling: ${fileName}`);
      const root = path.resolve(outputDir);
      const target = path.resolve(root, fileName);
      if (!target.startsWith(`${root}${path.sep}`)) throw new Error('Unsafe output path');
      fs.mkdirSync(path.dirname(target), { recursive: true });
      fs.writeFileSync(target, file.content);
    }
    console.log(`Generated: ${comp.name}`);
    // Stop on a provider/Figma rate-limit result; do not guess a safe quota.
  }
}

main().catch(() => {
  console.error({ failureClass: 'design-sync-failed' });
  process.exit(1);
});
```

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- Scheduled GitHub Actions workflow for design-to-code sync
- Auto-PR creation when generated code changes
- Lint, type, secret, dependency, and visual checks on generated output
- A bounded generation script that stops on rate-limit or authorization failure

## Examples

Run the workflow manually against a staging Figma file containing only an
approved `Card` node. Confirm it generates files beneath the dedicated output
directory, runs formatting and tests, and creates a PR with a diff that a
maintainer can inspect. The PR should include the source node identifier and
the generation run, but never the Figma or Anima token. If generation changes
an unexpected path, output is invalid, or token access fails, stop before PR
creation, retain sanitized logs, and correct the allowlist or secret binding
before retrying.

## Error Handling

| Failure | Response |
|---------|----------|
| Design token or file access is denied | Fail the job without printing credentials; verify scoped secret configuration. |
| Generator writes outside the approved directory | Refuse to commit or open a PR and investigate the path mapping. |
| Generated code fails lint or tests | Keep the branch unmerged and return the actionable failure to the design/code owners. |
| Scheduled run has no approved changes | Exit cleanly without creating an empty PR or deployment. |

## Resources

- [Anima API](https://docs.animaapp.com/docs/anima-api)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---
name: anima-local-dev-loop
description: 'Set up iterative design-to-code development loop with Anima SDK.

  Use when rapidly iterating on Figma-to-code output, comparing framework outputs,

  or building a local preview server for generated components.

  Trigger with: "anima local dev", "anima dev loop", "anima preview", "anima iteration".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 2.0.0
argument-hint: "[figma-file-key] [node-id]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- development
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Local Dev Loop

## Overview

Iterate on one approved Figma node with supported React or HTML settings. Preserve
the source revision and settings for each run, preview locally, and accept a result
only after deterministic code and visual checks.

## Prerequisites

- A staging Figma file and allowlisted node IDs, with scoped credentials loaded
  from an ignored local environment file or development secret store.
- A disposable generated-output directory that is not imported by the
  production application until code and visual review pass.
- Agreed comparison criteria for accessibility, design-token use, responsive
  behavior, dependencies, and generation settings.

## Instructions

### Step 1: Project Setup

```bash
mkdir anima-dev && cd anima-dev
npm init -y
npm install @animaapp/anima-sdk dotenv
npm install -D vite @vitejs/plugin-react typescript
```

### Step 2: Generate and Preview Script

```typescript
// scripts/generate-preview.ts
import { Anima } from '@animaapp/anima-sdk';
import fs from 'fs';
import path from 'path';
import 'dotenv/config';

const anima = new Anima({ auth: { token: process.env.ANIMA_TOKEN! } });

const SETTINGS_PRESETS = {
  'react-tailwind': { language: 'typescript' as const, framework: 'react' as const, styling: 'tailwind' as const },
  'react-shadcn': { language: 'typescript' as const, framework: 'react' as const, styling: 'tailwind' as const, uiLibrary: 'shadcn' as const },
  'react-plain-css': { language: 'typescript' as const, framework: 'react' as const, styling: 'plain_css' as const },
  'html-plain-css': { language: 'javascript' as const, framework: 'html' as const, styling: 'plain_css' as const },
};

async function generateWithPreset(preset: keyof typeof SETTINGS_PRESETS, nodeId: string) {
  const settings = SETTINGS_PRESETS[preset];
  const outputDir = `./generated/${preset}`;
  fs.mkdirSync(outputDir, { recursive: true });

  const { files } = await anima.generateCode({
    fileKey: process.env.FIGMA_FILE_KEY!,
    figmaToken: process.env.FIGMA_TOKEN!,
    nodesId: [nodeId],
    settings,
  });

  for (const [fileName, file] of Object.entries(files)) {
    if (file.isBinary) throw new Error(`Handle binary output separately: ${fileName}`);
    const root = path.resolve(outputDir);
    const target = path.resolve(root, fileName);
    if (!target.startsWith(`${root}${path.sep}`)) throw new Error('Unsafe output path');
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, file.content);
  }
  console.log(`${preset}: ${Object.keys(files).length} files generated`);
}

// Compare all presets
async function compareOutputs(nodeId: string) {
  for (const preset of Object.keys(SETTINGS_PRESETS) as Array<keyof typeof SETTINGS_PRESETS>) {
    await generateWithPreset(preset, nodeId);
    // Stop on provider/Figma rate limits; apply the bounded rate-limit workflow.
  }
  console.log('\nAll presets generated in ./generated/');
}

const nodeId = process.argv[2] || '1:2';
compareOutputs(nodeId).catch(() => {
  console.error({ failureClass: 'preview-generation-failed' });
  process.exitCode = 1;
});
```

### Step 3: Development Scripts

```json
{
  "scripts": {
    "generate": "tsx scripts/generate-preview.ts",
    "generate:node": "tsx scripts/generate-preview.ts",
    "preview": "vite",
    "dev": "npm run generate && npm run preview"
  }
}
```

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- Multi-preset code generation comparison
- Side-by-side supported React/HTML output for the same design
- Vite preview server for instant component viewing
- Iterative generate-preview-tweak loop

## Examples

Select one approved staging frame and run only the `react-tailwind` preset
first. Preview the result locally, compare it to the design for semantics and
responsive behavior, and run the project formatter/type check before trying a
second preset. Store the Figma version and preset alongside the generated
review artifact so the comparison is repeatable. If generation hits a rate
limit, output changes unexpectedly, or an unapproved dependency appears, stop
the loop, preserve the sanitized error, and correct the fixture or settings
instead of continuously regenerating.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Rate limited | Too many generations | Add 2s delay between calls |
| Different outputs each run | Anima AI variation | Pin settings; use consistent node IDs |

## Resources

- [Anima SDK GitHub](https://github.com/AnimaApp/anima-sdk)
- [Vite](https://vitejs.dev/)

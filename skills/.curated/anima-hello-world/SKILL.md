---
name: anima-hello-world
description: 'Generate reviewable React or HTML code from a Figma design using the Anima SDK.

  Use when testing design-to-code conversion, learning Anima''s code output format,

  or building your first automated design-to-code pipeline.

  Trigger with: "anima hello world", "anima example", "figma to react",

  "figma to code", "anima generate code".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*)
version: 2.0.0
argument-hint: "[figma-url] [node-id]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- react
- code-generation
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Hello World

## Overview

Generate reviewable React or HTML from one approved Figma node with the backend-only
`@animaapp/anima-sdk`. Keep credentials server-side and treat every generated file
as untrusted output until its path, dependencies, build, and visual result pass review.

## Prerequisites

- Completed `anima-install-auth` setup
- A Figma file with at least one frame/component
- Know your file key and node ID

## Instructions

### Step 1: Generate React + Tailwind Code

```typescript
// src/hello-world.ts
import { Anima } from '@animaapp/anima-sdk';
import fs from 'fs';
import path from 'path';

const anima = new Anima({
  auth: { token: process.env.ANIMA_TOKEN! },
});

async function generateReactComponent() {
  const { files } = await anima.generateCode({
    fileKey: process.env.FIGMA_FILE_KEY!,     // From Figma URL
    figmaToken: process.env.FIGMA_TOKEN!,
    nodesId: [process.env.FIGMA_NODE_ID!],    // e.g., '1:2'
    settings: {
      language: 'typescript',
      framework: 'react',
      styling: 'tailwind',
      // Omit uiLibrary for vanilla React, or select a supported library.
    },
  });

  // Write generated files to disk
  const outputDir = './generated';
  fs.mkdirSync(outputDir, { recursive: true });

  for (const [fileName, file] of Object.entries(files)) {
    const filePath = path.resolve(outputDir, fileName);
    if (!filePath.startsWith(`${path.resolve(outputDir)}${path.sep}`)) {
      throw new Error(`Refusing output path: ${fileName}`);
    }
    if (file.isBinary) throw new Error(`Handle binary output separately: ${fileName}`);
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, file.content, { flag: 'wx' });
    console.log(`Generated: ${fileName} (${file.content.length} chars)`);
  }

  return files;
}

generateReactComponent().catch(() => {
  console.error({ failureClass: 'generation-failed' });
  process.exitCode = 1;
});
```

### Step 2: Try Supported Output Settings

```typescript
// Generate HTML with the SDK's plain_css setting.
const htmlFiles = await anima.generateCode({
  fileKey: process.env.FIGMA_FILE_KEY!,
  figmaToken: process.env.FIGMA_TOKEN!,
  nodesId: ['1:2'],
  settings: {
    language: 'javascript',
    framework: 'html',
    styling: 'plain_css',
  },
});

// Generate React + shadcn/ui
const shadcnFiles = await anima.generateCode({
  fileKey: process.env.FIGMA_FILE_KEY!,
  figmaToken: process.env.FIGMA_TOKEN!,
  nodesId: ['1:2'],
  settings: {
    language: 'typescript',
    framework: 'react',
    styling: 'tailwind',
    uiLibrary: 'shadcn',
  },
});
```

### Step 3: Inspect Generated Output

```typescript
// `files` is a record keyed by relative filename.
type GeneratedFiles = Record<string, { content: string; isBinary: boolean }>;

// Example output structure for React + Tailwind:
// generated/
// ├── HeroSection.tsx       # React component with Tailwind classes
// ├── Button.tsx            # Child components
// └── types.ts              # TypeScript interfaces (if applicable)
```

### Step 4: Integrate into Existing Project

```bash
# Review before copying; do not execute generated package scripts.
npm run format -- --check generated
npm run typecheck
```

## Settings Reference

| Setting | Options | Default |
|---------|---------|---------|
| `language` | `typescript`, `javascript` | `typescript` |
| `framework` | `react`, `html` | Required |
| `styling` | `plain_css`, `tailwind`, `inline_styles` | Required |
| `uiLibrary` | `mui`, `antd`, `radix`, `shadcn`, `clean_react`, `custom_design_system` | Omit for vanilla React |

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- A contained React or HTML generation result from one approved Figma node
- A filename/content manifest and rejected-path report
- Formatter, type-check, dependency, and visual-review receipts

## Examples

Create a small staging Figma frame with an approved button and heading, store
the Anima/Figma credentials in a local ignored environment file, and generate
only that node into `./generated`. Confirm each filename resolves under the
output directory, inspect the component for expected labels and styles, then
run the project formatter and type check before copying it into a feature
branch. If the node cannot be found, output is empty, or the generation writes
an unexpected path, stop and correct the Figma link or output mapping; do not
use a broader file token or copy unreviewed generated code directly to main.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `File not found` | Wrong Figma file key | Extract key from URL after `/file/` |
| `Node not found` | Wrong node ID | Use Figma's "Copy link" on the frame |
| Empty `files` array | Node has no renderable content | Select a frame/component, not a page |
| Malformed output | Complex nested auto-layout | Simplify Figma structure; use components |

## Resources

- [Anima API Docs](https://docs.animaapp.com/docs/anima-api)
- [Anima SDK GitHub](https://github.com/AnimaApp/anima-sdk)
- [Anima Blog: Figma to React](https://www.animaapp.com/blog/design-to-code/how-to-export-figma-to-react/)

---
name: anima-core-workflow-a
description: 'Build automated Figma-to-React pipeline with the Anima SDK.

  Use when automating design handoff, building CI/CD design-to-code workflows,

  or creating a design system code generator from Figma components.

  Trigger with: "anima design pipeline", "figma to react pipeline",

  "automated design handoff", "anima component generator".

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
- react
- automation
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Core Workflow A — Figma-to-React Pipeline

## Overview

Build a review-driven Figma-to-React pipeline. Detect an approved source revision,
generate only allowlisted nodes, contain the output, and open a review change; never
turn a Figma change directly into merged or deployed application code.

## Prerequisites

- Completed `anima-install-auth` setup
- Figma file with organized components (auto-layout recommended)
- React project (Next.js, Vite, or CRA)

## Authentication

Create the `Anima` client only on the backend with `ANIMA_TOKEN`; pass a managed
`FIGMA_TOKEN` for the allowlisted file to `generateCode`. Stop on either token's
401/403 result and correct access without widening the source allowlist.

## Instructions

### Step 1: Design System Scanner

```typescript
// src/pipeline/figma-scanner.ts
import { Anima } from '@animaapp/anima-sdk';

interface FigmaComponent {
  nodeId: string;
  name: string;
  type: 'COMPONENT' | 'FRAME' | 'COMPONENT_SET';
}

const anima = new Anima({
  auth: { token: process.env.ANIMA_TOKEN! },
});

// Fetch all top-level components from a Figma page
async function scanFigmaComponents(fileKey: string) {
  const response = await fetch(
    `https://api.figma.com/v1/files/${fileKey}/components`,
    { headers: { 'X-Figma-Token': process.env.FIGMA_TOKEN! } }
  );
  const data = await response.json();

  return data.meta.components.map((comp: any) => ({
    nodeId: comp.node_id,
    name: comp.name,
    type: comp.containing_frame?.type || 'COMPONENT',
  }));
}
```

### Step 2: Batch Code Generator

```typescript
// src/pipeline/batch-generator.ts
import { Anima } from '@animaapp/anima-sdk';
import fs from 'fs';
import path from 'path';

const anima = new Anima({
  auth: { token: process.env.ANIMA_TOKEN! },
});

interface GenerationConfig {
  fileKey: string;
  outputDir: string;
  settings: {
    language: 'typescript' | 'javascript';
    framework: 'react' | 'html';
    styling: 'plain_css' | 'tailwind' | 'inline_styles';
    uiLibrary?: 'mui' | 'antd' | 'radix' | 'shadcn' | 'clean_react' | 'custom_design_system';
  };
}

async function generateComponentBatch(
  config: GenerationConfig,
  nodeIds: string[],
): Promise<{ generated: number; failed: string[] }> {
  const failed: string[] = [];
  let generated = 0;

  fs.mkdirSync(config.outputDir, { recursive: true });

  // Generate each component (Anima processes one node at a time)
  for (const nodeId of nodeIds) {
    try {
      const { files } = await anima.generateCode({
        fileKey: config.fileKey,
        figmaToken: process.env.FIGMA_TOKEN!,
        nodesId: [nodeId],
        settings: config.settings,
      });

      for (const [fileName, file] of Object.entries(files)) {
        const root = path.resolve(config.outputDir);
        const filePath = path.resolve(root, fileName);
        if (!filePath.startsWith(`${root}${path.sep}`) || file.isBinary) {
          throw new Error(`Rejected generated file: ${fileName}`);
        }
        fs.mkdirSync(path.dirname(filePath), { recursive: true });
        fs.writeFileSync(filePath, file.content);
        console.log(`Generated: ${fileName}`);
      }
      generated++;
    } catch {
      console.error({ failureClass: 'node-generation-failed', nodeId });
      failed.push(nodeId);
    }

    // Concurrency and retry policy belong to the measured rate-limit workflow.
  }

  return { generated, failed };
}

export { generateComponentBatch, GenerationConfig };
```

### Step 3: Figma Change Detection

```typescript
// src/pipeline/change-detector.ts
interface FileVersion {
  id: string;
  created_at: string;
  label: string;
}

async function getLatestVersion(fileKey: string) {
  const response = await fetch(
    `https://api.figma.com/v1/files/${fileKey}/versions`,
    { headers: { 'X-Figma-Token': process.env.FIGMA_TOKEN! } }
  );
  const data = await response.json();
  return data.versions[0];
}

// Check if file changed since last generation
let lastVersionId = '';

async function hasDesignChanged(fileKey: string) {
  const latest = await getLatestVersion(fileKey);
  if (latest.id !== lastVersionId) {
    lastVersionId = latest.id;
    return true;
  }
  return false;
}

export { hasDesignChanged, getLatestVersion };
```

### Step 4: Full Pipeline Runner

```typescript
// src/pipeline/run.ts
import { scanFigmaComponents } from './figma-scanner';
import { generateComponentBatch, GenerationConfig } from './batch-generator';
import { hasDesignChanged } from './change-detector';

const config: GenerationConfig = {
  fileKey: process.env.FIGMA_FILE_KEY!,
  outputDir: './src/components/generated',
  settings: {
    language: 'typescript',
    framework: 'react',
    styling: 'tailwind',
    uiLibrary: 'shadcn',
  },
};

async function runPipeline() {
  console.log('Scanning Figma file for components...');
  const components = await scanFigmaComponents(config.fileKey);
  console.log(`Found ${components.length} components`);

  console.log('Generating code...');
  const result = await generateComponentBatch(
    config,
    components.map(c => c.nodeId)
  );

  console.log(`\nPipeline complete: ${result.generated} generated, ${result.failed.length} failed`);
}

runPipeline().catch(() => {
  console.error({ failureClass: 'figma-pipeline-failed' });
  process.exitCode = 1;
});
```

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- Automated Figma component scanning and enumeration
- Batch code generation for entire design systems
- Change detection for continuous design-to-code sync
- A durable source-revision receipt suitable for a PR review gate

## Examples

Create a staging Figma file with two approved components and configure the
pipeline to write only to `src/components/generated`. Run one generation cycle,
inspect the resulting diff, and run the project formatter, type check, and
visual review before accepting either component. Persist the last approved
Figma version outside the process so a restart does not regenerate an unknown
set of nodes. If the scanner returns unexpected components, a generator writes
outside the output directory, or validation fails, stop the watch loop and
correct the node allowlist or design source before the next run.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Rate limited | Too many API calls | Add 2s delay between component generations |
| Component not renderable | Figma node is group, not frame | Ensure components use auto-layout |
| Inconsistent output | Complex nested structures | Flatten deep nesting in Figma |
| Missing styles | Custom fonts not available | Map fonts in Anima settings |

## Resources

- [Anima API](https://docs.animaapp.com/docs/anima-api)
- [Figma API Components](https://www.figma.com/developers/api#components)
- [Anima Blog](https://www.animaapp.com/blog/design-to-code/)

---
name: anima-core-workflow-b
description: 'Clone websites to React/HTML code and customize Anima output with AI.

  Use when converting live websites to code, customizing generated components,

  or building design-system-aware code from URL screenshots.

  Trigger with: "anima website to code", "anima URL clone", "anima AI customization",

  "website to react", "clone website to code".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 2.0.0
argument-hint: "[public-url-or-prompt]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- website-cloning
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Core Workflow B — Website-to-Code & AI Customization

## Overview

Convert an authorized public website with the current backend SDK, then review the
result against rights, asset, dependency, accessibility, and output-containment
policies. Use prompt generation only as an explicitly accepted early-preview path.

## Prerequisites

- Completed `anima-install-auth` setup
- Written authority to reproduce the source site and its assets
- An allowlisted public URL; private sites require the licensed MHTML path and a
  separate sensitive-capture handling policy

## Authentication

Instantiate the backend `Anima` client with a managed Anima token. Website and
prompt requests do not use a browser-exposed credential; reject unauthorized
callers and non-allowlisted source URLs before calling the SDK.

## Instructions

### Step 1: Website-to-Code Conversion

```typescript
// src/workflows/website-to-code.ts
// Generate from an allowlisted public website you are authorized to reproduce.

import { Anima } from '@animaapp/anima-sdk';
import crypto from 'node:crypto';

const APPROVED_HOSTS = new Set(['docs.example.com']);

const anima = new Anima({
  auth: { token: process.env.ANIMA_TOKEN! },
});

async function cloneWebsiteToReact(url: string) {
  const source = new URL(url);
  if (source.protocol !== 'https:' || !APPROVED_HOSTS.has(source.hostname)) {
    throw new Error('Source URL is not approved');
  }
  return anima.generateCodeFromWebsite({
    url: source.href,
    settings: {
      framework: 'react',
      language: 'typescript',
      styling: 'tailwind',
      uiLibrary: 'shadcn',
    },
    tracking: { externalId: crypto.randomUUID() },
  });
}

async function generateFromApprovedPrompt(prompt: string) {
  if (prompt.length < 20 || prompt.length > 2_000) {
    throw new Error('Prompt length is outside the approved range');
  }
  return anima.generateCodeFromPrompt({
    prompt,
    settings: {
      framework: 'react',
      language: 'typescript',
      styling: 'tailwind',
      uiLibrary: 'shadcn',
    },
    tracking: { externalId: crypto.randomUUID() },
  });
}
```

### Step 2: Post-Generation Customization

```typescript
// src/workflows/customize-output.ts
interface CustomizationRule {
  pattern: RegExp;
  replacement: string;
  description: string;
}

// Apply project-specific customizations to Anima output
function customizeGeneratedCode(
  files: Record<string, { content: string; isBinary: boolean }>,
  rules: CustomizationRule[],
): Record<string, { content: string; isBinary: boolean }> {
  return Object.fromEntries(Object.entries(files).map(([fileName, file]) => {
    if (file.isBinary) return [fileName, file];
    let content = file.content;
    for (const rule of rules) {
      content = content.replace(rule.pattern, rule.replacement);
    }
    return [fileName, { ...file, content }];
  }));
}

// Common customization rules
const PROJECT_RULES: CustomizationRule[] = [
  {
    pattern: /className="([^"]+)"/g,
    replacement: 'className={cn("$1")}',
    description: 'Wrap Tailwind classes with cn() utility',
  },
  {
    pattern: /import React from 'react'/g,
    replacement: "import React from 'react';\nimport { cn } from '@/lib/utils'",
    description: 'Add cn import for className merging',
  },
  {
    pattern: /export default function (\w+)/g,
    replacement: 'export const $1: React.FC = function $1',
    description: 'Use React.FC type annotation',
  },
];
```

### Step 3: Design Token Mapper

```typescript
// src/workflows/token-mapper.ts
// Map Anima's raw Tailwind classes to your design system tokens

interface TokenMap {
  colors: Record<string, string>;     // Anima color → your token
  spacing: Record<string, string>;    // Anima spacing → your token
  typography: Record<string, string>; // Anima font → your token
}

const tokenMap: TokenMap = {
  colors: {
    'bg-\\[#1a1a2e\\]': 'bg-primary',
    'text-\\[#e94560\\]': 'text-accent',
    'bg-\\[#16213e\\]': 'bg-surface',
  },
  spacing: {
    'p-\\[24px\\]': 'p-6',
    'gap-\\[16px\\]': 'gap-4',
    'mt-\\[32px\\]': 'mt-8',
  },
  typography: {
    'text-\\[32px\\]': 'text-3xl',
    'font-\\[600\\]': 'font-semibold',
  },
};

function applyDesignTokens(content: string, map: TokenMap): string {
  let result = content;
  for (const category of Object.values(map)) {
    for (const [from, to] of Object.entries(category)) {
      result = result.replace(new RegExp(from, 'g'), to);
    }
  }
  return result;
}
```

### Step 4: Multi-Component Output Organizer

```typescript
// src/workflows/organizer.ts
import fs from 'fs';
import path from 'path';

function organizeGeneratedFiles(
  files: Record<string, { content: string; isBinary: boolean }>,
  baseDir: string,
): void {
  // Organize by component type
  const structure: Record<string, string> = {
    '.tsx': 'components',
    '.css': 'styles',
    '.ts': 'types',
    '.html': 'pages',
  };

  for (const [fileName, file] of Object.entries(files)) {
    if (file.isBinary) throw new Error(`Binary asset needs explicit handling: ${fileName}`);
    const ext = path.extname(fileName);
    const subDir = structure[ext] || 'misc';
    const dir = path.join(baseDir, subDir);
    const target = path.resolve(dir, fileName);
    if (!target.startsWith(`${path.resolve(baseDir)}${path.sep}`)) throw new Error('Unsafe output path');
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(target, file.content);
  }

  // Generate barrel export
  const components = Object.keys(files).filter(fileName => fileName.endsWith('.tsx'));
  if (components.length > 0) {
    const exports = components.map(fileName => {
      const name = path.basename(fileName, '.tsx');
      return `export { default as ${name} } from './${name}';`;
    });
    fs.writeFileSync(
      path.join(baseDir, 'components', 'index.ts'),
      exports.join('\n') + '\n'
    );
  }
}
```

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- Website conversion through `generateCodeFromWebsite`
- Early-preview prompt generation through `generateCodeFromPrompt`
- Post-generation customization rules engine
- Design token mapper for project consistency
- File organizer with barrel exports

## Examples

Use a page you own or have written permission to reproduce, capture only the
approved layout into a staging Figma file, and generate a single React component
into an isolated output directory. Apply the project token map, then review the
result for brand assets, copy, accessibility, responsive behavior, and license
constraints before it enters the application. Treat generated markup as a
starting point rather than a faithful or authorized reproduction of a third
party’s product. If access is blocked, output contains unapproved material, or
the result fails visual/semantic review, stop and obtain the needed rights or
redesign from an original specification instead of bypassing site controls.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| URL not accessible | Source blocks capture or is not public | Stop; do not bypass source controls |
| Output doesn't match design | Complex animations/interactions | Simplify to static layout first |
| Token mapping misses | New colors/spacing in design | Update token map after each generation |

## Resources

- [Anima API](https://docs.animaapp.com/docs/anima-api)
- [Anima Playground](https://www.animaapp.com)
- [Anima Blog: GenAI Customization](https://www.animaapp.com/blog/genai/genai-figma-to-code-6-examples-of-how-to-use-animas-new-ai-code-customization/)

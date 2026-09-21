---
name: anima-sdk-patterns
description: 'Apply production-ready patterns for the Anima SDK design-to-code pipeline.

  Use when building reusable Anima client wrappers, implementing output caching,

  or establishing team standards for design-to-code automation.

  Trigger with: "anima SDK patterns", "anima best practices", "anima code patterns".

  '
allowed-tools: Read, Write, Edit
version: 2.0.0
argument-hint: "[sdk-wrapper-or-pipeline]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- patterns
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima SDK Patterns

## Overview

Build a backend `@animaapp/anima-sdk` wrapper with a pinned client, supported
settings, source-bound caching, contained output normalization, and bounded error
recovery. Reject unsupported framework values and ambiguous cache entries.

## Prerequisites

- Pin the Anima SDK and TypeScript runtime versions, define the supported framework presets, and provide a sandbox Figma file containing synthetic components for tests and examples.
- Inject `ANIMA_TOKEN` and any Figma credentials from a secret manager at runtime. Authentication failures must be distinguishable from generation failures; never hard-code, log, cache, or include credentials in generated output or receipts.
- Make `.anima-cache` private to the worker, exclude it from version control and artifact uploads, and define a retention/deletion policy. Cache keys may identify a request, but cached design source and generated content must not be sent to telemetry.
- Set an allowlist for input file/node IDs and output paths, a maximum cache size, a bounded retry count, and an owner-approved normalization configuration before enabling the wrapper in CI or production.

## Instructions

### Step 1: Singleton Client with Configuration

```typescript
// src/anima/client.ts
import { Anima } from '@animaapp/anima-sdk';

let instance: Anima | null = null;

export function getAnimaClient(): Anima {
  if (!instance) {
    if (!process.env.ANIMA_TOKEN) throw new Error('ANIMA_TOKEN not set');
    instance = new Anima({ auth: { token: process.env.ANIMA_TOKEN } });
  }
  return instance;
}

// Preset configurations for different project needs
export const PRESETS = {
  nextjs: { language: 'typescript' as const, framework: 'react' as const, styling: 'tailwind' as const, uiLibrary: 'shadcn' as const },
  vite: { language: 'typescript' as const, framework: 'react' as const, styling: 'tailwind' as const },
  reactPlainCss: { language: 'typescript' as const, framework: 'react' as const, styling: 'plain_css' as const },
  static: { language: 'javascript' as const, framework: 'html' as const, styling: 'plain_css' as const },
} as const;
```

### Step 2: Generation Cache

```typescript
// src/anima/cache.ts
import crypto from 'crypto';
import fs from 'fs';

interface CacheEntry {
  files: Record<string, { content: string; isBinary: boolean }>;
  generatedAt: string;
  settingsHash: string;
}

class AnimaCache {
  private cacheDir: string;

  constructor(cacheDir: string = '.anima-cache') {
    this.cacheDir = cacheDir;
    fs.mkdirSync(cacheDir, { recursive: true });
  }

  private getKey(fileKey: string, sourceRevision: string, nodeId: string, settings: object): string {
    const hash = crypto.createHash('sha256')
      .update(`${fileKey}:${sourceRevision}:${nodeId}:${JSON.stringify(settings)}`)
      .digest('hex');
    return hash;
  }

  get(fileKey: string, sourceRevision: string, nodeId: string, settings: object): CacheEntry | null {
    const key = this.getKey(fileKey, sourceRevision, nodeId, settings);
    const path = `${this.cacheDir}/${key}.json`;
    if (!fs.existsSync(path)) return null;
    return JSON.parse(fs.readFileSync(path, 'utf8'));
  }

  set(fileKey: string, sourceRevision: string, nodeId: string, settings: object, files: CacheEntry['files']): void {
    const key = this.getKey(fileKey, sourceRevision, nodeId, settings);
    const entry: CacheEntry = {
      files,
      generatedAt: new Date().toISOString(),
      settingsHash: key,
    };
    fs.writeFileSync(`${this.cacheDir}/${key}.json`, JSON.stringify(entry));
  }
}

export { AnimaCache };
```

### Step 3: Output Normalizer

```typescript
// src/anima/normalizer.ts
// Normalize Anima output to match project conventions

interface NormalizationConfig {
  componentNameCase: 'PascalCase' | 'kebab-case';
  addBarrelExport: boolean;
  wrapWithCn: boolean;
  addTypeAnnotations: boolean;
}

function normalizeOutput(
  files: Record<string, { content: string; isBinary: boolean }>,
  config: NormalizationConfig,
): Record<string, { content: string; isBinary: boolean }> {
  return Object.fromEntries(Object.entries(files).map(([fileName, file]) => {
    if (file.isBinary) return [fileName, file];
    let content = file.content;

    if (config.wrapWithCn && fileName.endsWith('.tsx')) {
      // Add cn() import and wrap className strings
      if (!content.includes("import { cn }")) {
        content = content.replace(
          /^(import .+\n)/m,
          "$1import { cn } from '@/lib/utils';\n"
        );
      }
    }

    if (config.addTypeAnnotations && fileName.endsWith('.tsx')) {
      content = content.replace(
        /export default function (\w+)\(\)/g,
        'export default function $1(): React.ReactElement'
      );
    }

    return [fileName, { ...file, content }];
  }));
}

export { normalizeOutput, NormalizationConfig };
```

### Step 4: Error Recovery Pattern

```typescript
// src/anima/retry.ts
import { Anima } from '@animaapp/anima-sdk';

async function generateWithRetry(
  anima: Anima,
  params: Parameters<Anima['generateCode']>[0],
  maxAttempts = 3,
  maxElapsedMs = 15_000,
): Promise<Awaited<ReturnType<Anima['generateCode']>>> {
  const started = Date.now();
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await anima.generateCode(params);
    } catch (error: unknown) {
      const status = typeof error === 'object' && error !== null && 'status' in error
        ? Number(error.status)
        : undefined;
      const retryable = status === 429 || (status !== undefined && status >= 500);
      const delay = Math.min(2_000 * 2 ** (attempt - 1) + Math.floor(Math.random() * 250), 8_000);
      if (!retryable || attempt === maxAttempts || Date.now() + delay - started > maxElapsedMs) {
        throw error;
      }
      console.warn({ event: 'anima-retry', attempt, delay, status });
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  throw new Error('Retry loop exhausted');
}
```

## Error Handling

- Fail fast with a redacted configuration error when `ANIMA_TOKEN` is missing or rejected, and do not retry 401/403 responses. Check Figma file/node permissions separately from Anima authentication so an operator can correct the smallest scope.
- Treat cache misses as normal, but treat malformed JSON, schema drift, a settings-hash mismatch, or a cache entry outside the approved directory as a cache failure: quarantine or delete that entry and regenerate from the sandbox-approved request rather than trusting it.
- Retry only bounded transient network, timeout, 429, and 5xx failures with exponential backoff and jitter. Cap total attempts and elapsed time; use a request fingerprint to make a resume idempotent and never retry a whole batch when only selected nodes failed.
- If normalization or type-checking fails, retain the raw result only in the private quarantine area, block publication, and report rule IDs plus file counts. Never write generated source, design contents, personal data, or exception payloads to logs.
- On process interruption or partial cache writes, use atomic replacement and restore the previous valid entry. A rollback removes quarantined artifacts, revokes temporary access, and records only the digest, stage, and retention/deletion result.

## Examples

The wrapper can keep a sandbox run deterministic while avoiding duplicate generation:

```typescript
const settings = PRESETS.nextjs;
const fileKey = 'synthetic-design-system';
const sourceRevision = 'synthetic-version-1';
const nodeId = 'button-primary-fixture';
const cache = new AnimaCache('/var/lib/anima-cache/sandbox');

const cached = cache.get(fileKey, sourceRevision, nodeId, settings);
const files = cached?.files ?? (await getAnimaClient().generateCode({
  fileKey,
  figmaToken: process.env.FIGMA_TOKEN!,
  nodesId: [nodeId],
  settings,
})).files;

if (!cached) cache.set(fileKey, sourceRevision, nodeId, settings, files);
const normalized = normalizeOutput(files, {
  componentNameCase: 'PascalCase',
  addBarrelExport: true,
  wrapWithCn: false,
  addTypeAnnotations: true,
});
console.log(JSON.stringify({ fileKey, nodeCount: 1, files: Object.keys(normalized).length, contactsExported: 0 }));
```

The acceptance receipt for this fixture is `cache=miss|hit; source=synthetic; files=bounded; contacts_exported=0; secret_scan=pass`. A production run additionally requires an approved file/node allowlist, a reviewed diff, and a tested rollback reference before the normalized files are published.

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- Singleton client with preset configurations
- File-based generation cache (avoid redundant API calls)
- Output normalizer for project convention matching
- Retry pattern for API resilience

## Resources

- [Anima SDK GitHub](https://github.com/AnimaApp/anima-sdk)
- [Anima API Docs](https://docs.animaapp.com/docs/anima-api)

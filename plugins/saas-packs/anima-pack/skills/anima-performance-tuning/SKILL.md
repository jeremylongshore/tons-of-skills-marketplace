---
name: anima-performance-tuning
description: 'Optimize Anima code generation performance with caching, parallelism,
  and output tuning.

  Use when reducing generation latency, optimizing batch component generation,

  or improving generated code quality for production use.

  Trigger with: "anima performance", "anima slow", "anima optimization", "anima caching".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*)
version: 2.0.0
argument-hint: "[generation-workload]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- performance
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Performance Tuning

## Overview

Improve design-to-code throughput without treating cache hits or smaller output
as success unless the result still matches the approved design version,
accessibility expectations, and project build contract.

## Measurement Contract

Record source-fetch, queue, generation, asset, validation, and review durations
separately. Establish targets from the team's own representative fixtures and
provider agreement; do not present illustrative latency or quota numbers as an
Anima service-level objective.

## Prerequisites

- A representative staging fixture and a baseline measurement of generation
  duration, cache hit rate, failure rate, and generated-code validation result.
- A version-aware cache key and retention policy that ties each artifact to
  Figma source version, node ID, and generation settings.
- Review gates for generated output so performance changes cannot automatically
  replace approved components or strip required licenses/accessibility content.

## Authentication

Load `ANIMA_TOKEN` and the source-scoped `FIGMA_TOKEN` only in the backend worker.
Performance tests use synthetic allowlisted sources; do not broaden credentials
or retry authorization failures to make a benchmark complete.

## Instructions

### Step 1: File-Based Generation Cache

```typescript
// src/performance/cache.ts
import crypto from 'crypto';
import fs from 'fs';
import { Anima } from '@animaapp/anima-sdk';

class GenerationCache {
  private dir: string;

  constructor(cacheDir = '.anima-cache') {
    this.dir = cacheDir;
    fs.mkdirSync(cacheDir, { recursive: true });
  }

  private hash(fileKey: string, sourceRevision: string, nodeId: string, settings: object): string {
    return crypto.createHash('sha256').update(`${fileKey}:${sourceRevision}:${nodeId}:${JSON.stringify(settings)}`).digest('hex');
  }

  async getOrGenerate(
    anima: Anima,
    params: Parameters<Anima['generateCode']>[0],
    sourceRevision: string,
    maxAgeMs: number = 3600000, // 1 hour
  ): Promise<Awaited<ReturnType<Anima['generateCode']>>> {
    const key = this.hash(params.fileKey, sourceRevision, params.nodesId[0], params.settings);
    const path = `${this.dir}/${key}.json`;

    if (fs.existsSync(path)) {
      const stat = fs.statSync(path);
      if (Date.now() - stat.mtimeMs < maxAgeMs) {
        return JSON.parse(fs.readFileSync(path, 'utf8'));
      }
    }

    const result = await anima.generateCode(params);
    fs.writeFileSync(path, JSON.stringify(result));
    return result;
  }

  clearOlderThan(maxAgeMs: number): number {
    let cleared = 0;
    for (const file of fs.readdirSync(this.dir)) {
      const path = `${this.dir}/${file}`;
      if (Date.now() - fs.statSync(path).mtimeMs > maxAgeMs) {
        fs.unlinkSync(path);
        cleared++;
      }
    }
    return cleared;
  }
}

export { GenerationCache };
```

### Step 2: Incremental Generation (Only Changed Components)

```typescript
// src/performance/incremental.ts
// Only regenerate components whose Figma nodes changed

async function getNodeLastModified(fileKey: string, nodeId: string): Promise<string> {
  const res = await fetch(
    `https://api.figma.com/v1/files/${fileKey}/nodes?ids=${nodeId}`,
    { headers: { 'X-Figma-Token': process.env.FIGMA_TOKEN! } }
  );
  const data = await res.json();
  return data.lastModified;
}

async function generateOnlyChanged(
  anima: any,
  fileKey: string,
  nodeIds: string[],
  lastModifiedCache: Map<string, string>,
): Promise<string[]> {
  const changed: string[] = [];

  for (const nodeId of nodeIds) {
    const lastMod = await getNodeLastModified(fileKey, nodeId);
    if (lastMod !== lastModifiedCache.get(nodeId)) {
      changed.push(nodeId);
      lastModifiedCache.set(nodeId, lastMod);
    }
  }

  console.log(`${changed.length}/${nodeIds.length} components changed — regenerating`);
  return changed;
}
```

### Step 3: Validate Output Without Semantic Rewriting

```typescript
// Preserve generated semantics; measure before applying reviewed transforms.
function recordOutput(fileName: string, content: string) {
  return {
    fileName,
    bytes: Buffer.byteLength(content),
    digest: crypto.createHash('sha256').update(content).digest('hex'),
  };
}
```

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- File-based generation cache with TTL
- Incremental generation (only changed components)
- Output size and digest measurements without destructive rewriting

## Examples

Benchmark ten approved staging components once without cache and once with the
cache keyed by source version, node ID, and settings. Compare duration, API
calls, output size, lint/type results, and visual review rather than just cache
hit rate. Regenerate only components whose recorded source version changed, and
keep the prior generated artifact available for diff review. If a cache entry
cannot prove its source version, post-processing changes required behavior, or
rate limits increase, disable the optimization and return to the prior
validated generation path while investigating the aggregate measurements.

## Error Handling

| Failure | Response |
|---------|----------|
| Cache artifact lacks valid source/version metadata | Refuse reuse and regenerate the approved component. |
| Incremental detector cannot determine change state | Treat the affected component as needing controlled regeneration. |
| Optimizer changes semantics or removes required content | Revert the post-processing rule and restore the reviewed artifact. |
| Throughput increases provider failures or rate limits | Reduce concurrency, apply bounded backoff, and preserve user-visible job state. |

## Resources

- [Anima API](https://docs.animaapp.com/docs/anima-api)
- [Figma API Nodes](https://www.figma.com/developers/api#get-file-nodes-endpoint)

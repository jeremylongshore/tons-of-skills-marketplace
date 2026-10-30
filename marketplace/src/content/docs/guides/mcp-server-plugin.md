---
title: 'Building an MCP Server Plugin'
description: 'Step-by-step guide to building a Model Context Protocol (MCP) server plugin for Claude Code. Covers TypeScript project setup, tool implementation, building executables, .mcp.json configuration, and testing.'
section: 'guides'
order: 5
keywords:
  - 'MCP'
  - 'Model Context Protocol'
  - 'MCP server'
  - 'MCP plugin'
  - 'TypeScript'
  - 'tool implementation'
  - 'Claude Code MCP'
  - 'server plugin'
officialLinks:
  - title: 'Anthropic Claude Code Documentation'
    url: 'https://code.claude.com/docs/en/'
  - title: 'Model Context Protocol Specification'
    url: 'https://modelcontextprotocol.io/'
  - title: 'MCP TypeScript SDK'
    url: 'https://github.com/modelcontextprotocol/typescript-sdk'
relatedDocs:
  - 'concepts/mcp-servers'
  - 'reference/plugin-json-schema'
---

## Choose a runtime tool, not an instruction-only promise

MCP exposes runtime tools through a protocol. It is language-independent; this tutorial chooses Node.js and TypeScript. It does not require every MCP server to be TypeScript, compiled, or a directly executable JavaScript file.

The example below is a local, read-only JSON summarizer. It accepts a bounded string and returns counts, not the input's contents. It has no network, filesystem storage, provider credentials, CSV transformation, or production rate-limiting feature. Those capabilities require their own reviewed contracts rather than unfinished stubs.

Use the [MCP server guide](https://modelcontextprotocol.io/docs/develop/build-server), [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk), and [native plugin reference](https://code.claude.com/docs/en/plugins-reference) for their respective protocol and integration facts.

## Project layout

```text
my-json-plugin/
  .claude-plugin/plugin.json
  .mcp.json
  package.json
  pnpm-lock.yaml
  tsconfig.json
  src/summary.ts
  src/index.ts
  test/summary.test.mjs
  test/protocol.test.mjs
  dist/summary.js
  dist/index.js
  README.md
  LICENSE
```

Use Node22.12+ for this repository workflow. The example pins SDK1.32.1 and TypeScript5.9.3; the SDK's own floor is a separate package fact, not permission to run the full repository on an older Node version. Review dependencies and retain the generated lockfile. Do not install tutorial dependencies into an unrelated project.

## Package and compiler configuration

Create `package.json` in the example project:

```json
{
  "name": "example-json-summary",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "tsc -p tsconfig.json",
    "test": "pnpm run build && node --test test/summary.test.mjs test/protocol.test.mjs"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "1.32.1",
    "zod": "3.25.76"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "typescript": "5.9.3"
  }
}
```

Create `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*.ts"]
}
```

Review and install the selected dependencies in that project, then retain and review the lockfile. Subsequent clean installs should use its frozen form:

```bash
pnpm install
pnpm run build
# On subsequent clean installs with the reviewed lockfile:
pnpm install --frozen-lockfile
```

The metadata here is for this private tutorial project, not a replacement for the marketplace's generated or explicitly custom-owned package contract.

## Pure, bounded implementation

Save as `src/summary.ts`. The iterative walk avoids recursive call-stack growth. Byte, node, and depth limits are part of this example's contract, not provider-wide thresholds.

```typescript
export function summarizeJson(input: unknown): { nodes: number; maxDepth: number } {
  if (typeof input !== 'string') throw new Error('Expected a JSON string');
  if (Buffer.byteLength(input, 'utf8') > 65_536) throw new Error('Input exceeds byte limit');
  let value: unknown;
  try {
    value = JSON.parse(input);
  } catch {
    throw new Error('Invalid JSON');
  }
  const pending: Array<{ value: unknown; depth: number }> = [{ value, depth: 0 }];
  let nodes = 0;
  let maxDepth = 0;
  while (pending.length > 0) {
    const item = pending.pop()!;
    nodes += 1;
    if (nodes > 4096) throw new Error('Input exceeds node limit');
    if (item.depth > 20) throw new Error('Input exceeds depth limit');
    maxDepth = Math.max(maxDepth, item.depth);
    if (item.value !== null && typeof item.value === 'object') {
      for (const child of Object.values(item.value)) {
        pending.push({ value: child, depth: item.depth + 1 });
      }
    }
  }
  return { nodes, maxDepth };
}
```

No strings, property names, or user records are returned. Do not add raw inputs to error messages or logs.

## Stdio server

Save as `src/index.ts`. It imports the pure helper instead of embedding an unexported implementation that tests cannot access.

```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { summarizeJson } from './summary.js';

const server = new Server(
  { name: 'example-json-summary', version: '1.0.0' },
  { capabilities: { tools: {} } },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'summarize_json',
      description: 'Count nodes and maximum depth in bounded JSON without returning its contents.',
      inputSchema: {
        type: 'object' as const,
        properties: { json: { type: 'string', maxLength: 65_536 } },
        required: ['json'],
        additionalProperties: false,
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name !== 'summarize_json') {
    throw new McpError(ErrorCode.MethodNotFound, 'Unknown tool');
  }
  try {
    const args = request.params.arguments;
    if (!args || Object.keys(args).some((key) => key !== 'json')) {
      throw new Error('Expected only the json argument');
    }
    const result = summarizeJson(args.json);
    return { content: [{ type: 'text', text: JSON.stringify(result) }] };
  } catch (error) {
    return {
      isError: true,
      content: [{ type: 'text', text: error instanceof Error ? error.message : 'Summary failed' }],
    };
  }
});

async function main(): Promise<void> {
  await server.connect(new StdioServerTransport());
}

void main().catch(() => {
  console.error('MCP server startup failed');
  process.exitCode = 1;
});
```

Tool execution failures use an `isError` result. Protocol failures, such as an unknown tool, use a protocol error. “Always throw McpError” is not the correct contract for every application failure. Stdout belongs exclusively to the MCP transport; use sanitized stderr for diagnostics.

## Manifest and absolute launch path

Create `.claude-plugin/plugin.json` with the actual author, license, and public URLs. This is the marketplace metadata envelope; example identities and URLs need replacement:

```json
{
  "name": "example-json-summary",
  "version": "1.0.0",
  "description": "Summarize bounded JSON locally without returning user data or contacting services.",
  "author": { "name": "Example Maintainer" },
  "homepage": "https://example.com/example-json-summary",
  "license": "MIT",
  "keywords": ["json", "mcp", "local"],
  "commands": []
}
```

Create the native `.mcp.json`:

```json
{
  "mcpServers": {
    "example-json-summary": {
      "type": "stdio",
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/dist/index.js"],
      "env": {}
    }
  }
}
```

Each argument remains a separate JSON array item, including paths with spaces. Do not rely on a relative `dist/index.js` plus an invented `cwd`-relative-to-plugin guarantee. The `node` command interprets JavaScript, so this route does not require a shebang or executable bit on the `.js` file. Direct executable launches have different requirements.

This native configuration does not settle every marketplace prescreen tracking field or approval requirement. Check those separately without inventing runtime switches.

From the example plugin project root containing `package.json`, build before manual development loading:

```bash
pnpm run build
claude --plugin-dir .
```

Here `.` is that same plugin project root. A published copy-install contract must include the built entry and its dependency closure, or explicitly document and test required provisioning. This tutorial's manual build is not an exemption or proof that every marketplace installer builds code.

## Pure helper tests

Save as `test/summary.test.mjs`:

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { summarizeJson } from '../dist/summary.js';

test('returns counts without echoing the input', () => {
  assert.deepEqual(summarizeJson('{"a":1,"b":[true,null]}'), { nodes: 5, maxDepth: 2 });
  assert.deepEqual(summarizeJson('null'), { nodes: 1, maxDepth: 0 });
});

test('rejects malformed input and the actual resource boundaries', () => {
  assert.throws(() => summarizeJson(undefined), /Expected a JSON string/);
  assert.throws(() => summarizeJson('{'), /Invalid JSON/);
  assert.throws(() => summarizeJson(' '.repeat(65_537)), /byte limit/);
  assert.throws(() => summarizeJson(JSON.stringify(Array(5000).fill(0))), /node limit/);
  const tooDeep = '['.repeat(22) + '0' + ']'.repeat(22);
  assert.throws(() => summarizeJson(tooDeep), /depth limit/);
});
```

## Protocol lifecycle test

Save as `test/protocol.test.mjs`. The SDK client performs initialization and the initialized notification before tool requests; one `echo tools/list` line is not a complete integration test.

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

test(
  'initializes, lists, calls, rejects bad input, and closes its own child',
  { timeout: 10_000 },
  async () => {
    const entry = fileURLToPath(new URL('../dist/index.js', import.meta.url));
    const transport = new StdioClientTransport({ command: process.execPath, args: [entry] });
    const client = new Client({ name: 'local-fixture', version: '1.0.0' });
    let childPid;
    try {
      await client.connect(transport, { timeout: 3000 });
      childPid = transport.pid;
      assert.equal(typeof childPid, 'number');
      const listed = await client.listTools({}, { timeout: 3000 });
      assert.deepEqual(
        listed.tools.map((tool) => tool.name),
        ['summarize_json'],
      );
      const result = await client.callTool(
        { name: 'summarize_json', arguments: { json: '{"x":1}' } },
        undefined,
        { timeout: 3000 },
      );
      assert.equal(result.isError, undefined);
      assert.equal(result.content[0].type, 'text');
      assert.deepEqual(JSON.parse(result.content[0].text), { nodes: 2, maxDepth: 1 });
      const rejected = await client.callTool(
        { name: 'summarize_json', arguments: { json: '{' } },
        undefined,
        { timeout: 3000 },
      );
      assert.equal(rejected.isError, true);
      assert.equal(rejected.content[0].text, 'Invalid JSON');
      await assert.rejects(
        client.callTool({ name: 'unknown', arguments: {} }, undefined, { timeout: 3000 }),
      );
    } finally {
      await client.close();
      if (childPid !== undefined) {
        assert.throws(() => process.kill(childPid, 0), { code: 'ESRCH' });
      }
    }
  },
);
```

Run the actual package tests after building. Use an isolated temporary project and synthetic data for these checks; do not add production credentials or activate an unrelated provider to prove a local stdio tool works.

## Storage and external services require separate designs

This server does not persist data. If storage is added, use an explicitly owned persistent root, not an unchecked `./data` fallback. Treat caller keys as untrusted: reject separators and traversal, enforce containment, handle symlinks and same-user race limitations, use exclusive/atomic writes where appropriate, and preserve corrupt data rather than overwriting it. Test those real helpers and failure paths before exposing a storage tool.

Likewise, an outbound API tool needs verified identity, authorization, credential isolation, bounded queues, cancellation, deadlines, and retry/idempotency behavior appropriate to its provider. A timestamp-array sleep example is not a concurrency-safe rate limiter; do not ship it as one.

## Validate and review

From the repository root, with the real plugin path:

```bash
claude plugin validate ./plugins/mcp/example-json-summary
python3 scripts/validate-skills-schema.py --marketplace --verbose plugins/mcp/example-json-summary/
```

Check the complete installed runtime, not only manifest syntax: exact artifacts, dependency provenance, path spaces, successful lifecycle, malformed requests, resource limits, errors, and child cleanup. A static grade does not certify the runtime, and these local synthetic tests do not certify an external provider or every operating system.

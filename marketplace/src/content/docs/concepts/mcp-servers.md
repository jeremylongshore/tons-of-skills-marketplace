---
title: 'MCP Servers in Claude Code Plugins'
description: 'How MCP servers connect Claude Code to tools and data, with clean-copy runtime, transport, validation, and credential boundaries.'
section: 'concepts'
order: 5
keywords:
  - 'MCP server'
  - 'Model Context Protocol'
  - 'Claude Code MCP'
  - 'MCP tools'
  - 'TypeScript MCP server'
  - 'mcp.json'
  - 'Claude Code external tools'
  - 'MCP plugin'
officialLinks:
  - title: 'Model Context Protocol Specification'
    url: 'https://modelcontextprotocol.io'
  - title: 'Claude Code MCP Documentation'
    url: 'https://code.claude.com/docs/en/mcp'
  - title: 'MCP TypeScript SDK'
    url: 'https://github.com/modelcontextprotocol/typescript-sdk'
relatedDocs:
  - 'concepts/plugins'
  - 'concepts/skills'
  - 'concepts/agents'
---

## Overview

Model Context Protocol (MCP) connects a client such as Claude Code to tools, resources, and prompts supplied by a server. Servers can be local or remote and can be written in different languages. They are not necessarily TypeScript applications.

MCP access is an execution and data boundary. Review each server's source, dependency provenance, permissions, credentials, and runtime prerequisites. Instruction plugins can also execute scripts or hooks, so “instructions versus MCP” is not a safe-versus-unsafe classification.

## Package a runnable server

A Node-based plugin might contain:

```text
example-mcp/
├── .claude-plugin/plugin.json
├── .mcp.json
├── src/index.ts
├── dist/index.js
├── package.json
├── package-lock.json
└── README.md
```

The shipped launch target must exist in a clean installed copy. A TypeScript source tree with an ignored, absent `dist/` directory is not a runnable distribution. Either ship the reviewed runtime artifact or document and verify the actual supported installation/build route. A development machine's leftover build does not prove clean-copy readiness.

A marketplace manifest can use this illustrative identity:

```json
{
  "name": "example-mcp",
  "version": "1.0.0",
  "description": "Expose a bounded example tool through a reviewed MCP server.",
  "author": { "name": "Example Team" },
  "homepage": "https://example.com/example-mcp",
  "license": "MIT",
  "keywords": ["mcp", "example"],
  "commands": []
}
```

Replace placeholder metadata with truthful values. The native manifest floor and this repository's stricter overlay are distinct; see [plugins](/docs/concepts/plugins/).

Bind the runtime path to the installed plugin root:

```json
{
  "mcpServers": {
    "example-mcp": {
      "type": "stdio",
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/dist/index.js"]
    }
  }
}
```

The interpreter must be available and compatible with the artifact. A JavaScript file passed to `node` does not need a shebang or executable bit; a directly invoked executable has different requirements. Keep `${CLAUDE_PLUGIN_ROOT}` in execution configuration rather than replacing it with a documentation-relative path.

## Choose a supported SDK and transport

Use the [official SDK](https://github.com/modelcontextprotocol/typescript-sdk) for the selected language and version. The TypeScript SDK has distinct v1 and v2 APIs. The `@modelcontextprotocol/sdk` v1 line remains maintained after the v2 release; v2's existence does not by itself invalidate a pinned v1 integration. Do not mix imports or examples from different API generations.

For a TypeScript server, pin a coherent dependency set and lockfile, include the required Node declarations, and verify compilation against the documented runtime. A bare `typescript: ^5.0.0` entry is not proof of a reproducible build. This page does not claim to provide a complete SDK-specific server implementation or a tested dependency lock.

The current MCP transport specification defines **stdio** and **Streamable HTTP**. Legacy HTTP+SSE compatibility exists, but SSE is not the sole modern remote option. Claude's supported connection types and configuration are owned by its [MCP documentation](https://code.claude.com/docs/en/mcp).

For stdio, keep protocol messages on stdout and diagnostics on stderr. Never print banners, secrets, or unrelated debug output into the protocol stream.

## Validate tool inputs at runtime

A TypeScript cast is not validation. The following complete pure JavaScript function demonstrates a bounded **fixture**, not a weather API, SDK registration, or provider call:

```javascript
export function weatherFixture(input) {
  if (
    input === null ||
    typeof input !== 'object' ||
    Array.isArray(input) ||
    Object.keys(input).some((key) => key !== 'city') ||
    typeof input.city !== 'string' ||
    input.city.trim().length === 0 ||
    input.city.length > 100
  ) {
    throw new TypeError('Expected only a nonempty city string of at most 100 characters');
  }
  return {
    city: input.city.trim(),
    temperatureF: 72,
    fixture: true,
  };
}
```

A real SDK handler must connect the declared input schema to runtime validation and validate provider responses too. Registering this fixture does not turn its fixed temperature into live weather evidence.

## Database and output safety

Do not authorize SQL with `startsWith("SELECT")`, a blacklist, or a few regular expressions. SELECT expressions can invoke effectful functions, and comments, multiple statements, or other syntax defeat simplistic filters. Prefer narrowly designed operations with parameterized inputs, a least-privilege database role, appropriate read-only transactions, and a reviewed parser/allowlist where arbitrary SQL is unavoidable. Database configuration and function privileges remain part of the boundary.

Likewise, removing only `password_hash` and `api_key` is not complete sanitization. Allowlist the approved output fields, validate nested structures, bound result size, and exclude credentials and personal data not needed by the tool. Treat returned text as untrusted data.

## Secrets and operational evidence

Runtime environment substitution avoids committing literal credentials; it does not guarantee that values never appear in process diagnostics, logs, model output, or downstream systems. Document which component reads each secret and minimize its privilege and lifetime. Do not ask users to paste credentials into prompts.

Test clean-copy launch, protocol negotiation, malformed input, refusal paths, and error propagation using isolated fixtures before any separately authorized live integration. Offline compilation or a mocked tool test does not certify a provider connection or production security.

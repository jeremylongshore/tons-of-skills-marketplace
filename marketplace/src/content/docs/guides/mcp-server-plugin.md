---
title: "Building an MCP Server Plugin"
description: "Step-by-step guide to building a Model Context Protocol (MCP) server plugin for Claude Code. Covers TypeScript project setup, tool implementation, building executables, .mcp.json configuration, and testing."
section: "guides"
order: 5
keywords:
  - "MCP"
  - "Model Context Protocol"
  - "MCP server"
  - "MCP plugin"
  - "TypeScript"
  - "tool implementation"
  - "Claude Code MCP"
  - "server plugin"
officialLinks:
  - title: "Anthropic Claude Code Documentation"
    url: "https://code.claude.com/docs/en/"
  - title: "Model Context Protocol Specification"
    url: "https://modelcontextprotocol.io/"
  - title: "MCP TypeScript SDK"
    url: "https://github.com/modelcontextprotocol/typescript-sdk"
relatedDocs:
  - "concepts/mcp-servers"
  - "reference/plugin-json-schema"
---

## When to Build an MCP Server

Most Claude Code plugins are instruction plugins -- Markdown files that teach Claude how to perform tasks. MCP server plugins are fundamentally different. They provide runtime tools that Claude can call as functions during a session.

**Build an MCP server when:**

- You need to access external APIs with authentication at runtime
- You need persistent state across tool invocations (in-memory storage, database connections)
- You need to perform operations that Markdown instructions cannot express (binary data processing, cryptographic operations, real-time data feeds)
- You want to expose a reusable tool interface that multiple skills and agents can call

**Use an instruction plugin instead when:**

- The task can be accomplished by reading/writing files and running shell commands
- The knowledge is primarily "how to do X" rather than "execute X"
- You do not need runtime state or external API connections

MCP server plugins make up roughly 2% of the Tons of Skills ecosystem. They require TypeScript development, a build step, and more careful testing than instruction plugins.

## Step 1: Project Setup

### Directory Structure

MCP server plugins live in `plugins/mcp/` and follow this structure:

```
plugins/mcp/my-mcp-tool/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json                # MCP server configuration
├── src/
│   ├── index.ts            # Entry point and tool definitions
│   ├── types.ts            # TypeScript type definitions
│   └── storage.ts          # Optional: persistent storage
├── dist/
│   └── index.js            # Built output (executable)
├── package.json
├── tsconfig.json
├── README.md
└── LICENSE
```

### Initialize the Project

```bash
mkdir -p plugins/mcp/my-mcp-tool/.claude-plugin
mkdir -p plugins/mcp/my-mcp-tool/src
cd plugins/mcp/my-mcp-tool

# Initialize package.json
cat > package.json << 'EOF'
{
  "name": "@plugins/my-mcp-tool",
  "version": "1.0.0",
  "description": "An MCP server providing custom tools for Claude Code",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc && chmod +x dist/index.js",
    "dev": "tsc --watch"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0"
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "@types/node": "^22.0.0"
  }
}
EOF

# Install dependencies
pnpm install
```

### TypeScript Configuration

Create `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "node",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "declaration": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### Plugin Manifest

Create `.claude-plugin/plugin.json`:

```json
{
  "name": "my-mcp-tool",
  "version": "1.0.0",
  "description": "Custom MCP server providing specialized tools for data analysis and transformation",
  "author": "Your Name <you@example.com>",
  "repository": "https://github.com/username/my-mcp-tool",
  "license": "MIT",
  "keywords": ["mcp", "tools", "data-analysis"]
}
```

## Step 2: Implement MCP Tools

### The Entry Point

Create `src/index.ts`. This is the main file that defines your MCP server and its tools:

```typescript
#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';

// Create the MCP server
const server = new Server(
  {
    name: 'my-mcp-tool',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'analyze_json',
        description:
          'Analyze a JSON object and return statistics about its structure: key count, depth, types, and size',
        inputSchema: {
          type: 'object' as const,
          properties: {
            json_string: {
              type: 'string',
              description: 'The JSON string to analyze',
            },
          },
          required: ['json_string'],
        },
      },
      {
        name: 'transform_csv',
        description:
          'Transform CSV data: filter rows, select columns, sort, and compute aggregates',
        inputSchema: {
          type: 'object' as const,
          properties: {
            csv_data: {
              type: 'string',
              description: 'Raw CSV data as a string',
            },
            columns: {
              type: 'array',
              items: { type: 'string' },
              description: 'Columns to include in output (empty = all)',
            },
            sort_by: {
              type: 'string',
              description: 'Column name to sort by',
            },
            filter: {
              type: 'string',
              description:
                'Filter expression (e.g., "age > 30")',
            },
          },
          required: ['csv_data'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'analyze_json': {
      try {
        const data = JSON.parse(args?.json_string as string);
        const analysis = analyzeJsonStructure(data);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(analysis, null, 2),
            },
          ],
        };
      } catch (error) {
        throw new McpError(
          ErrorCode.InvalidParams,
          `Invalid JSON: ${(error as Error).message}`
        );
      }
    }

    case 'transform_csv': {
      try {
        const result = transformCsv(
          args?.csv_data as string,
          args?.columns as string[] | undefined,
          args?.sort_by as string | undefined,
          args?.filter as string | undefined
        );
        return {
          content: [
            {
              type: 'text',
              text: result,
            },
          ],
        };
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          `Transform failed: ${(error as Error).message}`
        );
      }
    }

    default:
      throw new McpError(
        ErrorCode.MethodNotFound,
        `Unknown tool: ${name}`
      );
  }
});

// Tool implementation functions

function analyzeJsonStructure(data: unknown, depth = 0): Record<string, unknown> {
  const type = Array.isArray(data) ? 'array' : typeof data;

  const result: Record<string, unknown> = {
    type,
    depth,
  };

  if (type === 'object' && data !== null) {
    const keys = Object.keys(data as Record<string, unknown>);
    result.keyCount = keys.length;
    result.keys = keys;
    result.children = {};

    for (const key of keys) {
      (result.children as Record<string, unknown>)[key] = analyzeJsonStructure(
        (data as Record<string, unknown>)[key],
        depth + 1
      );
    }
  } else if (type === 'array') {
    const arr = data as unknown[];
    result.length = arr.length;
    if (arr.length > 0) {
      result.firstElementType = typeof arr[0];
    }
  } else if (type === 'string') {
    result.length = (data as string).length;
  }

  return result;
}

function transformCsv(
  csvData: string,
  columns?: string[],
  sortBy?: string,
  filter?: string
): string {
  const lines = csvData.trim().split('\n');
  if (lines.length === 0) return '';

  const headers = lines[0].split(',').map((h) => h.trim());
  let rows = lines.slice(1).map((line) =>
    line.split(',').map((cell) => cell.trim())
  );

  // Apply filter (simple column > value comparison)
  if (filter) {
    const match = filter.match(/(\w+)\s*(>|<|=|>=|<=|!=)\s*(.+)/);
    if (match) {
      const [, col, op, val] = match;
      const colIdx = headers.indexOf(col);
      if (colIdx >= 0) {
        rows = rows.filter((row) => {
          const cellVal = parseFloat(row[colIdx]) || row[colIdx];
          const filterVal = parseFloat(val) || val;
          switch (op) {
            case '>': return cellVal > filterVal;
            case '<': return cellVal < filterVal;
            case '=': return cellVal === filterVal;
            case '>=': return cellVal >= filterVal;
            case '<=': return cellVal <= filterVal;
            case '!=': return cellVal !== filterVal;
            default: return true;
          }
        });
      }
    }
  }

  // Apply sort
  if (sortBy) {
    const sortIdx = headers.indexOf(sortBy);
    if (sortIdx >= 0) {
      rows.sort((a, b) => {
        const aVal = parseFloat(a[sortIdx]) || a[sortIdx];
        const bVal = parseFloat(b[sortIdx]) || b[sortIdx];
        if (aVal < bVal) return -1;
        if (aVal > bVal) return 1;
        return 0;
      });
    }
  }

  // Select columns
  let selectedHeaders = headers;
  let selectedRows = rows;

  if (columns && columns.length > 0) {
    const indices = columns
      .map((c) => headers.indexOf(c))
      .filter((i) => i >= 0);
    selectedHeaders = indices.map((i) => headers[i]);
    selectedRows = rows.map((row) => indices.map((i) => row[i]));
  }

  // Rebuild CSV
  const output = [selectedHeaders.join(',')];
  for (const row of selectedRows) {
    output.push(row.join(','));
  }

  return output.join('\n');
}

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('MCP server running on stdio');
}

main().catch(console.error);
```

### Type Definitions

Create `src/types.ts` for shared types:

```typescript
export interface AnalysisResult {
  type: string;
  depth: number;
  keyCount?: number;
  keys?: string[];
  length?: number;
  children?: Record<string, AnalysisResult>;
}

export interface TransformOptions {
  columns?: string[];
  sortBy?: string;
  filter?: string;
}
```

## Step 3: Build and Make Executable

MCP servers must be executable files. The build process compiles TypeScript to JavaScript and sets the executable bit.

### Build Script

The shebang line (`#!/usr/bin/env node`) at the top of `src/index.ts` tells the OS to run the file with Node.js. After compilation, make the output executable:

```bash
cd plugins/mcp/my-mcp-tool

# Build
pnpm build

# Verify the shebang is present in dist/index.js
head -1 dist/index.js
# Should output: #!/usr/bin/env node

# Verify it is executable
ls -la dist/index.js
# Should show -rwxr-xr-x permissions
```

If the shebang is stripped during compilation, add it manually to your build script in `package.json`:

```json
{
  "scripts": {
    "build": "tsc && echo '#!/usr/bin/env node' | cat - dist/index.js > dist/tmp.js && mv dist/tmp.js dist/index.js && chmod +x dist/index.js"
  }
}
```

### Verify the Build

```bash
# Test that the server starts without errors
echo '{}' | node dist/index.js 2>&1 | head -5

# The server should start and wait for stdin input
# Press Ctrl+C to stop
```

## Step 4: Create the MCP Configuration

The `.mcp.json` file tells Claude Code how to start your MCP server. Create it in the plugin root:

```json
{
  "mcpServers": {
    "my-mcp-tool": {
      "command": "node",
      "args": ["dist/index.js"],
      "cwd": "."
    }
  }
}
```

### Configuration Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `command` | The executable to run | `"node"` |
| `args` | Arguments passed to the command | `["dist/index.js"]` |
| `cwd` | Working directory (relative to plugin root) | `"."` |
| `env` | Environment variables | `{ "API_KEY": "..." }` |

### Environment Variables

If your MCP server needs API keys or configuration, reference environment variables:

```json
{
  "mcpServers": {
    "my-mcp-tool": {
      "command": "node",
      "args": ["dist/index.js"],
      "env": {
        "API_BASE_URL": "${MY_API_URL}",
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

Users set these variables in their shell environment before starting Claude Code.

## Step 5: Add Optional Components

### Instruction Files

MCP plugins can also include commands, skills, and agents alongside the server. A skill might tell Claude when and how to use your MCP tools:

```
plugins/mcp/my-mcp-tool/
├── .mcp.json
├── src/
├── dist/
├── commands/
│   └── analyze-data.md        # Command that uses MCP tools
└── skills/
    └── data-analysis/
        └── SKILL.md           # Skill that auto-activates for data tasks
```

The skill can reference MCP tools in its instructions:

```markdown
## Instructions

1. When the user provides data for analysis, use the `analyze_json`
   MCP tool for JSON data and the `transform_csv` MCP tool for CSV data
2. Present the results in a readable format
```

### Persistent Storage

If your MCP server needs to store state between invocations, use `${CLAUDE_PLUGIN_DATA}` for the storage path. This directory survives plugin updates and reinstalls.

Create `src/storage.ts`:

```typescript
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

export class Storage {
  private dataDir: string;

  constructor() {
    this.dataDir = process.env.CLAUDE_PLUGIN_DATA || './data';
    if (!existsSync(this.dataDir)) {
      mkdirSync(this.dataDir, { recursive: true });
    }
  }

  get(key: string): unknown | null {
    const filePath = join(this.dataDir, `${key}.json`);
    if (!existsSync(filePath)) return null;
    return JSON.parse(readFileSync(filePath, 'utf-8'));
  }

  set(key: string, value: unknown): void {
    const filePath = join(this.dataDir, `${key}.json`);
    writeFileSync(filePath, JSON.stringify(value, null, 2));
  }
}
```

## Step 6: Testing

### Unit Testing

Add Vitest for unit tests:

```bash
pnpm add -D vitest
```

Create a test file:

```typescript
// src/index.test.ts
import { describe, it, expect } from 'vitest';

describe('analyzeJsonStructure', () => {
  it('analyzes a flat object', () => {
    const data = { name: 'test', age: 30 };
    const result = analyzeJsonStructure(data);
    expect(result.type).toBe('object');
    expect(result.keyCount).toBe(2);
    expect(result.keys).toContain('name');
  });

  it('analyzes nested objects', () => {
    const data = { user: { name: 'test', address: { city: 'NYC' } } };
    const result = analyzeJsonStructure(data);
    expect(result.depth).toBe(0);
  });
});

describe('transformCsv', () => {
  const csv = 'name,age,city\nAlice,30,NYC\nBob,25,LA\nCarol,35,Chicago';

  it('selects specific columns', () => {
    const result = transformCsv(csv, ['name', 'city']);
    expect(result).toContain('name,city');
    expect(result).not.toContain('age');
  });

  it('filters rows', () => {
    const result = transformCsv(csv, undefined, undefined, 'age > 28');
    expect(result).toContain('Alice');
    expect(result).toContain('Carol');
    expect(result).not.toContain('Bob');
  });

  it('sorts by column', () => {
    const result = transformCsv(csv, undefined, 'age');
    const lines = result.split('\n');
    expect(lines[1]).toContain('Bob');   // age 25
    expect(lines[3]).toContain('Carol'); // age 35
  });
});
```

### Integration Testing

Test the full MCP server by sending JSON-RPC messages via stdin:

```bash
# List available tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node dist/index.js 2>/dev/null

# Call a tool
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"analyze_json","arguments":{"json_string":"{\"key\":\"value\"}"}}}' | node dist/index.js 2>/dev/null
```

### Validation

Run the plugin validator:

```bash
python3 scripts/validate-skills-schema.py --enterprise --verbose \
  plugins/mcp/my-mcp-tool/
```

## Common Patterns

### Error Handling

Always use `McpError` with appropriate error codes:

```typescript
import { ErrorCode, McpError } from '@modelcontextprotocol/sdk/types.js';

// Invalid input from the user
throw new McpError(ErrorCode.InvalidParams, 'Missing required field: name');

// Tool not found
throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);

// Internal server error
throw new McpError(ErrorCode.InternalError, `Database connection failed`);
```

### Rate Limiting

If your MCP server calls external APIs, implement rate limiting:

```typescript
class RateLimiter {
  private timestamps: number[] = [];
  private maxRequests: number;
  private windowMs: number;

  constructor(maxRequests: number, windowMs: number) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
  }

  async acquire(): Promise<void> {
    const now = Date.now();
    this.timestamps = this.timestamps.filter(
      (t) => now - t < this.windowMs
    );

    if (this.timestamps.length >= this.maxRequests) {
      const waitTime = this.timestamps[0] + this.windowMs - now;
      await new Promise((resolve) => setTimeout(resolve, waitTime));
    }

    this.timestamps.push(Date.now());
  }
}
```

### Logging

Write diagnostic logs to stderr (not stdout, which is the MCP transport):

```typescript
console.error('[my-mcp-tool] Starting server...');
console.error(`[my-mcp-tool] Tool called: ${name}`);
```

## Checklist Before Publishing

Before submitting your MCP server plugin, verify:

- [ ] `dist/index.js` has the `#!/usr/bin/env node` shebang on line 1
- [ ] `dist/index.js` has executable permissions (`chmod +x`)
- [ ] `.mcp.json` is present with valid server configuration
- [ ] `plugin.json` contains only allowed fields
- [ ] All tools have descriptive names and complete input schemas
- [ ] Error cases return `McpError` with appropriate codes
- [ ] Unit tests pass (`pnpm test`)
- [ ] Integration test via stdin/stdout works
- [ ] `README.md` documents all available tools
- [ ] No secrets or API keys in the source code
- [ ] Enterprise validation passes at B grade or higher

## Next Steps

- [Build a complete plugin](/docs/guides/build-a-plugin) with commands, skills, and your MCP server
- [Publish to the marketplace](/docs/guides/publish-to-marketplace)
- Explore existing MCP plugins on the [marketplace](/explore) for patterns and inspiration

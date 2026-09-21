---
title: "MCP Servers in Claude Code Plugins"
description: "How Model Context Protocol (MCP) servers work in Claude Code plugins — building TypeScript MCP servers that expose external tools, data sources, and APIs to Claude through a standardized protocol."
section: "concepts"
order: 5
keywords:
  - "MCP server"
  - "Model Context Protocol"
  - "Claude Code MCP"
  - "MCP tools"
  - "TypeScript MCP server"
  - "mcp.json"
  - "Claude Code external tools"
  - "MCP plugin"
officialLinks:
  - title: "Model Context Protocol Specification"
    url: "https://modelcontextprotocol.io"
  - title: "Claude Code MCP Documentation"
    url: "https://code.claude.com/docs/en/mcp"
  - title: "MCP TypeScript SDK"
    url: "https://github.com/modelcontextprotocol/typescript-sdk"
relatedDocs:
  - "concepts/plugins"
  - "concepts/skills"
  - "concepts/agents"
---

Most Claude Code plugins are AI instruction plugins -- collections of markdown files that teach Claude new behaviors through carefully written instructions. MCP server plugins are different. They are executable TypeScript applications that give Claude access to external systems, APIs, and data sources through a standardized protocol called the Model Context Protocol.

Where an instruction plugin says "here is how to think about Kubernetes," an MCP server plugin says "here is a live connection to the Kubernetes API -- query pods, read logs, apply manifests." The distinction is between knowledge and access.

## What Is the Model Context Protocol?

The Model Context Protocol (MCP) is an open standard that defines how AI applications communicate with external tool servers. It provides a structured way for an AI model to:

- **Discover** what tools are available on a server
- **Understand** each tool's parameters, types, and behavior
- **Invoke** tools with validated inputs
- **Receive** structured results

MCP follows a client-server architecture. Claude Code acts as the MCP client, and your plugin runs an MCP server. The client discovers the server's capabilities at startup, then invokes tools as needed during conversation.

The protocol handles serialization, transport, error handling, and capability negotiation -- so you can focus on implementing the tools themselves rather than the communication layer.

### How MCP Fits Into Claude Code

Claude Code has a set of built-in tools: `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `WebFetch`, `WebSearch`, `Task`, `TodoWrite`, `NotebookEdit`, `AskUserQuestion`, and `Skill`. These cover general-purpose development tasks.

MCP servers extend this tool set with domain-specific capabilities. When an MCP server is running, its tools appear alongside the built-in tools. Claude can call them in the same way -- seamlessly mixing built-in file operations with, say, a database query tool or a Jira ticket creator.

From Claude's perspective, an MCP tool is just another tool. The protocol abstraction means Claude does not need to know whether a tool is built-in or provided by an MCP server. It sees the tool's name, description, and parameter schema, and invokes it accordingly.

## MCP Server Plugin Structure

An MCP server plugin follows this directory layout:

```
my-mcp-plugin/
├── .claude-plugin/
│   └── plugin.json           # Standard plugin manifest
├── src/
│   └── index.ts              # TypeScript source code
├── dist/
│   └── index.js              # Compiled JavaScript (must be executable)
├── package.json              # Dependencies and build scripts
├── tsconfig.json             # TypeScript configuration
├── .mcp.json                 # MCP server configuration
└── README.md                 # Documentation
```

### plugin.json

The plugin manifest follows the same schema as any Claude Code plugin:

```json
{
  "name": "database-explorer",
  "version": "1.0.0",
  "description": "Query and explore SQL databases directly from Claude Code",
  "author": "Data Team <data@example.com>",
  "repository": "https://github.com/example/database-explorer",
  "license": "MIT",
  "keywords": ["database", "sql", "mcp", "query"]
}
```

### .mcp.json

The `.mcp.json` file configures how Claude Code launches and connects to the MCP server:

```json
{
  "mcpServers": {
    "database-explorer": {
      "command": "node",
      "args": ["dist/index.js"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

| Field | Description |
|-------|-------------|
| `command` | The executable to run (typically `node`) |
| `args` | Command-line arguments (path to the compiled entry point) |
| `env` | Environment variables to pass to the server process |

Environment variables in `.mcp.json` can reference the user's shell environment using `${VARIABLE_NAME}` syntax. This allows configuration like database URLs and API keys to be provided at runtime without hardcoding them in the plugin.

### src/index.ts

The TypeScript source file implements the MCP server. It uses the `@modelcontextprotocol/sdk` package to define tools, handle requests, and manage the server lifecycle.

Here is a minimal but complete MCP server that provides a single tool:

```typescript
#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  { name: "example-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// Register available tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "get_weather",
      description: "Get current weather for a city",
      inputSchema: {
        type: "object" as const,
        properties: {
          city: {
            type: "string",
            description: "City name (e.g., 'San Francisco')",
          },
        },
        required: ["city"],
      },
    },
  ],
}));

// Handle tool invocations
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "get_weather") {
    const city = request.params.arguments?.city as string;

    // In a real implementation, call a weather API here
    return {
      content: [
        {
          type: "text",
          text: `Weather in ${city}: 72°F, partly cloudy`,
        },
      ],
    };
  }

  throw new Error(`Unknown tool: ${request.params.name}`);
});

// Start the server
const transport = new StdioServerTransport();
await server.connect(transport);
```

### dist/index.js

The compiled JavaScript entry point must meet two requirements:

1. **Shebang line.** The file must start with `#!/usr/bin/env node` so it can be executed directly.

2. **Executable permissions.** The file must have the execute bit set (`chmod +x dist/index.js`).

These requirements exist because Claude Code launches MCP servers as child processes. Without the shebang and execute permission, the operating system cannot run the file directly.

After compiling, always set the permissions:

```bash
npx tsc
chmod +x dist/index.js
```

Or automate this in your `package.json`:

```json
{
  "scripts": {
    "build": "tsc && chmod +x dist/index.js",
    "dev": "tsc --watch"
  }
}
```

### package.json

A typical `package.json` for an MCP server plugin:

```json
{
  "name": "database-explorer",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "build": "tsc && chmod +x dist/index.js",
    "dev": "tsc --watch",
    "test": "vitest"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vitest": "^1.0.0"
  }
}
```

Note `"type": "module"` -- the MCP SDK uses ESM imports, so your project must be configured for ES modules.

## Designing MCP Tools

The tools you expose through your MCP server are the interface between Claude and your external system. Well-designed tools make Claude more effective; poorly designed ones lead to confusion and errors.

### Tool Anatomy

Each tool has three components:

| Component | Purpose |
|-----------|---------|
| `name` | Identifier Claude uses to invoke the tool (snake_case) |
| `description` | Natural language explanation of what the tool does |
| `inputSchema` | JSON Schema defining the tool's parameters |

### Writing Good Tool Descriptions

Tool descriptions are critical because Claude uses them to decide when and how to invoke the tool. The description should answer:

- What does this tool do?
- When should Claude use it?
- What are the important constraints or side effects?

```typescript
// Good: specific, actionable, mentions constraints
{
  name: "query_database",
  description: "Execute a read-only SQL query against the connected database. Returns up to 100 rows. Use for data exploration and analysis. Does not support INSERT, UPDATE, DELETE, or DDL statements.",
  inputSchema: { /* ... */ }
}

// Poor: vague, no constraints mentioned
{
  name: "query_database",
  description: "Run a database query",
  inputSchema: { /* ... */ }
}
```

### Input Schema Design

Define precise JSON Schemas for tool parameters. Include `description` fields on every property and use `required` to mark mandatory parameters:

```typescript
inputSchema: {
  type: "object" as const,
  properties: {
    query: {
      type: "string",
      description: "SQL SELECT query to execute. Must be a read-only query.",
    },
    database: {
      type: "string",
      description: "Target database name. Defaults to the primary database.",
      default: "main",
    },
    limit: {
      type: "number",
      description: "Maximum number of rows to return (1-1000).",
      default: 100,
      minimum: 1,
      maximum: 1000,
    },
  },
  required: ["query"],
}
```

### Tool Categories

MCP tools generally fall into four categories:

**Query tools** retrieve information without side effects:

```typescript
{
  name: "list_tables",
  description: "List all tables in the database with their column counts and row counts",
}
```

**Action tools** perform operations with side effects:

```typescript
{
  name: "create_ticket",
  description: "Create a new Jira ticket in the specified project. Returns the ticket ID.",
}
```

**Analysis tools** process data and return insights:

```typescript
{
  name: "explain_query",
  description: "Analyze a SQL query's execution plan and suggest optimizations",
}
```

**Configuration tools** modify settings or state:

```typescript
{
  name: "set_connection",
  description: "Switch the active database connection to a different server",
}
```

## Building an MCP Server Step by Step

### Step 1: Initialize the Project

```bash
mkdir my-mcp-plugin
cd my-mcp-plugin
npm init -y
npm install @modelcontextprotocol/sdk
npm install -D typescript vitest
```

### Step 2: Configure TypeScript

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
    "esModuleInterop": true,
    "declaration": true
  },
  "include": ["src/**/*"]
}
```

### Step 3: Implement the Server

Create `src/index.ts` with your tool definitions and handlers. Follow the pattern shown in the source code example above.

### Step 4: Build and Set Permissions

```bash
npx tsc
chmod +x dist/index.js
```

### Step 5: Create the Plugin Manifest

Create `.claude-plugin/plugin.json` and `.mcp.json` as described above.

### Step 6: Test Locally

Build the plugin and verify the server starts:

```bash
cd plugins/mcp/my-mcp-plugin/
pnpm build
node dist/index.js
```

The server should start without errors and wait for input on stdin (since it uses the stdio transport).

## Transport Mechanisms

MCP supports two transport mechanisms for communication between the client (Claude Code) and the server (your plugin):

### stdio (Standard I/O)

The default and most common transport. Claude Code launches the server as a child process and communicates through stdin/stdout:

```typescript
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const transport = new StdioServerTransport();
await server.connect(transport);
```

**Advantages:** Simple, no network configuration, works in sandboxed environments.
**Limitations:** Server lifecycle is tied to the Claude Code process.

### SSE (Server-Sent Events)

For servers that run independently (e.g., a shared team server or a remote service):

```typescript
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";

const transport = new SSEServerTransport("/messages", response);
await server.connect(transport);
```

**Advantages:** Server can run independently, shared across users, remote hosting.
**Limitations:** Requires network access, more complex deployment.

For most Claude Code plugins, stdio is the right choice. SSE is appropriate when you need a shared server that multiple team members connect to, or when the server needs to maintain long-lived connections to external services.

## Error Handling

Robust error handling is essential for MCP servers. When a tool call fails, Claude needs a clear error message to understand what went wrong and how to proceed.

### Returning Errors

Return errors as text content with the `isError` flag:

```typescript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const result = await executeQuery(request.params.arguments?.query);
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `Query failed: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
      isError: true,
    };
  }
});
```

### Common Error Patterns

**Connection errors:** When the external service is unavailable:

```typescript
if (!connection) {
  return {
    content: [{
      type: "text",
      text: "Database connection not established. Set DATABASE_URL environment variable and restart Claude Code.",
    }],
    isError: true,
  };
}
```

**Validation errors:** When the input is invalid:

```typescript
if (!query.trim().toUpperCase().startsWith("SELECT")) {
  return {
    content: [{
      type: "text",
      text: "Only SELECT queries are allowed. This tool does not support INSERT, UPDATE, DELETE, or DDL statements.",
    }],
    isError: true,
  };
}
```

**Rate limiting:** When the external API throttles requests:

```typescript
if (response.status === 429) {
  const retryAfter = response.headers.get("retry-after") || "60";
  return {
    content: [{
      type: "text",
      text: `Rate limited by external API. Retry after ${retryAfter} seconds.`,
    }],
    isError: true,
  };
}
```

## Security Considerations

MCP servers have real-world impact -- they connect to databases, APIs, and services. Security must be a first-class concern.

### Principle of Least Privilege

Grant the MCP server only the permissions it needs:

- Database tools should use read-only database users when possible
- API integrations should use scoped tokens with minimal permissions
- File system access should be limited to specific directories

### Input Validation

Never trust inputs from Claude directly. Validate and sanitize all parameters:

```typescript
// Validate query is read-only
const normalized = query.trim().toUpperCase();
if (normalized.startsWith("DROP") || normalized.startsWith("DELETE") ||
    normalized.startsWith("INSERT") || normalized.startsWith("UPDATE") ||
    normalized.startsWith("ALTER") || normalized.startsWith("CREATE")) {
  throw new Error("Only read-only queries are permitted");
}
```

### Secret Management

Never hardcode secrets in your MCP server. Use environment variables configured in `.mcp.json`:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["dist/index.js"],
      "env": {
        "API_KEY": "${MY_SERVICE_API_KEY}",
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

Users set these environment variables in their shell profile. The values never appear in the plugin source code.

### Output Sanitization

Be careful about what your tools return. Avoid leaking sensitive data in tool responses:

```typescript
// Strip sensitive columns before returning
const sanitized = results.map(row => {
  const { password_hash, api_key, ...safe } = row;
  return safe;
});
```

## MCP Servers in the Marketplace

The [Tons of Skills marketplace](/) hosts MCP server plugins alongside AI instruction plugins. MCP plugins are identified by the `mcp` category in the [Explore](/explore) page.

When publishing an MCP server plugin to the marketplace:

- Ensure the compiled `dist/index.js` is included and has the correct permissions
- Document all required environment variables in the README
- List all exposed tools with their descriptions and parameter schemas
- Include a test suite (vitest) that covers the core tool logic
- Follow the `plugin.json` schema strictly -- no extra fields

The marketplace CI pipeline validates MCP plugins by running `pnpm build` and executing the test suite. Build failures or test failures block publishing.

## Consuming MCP Servers

From the user's perspective, consuming an MCP server plugin is transparent. After installation, the server's tools are available alongside Claude's built-in tools. Users do not need to know which tools come from MCP servers versus which are built-in.

However, MCP tools can be referenced in skill and agent configurations:

### In Skills (allowed-tools)

```yaml
allowed-tools: Read, Glob, mcp__database-explorer__query_database
```

MCP tools use the naming convention `mcp__<server-name>__<tool-name>` when referenced in `allowed-tools`.

### In Agents (disallowedTools)

```yaml
disallowedTools:
  - "mcp__database-explorer__query_database"
  - "mcp__slack__send_message"
```

This allows fine-grained control over which MCP tools an agent or skill can access.

## Next Steps

- Learn about the plugin system that hosts MCP servers: [What Are Claude Code Plugins?](/docs/concepts/plugins)
- Understand skills that can reference MCP tools: [Understanding Agent Skills (SKILL.md)](/docs/concepts/skills)
- See how agents can use or restrict MCP tools: [Claude Code Agents and Subagents](/docs/concepts/agents)
- Browse MCP server plugins: [Explore Plugins](/explore)

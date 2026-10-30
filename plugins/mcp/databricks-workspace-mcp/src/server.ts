/**
 * MCP server factory. Registers all control-plane tools on a low-level `Server` (the same
 * pattern the repo's design-to-code MCP uses) so the identical instance can be driven by either
 * the stdio transport (CLI) or the Streamable HTTP transport (Databricks App mode).
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  type Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import type { DatabricksClient } from "./client.js";
import { toStructuredError } from "./errors.js";
import { allTools, toolsByName } from "./tools/index.js";

export const SERVER_NAME = "databricks-workspace-mcp";
export const SERVER_VERSION = "0.1.0";

export interface ToolCallResult {
  content: Array<{ type: "text"; text: string }>;
  isError?: boolean;
}

/**
 * A client provider. Returns a ready client or throws a structured `DatabricksError` (e.g. when
 * credentials are missing). Resolving lazily lets `tools/list` succeed even on an unconfigured
 * workspace — the agent sees the 8 tools and gets a clean auth error only when it actually calls
 * one (013-AT-ADEC: "report cleanly rather than failing mid-flow").
 */
export type ClientProvider = () => DatabricksClient;

/**
 * Pure tool-dispatch: resolve the client, validate args against the tool's zod schema, run the
 * handler, and return the MCP content envelope. Exposed separately so tests exercise the full
 * call path (auth → validation → handler → error normalization) without standing up a transport.
 */
export async function callTool(
  getClient: ClientProvider,
  name: string,
  args: unknown,
): Promise<ToolCallResult> {
  const tool = toolsByName.get(name);
  if (!tool) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ error: { kind: "config", message: `Unknown tool: ${name}` } }, null, 2),
        },
      ],
      isError: true,
    };
  }
  const parsed = tool.schema.safeParse(args ?? {});
  if (!parsed.success) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { error: { kind: "config", message: "Invalid arguments", issues: parsed.error.issues } },
            null,
            2,
          ),
        },
      ],
      isError: true,
    };
  }
  try {
    const client = getClient();
    const result = await tool.handler(client, parsed.data);
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    return {
      content: [{ type: "text", text: JSON.stringify({ error: toStructuredError(err) }, null, 2) }],
      isError: true,
    };
  }
}

export function createServer(getClient: ClientProvider): Server {
  const server = new Server(
    { name: SERVER_NAME, version: SERVER_VERSION },
    { capabilities: { tools: {} } },
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: allTools.map((t) => ({
      name: t.name,
      description: t.description,
      // Publish the input view so defaulted arguments remain optional for MCP clients.
      inputSchema: z.toJSONSchema(t.schema, { target: "draft-07", io: "input" }) as Tool["inputSchema"],
    })),
  }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    // ToolCallResult is a structural CallToolResult; cast past the SDK's task-augmented union.
    return (await callTool(getClient, name, args)) as never;
  });

  return server;
}

#!/usr/bin/env node
/**
 * databricks-workspace-mcp — Databricks App entry (T13).
 *
 * Same tool set, served over Streamable HTTP so the server can be deployed as a Databricks App
 * (`mcp-databricks-workspace`), making it discoverable by the Mosaic AI Agent Framework + AI
 * Playground in addition to Claude Code. Deployment mode is forced to "app", which means OAuth
 * M2M only — PAT is rejected at auth resolution (013-AT-ADEC Finding 5).
 *
 * Run with: `node dist/app.js` (Databricks App start command). Binds DATABRICKS_APP_PORT.
 */

import http from "node:http";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { createServer, SERVER_NAME, SERVER_VERSION } from "./server.js";
import { makeClientProvider, probeAuth } from "./runtime.js";

const PORT = Number(process.env.DATABRICKS_APP_PORT ?? process.env.PORT ?? 8000);
const MCP_PATH = "/mcp";

function readBody(req: http.IncomingMessage): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (c: Buffer) => chunks.push(c));
    req.on("end", () => {
      const raw = Buffer.concat(chunks).toString("utf8");
      if (!raw) return resolve(undefined);
      try {
        resolve(JSON.parse(raw));
      } catch (err) {
        reject(err);
      }
    });
    req.on("error", reject);
  });
}

export function createHttpServer(): http.Server {
  // Force App deployment mode -> OAuth M2M only.
  const getClient = makeClientProvider({ deployment: "app" });

  return http.createServer(async (req, res) => {
    try {
      const path = (req.url ?? "").split("?")[0];

      if (req.method === "GET" && (path === "/healthz" || path === "/")) {
        res.writeHead(200, { "content-type": "application/json" });
        res.end(JSON.stringify({ status: "ok", server: SERVER_NAME, version: SERVER_VERSION }));
        return;
      }

      if (path !== MCP_PATH) {
        res.writeHead(404, { "content-type": "application/json" });
        res.end(JSON.stringify({ error: `Not found. MCP endpoint is ${MCP_PATH}` }));
        return;
      }

      const body = req.method === "POST" ? await readBody(req) : undefined;

      // Stateless: a fresh transport + server per request avoids cross-request id collisions.
      const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: undefined,
        enableJsonResponse: true,
      });
      const server = createServer(getClient);
      res.on("close", () => {
        void transport.close();
        void server.close();
      });
      await server.connect(transport);
      await transport.handleRequest(req, res, body);
    } catch (err) {
      // Log full detail server-side only; never return stack-trace/error-message
      // internals to the HTTP client (CodeQL js/stack-trace-exposure).
      console.error(`${SERVER_NAME} request error:`, err);
      if (!res.headersSent) res.writeHead(500, { "content-type": "application/json" });
      res.end(JSON.stringify({ error: "Internal server error" }));
    }
  });
}

function main(): void {
  const httpServer = createHttpServer();
  httpServer.listen(PORT, () => {
    const auth = probeAuth({ deployment: "app" });
    console.error(
      `${SERVER_NAME} v${SERVER_VERSION} (App mode) on :${PORT}${MCP_PATH} — ${
        auth ? `${auth.provider.mode} auth -> ${auth.host}` : "UNCONFIGURED (set DATABRICKS_CLIENT_ID + DATABRICKS_CLIENT_SECRET)"
      }`,
    );
  });
}

// Only auto-start when run directly (not when imported by tests).
if (process.argv[1] && process.argv[1].endsWith("app.js")) {
  main();
}

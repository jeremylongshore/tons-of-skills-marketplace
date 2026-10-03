import { describe, expect, it, afterEach } from "vitest";
import http from "node:http";
import type { AddressInfo } from "node:net";
import { createHttpServer } from "../src/app.js";

/**
 * CodeQL js/stack-trace-exposure: the request handler's catch block used to
 * return `err.message` (and implicitly stack-trace-adjacent detail) straight
 * to the HTTP client. It must now always return a generic message, with
 * detail going to the server log instead.
 */
describe("createHttpServer — error responses never leak internals", () => {
  let server: http.Server | undefined;

  afterEach(() => {
    server?.close();
    server = undefined;
  });

  function listen(): Promise<number> {
    return new Promise((resolve) => {
      server = createHttpServer();
      server.listen(0, () => resolve((server!.address() as AddressInfo).port));
    });
  }

  function post(port: number, path: string, body: string): Promise<{ status: number; body: string }> {
    return new Promise((resolve, reject) => {
      const req = http.request(
        { host: "127.0.0.1", port, path, method: "POST", headers: { "content-type": "application/json" } },
        (res) => {
          const chunks: Buffer[] = [];
          res.on("data", (c) => chunks.push(c));
          res.on("end", () =>
            resolve({ status: res.statusCode ?? 0, body: Buffer.concat(chunks).toString("utf8") }),
          );
        },
      );
      req.on("error", reject);
      req.end(body);
    });
  }

  it("returns a generic 500 body for a malformed JSON request, never the parse error detail", async () => {
    const port = await listen();
    const { status, body } = await post(port, "/mcp", "{not valid json");
    expect(status).toBe(500);
    const parsed = JSON.parse(body);
    expect(parsed).toEqual({ error: "Internal server error" });
    // The underlying JSON.parse error message ("Unexpected token ...") must
    // never reach the client.
    expect(body).not.toMatch(/unexpected token/i);
    expect(body).not.toMatch(/at JSON\.parse/i);
  });
});

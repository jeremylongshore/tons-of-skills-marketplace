import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, it } from 'vitest';

it('publishes OpenAPI inputs accepted by the MCP client and calls the real handler', async () => {
  const cwd = await mkdtemp(join(tmpdir(), 'api-debugger-protocol-'));
  const filePath = join(cwd, 'fixture.json');
  await writeFile(filePath, JSON.stringify({
    openapi: '3.0.0', info: { title: 'fixture', version: '1.0.0' },
    paths: { '/health': { get: { responses: { '200': { description: 'OK' } } } } },
  }));
  const client = new Client({ name: 'protocol-fixture', version: '1.0.0' });
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [fileURLToPath(new URL('../dist/servers/api-debugger.js', import.meta.url))],
    cwd,
    stderr: 'pipe',
  });
  try {
    await client.connect(transport);
    const { tools } = await client.listTools();
    expect(tools).toHaveLength(4);
    for (const tool of tools) expect(tool.inputSchema.type).toBe('object');
    const load = tools.find(tool => tool.name === 'load_openapi')!;
    expect(load.inputSchema).toMatchObject({ properties: { filePath: { type: 'string' } } });
    expect(load.inputSchema.required).toContain('filePath');
    expect(load.inputSchema.required ?? []).not.toContain('name');
    const result = await client.callTool({ name: 'load_openapi', arguments: { filePath } });
    expect(result.isError).not.toBe(true);
    const content = Array.isArray(result.content) ? result.content.find(block => block.type === 'text') : undefined;
    if (!content || typeof content.text !== 'string') throw new Error('missing OpenAPI response');
    expect(JSON.parse(content.text)).toMatchObject({ loaded: true, endpoints: 1 });
  } finally {
    await client.close();
    await rm(cwd, { recursive: true });
  }
}, 10_000);

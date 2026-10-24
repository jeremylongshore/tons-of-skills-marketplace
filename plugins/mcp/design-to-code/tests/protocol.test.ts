import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, it } from 'vitest';

it('publishes valid tool inputs and preserves optional defaults through MCP', async () => {
  const cwd = await mkdtemp(join(tmpdir(), 'design-protocol-'));
  const client = new Client({ name: 'protocol-fixture', version: '1.0.0' });
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [fileURLToPath(new URL('../dist/servers/design-converter.js', import.meta.url))],
    cwd,
    stderr: 'pipe',
  });
  try {
    await client.connect(transport);
    const { tools } = await client.listTools();
    expect(tools).toHaveLength(3);
    for (const tool of tools) expect(tool.inputSchema.type).toBe('object');
    const parse = tools.find(tool => tool.name === 'parse_figma')!;
    expect(parse.inputSchema).toMatchObject({
      properties: { json: { type: 'string' }, framework: { default: 'react' } },
    });
    expect(parse.inputSchema.required).toContain('json');
    expect(parse.inputSchema.required ?? []).not.toContain('framework');
    const result = await client.callTool({
      name: 'parse_figma',
      arguments: { json: JSON.stringify({ name: 'FixturePanel', type: 'FRAME' }) },
    });
    expect(result.isError).not.toBe(true);
    expect(JSON.stringify(result.content)).toContain('FixturePanel');
    const invalid = await client.callTool({ name: 'parse_figma', arguments: { json: '{invalid' } });
    expect(invalid.isError).toBe(true);
  } finally {
    await client.close();
    await rm(cwd, { recursive: true });
  }
}, 10_000);

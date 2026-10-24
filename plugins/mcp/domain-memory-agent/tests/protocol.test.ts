import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, it } from 'vitest';

it('publishes document inputs and leaves defaulted list arguments optional', async () => {
  const cwd = await mkdtemp(join(tmpdir(), 'memory-protocol-'));
  const client = new Client({ name: 'protocol-fixture', version: '1.0.0' });
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [fileURLToPath(new URL('../dist/servers/knowledge-base.js', import.meta.url))],
    cwd,
    stderr: 'pipe',
  });
  try {
    await client.connect(transport);
    const { tools } = await client.listTools();
    expect(tools).toHaveLength(6);
    for (const tool of tools) expect(tool.inputSchema.type).toBe('object');
    const list = tools.find(tool => tool.name === 'list_documents')!;
    expect(list.inputSchema).toMatchObject({ properties: { limit: { default: 50 }, offset: { default: 0 } } });
    expect(list.inputSchema.required ?? []).not.toContain('limit');
    expect(list.inputSchema.required ?? []).not.toContain('offset');
    const result = await client.callTool({ name: 'list_documents', arguments: {} });
    expect(result.isError).not.toBe(true);
    const content = Array.isArray(result.content) ? result.content.find(block => block.type === 'text') : undefined;
    if (!content || typeof content.text !== 'string') throw new Error('missing document response');
    expect(JSON.parse(content.text)).toMatchObject({ total: 0, showing: 0, documents: [] });
  } finally {
    await client.close();
    await rm(cwd, { recursive: true });
  }
}, 10_000);

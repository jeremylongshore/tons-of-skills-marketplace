import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, it } from 'vitest';

it('publishes usable workflow inputs without requiring defaulted arguments', async () => {
  const cwd = await mkdtemp(join(tmpdir(), 'workflow-protocol-'));
  const client = new Client({ name: 'protocol-fixture', version: '1.0.0' });
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [fileURLToPath(new URL('../dist/servers/workflow-engine.js', import.meta.url))],
    cwd,
    stderr: 'pipe',
  });
  try {
    await client.connect(transport);
    const { tools } = await client.listTools();
    expect(tools).toHaveLength(4);
    for (const tool of tools) expect(tool.inputSchema.type).toBe('object');
    const execute = tools.find(tool => tool.name === 'execute_workflow')!;
    expect(execute.inputSchema).toMatchObject({ properties: { parallel: { default: true } } });
    expect(execute.inputSchema.required).toContain('workflowId');
    expect(execute.inputSchema.required ?? []).not.toContain('parallel');
    const created = await client.callTool({ name: 'create_workflow', arguments: { name: 'fixture', tasks: [] } });
    expect(created.isError).not.toBe(true);
    const listed = await client.callTool({ name: 'list_workflows', arguments: {} });
    expect(listed.isError).not.toBe(true);
    const content = Array.isArray(listed.content) ? listed.content.find(block => block.type === 'text') : undefined;
    if (!content || typeof content.text !== 'string') throw new Error('missing workflow response');
    expect(JSON.parse(content.text).total).toBe(1);
  } finally {
    await client.close();
    await rm(cwd, { recursive: true });
  }
}, 10_000);

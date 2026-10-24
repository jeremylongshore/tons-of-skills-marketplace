import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { InMemoryTransport } from '@modelcontextprotocol/sdk/inMemory.js';
import { expect, it, vi } from 'vitest';
import { createServer } from '../src/server.js';

it('publishes all eight tool schemas without initializing a provider', async () => {
  const getClient = vi.fn(() => { throw new Error('provider initialization forbidden in this fixture'); });
  const server = createServer(getClient);
  const client = new Client({ name: 'protocol-fixture', version: '1.0.0' });
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  try {
    await server.connect(serverTransport);
    await client.connect(clientTransport);
    const { tools } = await client.listTools();
    expect(tools).toHaveLength(8);
    for (const tool of tools) expect(tool.inputSchema.type).toBe('object');
    const events = tools.find(tool => tool.name === 'clusters_events')!;
    expect(events.inputSchema).toMatchObject({
      properties: { cluster_id: { type: 'string' }, limit: { minimum: 1, maximum: 500 } },
    });
    expect(events.inputSchema.required).toContain('cluster_id');
    expect(events.inputSchema.required ?? []).not.toContain('limit');
    const invalid = await client.callTool({ name: 'clusters_events', arguments: { cluster_id: 'fixture', limit: 501 } });
    expect(invalid.isError).toBe(true);
    expect(getClient).not.toHaveBeenCalled();
  } finally {
    await client.close();
    await server.close();
  }
});

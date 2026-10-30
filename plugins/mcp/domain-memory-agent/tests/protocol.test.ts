import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, it } from 'vitest';

async function withClient(run: (client: Client) => Promise<void>) {
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
    await run(client);
  } finally {
    await client.close();
    await rm(cwd, { recursive: true });
  }
}

function textResult(result: Awaited<ReturnType<Client['callTool']>>) {
  expect(result.isError).not.toBe(true);
  const content = Array.isArray(result.content) ? result.content.find(block => block.type === 'text') : undefined;
  if (!content || typeof content.text !== 'string') throw new Error('missing document response');
  return { text: content.text, value: JSON.parse(content.text) };
}

it('publishes document inputs and leaves defaulted list arguments optional', async () => {
  await withClient(async client => {
    const { tools } = await client.listTools();
    expect(tools).toHaveLength(6);
    for (const tool of tools) expect(tool.inputSchema.type).toBe('object');
    const list = tools.find(tool => tool.name === 'list_documents')!;
    expect(list.inputSchema).toMatchObject({ properties: { limit: { default: 50 }, offset: { default: 0 } } });
    expect(list.inputSchema.required ?? []).not.toContain('limit');
    expect(list.inputSchema.required ?? []).not.toContain('offset');
    const result = await client.callTool({ name: 'list_documents', arguments: {} });
    expect(textResult(result).value).toMatchObject({ total: 0, showing: 0, documents: [] });
  });
}, 10_000);

it('validates page inputs and makes every matching document reachable through real tools', async () => {
  await withClient(async client => {
    const { tools } = await client.listTools();
    for (const [name, defaultLimit] of [['list_documents', 50], ['semantic_search', 10]] as const) {
      const tool = tools.find(entry => entry.name === name)!;
      expect(tool.inputSchema).toMatchObject({ properties: {
        limit: { type: 'integer', minimum: 1, maximum: 100, default: defaultLimit },
        offset: { type: 'integer', minimum: 0, default: 0 },
      } });
      expect(tool.inputSchema.required ?? []).not.toContain('limit');
      expect(tool.inputSchema.required ?? []).not.toContain('offset');
    }

    const ids = Array.from({ length: 120 }, (_, index) => 'fixture-' + String(index).padStart(3, '0'));
    for (const id of ids) {
      textResult(await client.callTool({ name: 'store_document', arguments: {
        id, title: id, content: 'Archive evidence supports complete retrieval across deterministic result pages.', tags: ['fixture'],
      } }));
    }
    const invoke = async (name: string, args: Record<string, unknown>) =>
      textResult(await client.callTool({ name, arguments: args })).value;

    expect((await invoke('list_documents', {})).showing).toBe(50);
    expect((await invoke('semantic_search', { query: 'archive' })).showing).toBe(10);
    const listed = [];
    for (const offset of [0, 100]) {
      const page = await invoke('list_documents', { limit: 100, offset, sortBy: 'title' });
      expect(page).toMatchObject({ total: 120, offset, hasMore: offset === 0, showing: offset === 0 ? 100 : 20 });
      listed.push(...page.documents.map((document: { id: string }) => document.id));
    }
    expect(listed).toEqual(ids);

    const searched = [];
    for (const offset of [0, 37, 74, 111]) {
      const page = await invoke('semantic_search', { query: 'archive', limit: 37, offset });
      expect(page).toMatchObject({ totalResults: 120, offset, hasMore: offset < 111 });
      searched.push(...page.results.map((document: { id: string }) => document.id));
    }
    expect(searched).toEqual(ids);
    expect((await invoke('semantic_search', { query: 'archive', limit: 100 })).showing).toBe(100);
    expect(await invoke('semantic_search', { query: 'archive', offset: 120 })).toMatchObject({ results: [], showing: 0, hasMore: false });
    expect(await invoke('semantic_search', { query: 'x', offset: 5 })).toMatchObject({ results: [], totalResults: 0, showing: 0, offset: 5, hasMore: false });

    for (const name of ['list_documents', 'semantic_search']) {
      for (const invalid of [{ limit: 0 }, { limit: -1 }, { limit: 1.5 }, { limit: 101 }, { offset: -1 }, { offset: 1.5 }]) {
        const result = await client.callTool({ name, arguments: { query: 'archive', ...invalid } });
        expect(result.isError, JSON.stringify({ name, invalid })).toBe(true);
      }
    }
    expect((await invoke('list_documents', { limit: 100 })).total).toBe(120);
  });
}, 20_000);

it('preserves complete large document, metadata and excerpt values across read tools', async () => {
  await withClient(async client => {
    const content = 'Nebula '.repeat(10000) + 'fixture.';
    const note = 'x'.repeat(60000);
    textResult(await client.callTool({ name: 'store_document', arguments: {
      id: 'large-fixture', title: 'Large fixture', content, metadata: { note },
    } }));
    const get = textResult(await client.callTool({ name: 'get_document', arguments: { documentId: 'large-fixture' } }));
    expect(get.text.length).toBeGreaterThan(50000);
    expect(get.value.content).toBe(content);
    expect(get.value.metadata.note).toBe(note);
    const list = textResult(await client.callTool({ name: 'list_documents', arguments: {} }));
    expect(list.text.length).toBeGreaterThan(50000);
    expect(list.value.documents[0].metadata.note).toBe(note);
    const search = textResult(await client.callTool({ name: 'semantic_search', arguments: { query: 'nebula' } }));
    expect(search.text.length).toBeGreaterThan(50000);
    expect(search.value.results[0].relevantExcerpts).toEqual([content.slice(0, -1)]);
  });
}, 10_000);

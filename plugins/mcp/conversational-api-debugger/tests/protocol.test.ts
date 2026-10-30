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

it.skipIf(process.platform === 'win32')('renders literal shell arguments and JavaScript data from hostile log text', async () => {
  const { mkdir, readFile } = await import('node:fs/promises');
  const { execFile } = await import('node:child_process');
  const { promisify } = await import('node:util');
  const { runInNewContext } = await import('node:vm');
  const run = promisify(execFile);
  const cwd = await mkdtemp(join(tmpdir(), 'api-repro-literals-'));
  const bin = join(cwd, 'bin'); await mkdir(bin);
  const capture = join(cwd, 'args.json');
  for (const name of ['curl', 'http']) {
    await writeFile(join(bin, name), `#!${process.execPath}\nimport fs from 'node:fs'; fs.writeFileSync(${JSON.stringify(capture)}, JSON.stringify(process.argv.slice(2)));\n`, { mode: 0o700 });
  }
  const client = new Client({ name: 'literal-repro-fixture', version: '1.0.0' });
  const transport = new StdioClientTransport({ command: process.execPath,
    args: [fileURLToPath(new URL('../dist/servers/api-debugger.js', import.meta.url))], cwd, stderr: 'pipe' });
  const call = async (args: Record<string, unknown>) => {
    const result = await client.callTool({ name: 'make_repro', arguments: args });
    const block = (result.content as Array<{ type: string; text?: string }>).find(x => x.type === 'text');
    if (!block?.text) throw new Error('Missing reproduction result');
    if (result.isError) throw new Error(block.text);
    return JSON.parse(block.text);
  };
  const argv = async (command: string) => {
    await run('/bin/sh', ['-c', command], { cwd, env: { PATH: bin } });
    return JSON.parse(await readFile(capture, 'utf8')) as string[];
  };
  try {
    await client.connect(transport);
    const text = 'single\' double" $(printf EXPANDED) `printf EXPANDED` \\ ;\nline';
    const log = { method: `POST${text}`, url: `https://example.invalid/${text}`,
      requestHeaders: { 'X-Fixture': text, 'X-File': '@not-a-file' }, requestBody: `@not-a-file ${text}` };
    for (const pretty of [true, false]) {
      const value = await call({ log, pretty });
      expect(await argv(value.curl)).toEqual(['-X', log.method, '-H', `X-Fixture: ${text}`, '-H', 'X-File: @not-a-file', '--data-raw', log.requestBody, '--url', log.url]);
      expect(await argv(value.alternative.httpie)).toEqual(['--ignore-stdin', `--raw=${log.requestBody}`, '--', log.method, log.url, `X-Fixture:${text}`, 'X-File:\\@not-a-file']);
      let observed: unknown;
      const result = runInNewContext(value.alternative.javascript, {
        fetch: (url: string, options: unknown) => { observed = JSON.parse(JSON.stringify({ url, options })); return Promise.resolve({ json: () => Promise.resolve({}) }); },
        console: { log: () => {}, error: () => {} },
      });
      await result;
      expect(observed).toEqual({ url: log.url, options: { method: log.method, headers: log.requestHeaders, body: log.requestBody } });
      expect(value.hasBody).toBe(true);
    }
    const hidden = await call({ log, includeHeaders: false });
    expect(hidden.headerCount).toBe(0);
    expect(await argv(hidden.curl)).not.toContain('-H');
    expect(await argv(hidden.alternative.httpie)).toEqual(['--ignore-stdin', `--raw=${log.requestBody}`, '--', log.method, log.url]);
    expect(hidden.alternative.javascript).not.toContain('X-Fixture');
    for (const body of [false, 0, '', null, '--option-like-body', { nested: { text }, literal: '@not-a-file' }]) {
      const value = await call({ log: { method: 'POST', url: '--option-like-url', requestBody: body } });
      const encoded = typeof body === 'string' ? body : JSON.stringify(body);
      expect(await argv(value.curl)).toEqual(['-X', 'POST', '--data-raw', encoded, '--url', '--option-like-url']);
      expect(await argv(value.alternative.httpie)).toEqual(['--ignore-stdin', `--raw=${encoded}`, '--', 'POST', '--option-like-url']);
      expect(value.hasBody).toBe(true);
    }
    expect(await argv((await call({ log: { method: 'GET', url: 'https://example.invalid/health', requestBody: '--body' } })).curl))
      .toEqual(['-X', 'GET', '--data-raw', '--body', '--url', 'https://example.invalid/health']);
    expect(await argv((await call({ log: { method: 'GET', url: 'https://example.invalid/health' } })).curl))
      .toEqual(['--url', 'https://example.invalid/health']);
    await expect(call({ log: { method: 'GET', url: 'contains\0NUL' } })).rejects.toThrow(/NUL/);
    await expect(call({ log: { method: 'GET', url: 'https://example.invalid', requestHeaders: { 'bad:name': 'value' } } })).rejects.toThrow(/HTTP tokens/);
    // Header suppression must not mutate logs used by later calls.
    await client.callTool({ name: 'ingest_logs', arguments: { logs: [{ ...log, timestamp: '2026-01-01T00:00:00Z', statusCode: 400 }] } });
    await call({ logIndex: 0, includeHeaders: false });
    expect((await call({ logIndex: 0 })).headerCount).toBe(2);
    await expect(call({ logIndex: 0.5 })).rejects.toThrow(/Invalid log index/);
  } finally { await client.close(); await transport.close(); await rm(cwd, { recursive: true, force: true }); }
}, 20000);

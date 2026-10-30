import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

test('MCP validates ratings and persists experiments in isolated storage', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'logger-protocol-'));
  const client = new Client({ name: 'protocol-fixture', version: '1.0.0' });
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: ['--require', fileURLToPath(new URL('./storage-fixture.cjs', import.meta.url)),
      fileURLToPath(new URL('../dist/index.js', import.meta.url))],
    cwd: fixture,
    env: { CCPI_TEST_STORAGE_ROOT: fixture },
    stderr: 'pipe',
  });
  const value = result => {
    assert.notEqual(result.isError, true);
    return JSON.parse(result.content.find(item => item.type === 'text').text);
  };
  try {
    await client.connect(transport);
    const { tools } = await client.listTools();
    assert.equal(tools.length, 7);
    for (const tool of tools) assert.equal(tool.inputSchema.type, 'object');
    assert.equal(value(await client.callTool({ name: 'list_experiments', arguments: {} })).count, 0);
    const experiment = { aiTool: 'fixture', prompt: 'synthetic', result: 'synthetic', rating: 5 };
    const invalid = await client.callTool({ name: 'log_experiment', arguments: { ...experiment, rating: 0 } });
    assert.equal(invalid.isError, true);
    value(await client.callTool({ name: 'log_experiment', arguments: experiment }));
    assert.equal(value(await client.callTool({ name: 'list_experiments', arguments: {} })).count, 1);
    const stored = JSON.parse(await readFile(join(fixture, '.ai-experiment-logger/experiments.json'), 'utf8'));
    assert.equal(stored.experiments.length, 1);
    assert.equal(stored.experiments[0].rating, 5);
  } finally {
    await client.close();
    await rm(fixture, { recursive: true });
  }
});

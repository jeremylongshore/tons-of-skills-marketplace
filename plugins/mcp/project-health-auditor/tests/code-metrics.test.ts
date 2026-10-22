import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { InMemoryTransport } from '@modelcontextprotocol/sdk/inMemory.js';
import { createServer, fileMetrics, listRepoFiles } from '../servers/code-metrics.js';

const execFileAsync = promisify(execFile);
const packageRoot = fileURLToPath(new URL('../', import.meta.url));
const sample = [
  '// café',
  'export function classify(value: number) {',
  '  if (value > 0) return 1;',
  '  return 0;',
  '}',
].join('\n');
let repoPath: string;
let filePath: string;

async function write(relativePath: string, content = '') {
  const target = path.join(repoPath, relativePath);
  await fs.mkdir(path.dirname(target), { recursive: true });
  await fs.writeFile(target, content);
  return target;
}

beforeEach(async () => {
  repoPath = await fs.mkdtemp(path.join(os.tmpdir(), 'health-auditor-'));
  filePath = await write('src/classify.ts', sample);
});

afterEach(async () => {
  vi.restoreAllMocks();
  await fs.rm(repoPath, { recursive: true, force: true });
});

describe('fileMetrics', () => {
  it('analyzes the real file and reports byte size for UTF-8 content', async () => {
    expect(await fileMetrics({ filePath })).toEqual({
      file: filePath,
      size: Buffer.byteLength(sample),
      lines: 5,
      extension: '.ts',
      complexity: { cyclomatic: 2, functions: 1, averagePerFunction: 2 },
      comments: { lines: 1, ratio: 20 },
      healthScore: 100,
    });
  });

  it('handles a file without functions or comments', async () => {
    const empty = await write('empty.txt');
    expect(await fileMetrics({ filePath: empty })).toMatchObject({
      size: 0,
      lines: 1,
      complexity: { cyclomatic: 1, functions: 0, averagePerFunction: 0 },
      comments: { lines: 0, ratio: 0 },
      healthScore: 90,
    });
  });

  it('penalizes a long, complex file through the real analyzer', async () => {
    const complex = await write('complex.js', [
      'function complicated(value) {',
      ...Array.from({ length: 12 }, () => 'if (value) value--;'),
      ...Array.from({ length: 500 }, () => ''),
      '}',
    ].join('\n'));
    expect(await fileMetrics({ filePath: complex })).toMatchObject({
      complexity: { cyclomatic: 13, functions: 1, averagePerFunction: 13 },
      healthScore: 40,
    });
  });

  it('stats and reads the same open file even when its path is replaced', async () => {
    const open = fs.open.bind(fs);
    const handle = await open(filePath, 'r');
    const stat = handle.stat.bind(handle);
    const statSpy = vi.spyOn(handle, 'stat').mockImplementationOnce(async () => {
      const originalStats = await stat();
      await fs.rename(filePath, `${filePath}.original`);
      await fs.writeFile(filePath, 'replacement');
      return originalStats;
    });
    const readSpy = vi.spyOn(handle, 'readFile');
    const closeSpy = vi.spyOn(handle, 'close');
    const openSpy = vi.spyOn(fs, 'open').mockResolvedValueOnce(handle);
    try {
      expect(await fileMetrics({ filePath })).toMatchObject({
        size: Buffer.byteLength(sample),
        lines: 5,
        comments: { lines: 1, ratio: 20 },
      });
      expect(await fs.readFile(filePath, 'utf8')).toBe('replacement');
      expect(openSpy).toHaveBeenCalledExactlyOnceWith(filePath, 'r');
      expect(statSpy).toHaveBeenCalledTimes(1);
      expect(readSpy).toHaveBeenCalledExactlyOnceWith('utf-8');
      expect(closeSpy).toHaveBeenCalledTimes(1);
    } finally {
      await handle.close();
    }
  });

  it.each(['stat', 'readFile'] as const)('closes its handle when %s fails', async (operation) => {
    const handle = await fs.open(filePath, 'r');
    vi.spyOn(fs, 'open').mockResolvedValueOnce(handle);
    vi.spyOn(handle, operation).mockRejectedValueOnce(new Error('injected failure'));
    const closeSpy = vi.spyOn(handle, 'close');
    try {
      await expect(fileMetrics({ filePath })).rejects.toThrow('Failed to analyze file: injected failure');
      expect(closeSpy).toHaveBeenCalledTimes(1);
    } finally {
      await handle.close();
    }
  });

  it('reports an actual missing file', async () => {
    await expect(fileMetrics({ filePath: path.join(repoPath, 'missing.ts') }))
      .rejects.toThrow(/Failed to analyze file: ENOENT/);
  });
});

describe('listRepoFiles', () => {
  it('sorts and deduplicates overlapping globs, excludes directories and ignored files', async () => {
    await write('README.md');
    await write('src/second.ts');
    await write('src/generated/ignored.ts');
    const result = await listRepoFiles({
      repoPath,
      globs: ['src/**/*.ts', '**/*.ts', '*.md'],
      exclude: ['src/generated/**'],
    });
    expect(result.files).toEqual(['README.md', 'src/classify.ts', 'src/second.ts']);
    expect(result.totalFiles).toBe(3);
    expect(result.repoPath).toBe(repoPath);
  });

  it('returns no files when no pattern matches', async () => {
    expect(await listRepoFiles({ repoPath, globs: ['**/*.py'], exclude: [] }))
      .toMatchObject({ totalFiles: 0, files: [] });
  });
});

describe('MCP handlers', () => {
  let client: Client;
  let server: ReturnType<typeof createServer>;

  beforeEach(async () => {
    server = createServer();
    client = new Client({ name: 'health-auditor-tests', version: '1.0.0' });
    const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
    await server.connect(serverTransport);
    await client.connect(clientTransport);
  });

  afterEach(async () => {
    await client.close();
    await server.close();
  });

  it('lists all four tools', async () => {
    const result = await client.listTools();
    expect(result.tools.map(tool => tool.name)).toEqual([
      'list_repo_files', 'file_metrics', 'git_churn', 'map_tests',
    ]);
  });

  it('applies real schema defaults before listing repository files', async () => {
    for (const ignored of ['node_modules', '.git', 'dist', 'build']) {
      await write(`${ignored}/ignored.ts`);
    }
    const result = await client.callTool({ name: 'list_repo_files', arguments: { repoPath } });
    expect(result.content).toEqual([{ type: 'text', text: expect.any(String) }]);
    const content = result.content as Array<{ type: 'text'; text: string }>;
    expect(JSON.parse(content[0].text)).toMatchObject({
      files: ['src/classify.ts'], totalFiles: 1, patterns: ['**/*'],
      excluded: ['node_modules/**', '.git/**', 'dist/**', 'build/**'],
    });
  });

  it('routes file metrics to the real analyzer', async () => {
    const result = await client.callTool({ name: 'file_metrics', arguments: { filePath } });
    expect(result.content).toEqual([{ type: 'text', text: JSON.stringify(await fileMetrics({ filePath }), null, 2) }]);
  });

  it('maps real source and test files', async () => {
    await write('src/untested.ts');
    await write('tests/classify.test.ts');
    const result = await client.callTool({ name: 'map_tests', arguments: { repoPath } });
    const content = result.content as Array<{ type: 'text'; text: string }>;
    expect(JSON.parse(content[0].text)).toMatchObject({
      summary: { totalSourceFiles: 2, totalTestFiles: 1, testedFiles: 1, coverageRatio: 50 },
      coverage: { 'src/classify.ts': ['tests/classify.test.ts'] },
      missingTests: ['src/untested.ts'],
    });
  });

  it('rejects invalid tool arguments using the registered schema', async () => {
    await expect(client.callTool({ name: 'file_metrics', arguments: { filePath: 42 } }))
      .rejects.toThrow(/Invalid arguments: filePath/);
  });

  it('rejects unknown tools', async () => {
    await expect(client.callTool({ name: 'missing', arguments: {} }))
      .rejects.toThrow('Unknown tool: missing');
  });
});

describe('server lifecycle', () => {
  it.each(['servers/code-metrics.ts', 'dist/servers/code-metrics.js'])(
    'imports %s without starting stdio or keeping the process alive', async (entry) => {
      const url = pathToFileURL(path.join(packageRoot, entry)).href;
      const result = await execFileAsync(process.execPath, [
        '--import', import.meta.resolve('tsx'), '--input-type=module', '--eval',
        `await import(${JSON.stringify(url)}); process.stdout.write('imported\\n');`,
      ], { cwd: repoPath, timeout: 10000 });
      expect(result.stdout).toBe('imported\n');
      expect(result.stderr).toBe('');
    }, 15000,
  );

  it.each(['direct', 'symlink'])(
    'starts the shipped bundle through a %s launcher', async (kind) => {
      let entry = path.join(packageRoot, 'dist/servers/code-metrics.js');
      if (kind === 'symlink') {
        const link = path.join(repoPath, 'launcher.mjs');
        await fs.symlink(entry, link);
        entry = link;
      }
      const transport = new StdioClientTransport({
        command: process.execPath, args: [entry], cwd: repoPath, stderr: 'pipe',
      });
      const client = new Client({ name: 'launch-test', version: '1.0.0' });
      try {
        await client.connect(transport);
        expect((await client.listTools()).tools).toHaveLength(4);
        const result = await client.callTool({ name: 'file_metrics', arguments: { filePath } });
        expect(result.content).toEqual([{ type: 'text', text: JSON.stringify(await fileMetrics({ filePath }), null, 2) }]);
      } finally {
        await client.close();
        await transport.close();
      }
    }, 15000,
  );
});

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

describe('shipped inventory pagination', () => {
  it('traverses matched and unmatched sources with unchanged global summaries', async () => {
    for (let i = 0; i < 125; i++) {
      const name = `item_${String(i).padStart(4, '0')}`;
      await write(`src/${name}.ts`);
      if (i % 2 === 0) await write(`tests/${name}.test.ts`);
    }
    const transport = new StdioClientTransport({
      command: process.execPath, args: [path.join(packageRoot, 'dist/servers/code-metrics.js')],
      cwd: repoPath, stderr: 'pipe',
    });
    const client = new Client({ name: 'inventory-pages', version: '1.0.0' });
    const call = async (name: string, args: Record<string, unknown> = {}) => {
      const result = await client.callTool({ name, arguments: { repoPath, ...args } });
      return JSON.parse((result.content as Array<{ type: 'text'; text: string }>)[0].text);
    };
    try {
      await client.connect(transport);
      for (const tool of (await client.listTools()).tools.filter(t => ['list_repo_files', 'map_tests'].includes(t.name))) {
        expect(tool.inputSchema.properties).toMatchObject({
          limit: { type: 'integer', minimum: 1, maximum: 100, default: 100 },
          offset: { type: 'integer', minimum: 0, default: 0 },
        });
        expect(await call(tool.name)).toMatchObject({ offset: 0, limit: 100, showing: 100, hasMore: true });
        for (const args of [{ limit: 0 }, { limit: -1 }, { limit: 1.5 }, { limit: 101 }, { offset: -1 }, { offset: 0.5 }]) {
          await expect(call(tool.name, args)).rejects.toThrow(/Invalid arguments/);
        }
      }
      const files: string[] = [], sources: string[] = [], missing: string[] = [];
      const covered: Record<string, string[]> = {};
      for (const name of ['list_repo_files', 'map_tests']) {
        let offset = 0;
        while (true) {
          const page = await call(name, { limit: 37, offset, ...(name === 'list_repo_files' ? { globs: ['**/*.ts', 'src/**/*.ts'] } : {}) });
          if (name === 'list_repo_files') {
            expect(page.totalFiles).toBe(189); files.push(...page.files);
          } else {
            expect(page.summary).toEqual({ totalSourceFiles: 126, totalTestFiles: 63, testedFiles: 63, coverageRatio: 50 });
            expect([...Object.keys(page.coverage), ...page.missingTests].sort()).toEqual([...page.sourceFiles].sort());
            Object.assign(covered, page.coverage); sources.push(...page.sourceFiles); missing.push(...page.missingTests);
          }
          if (!page.hasMore) break;
          expect(page.showing).toBeGreaterThan(0); offset += page.showing;
        }
        expect(await call(name, { offset: 1000 })).toMatchObject({ showing: 0, hasMore: false });
        const empty = await fs.mkdtemp(path.join(os.tmpdir(), 'empty-health-page-'));
        try { expect(await call(name, { repoPath: empty })).toMatchObject({ showing: 0, hasMore: false }); }
        finally { await fs.rm(empty, { recursive: true, force: true }); }
      }
      expect(files).toHaveLength(189); expect(new Set(files).size).toBe(189);
      expect(files).toEqual([...files].sort());
      expect(sources).toHaveLength(126); expect(new Set(sources).size).toBe(126);
      expect(sources).toEqual(files.filter(file => file.startsWith('src/')));
      expect(Object.keys(covered)).toHaveLength(63); expect(missing).toHaveLength(63);
      expect(missing).toContain('src/classify.ts');
      const expectedMissing = ['src/classify.ts', ...Array.from({ length: 62 }, (_,i) =>
        `src/item_${String(2 * i + 1).padStart(4, '0')}.ts`)].sort();
      expect(missing).toEqual(expectedMissing);
      const expectedCovered = Object.fromEntries(Array.from({ length: 63 }, (_,i) => {
        const name = `item_${String(2 * i).padStart(4, '0')}`;
        return [`src/${name}.ts`, [`tests/${name}.test.ts`]];
      }));
      expect(covered).toEqual(expectedCovered);
    } finally { await client.close(); await transport.close(); }
  }, 20000);
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

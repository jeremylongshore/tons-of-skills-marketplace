import assert from 'node:assert/strict';
import { spawn, execFileSync } from 'node:child_process';
import { copyFile, lstat, mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, relative, resolve } from 'node:path';
import { createInterface } from 'node:readline';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const plugin = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const repository = resolve(plugin, '../../..');
const tools = [
  'delete_experiment', 'export_experiments', 'get_experiment', 'get_statistics',
  'list_experiments', 'log_experiment', 'update_experiment',
];

async function fixture() {
  const scratch = await mkdtemp(join(tmpdir(), 'ai logger clean copy '));
  try {
  const copy = join(scratch, 'copied plugin');
  const home = join(scratch, 'isolated home');
  const cwd = join(scratch, 'unrelated working directory');
  await Promise.all([mkdir(copy), mkdir(home), mkdir(cwd)]);
  for (let ancestor = scratch; ; ancestor = dirname(ancestor)) {
    assert.equal(existsSync(join(ancestor, 'node_modules')), false, `ancestor dependency leak: ${ancestor}`);
    if (dirname(ancestor) === ancestor) break;
  }
  const files = execFileSync('git', ['ls-files', '-z', '--', relative(repository, plugin)], {
    cwd: repository, encoding: 'utf8',
  }).split('\0').filter(Boolean);
  for (const file of files) {
    const source = join(repository, file);
    assert.equal((await lstat(source)).isSymbolicLink(), false, `unexpected tracked symlink: ${file}`);
    const destination = join(copy, relative(plugin, source));
    await mkdir(dirname(destination), { recursive: true });
    await copyFile(source, destination);
  }
  assert.ok(existsSync(join(copy, 'dist/index.js')), 'the published entry must be Git tracked');
  assert.equal(existsSync(join(copy, 'node_modules')), false);
  const env = {
    PATH: process.env.PATH,
    HOME: home,
    USERPROFILE: home,
    TMPDIR: scratch,
    TEMP: scratch,
    TMP: scratch,
    NODE_PATH: '',
  };
  return { scratch, copy, home, cwd, env, data: join(home, '.ai-experiment-logger/experiments.json') };
  } catch (error) {
    await rm(scratch, { recursive: true, force: true });
    throw error;
  }
}

function launch(f) {
  const child = spawn(process.execPath, [join(f.copy, 'dist/index.js')], {
    cwd: f.cwd, env: f.env, stdio: ['pipe', 'pipe', 'pipe'],
  });
  let stderr = '';
  let nextId = 1;
  const pending = new Map();
  const protocolErrors = [];
  const rejectPending = (error) => {
    for (const listener of pending.values()) listener.reject(error);
    pending.clear();
  };
  child.stdin.on('error', rejectPending);
  child.stderr.on('data', (chunk) => { stderr += chunk; });
  const lines = createInterface({ input: child.stdout });
  lines.on('line', (line) => {
    let response;
    try { response = JSON.parse(line); } catch { protocolErrors.push(line); return; }
    const listener = pending.get(response.id);
    if (listener) { pending.delete(response.id); listener.resolve(response); }
  });
  const exited = new Promise((resolveExit, rejectExit) => {
    child.once('error', rejectExit);
    child.once('exit', (code, signal) => {
      for (const listener of pending.values()) listener.reject(new Error(`server exited ${code}: ${stderr}`));
      pending.clear();
      resolveExit({ code, signal });
    });
  });
  const request = async (method, params) => {
    const id = nextId++;
    let timer;
    try {
      const response = await new Promise((resolveResponse, rejectResponse) => {
        timer = setTimeout(() => { pending.delete(id); rejectResponse(new Error(`timeout: ${method}; ${stderr}`)); }, 5000);
        pending.set(id, { resolve: resolveResponse, reject: rejectResponse });
        child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
      });
      assert.equal(response.error, undefined, JSON.stringify(response.error));
      return response.result;
    } finally { clearTimeout(timer); }
  };
  return {
    request, protocolErrors,
    stderr: () => stderr,
    async initialize() {
      const result = await request('initialize', {
        protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'isolated-fixture', version: '1' },
      });
      child.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) + '\n');
      return result;
    },
    async call(name, args = {}) {
      const result = await request('tools/call', { name, arguments: args });
      return { isError: result.isError === true, value: JSON.parse(result.content[0].text) };
    },
    async close() {
      child.stdin.end();
      const timer = setTimeout(() => child.kill(), 2000);
      try { return await exited; } finally { clearTimeout(timer); lines.close(); }
    },
  };
}

async function withFixture(run) {
  const f = await fixture();
  try { await run(f); } finally { await rm(f.scratch, { recursive: true, force: true }); }
}

test('tracked copy initializes from an unrelated cwd without dependencies or credentials', async () => {
  await withFixture(async (f) => {
    const server = launch(f);
    try {
      const info = await server.initialize();
      assert.deepEqual(info.serverInfo, { name: 'ai-experiment-logger', version: '1.0.0' });
      const listed = await server.request('tools/list', {});
      assert.deepEqual(listed.tools.map((tool) => tool.name).sort(), tools);
      assert.deepEqual(JSON.parse(await readFile(f.data, 'utf8')), { experiments: [], version: '1.0.0' });
      assert.deepEqual(server.protocolErrors, []);
      assert.ok(server.stderr().includes(f.data));
    } finally { assert.equal((await server.close()).code, 0); }
  });
});

test('real stdio tools persist, filter, update, export and delete only isolated synthetic data', async () => {
  await withFixture(async (f) => {
    let server = launch(f);
    let id;
    try {
      await server.initialize();
      const created = await server.call('log_experiment', {
        aiTool: 'Synthetic Model', prompt: 'say "hello"\nsecond line', result: 'Synthetic result',
        rating: 4, tags: ['fixture'], date: '2026-01-02T00:00:00.000Z',
      });
      assert.equal(created.isError, false);
      assert.equal(created.value.success, true);
      id = created.value.experiment.id;
      assert.match(id, /^exp_/);
      assert.equal((await server.call('get_experiment', { id })).value.experiment.prompt, 'say "hello"\nsecond line');
      assert.equal((await server.call('list_experiments', { tags: ['fixture'], searchQuery: 'synthetic' })).value.count, 1);
      assert.equal((await server.call('list_experiments', { aiTool: 'other' })).value.count, 0);
      assert.equal((await server.call('update_experiment', { id, rating: 5 })).value.experiment.rating, 5);
      const stats = (await server.call('get_statistics')).value.statistics;
      assert.equal(stats.totalExperiments, 1);
      assert.equal(stats.averageRating, 5);
      const csv = (await server.call('export_experiments')).value.data;
      assert.ok(csv.includes('"say ""hello""\nsecond line"'));
      assert.equal(JSON.parse(await readFile(f.data, 'utf8')).experiments[0].rating, 5);
    } finally { assert.equal((await server.close()).code, 0); }
    server = launch(f);
    try {
      await server.initialize();
      assert.equal((await server.call('get_experiment', { id })).value.experiment.rating, 5);
      assert.equal((await server.call('delete_experiment', { id })).value.success, true);
      assert.equal((await server.call('list_experiments')).value.count, 0);
      assert.deepEqual(JSON.parse(await readFile(f.data, 'utf8')).experiments, []);
      assert.deepEqual(server.protocolErrors, []);
    } finally { assert.equal((await server.close()).code, 0); }
  });
});

test('invalid input and absent IDs return errors without mutating persisted data', async () => {
  await withFixture(async (f) => {
    const server = launch(f);
    try {
      await server.initialize();
      const before = await readFile(f.data, 'utf8');
      for (const [name, args] of [
        ['log_experiment', { aiTool: 'Synthetic', prompt: 'fixture', result: 'fixture', rating: 0 }],
        ['get_experiment', { id: 'missing-fixture' }],
        ['update_experiment', { id: 'missing-fixture', rating: 3 }],
        ['delete_experiment', { id: 'missing-fixture' }],
      ]) {
        const result = await server.call(name, args);
        assert.equal(result.isError, true, name);
        assert.equal(result.value.success, false, name);
        assert.equal(await readFile(f.data, 'utf8'), before, name);
      }
    } finally { assert.equal((await server.close()).code, 0); }
  });
});

test('an unusable isolated data directory prevents successful initialization', async () => {
  await withFixture(async (f) => {
    await writeFile(join(f.home, '.ai-experiment-logger'), 'synthetic path collision');
    const server = launch(f);
    try { await assert.rejects(server.initialize(), /server exited/); }
    finally { assert.notEqual((await server.close()).code, 0); }
    assert.deepEqual(server.protocolErrors, []);
  });
});

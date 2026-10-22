/** Actual CLI subprocesses run only from physical, configuration-free temp copies. */
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import test from 'node:test';

const MODULES = [
  'sync-external.mjs',
  'sync-lockfile.mjs',
  'scan-synced-content.mjs',
  'safe-fs.mjs',
];
const scriptDir = path.dirname(fileURLToPath(import.meta.url));

// Dependency resolution stays in the fixture. The zero-install lockfile lane
// need not install js-yaml: help must never parse YAML, and normal execution is
// stopped by the configuration-read guard before it can reach yaml.load().
const LOADER = String.raw`
import { builtinModules } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = process.env.SYNC_HELP_ROOT;
export async function resolve(specifier, context, nextResolve) {
  if (specifier === 'js-yaml') return {
    url: 'data:text/javascript,export default { load() { globalThis.__syncHelpDenied("yaml.load"); } };',
    shortCircuit: true,
  };
  if (specifier.startsWith('node:') || builtinModules.includes(specifier)) return nextResolve(specifier, context);
  const result = await nextResolve(specifier, context);
  if (!result.url.startsWith('file:') || !fileURLToPath(result.url).startsWith(root + path.sep)) {
    throw new Error('SYNC_HELP_EXTERNAL_MODULE_REFUSED');
  }
  return result;
}
`;

const GUARD = String.raw`
const fs = require('node:fs');
const path = require('node:path');
const { fileURLToPath } = require('node:url');
const { syncBuiltinESMExports } = require('node:module');
const root = process.env.SYNC_HELP_ROOT;
const record = fs.writeSync.bind(fs);
const auditDescriptor = fs.openSync(process.env.SYNC_HELP_AUDIT, 'a', 0o600);
const allowedFiles = new Set(JSON.parse(process.env.SYNC_HELP_FILES));
const allowedDirs = new Set();
for (let dir = root; ; dir = path.dirname(dir)) {
  allowedDirs.add(dir);
  if (path.dirname(dir) === dir) break;
}
allowedDirs.add(path.join(root, 'scripts'));
function deny(operation) {
  record(auditDescriptor, operation + '\n');
  throw new Error('SYNC_HELP_DENIED:' + operation);
}
globalThis.__syncHelpDenied = deny;
function checkRead(value) {
  if (typeof value === 'number') return;
  const location = path.resolve(value instanceof URL ? fileURLToPath(value) : String(value));
  if (!allowedFiles.has(location) && !allowedDirs.has(location)) deny('read:' + path.basename(location));
}
for (const name of ['accessSync', 'existsSync', 'lstatSync', 'statSync', 'realpathSync', 'readlinkSync', 'readFileSync']) {
  const original = fs[name].bind(fs);
  fs[name] = (value, ...args) => { checkRead(value); return original(value, ...args); };
}
const writeFlags = fs.constants.O_WRONLY | fs.constants.O_RDWR | fs.constants.O_CREAT | fs.constants.O_TRUNC | fs.constants.O_APPEND;
const open = fs.openSync.bind(fs);
fs.openSync = (value, flags, ...args) => {
  if (typeof flags === 'string' ? /[wa+]/.test(flags) : (flags & writeFlags) !== 0) deny('write:open');
  checkRead(value);
  return open(value, flags, ...args);
};
for (const name of ['writeFile', 'writeFileSync', 'appendFile', 'appendFileSync', 'truncate', 'truncateSync', 'ftruncate', 'ftruncateSync', 'rename', 'renameSync', 'copyFile', 'copyFileSync', 'cp', 'cpSync', 'mkdir', 'mkdirSync', 'mkdtemp', 'mkdtempSync', 'rm', 'rmSync', 'rmdir', 'rmdirSync', 'unlink', 'unlinkSync', 'symlink', 'symlinkSync', 'link', 'linkSync', 'chmod', 'chmodSync', 'chown', 'chownSync', 'createWriteStream']) {
  fs[name] = () => deny('write:' + name);
}
for (const name of ['writeFile', 'appendFile', 'truncate', 'rename', 'copyFile', 'cp', 'mkdir', 'mkdtemp', 'rm', 'rmdir', 'unlink', 'symlink', 'link', 'chmod', 'chown', 'open']) {
  fs.promises[name] = () => deny('write:promises.' + name);
}
const child = require('node:child_process');
for (const name of ['exec', 'execSync', 'execFile', 'execFileSync', 'spawn', 'spawnSync', 'fork']) child[name] = () => deny('process:' + name);
for (const [module, names] of [
  ['node:http', ['request', 'get']], ['node:https', ['request', 'get']],
  ['node:net', ['connect', 'createConnection']], ['node:tls', ['connect']],
  ['node:dgram', ['createSocket']], ['node:dns', ['lookup', 'resolve']],
]) {
  const object = require(module);
  for (const name of names) object[name] = () => deny('network:' + module + '.' + name);
}
require('node:net').Socket.prototype.connect = () => deny('network:Socket.connect');
globalThis.fetch = () => deny('network:fetch');
syncBuiltinESMExports();
`;

function fixture(t) {
  const root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'sync-cli-help-')));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  fs.mkdirSync(path.join(root, 'scripts'));
  const files = MODULES.map((name) => path.join(root, 'scripts', name));
  for (const name of MODULES)
    fs.copyFileSync(path.join(scriptDir, name), path.join(root, 'scripts', name));
  const guard = path.join(root, 'guard.cjs');
  const loader = path.join(root, 'loader.mjs');
  const output = path.join(root, 'github-output');
  const audit = path.join(root, 'audit');
  fs.writeFileSync(guard, GUARD);
  fs.writeFileSync(loader, LOADER);
  fs.writeFileSync(output, 'untouched\n');
  const before = new Map(
    [...files, guard, loader, output].map((file) => [file, fs.readFileSync(file)]),
  );
  const env = {
    ...(process.env.SystemRoot ? { SystemRoot: process.env.SystemRoot } : {}),
    SYNC_HELP_ROOT: root,
    SYNC_HELP_FILES: JSON.stringify([...files, guard, loader]),
    SYNC_HELP_AUDIT: audit,
    GITHUB_OUTPUT: output,
  };
  const run = (args, { probe } = {}) => {
    const result = spawnSync(
      process.execPath,
      [
        '--no-warnings',
        '--require',
        guard,
        '--experimental-loader',
        pathToFileURL(loader).href,
        ...(probe ? ['--input-type=module', '--eval', probe] : [files[0], ...args]),
      ],
      { cwd: root, env, encoding: 'utf8', timeout: 10000 },
    );
    assert.equal(result.error, undefined, result.error?.message);
    for (const [file, bytes] of before) assert.deepEqual(fs.readFileSync(file), bytes, file);
    assert.equal(fs.existsSync(path.join(root, 'sources.yaml')), false);
    assert.equal(fs.existsSync(path.join(root, 'sources.lock.json')), false);
    assert.equal(fs.existsSync(path.join(root, '.claude-plugin')), false);
    assert.equal(fs.existsSync(path.join(root, 'plugins')), false);
    const recorded = fs.existsSync(audit) ? fs.readFileSync(audit, 'utf8').trim() : '';
    return { ...result, operations: recorded ? recorded.split('\n') : [] };
  };
  return { root, run };
}

for (const args of [
  ['--help'],
  ['-h'],
  ['--help', '--force', '--relock-all', '--strict'],
  ['--force', '--relock=example', '--source=example', '--dry-run', '--verbose', '-h'],
])
  test(`direct CLI ${args.join(' ')} prints help without sync effects`, (t) => {
    const { run } = fixture(t);
    const result = run(args);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stderr, '');
    assert.match(result.stdout, /^Usage: node scripts\/sync-external\.mjs \[options\]/);
    for (const flag of [
      '--help',
      '-h',
      '--force',
      '--dry-run',
      '--source=NAME',
      '--relock=NAME',
      '--relock-all',
      '--strict',
      '--verbose',
    ])
      assert.ok(result.stdout.includes(flag), flag);
    assert.match(result.stdout, /does NOT bypass drift quarantine/);
    assert.match(result.stdout, /still fetches upstream/);
    assert.match(result.stdout, /Total source failure exits nonzero even without --strict/);
    assert.doesNotMatch(result.stdout, /External Plugin Sync|Found \d+ source|DRY RUN MODE/);
    assert.deepEqual(result.operations, []);
  });

test('normal CLI reaches a refused config read in the isolated copy before any source loop', (t) => {
  const result = fixture(t).run(['--force', '--relock-all', '--strict']);
  assert.notEqual(result.status, 0);
  assert.deepEqual(result.operations, ['read:sources.yaml']);
  assert.match(result.stderr, /SYNC_HELP_DENIED:read:sources.yaml/);
  assert.doesNotMatch(result.stdout, /Found \d+ source/);
});

for (const [name, probe, operation] of [
  [
    'configuration read',
    "import fs from 'node:fs'; fs.readFileSync('sources.yaml');",
    'read:sources.yaml',
  ],
  [
    'process execution',
    "import cp from 'node:child_process'; cp.execFileSync(process.execPath, ['--version']);",
    'process:execFileSync',
  ],
  [
    'network',
    "import https from 'node:https'; https.get('https://example.invalid/');",
    'network:node:https.get',
  ],
  ['fetch', "fetch('https://example.invalid/');", 'network:fetch'],
  [
    'filesystem write',
    "import fs from 'node:fs'; fs.writeFileSync('forbidden-write', 'no');",
    'write:writeFileSync',
  ],
  ['YAML parsing', "import yaml from 'js-yaml'; yaml.load('sources: []');", 'yaml.load'],
])
  test(`isolation guard refuses and records ${name}`, (t) => {
    const { root, run } = fixture(t);
    const result = run([], { probe });
    assert.notEqual(result.status, 0);
    assert.deepEqual(result.operations, [operation]);
    assert.ok(result.stderr.includes(`SYNC_HELP_DENIED:${operation}`));
    assert.equal(fs.existsSync(path.join(root, 'forbidden-write')), false);
  });

import assert from 'node:assert/strict';
import { chmodSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const installer = fileURLToPath(new URL('../ops/install-skill-redirects.sh', import.meta.url));
const source = fileURLToPath(new URL('../ops/snowflake-v2-redirects.caddy', import.meta.url));

function fixture() {
  const directory = mkdtempSync(join(tmpdir(), 'skill-redirect-install-'));
  const target = join(directory, 'redirects.caddy');
  const main = join(directory, 'Caddyfile');
  const bin = join(directory, 'bin');
  const caddy = join(bin, 'caddy');
  mkdirSync(bin);
  writeFileSync(caddy, '#!/usr/bin/env sh\n[ "$1" = "adapt" ]\n');
  chmodSync(caddy, 0o755);
  writeFileSync(target, '@redir083 path /old\nredir @redir083 /new permanent\n');
  writeFileSync(main, `example.invalid {\n  import ${target}\n}\n`);
  return { directory, target, main, bin };
}

function check(target, main, bin) {
  return spawnSync('bash', [installer, '--check', source, target, main], {
    encoding: 'utf8',
    env: { ...process.env, PATH: `${bin}:${process.env.PATH}` },
  });
}

test('installer accepts a non-colliding full Caddy candidate without mutation', () => {
  const paths = fixture();
  try {
    const before = readFileSync(paths.target, 'utf8');
    const result = check(paths.target, paths.main, paths.bin);
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /candidate valid; sha256=[0-9a-f]{64}/);
    assert.equal(readFileSync(paths.target, 'utf8'), before);
  } finally {
    rmSync(paths.directory, { recursive: true, force: true });
  }
});

test('installer refuses a matcher collision before touching live state', () => {
  const paths = fixture();
  try {
    writeFileSync(paths.target, '@redir084 path /collision\nredir @redir084 /new permanent\n');
    const result = check(paths.target, paths.main, paths.bin);
    assert.equal(result.status, 65);
    assert.match(result.stderr, /matcher collision/);
  } finally {
    rmSync(paths.directory, { recursive: true, force: true });
  }
});

test('installer defaults to every generated fragment, in order, without matcher collisions', () => {
  const paths = fixture();
  try {
    const result = spawnSync('bash', [installer, '--check', '', paths.target, paths.main], {
      encoding: 'utf8',
      env: { ...process.env, PATH: `${paths.bin}:${process.env.PATH}` },
    });
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /candidate valid; sha256=[0-9a-f]{64}/);
  } finally {
    rmSync(paths.directory, { recursive: true, force: true });
  }
});

test('installer refuses a retired-path matcher already present in the live file', () => {
  const paths = fixture();
  try {
    writeFileSync(paths.target, '@retired0001 path /collision\nredir @retired0001 /new permanent\n');
    const result = spawnSync('bash', [installer, '--check', '', paths.target, paths.main], {
      encoding: 'utf8',
      env: { ...process.env, PATH: `${paths.bin}:${process.env.PATH}` },
    });
    assert.equal(result.status, 65);
    assert.match(result.stderr, /matcher collision/);
  } finally {
    rmSync(paths.directory, { recursive: true, force: true });
  }
});

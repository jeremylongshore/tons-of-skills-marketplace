import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { checkNodeVersion, MIN_NODE_MAJOR } from './doctor.js';

describe('doctor Node.js version check', () => {
  it('matches the engines floor published in package.json', () => {
    const pkg = JSON.parse(readFileSync(new URL('../../package.json', import.meta.url), 'utf8'));
    expect(pkg.engines.node).toBe(`>=${MIN_NODE_MAJOR}.0.0`);
  });

  it.each(['v22.0.0', 'v22.12.1', 'v24.3.0'])('passes supported %s', (version) => {
    const result = checkNodeVersion(version);
    expect(result.status).toBe('pass');
    expect(result.message).toBe(`${version} (supported)`);
    expect(result.details).toBeUndefined();
  });

  it.each(['v18.20.4', 'v20.18.0', 'v21.7.3'])(
    'warns on unsupported %s and names the fallback',
    (version) => {
      const result = checkNodeVersion(version);
      expect(result.status).toBe('warn');
      expect(result.message).toBe(`${version} (unsupported)`);
      expect(result.details).toContain(`Node.js ${MIN_NODE_MAJOR} or later`);
      expect(result.details).toContain('@intentsolutionsio/ccpi@2');
    },
  );

  it('treats an unparseable version as unsupported rather than passing it', () => {
    expect(checkNodeVersion('not-a-version').status).toBe('warn');
  });
});

describe('doctor catalog file helpers', () => {
  it('readIfPresent returns null only for a missing file', async () => {
    const { mkdtemp, writeFile, rm } = await import('node:fs/promises');
    const { tmpdir } = await import('node:os');
    const { join } = await import('node:path');
    const { readIfPresent } = await import('./doctor.js');
    const dir = await mkdtemp(join(tmpdir(), 'doctor-'));
    try {
      expect(await readIfPresent(join(dir, 'absent.json'))).toBeNull();
      await writeFile(join(dir, 'present.json'), '{"plugins":[]}');
      expect(await readIfPresent(join(dir, 'present.json'))).toBe('{"plugins":[]}');
      await expect(readIfPresent(dir)).rejects.toThrow(); // a directory is an error, not "missing"
    } finally {
      await rm(dir, { recursive: true, force: true });
    }
  });

  it('writeFileAtomic replaces content and leaves no temp file behind', async () => {
    const { mkdtemp, writeFile, readFile, readdir, rm } = await import('node:fs/promises');
    const { tmpdir } = await import('node:os');
    const { join } = await import('node:path');
    const { writeFileAtomic } = await import('./doctor.js');
    const dir = await mkdtemp(join(tmpdir(), 'doctor-'));
    try {
      const target = join(dir, 'marketplace.json');
      await writeFile(target, 'old');
      await writeFileAtomic(target, 'new');
      expect(await readFile(target, 'utf-8')).toBe('new');
      expect((await readdir(dir)).filter((name) => name.endsWith('.tmp'))).toEqual([]);
    } finally {
      await rm(dir, { recursive: true, force: true });
    }
  });

  it('writeFileAtomic removes its temp file when the rename fails', async () => {
    const { mkdtemp, mkdir, readdir, rm } = await import('node:fs/promises');
    const { tmpdir } = await import('node:os');
    const { join } = await import('node:path');
    const { writeFileAtomic } = await import('./doctor.js');
    const dir = await mkdtemp(join(tmpdir(), 'doctor-'));
    try {
      const target = join(dir, 'occupied');
      await mkdir(join(target, 'child'), { recursive: true }); // rename over a non-empty dir fails
      await expect(writeFileAtomic(target, 'data')).rejects.toThrow();
      expect((await readdir(dir)).filter((name) => name.endsWith('.tmp'))).toEqual([]);
    } finally {
      await rm(dir, { recursive: true, force: true });
    }
  });
});

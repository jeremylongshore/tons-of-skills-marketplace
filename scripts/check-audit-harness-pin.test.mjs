import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import test from 'node:test';

const root = resolve(import.meta.dirname, '..');
const manifest = JSON.parse(readFileSync(resolve(root, 'package.json'), 'utf8'));

test('the required skill-conform harness is pinned exactly', () => {
  assert.equal(
    manifest.devDependencies['@intentsolutions/audit-harness'],
    '1.4.0',
    'skill-conform is required, so its implementing harness cannot float by semver range',
  );
});

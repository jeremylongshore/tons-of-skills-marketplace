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

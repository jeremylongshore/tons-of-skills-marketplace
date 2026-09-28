import assert from 'node:assert/strict';
import test from 'node:test';
import { buildBom, purl } from './generate-publication-sbom.mjs';

test('renders a deterministic CycloneDX production dependency graph', () => {
  const bom = buildBom({
    name: '@scope/root',
    version: '1.2.3',
    dependencies: {
      alpha: {
        name: 'alpha',
        version: '2.0.0',
        resolved: 'https://registry.npmjs.org/alpha/-/alpha-2.0.0.tgz',
        dependencies: {
          beta: { name: 'beta', version: '3.0.0' },
        },
      },
    },
  });
  assert.equal(bom.bomFormat, 'CycloneDX');
  assert.equal(bom.specVersion, '1.6');
  assert.equal(bom.metadata.component.purl, 'pkg:npm/%40scope/root@1.2.3');
  assert.deepEqual(bom.dependencies[0], {
    ref: 'pkg:npm/%40scope/root@1.2.3',
    dependsOn: ['pkg:npm/alpha@2.0.0'],
  });
  assert.equal(bom.components.length, 2);
});

test('purl follows the npm purl type: scope @ encoded, bad names refused', () => {
  assert.equal(purl('alpha', '2.0.0'), 'pkg:npm/alpha@2.0.0');
  assert.equal(purl('@angular/animation', '12.3.1'), 'pkg:npm/%40angular/animation@12.3.1');
  assert.throws(() => purl('@scope/name/extra', '1.0.0'), /invalid npm package name/);
  assert.throws(() => purl('@scope/', '1.0.0'), /invalid npm package name/);
});

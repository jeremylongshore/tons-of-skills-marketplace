import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { fieldDiagnostic, diagnosticSummary } from './kernel-field-diagnostics.mjs';

const context = { lane: 'authoring/v2', file: 'SKILL.md', kernelVersion: '0.10.0' };
for (const field of [
  'name',
  'description',
  'allowed-tools',
  'version',
  'author',
  'license',
  'compatibility',
  'tags',
]) {
  test(`missing ${field} points to the field and reviewed authorities`, () => {
    const diagnostic = fieldDiagnostic(
      {
        keyword: 'required',
        instancePath: '',
        schemaPath: '#/required',
        params: { missingProperty: field },
        message: 'required property missing',
      },
      context,
    );
    assert.equal(diagnostic.fieldPointer, `/${field}`);
    assert.equal(diagnostic.marketplaceRequired, true);
    assert.match(diagnostic.historicalUrl, /#31-yaml-frontmatter-required$/);
    assert.match(diagnostic.historicalSection, /superseded/);
    assert.match(diagnostic.exceptionUrl, /CONTRIBUTING.md#marketplace-acceptance-and-exceptions$/);
    assert.ok(diagnostic.fieldUrl.endsWith(`#${field}`));
    assert.ok(
      readFileSync(new URL('../docs/sak-field-diagnostics.md', import.meta.url), 'utf8').includes(
        `### ${field}\n`,
      ),
    );
    assert.ok(
      diagnosticSummary([diagnostic]).join('\n').includes(`[/${field}](${diagnostic.fieldUrl})`),
    );
    assert.equal(diagnostic.schemaPath, '#/required');
  });
}
test('nested missing and additional property names use JSON Pointer escaping', () => {
  for (const keyword of ['required', 'additionalProperties']) {
    const params =
      keyword === 'required' ? { missingProperty: 'a~/b' } : { additionalProperty: 'a~/b' };
    const result = fieldDiagnostic({ keyword, instancePath: '/metadata', params }, context);
    assert.equal(result.fieldPointer, '/metadata/a~0~1b');
    assert.equal(result.historicalUrl, null);
  }
});
test('type errors keep array indices; malformed YAML stays at document root', () => {
  assert.equal(
    fieldDiagnostic({ instancePath: '/tags/2', keyword: 'type' }, context).fieldPointer,
    '/tags/2',
  );
  const parse = fieldDiagnostic({ message: 'invalid YAML' }, context);
  assert.equal(parse.fieldPointer, '/');
  assert.equal(parse.historicalUrl, null);
});
test('Markdown cannot inject links, HTML or table rows from artifact data', () => {
  const row = fieldDiagnostic(
    { message: '<img src=x> | [click](evil)\n`fake`' },
    { ...context, file: '[file](evil)\n|row' },
  );
  const output = diagnosticSummary([row]).join('\n');
  assert.ok(!output.includes('<img'));
  assert.ok(!output.includes('[click]'));
  assert.ok(!output.includes('[file]'));
  assert.match(output, /&#124;/);
  assert.match(output, /exception request/);
});
test('summary truncation is explicit and does not mutate the full records', () => {
  const rows = Array.from({ length: 41 }, () => fieldDiagnostic({}, context));
  assert.match(diagnosticSummary(rows).join('\n'), /Showing 40 of 41/);
  assert.equal(rows.length, 41);
});
test('linked local headings exist and historical contract stays explicitly superseded', () => {
  const root = new URL('../', import.meta.url);
  for (const [path, heading] of [
    ['.github/CONTRIBUTING.md', '## Marketplace acceptance and exceptions'],
    ['000-docs/SCHEMA_CHANGELOG.md', '## NON-NEGOTIABLES — read before touching this file'],
    [
      '000-docs/6767-h-SPEC-DR-STND-claude-code-extensions-master.md',
      '### 3.1 YAML Frontmatter (Required)',
    ],
    [
      '000-docs/727-AT-ARCH-master-modernization-blueprint.md',
      '### Section-level disposition of 6767-h',
    ],
  ])
    assert.ok(readFileSync(new URL(path, root), 'utf8').includes(heading), path);
});

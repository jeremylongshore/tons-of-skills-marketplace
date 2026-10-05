import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { inlineFormat, isSafeLinkTarget, mdToHtml } from './md-to-html.mjs';

// Test-only sentinel consumed by scripts/generated-content-ci.test.mjs.
if (process.env.GENERATED_CONTENT_SECURITY_RED_PROOF_TARGET === 'md-to-html') {
  test('planted red proof: md-to-html security suite failure reaches its callers', () => {
    assert.fail('GENERATED_CONTENT_SECURITY_RED_PROOF:md-to-html');
  });
}

const ROOT_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

test('keeps inline code opaque and escapes its contents', () => {
  for (const identifier of [
    'QUERY_ATTRIBUTION_HISTORY',
    'VALIDATION_MODE',
    'MATCH_BY_COLUMN_NAME',
  ]) {
    assert.equal(inlineFormat(`Use \`${identifier}\`.`), `Use <code>${identifier}</code>.`);
  }

  assert.equal(
    inlineFormat('`<img src=x onerror=alert(1)> **not bold** [not a link](javascript:x)`'),
    '<code>&lt;img src=x onerror=alert(1)&gt; **not bold** [not a link](javascript:x)</code>',
  );
  assert.equal(inlineFormat('``a`b``'), '<code>a`b</code>');
});

test('handles unmatched and multiline backticks deterministically', () => {
  assert.equal(
    inlineFormat('before `QUERY_ATTRIBUTION_HISTORY after'),
    'before `QUERY_ATTRIBUTION_HISTORY after',
  );
  assert.equal(inlineFormat('`line 1\nline_2`'), '<code>line 1\nline_2</code>');
  assert.equal(inlineFormat('before ``code` after'), 'before ``code` after');
});

test('joins soft-wrapped paragraphs before resolving multiline inline code', () => {
  const markdown = [
    'The warehouse query does not prove the absence of an account-level monitor. Inspect both',
    'levels and report serverless coverage separately. Do not use `CREATE OR REPLACE RESOURCE',
    'MONITOR` as an audit shortcut because replacing an existing guardrail changes live state.',
  ].join('\n');

  assert.equal(
    mdToHtml(markdown),
    '<p>The warehouse query does not prove the absence of an account-level monitor. Inspect both levels and report serverless coverage separately. Do not use <code>CREATE OR REPLACE RESOURCE MONITOR</code> as an audit shortcut because replacing an existing guardrail changes live state.</p>',
  );
});

test('preserves nested formatting without crossing code or word boundaries', () => {
  assert.equal(
    inlineFormat('**bold *italic* and `VALIDATION_MODE`**'),
    '<strong>bold <em>italic</em> and <code>VALIDATION_MODE</code></strong>',
  );
  assert.equal(inlineFormat('***nested***'), '<strong><em>nested</em></strong>');
  assert.equal(inlineFormat('QUERY_ATTRIBUTION_HISTORY'), 'QUERY_ATTRIBUTION_HISTORY');
  assert.equal(
    inlineFormat('[**Safe** `MATCH_BY_COLUMN_NAME`](https://docs.example.test/path)'),
    '<a href="https://docs.example.test/path"><strong>Safe</strong> <code>MATCH_BY_COLUMN_NAME</code></a>',
  );
});

test('escapes raw Markdown HTML instead of passing executable elements to set:html', () => {
  const raw = [
    '<script>alert(1)</script>',
    '<style>body{display:none}</style>',
    '<img src=x onerror="alert(1)">',
    '<svg><animate onbegin=alert(1) /></svg>',
  ].join(' ');
  const rendered = mdToHtml(raw);

  assert.equal(rendered.includes('<script'), false);
  assert.equal(rendered.includes('<style'), false);
  assert.equal(rendered.includes('<img'), false);
  assert.equal(rendered.includes('<svg'), false);
  assert.match(rendered, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
  assert.match(rendered, /&lt;img src=x onerror=&quot;alert\(1\)&quot;&gt;/);
});

test('accounts for the authoritative README presentation cohort without editing mirrors', async () => {
  const registryPath = join(ROOT_DIR, 'marketplace', 'ops', 'readme-presentation-routes.json');
  const registry = JSON.parse(await readFile(registryPath, 'utf8'));
  const sourcesLock = JSON.parse(await readFile(join(ROOT_DIR, 'sources.lock.json'), 'utf8'));

  assert.equal(registry.schema_version, 'readme-presentation-routes/v1');
  assert.equal(registry.audit.intentional_raw_html_tag_tokens, 178);
  assert.match(registry.audit.source_commit, /^[0-9a-f]{40}$/u);
  assert.doesNotThrow(() =>
    execFileSync('git', ['cat-file', '-e', `${registry.audit.source_commit}^{commit}`], {
      cwd: ROOT_DIR,
      stdio: 'ignore',
    }),
  );
  assert.equal(registry.entries.length, 8);
  assert.deepEqual(registry.entries.map(({ plugin }) => plugin).sort(), [
    'claudebase',
    'databricks-workspace-mcp',
    'hermes-tweet',
    'kobiton-automate',
    'portaljs',
    'servicegraph',
    'slack-channel',
    'tonone',
  ]);

  const firstParty = registry.entries.filter(({ ownership }) => ownership === 'first-party');
  assert.deepEqual(
    firstParty.map(({ plugin }) => plugin),
    ['databricks-workspace-mcp'],
  );

  for (const entry of registry.entries) {
    const readmeBytes = await readFile(join(ROOT_DIR, entry.readme));
    const readme = readmeBytes.toString('utf8');
    assert.ok(readme.length > 0, entry.readme);
    // A mirror re-audited after a reviewed relock pins its own audit commit;
    // otherwise the registry-wide 2026-09-02 audit commit applies.
    const auditCommit = entry.source_commit ?? registry.audit.source_commit;
    if (entry.source_commit) {
      assert.equal(entry.ownership, 'upstream-mirror', `${entry.plugin} per-entry audit commit`);
      assert.match(entry.source_commit, /^[0-9a-f]{40}$/u);
    }
    const sourceBytes = execFileSync('git', ['show', `${auditCommit}:${entry.readme}`], {
      cwd: ROOT_DIR,
    });
    const sourceHash = createHash('sha256').update(sourceBytes).digest('hex');
    const currentHash = createHash('sha256').update(readmeBytes).digest('hex');
    assert.equal(entry.source_sha256, sourceHash, `${entry.plugin} source audit hash`);
    assert.equal(entry.current_sha256, currentHash, `${entry.plugin} current hash`);

    const route = new URL(entry.route);
    assert.equal(route.protocol, 'https:', entry.plugin);
    assert.equal(route.hostname, 'github.com', entry.plugin);

    if (entry.ownership === 'first-party') {
      assert.equal(entry.disposition, 'resolved-safe-markdown');
      assert.equal(entry.sources_lock_key, undefined);
      assert.notEqual(entry.source_sha256, entry.current_sha256);
      assert.doesNotMatch(readme, /<\/?[A-Za-z][^>]*>/u);
      continue;
    }

    assert.equal(entry.ownership, 'upstream-mirror');
    const provenance = JSON.parse(await readFile(join(ROOT_DIR, entry.provenance), 'utf8'));
    assert.equal(provenance.synced_from.repo, entry.upstream, entry.plugin);
    if (Array.isArray(provenance.files)) assert.ok(provenance.files.includes('README.md'));
    const lockEntry = sourcesLock.sources[entry.sources_lock_key];
    assert.ok(lockEntry, `${entry.plugin} must resolve through sources.lock.json`);
    assert.equal(lockEntry.repo, entry.upstream, entry.plugin);
    assert.equal(lockEntry.files['README.md'], `sha256:${entry.current_sha256}`, entry.plugin);
    assert.equal(entry.source_sha256, entry.current_sha256, `${entry.plugin} mirror changed`);
    assert.match(
      route.pathname,
      new RegExp(`^/${entry.upstream.replace('/', '\\/')}/issues/new$`, 'u'),
    );
  }
});

test('retains the first-party README meaning through safe Markdown only', async () => {
  const readme = await readFile(
    join(ROOT_DIR, 'plugins', 'mcp', 'databricks-workspace-mcp', 'README.md'),
    'utf8',
  );
  const intro = readme.slice(0, readme.indexOf('\n---\n'));
  const rendered = mdToHtml(intro);

  assert.match(rendered, /<h1>databricks-workspace-mcp<\/h1>/u);
  assert.match(rendered, /Databricks <strong>control plane<\/strong>/u);
  assert.match(rendered, /<code>system\.\*<\/code>/u);
  assert.match(rendered, /<li><strong>License:<\/strong> MIT<\/li>/u);
  assert.match(rendered, /<li><strong>Transport:<\/strong> MCP over stdio and HTTP<\/li>/u);
  assert.match(rendered, /<li><strong>Access:<\/strong> Read-only<\/li>/u);
  assert.doesNotMatch(rendered, /&lt;(?:h1|p|img|strong|br|code)\b/iu);
  assert.doesNotMatch(rendered, /(?:javascript|data|vbscript):/iu);
});

test('rejects executable, obfuscated, and attribute-injection link targets', () => {
  const dangerousTargets = [
    'javascript:alert(1)',
    'JaVaScRiPt:alert(1)',
    'java%73cript%3Aalert(1)',
    'javascript&#58;alert(1)',
    'java%0ascript:alert(1)',
    'data:text/html,<script>alert(1)</script>',
    'vbscript:msgbox(1)',
    'http://example.test/insecure',
    '//evil.example/steal',
    'https://safe.example/"onmouseover="alert(1)',
    'javascript%252525252525252525253Aalert(1)',
  ];

  for (const target of dangerousTargets) {
    assert.equal(isSafeLinkTarget(target), false, target);
    const rendered = inlineFormat(`[label](${target})`);
    assert.equal(rendered, 'label', target);
    assert.equal(rendered.includes('<a '), false, target);
  }

  assert.equal(
    inlineFormat('[label](https://safe.example/" onclick="alert(1))'),
    'label',
    'quotes and whitespace cannot break out of href',
  );
});

test('retains explicitly safe web, mail, anchor, and relative links with escaped attributes', () => {
  const safeTargets = [
    'https://docs.example.test/path?a=1&b=2',
    'https://docs.example.test/Simpson%27s_paradox',
    'https://docs.example.test/%22quoted%22',
    'mailto:owner@example.test',
    '#prerequisites',
    '#',
    'references/official-sources.md',
    './neighbor.md',
    '../parent.md',
    '/docs/start/',
    '?view=compact',
  ];

  for (const target of safeTargets) {
    assert.equal(isSafeLinkTarget(target), true, target);
    assert.equal(
      inlineFormat(`[label](${target})`),
      `<a href="${target.replace(/&/g, '&amp;')}">label</a>`,
      target,
    );
  }
});

test('preserves block structure while applying safe inline rendering everywhere', () => {
  const markdown = [
    '# Heading with `VALIDATION_MODE`',
    '',
    '- **Bold** and [docs](references/guide.md)',
    '1. *Italic* and `MATCH_BY_COLUMN_NAME`',
    '',
    '| Option | Value |',
    '| --- | --- |',
    '| Mode | `QUERY_ATTRIBUTION_HISTORY` |',
    '',
    '```sql',
    'SELECT MATCH_BY_COLUMN_NAME, "<script>";',
    '```',
  ].join('\n');

  assert.equal(
    mdToHtml(markdown),
    [
      '<h1>Heading with <code>VALIDATION_MODE</code></h1>',
      '<ul>',
      '<li><strong>Bold</strong> and <a href="references/guide.md">docs</a></li>',
      '</ul>',
      '<ol>',
      '<li><em>Italic</em> and <code>MATCH_BY_COLUMN_NAME</code></li>',
      '</ol>',
      '<table><thead><tr>',
      '<th>Option</th>',
      '<th>Value</th>',
      '</tr></thead><tbody>',
      '<tr>',
      '<td>Mode</td>',
      '<td><code>QUERY_ATTRIBUTION_HISTORY</code></td>',
      '</tr>',
      '</tbody></table>',
      '<pre data-lang="sql"><code>',
      'SELECT MATCH_BY_COLUMN_NAME, &quot;&lt;script&gt;&quot;;',
      '</code></pre>',
    ].join('\n'),
  );
});

test('flushes buffered paragraphs and list items at every block boundary and EOF', () => {
  const markdown = [
    'soft paragraph',
    'at heading boundary',
    '## Heading',
    '- wrapped list item',
    '  continuation',
    '',
    'paragraph before table',
    '| A | B |',
    '| --- | --- |',
    '| one | two |',
    'paragraph before fence',
    '```txt',
    '<unsafe>',
    '```',
    'final',
    'paragraph',
  ].join('\n');

  assert.equal(
    mdToHtml(markdown),
    [
      '<p>soft paragraph at heading boundary</p>',
      '<h2>Heading</h2>',
      '<ul>',
      '<li>wrapped list item continuation</li>',
      '</ul>',
      '<p>paragraph before table</p>',
      '<table><thead><tr>',
      '<th>A</th>',
      '<th>B</th>',
      '</tr></thead><tbody>',
      '<tr>',
      '<td>one</td>',
      '<td>two</td>',
      '</tr>',
      '</tbody></table>',
      '<p>paragraph before fence</p>',
      '<pre data-lang="txt"><code>',
      '&lt;unsafe&gt;',
      '</code></pre>',
      '<p>final paragraph</p>',
    ].join('\n'),
  );
});

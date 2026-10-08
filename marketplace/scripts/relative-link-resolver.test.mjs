import assert from 'node:assert/strict';
import test from 'node:test';

import { mdToHtml } from './md-to-html.mjs';
import {
  SOURCE_REPOSITORY_URL,
  createRelativeLinkResolver,
  createTrackedTreeLookup,
  isNonRelativeTarget,
} from './relative-link-resolver.mjs';

const SKILL = 'plugins/saas-packs/demo-pack/skills/demo-skill/SKILL.md';
const TREE = [
  SKILL,
  'plugins/saas-packs/demo-pack/README.md',
  'plugins/saas-packs/demo-pack/skills/demo-skill/references/official-docs.md',
  'plugins/saas-packs/demo-pack/skills/demo-skill/references/deep/nested guide.md',
  'plugins/saas-packs/demo-pack/skills/demo-skill/scripts/run.sh',
  'plugins/saas-packs/demo-pack/skills/shared/patterns.md',
  'plugins/saas-packs/demo-pack/docs/QUICK_START.md',
];
const BLOB = `${SOURCE_REPOSITORY_URL}/blob/main`;
const TREE_VIEW = `${SOURCE_REPOSITORY_URL}/tree/main`;

const kindOf = createTrackedTreeLookup(TREE);
const resolve = createRelativeLinkResolver({
  sourcePath: SKILL,
  pluginRoot: 'plugins/saas-packs/demo-pack',
  kindOf,
});

test('tracked-tree lookup distinguishes files, derived directories, and absences', () => {
  assert.equal(kindOf(SKILL), 'file');
  assert.equal(kindOf('plugins/saas-packs/demo-pack/skills/demo-skill/references'), 'directory');
  assert.equal(kindOf('plugins'), 'directory');
  assert.equal(kindOf('plugins/saas-packs/demo-pack/skills/demo-skill/references/missing.md'), null);
  assert.equal(kindOf('plugins/saas'), null, 'a path prefix that is not a segment is not a directory');
});

test('resolves a sibling reference file against the SKILL.md directory, not the page URL', () => {
  assert.equal(
    resolve('references/official-docs.md'),
    `${BLOB}/plugins/saas-packs/demo-pack/skills/demo-skill/references/official-docs.md`,
  );
  assert.equal(
    resolve('./references/official-docs.md'),
    `${BLOB}/plugins/saas-packs/demo-pack/skills/demo-skill/references/official-docs.md`,
  );
});

test('resolves nested paths and percent-encodes each segment of the GitHub URL', () => {
  assert.equal(
    resolve('references/deep/nested%20guide.md'),
    `${BLOB}/plugins/saas-packs/demo-pack/skills/demo-skill/references/deep/nested%20guide.md`,
  );
});

test('resolves ../ traversal inside the repository', () => {
  assert.equal(
    resolve('../shared/patterns.md'),
    `${BLOB}/plugins/saas-packs/demo-pack/skills/shared/patterns.md`,
  );
  assert.equal(
    resolve('../../docs/QUICK_START.md'),
    `${BLOB}/plugins/saas-packs/demo-pack/docs/QUICK_START.md`,
  );
});

test('keeps anchors, drops query strings, and links directories to the tree view', () => {
  assert.equal(
    resolve('references/official-docs.md#rate-limits'),
    `${BLOB}/plugins/saas-packs/demo-pack/skills/demo-skill/references/official-docs.md#rate-limits`,
  );
  assert.equal(
    resolve('references/official-docs.md?plain=1#top'),
    `${BLOB}/plugins/saas-packs/demo-pack/skills/demo-skill/references/official-docs.md#top`,
  );
  assert.equal(resolve('.'), `${TREE_VIEW}/plugins/saas-packs/demo-pack/skills/demo-skill`);
  assert.equal(
    resolve('references/'),
    `${TREE_VIEW}/plugins/saas-packs/demo-pack/skills/demo-skill/references`,
  );
});

test('expands Claude Code directory placeholders', () => {
  assert.equal(
    resolve('${CLAUDE_SKILL_DIR}/scripts/run.sh'),
    `${BLOB}/plugins/saas-packs/demo-pack/skills/demo-skill/scripts/run.sh`,
  );
  assert.equal(
    resolve('${CLAUDE_PLUGIN_ROOT}/docs/QUICK_START.md'),
    `${BLOB}/plugins/saas-packs/demo-pack/docs/QUICK_START.md`,
  );
  const noRoot = createRelativeLinkResolver({ sourcePath: SKILL, kindOf });
  assert.equal(noRoot('${CLAUDE_PLUGIN_ROOT}/docs/QUICK_START.md'), null);
});

test('leaves absolute URLs, site paths, anchors, and queries untouched', () => {
  for (const target of [
    'https://docs.example.com/guide',
    'http://example.com',
    'mailto:help@example.com',
    'javascript:alert(1)',
    '/skills/other-skill/',
    '#section',
    '?tab=usage',
  ]) {
    assert.equal(isNonRelativeTarget(target), true, target);
    assert.equal(resolve(target), target, target);
  }
});

test('fails closed on missing targets and repository escapes', () => {
  assert.equal(resolve('references/missing.md'), null);
  assert.equal(resolve('../../../../../../etc/passwd'), null);
  assert.equal(resolve('../../../../..'), null);
  assert.equal(resolve('../../../../..'), null, 'the repository root itself is not a link target');
  assert.equal(resolve('references%2'), null, 'malformed percent-encoding');
  assert.equal(resolve('references\\official-docs.md'), null);
  assert.equal(resolve('#'), '#');
  assert.equal(resolve('?'), '?');
});

test('requires a source path and a lookup', () => {
  assert.throws(() => createRelativeLinkResolver({ kindOf }), TypeError);
  assert.throws(() => createRelativeLinkResolver({ sourcePath: SKILL }), TypeError);
});

test('mdToHtml with the resolver emits no page-relative hrefs', () => {
  const html = mdToHtml(
    [
      'See [docs](references/official-docs.md) and [**shared**](../shared/patterns.md#x).',
      '',
      '- [gone](references/missing.md)',
      '- [site](/skills/) and [web](https://example.com)',
    ].join('\n'),
    { resolveLink: resolve },
  );
  assert.equal(
    html,
    [
      `<p>See <a href="${BLOB}/plugins/saas-packs/demo-pack/skills/demo-skill/references/official-docs.md">docs</a> and <a href="${BLOB}/plugins/saas-packs/demo-pack/skills/shared/patterns.md#x"><strong>shared</strong></a>.</p>`,
      '<ul>',
      '<li>gone</li>',
      '<li><a href="/skills/">site</a> and <a href="https://example.com">web</a></li>',
      '</ul>',
    ].join('\n'),
  );
});

test('mdToHtml without a resolver keeps its prior behavior', () => {
  assert.equal(
    mdToHtml('[docs](references/official-docs.md)'),
    '<p><a href="references/official-docs.md">docs</a></p>',
  );
});

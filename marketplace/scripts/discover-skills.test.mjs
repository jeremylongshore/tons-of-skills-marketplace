import assert from 'node:assert/strict';
import { win32 } from 'node:path';
import test from 'node:test';

import {
  extractCategory,
  extractPluginName,
  normalizeDescription,
  normalizeListField,
  repositoryRelativePath,
  resolveSkillVersion,
} from './discover-skills.mjs';
import { parseSkillFrontmatter as parseFrontmatter } from '../../scripts/skill-frontmatter.mjs';

// Test-only sentinel consumed by scripts/generated-content-ci.test.mjs.
if (process.env.GENERATED_CONTENT_SECURITY_RED_PROOF_TARGET === 'discover-skills') {
  test('planted red proof: discover-skills security suite failure reaches its callers', () => {
    assert.fail('GENERATED_CONTENT_SECURITY_RED_PROOF:discover-skills');
  });
}

const SNOWFLAKE_MIGRATION_DESCRIPTION =
  'Plan and govern evidence-backed migrations to Snowflake from Redshift, ' +
  'BigQuery, on-premises databases, or another Snowflake account. Use when ' +
  'assessing migration scope, translating schemas and SQL, designing staged ' +
  'loads, validating data, or preparing a controlled cutover and rollback. ' +
  'Trigger with phrases like "migrate to Snowflake", "Snowflake migration", ' +
  '"Redshift to Snowflake", "BigQuery to Snowflake", or "Snowflake replatform".';

test('normalizes Windows skill and parent-plugin paths for catalog projections', () => {
  const root = String.raw`C:\repo`;
  const plugin = String.raw`C:\repo\plugins\security\hol-guard`;
  const skill = String.raw`C:\repo\plugins\security\hol-guard\skills\guard\SKILL.md`;
  assert.equal(repositoryRelativePath(root, plugin, win32), 'plugins/security/hol-guard');
  assert.equal(
    repositoryRelativePath(root, skill, win32),
    'plugins/security/hol-guard/skills/guard/SKILL.md',
  );
  assert.equal(extractCategory(plugin, win32), 'security');
  assert.equal(extractPluginName(plugin, win32), 'hol-guard');
});

test('parses the exact Snowflake migration folded description semantically', () => {
  const metadata = parseFrontmatter(`---
name: snowflake-migration-deep-dive
description: >-
  Plan and govern evidence-backed migrations to Snowflake from Redshift,
  BigQuery, on-premises databases, or another Snowflake account. Use when
  assessing migration scope, translating schemas and SQL, designing staged
  loads, validating data, or preparing a controlled cutover and rollback.
  Trigger with phrases like "migrate to Snowflake", "Snowflake migration",
  "Redshift to Snowflake", "BigQuery to Snowflake", or "Snowflake replatform".
allowed-tools: Read, Write, Edit
---
# Snowflake Migration Deep Dive
`);

  assert.equal(metadata.description, SNOWFLAKE_MIGRATION_DESCRIPTION);
  assert.notEqual(metadata.description, '>-');
  assert.equal(metadata['allowed-tools'], 'Read, Write, Edit');
});

test('supports LF and CRLF block scalars, quoted scalars, and YAML list forms', () => {
  assert.deepEqual(
    parseFrontmatter(`---
name: "quoted: skill"
description: >
  Folded over
  two lines.
literal: |
  first line
  second line
allowed-tools:
  - Read
  - "Write"
tags: [snowflake, "data warehouse"]
---
`),
    {
      name: 'quoted: skill',
      description: 'Folded over two lines.\n',
      literal: 'first line\nsecond line\n',
      'allowed-tools': ['Read', 'Write'],
      tags: ['snowflake', 'data warehouse'],
    },
  );

  assert.deepEqual(
    parseFrontmatter(
      '---\r\nname: crlf-skill\r\ndescription: >-\r\n  folded across\r\n  CRLF lines\r\n---\r\n# Body\r\n',
    ),
    { name: 'crlf-skill', description: 'folded across CRLF lines' },
  );
});

test('normalizes complete description metadata to one searchable line', () => {
  assert.equal(
    normalizeDescription('First line.\n  Second line with\tspacing.\n'),
    'First line. Second line with spacing.',
  );
  assert.equal(
    normalizeDescription(SNOWFLAKE_MIGRATION_DESCRIPTION),
    SNOWFLAKE_MIGRATION_DESCRIPTION,
  );
  assert.throws(() => normalizeDescription(['not', 'a', 'string']), /must be a string/);
});

test('resolves top-level and AgentSkills metadata versions without silent fallback', () => {
  assert.equal(resolveSkillVersion({ version: '2.1.0', metadata: { version: '2.1.0' } }), '2.1.0');
  assert.equal(resolveSkillVersion({ metadata: { version: '0.6.0' } }), '0.6.0');
  assert.equal(resolveSkillVersion({}), '1.0.0');
  assert.throws(
    () => resolveSkillVersion({ version: '2.1.0', metadata: { version: '1.4.0' } }),
    /conflicts/,
  );
  assert.throws(() => resolveSkillVersion({ metadata: 'invalid' }), /must be a mapping/);
  assert.throws(
    () => resolveSkillVersion({ metadata: { version: ['0.6.0'] } }),
    /must be a string/,
  );
});

test('normalizes every supported tool-list YAML shape without syntax artifacts', () => {
  const sources = [
    'allowed-tools: Read, Write, Bash(git:*)',
    'allowed-tools: "Read, Write, Bash(git:*)"',
    'allowed-tools: [Read, Write, "Bash(git:*)"]',
    ['allowed-tools:', '  - Read', '  - Write', '  - Bash(git:*)'].join('\n'),
  ];

  for (const source of sources) {
    const metadata = parseFrontmatter(`---\nname: tools\n${source}\n---\n`);
    const tools = normalizeListField(metadata['allowed-tools'], 'allowed-tools');
    assert.deepEqual(tools, ['Read', 'Write', 'Bash(git:*)']);
    assert.equal(
      tools.some((tool) => !tool || /^[\[\]'\"]|[\[\]'\"]$/.test(tool)),
      false,
    );
  }

  assert.throws(
    () => normalizeListField(['Read', { tool: 'Write' }], 'allowed-tools'),
    /allowed-tools\[1\] must be a string/,
  );
  assert.throws(
    () => normalizeListField({ Read: true }, 'allowed-tools'),
    /must be a string or a list/,
  );
});

test('preserves safe mapping metadata while returning an ordinary own-property object', () => {
  const metadata = parseFrontmatter(`---
name: mapped-author
author:
  name: Intent Solutions
  email: team@example.com
empty:
---
`);

  assert.deepEqual(metadata, {
    name: 'mapped-author',
    author: { name: 'Intent Solutions', email: 'team@example.com' },
    empty: null,
  });
  assert.equal(Object.getPrototypeOf(metadata), Object.prototype);
  assert.equal(Object.hasOwn(metadata, 'name'), true);
});

test('returns null only when the document has no frontmatter', () => {
  assert.equal(parseFrontmatter('# Body only\n'), null);
  assert.throws(() => parseFrontmatter('---\nname: unfinished\n'), /unterminated/);
  assert.throws(() => parseFrontmatter({ source: '---\nname: object\n---\n' }), /must be a string/);
});

test('fails closed on malformed YAML, duplicate keys, non-mapping roots, and tags', () => {
  for (const [source, pattern] of [
    ['---\nname: [unterminated\n---\n', /invalid SKILL YAML frontmatter/],
    ['---\nname: first\nname: second\n---\n', /duplicated mapping key/],
    ['---\n- name\n- description\n---\n', /root must be a mapping/],
    ['---\njust-a-scalar\n---\n', /root must be a mapping/],
    ['---\nname: !!timestamp 2026-08-31\n---\n', /unknown tag/],
    ['---\nname: !!js/function function() {}\n---\n', /unknown tag/],
  ]) {
    assert.throws(() => parseFrontmatter(source), pattern);
  }
});

test('rejects prototype-sensitive keys and cyclic YAML aliases without pollution', () => {
  for (const source of [
    '---\n__proto__: polluted\nname: unsafe\n---\n',
    '---\nauthor:\n  constructor: polluted\n---\n',
    '---\nauthor:\n  prototype: polluted\n---\n',
  ]) {
    assert.throws(() => parseFrontmatter(source), /unsafe mapping key/);
  }

  assert.throws(
    () => parseFrontmatter('---\nrecursive: &self\n  child: *self\n---\n'),
    /anchors and aliases are not supported/,
  );
  assert.equal(Object.prototype.polluted, undefined);
});

test('rejects non-cyclic and Billion Laughs-style aliases before graph copying', () => {
  assert.throws(
    () =>
      parseFrontmatter(`---
defaults: &defaults
  tools: [Read, Write]
first: *defaults
second: *defaults
third: *defaults
---
`),
    /anchors and aliases are not supported/,
  );

  assert.throws(
    () =>
      parseFrontmatter(`---
laugh: &laugh [ha, ha, ha, ha, ha, ha, ha, ha, ha]
level1: &level1 [*laugh, *laugh, *laugh, *laugh, *laugh, *laugh, *laugh, *laugh, *laugh]
level2: &level2 [*level1, *level1, *level1, *level1, *level1, *level1, *level1, *level1]
payload: [*level2, *level2, *level2, *level2, *level2, *level2, *level2, *level2]
---
`),
    /anchors and aliases are not supported/,
  );
});

test('bounds YAML depth, node count, and frontmatter size', () => {
  const deeplyNested = `[${'['.repeat(70)}value${']'.repeat(70)}]`;
  assert.throws(
    () => parseFrontmatter(`---\ndeep: ${deeplyNested}\n---\n`),
    /nesting exceeds 64 levels/,
  );

  const manyNodes = Array.from({ length: 5000 }, (_, index) => `  - item-${index}`).join('\n');
  assert.throws(
    () => parseFrontmatter(`---\nitems:\n${manyNodes}\n---\n`),
    /document exceeds 4096 nodes/,
  );

  assert.throws(
    () => parseFrontmatter(`---\ndescription: ${'x'.repeat(256 * 1024)}\n---\n`),
    /exceeds 262144 characters/,
  );
});

test('does not mistake ordinary ampersands or asterisks in scalar content for aliases', () => {
  assert.deepEqual(
    parseFrontmatter(`---
name: symbols-are-content
description: "R&D keeps A&B and *asterisks* as text"
literal: |
  Anchors use & and aliases use * in prose.
items: ["R&D", "* wildcard", "A&B"]
---
`),
    {
      name: 'symbols-are-content',
      description: 'R&D keeps A&B and *asterisks* as text',
      literal: 'Anchors use & and aliases use * in prose.\n',
      items: ['R&D', '* wildcard', 'A&B'],
    },
  );
});

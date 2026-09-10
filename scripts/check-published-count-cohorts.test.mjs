import { deepEqual, equal, match } from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterEach, test } from 'node:test';
import { checkPublishedCountCohorts, parseArguments } from './check-published-count-cohorts.mjs';

const script = fileURLToPath(new URL('./check-published-count-cohorts.mjs', import.meta.url));
const temporaryRoots = [];
const cohorts = ['marketplace-visible', 'graded', 'first-party', 'curated-mirror', 'curriculum'];

afterEach(() => {
  for (const root of temporaryRoots.splice(0)) fs.rmSync(root, { recursive: true, force: true });
});

function registryFor(surfaces, deferredGroups = []) {
  return {
    schemaVersion: 1,
    cohorts: Object.fromEntries(
      cohorts.map((cohort) => [
        cohort,
        {
          label: cohort,
          description: `${cohort} fixture cohort`,
          command: `node scripts/corpus-resolver.mjs --cohort ${cohort} --json`,
          resolver: 'scripts/corpus-resolver.mjs',
        },
      ]),
    ),
    discovery: {
      roots: ['marketplace/src/pages', 'marketplace/src/components'],
      extension: '.astro',
      noun: 'skills',
      dynamicExpressionPolicy: 'any-braced-expression',
      ignoredPhrases: ['Tons of Skills'],
    },
    surfaces,
    deferredGroups,
  };
}

function enforcedSurface(overrides = {}) {
  return {
    path: 'marketplace/src/pages/index.astro',
    classification: 'live-global',
    cohort: 'marketplace-visible',
    expression: 'fmt(totalSkills)',
    label: 'marketplace-visible skills',
    provenance: '<CountProvenance cohort="marketplace-visible" />',
    status: 'enforced',
    ...overrides,
  };
}

function validSource() {
  return [
    '---',
    'const totalSkills = 3068;',
    '---',
    '<strong>{fmt(totalSkills)}</strong> marketplace-visible skills',
    '<CountProvenance cohort="marketplace-visible" />',
    '',
  ].join('\n');
}

function makeFixture({
  surfaces = [enforcedSurface()],
  source = validSource(),
  deferredGroups = [],
  files = {},
} = {}) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'published-count-cohorts-'));
  temporaryRoots.push(root);
  fs.mkdirSync(path.join(root, 'scripts'), { recursive: true });
  fs.mkdirSync(path.join(root, 'marketplace/src/pages'), { recursive: true });
  fs.mkdirSync(path.join(root, 'marketplace/src/components'), { recursive: true });
  fs.writeFileSync(
    path.join(root, 'scripts/published-count-cohorts.json'),
    `${JSON.stringify(registryFor(surfaces, deferredGroups), null, 2)}\n`,
  );
  fs.writeFileSync(path.join(root, 'marketplace/src/pages/index.astro'), source);
  for (const [relativePath, contents] of Object.entries(files)) {
    const absolutePath = path.join(root, relativePath);
    fs.mkdirSync(path.dirname(absolutePath), { recursive: true });
    fs.writeFileSync(absolutePath, contents);
  }
  return root;
}

function check(root, io) {
  return checkPublishedCountCohorts({ root, ...(io ? { io } : {}) });
}

function findingCode(report) {
  equal(report.allow, false);
  equal(report.decision, 'REFUSE');
  equal(report.findings.length, 1);
  return report.findings[0].code;
}

test('all enforced surfaces pass with structured counts', () => {
  const root = makeFixture({
    surfaces: [
      enforcedSurface(),
      {
        path: 'marketplace/src/pages/deferred.astro',
        classification: 'research',
        cohort: 'graded',
        status: 'deferred',
        owner: 'E1.10',
        reason: 'External snapshot requires a separate authority decision.',
      },
    ],
  });
  fs.writeFileSync(
    path.join(root, 'marketplace/src/pages/deferred.astro'),
    '<p>Research only</p>\n',
  );

  deepEqual(check(root), {
    schemaVersion: 1,
    cohorts: 5,
    enforced: 1,
    deferred: 1,
    discovered: 1,
    allow: true,
    decision: 'ALLOW',
    findings: [],
  });
});

test('red proof: an unlabeled, unregistered live count admitted before this gate is refused', () => {
  const root = makeFixture();
  fs.writeFileSync(
    path.join(root, 'marketplace/src/pages/legacy.astro'),
    '<strong>{totalSkills}</strong> skills\n',
  );
  equal(findingCode(check(root)), 'UNREGISTERED_PUBLIC_COUNT');
});

test('nested public count sources are discovered and cannot evade registration', () => {
  const root = makeFixture();
  fs.mkdirSync(path.join(root, 'marketplace/src/pages/nested'), { recursive: true });
  fs.writeFileSync(
    path.join(root, 'marketplace/src/pages/nested/legacy.astro'),
    '<strong>{totalSkills}</strong> skills\n',
  );
  equal(findingCode(check(root)), 'UNREGISTERED_PUBLIC_COUNT');
});

test('registered pages cannot add a second unregistered count expression', () => {
  const dynamic = makeFixture({
    source: `${validSource()}<div>{catalog.count} unlabelled skills</div>\n`,
  });
  equal(findingCode(check(dynamic)), 'UNREGISTERED_PUBLIC_COUNT_EXPRESSION');

  const numeric = makeFixture({
    source: `${validSource()}<div>1,372 unlabelled skills</div>\n`,
  });
  equal(findingCode(check(numeric)), 'UNREGISTERED_PUBLIC_COUNT_EXPRESSION');

  const identifierPrefix = makeFixture({
    surfaces: [enforcedSurface({ expression: 'stats.totalSkills' })],
    source: [
      '---',
      '---',
      '<strong>{stats.totalSkills}</strong> marketplace-visible skills',
      '<strong>{stats.totalSkillsOverride}</strong> unlabelled skills',
      '<CountProvenance cohort="marketplace-visible" />',
      '',
    ].join('\n'),
  });
  equal(findingCode(check(identifierPrefix)), 'UNREGISTERED_PUBLIC_COUNT_EXPRESSION');

  const callExtension = makeFixture({
    surfaces: [enforcedSurface({ expression: 'stats.totalSkills' })],
    source: [
      '---',
      '---',
      '<strong>{stats.totalSkills}</strong> marketplace-visible skills',
      '<strong>{stats.totalSkills.toLocaleString()}</strong> unlabelled skills',
      '<CountProvenance cohort="marketplace-visible" />',
      '',
    ].join('\n'),
  });
  equal(findingCode(check(callExtension)), 'UNREGISTERED_PUBLIC_COUNT_EXPRESSION');

  const exactFormattingCall = makeFixture({
    surfaces: [enforcedSurface({ expression: 'stats.totalSkills.toLocaleString()' })],
    source: [
      '---',
      '---',
      '<strong>{stats.totalSkills.toLocaleString()}</strong> marketplace-visible skills',
      '<CountProvenance cohort="marketplace-visible" />',
      '',
    ].join('\n'),
  });
  equal(check(exactFormattingCall).allow, true);

  const exactNestedObjectCall = makeFixture({
    surfaces: [enforcedSurface({ expression: 'format({ total: quantumWidgets })' })],
    source: [
      '---',
      '---',
      '<strong>{format({ total: quantumWidgets })}</strong> marketplace-visible skills',
      '<CountProvenance cohort="marketplace-visible" />',
      '',
    ].join('\n'),
  });
  equal(check(exactNestedObjectCall).allow, true);

  const nestedTemplateAttribute = makeFixture({
    source: validSource().replace(
      '<strong>{fmt(totalSkills)}</strong>',
      '<BaseLayout description={`${fmt(totalSkills)} marketplace-visible skills`} />\n<strong>{fmt(totalSkills)}</strong>',
    ),
  });
  equal(findingCode(check(nestedTemplateAttribute)), 'UNREGISTERED_PUBLIC_COUNT_EXPRESSION');
});

test('registered pages may explicitly defer a second owned count expression', () => {
  const deferredExpression = {
    expression: 'catalog.count',
    classification: 'entity-local',
    owner: 'fixture owner',
    reason: 'This fixture count is local to one entity.',
    label: 'entity-local skills',
    provenance: 'data-count-provenance="entity-local"',
    command: 'node scripts/check-published-count-cohorts.mjs --json',
    contract: 'data-count-provenance="entity-local">{catalog.count} entity-local skills',
    sink: 'metaParts.push',
    function: 'renderCard',
    call: 'renderCard',
  };
  const root = makeFixture({
    surfaces: [enforcedSurface({ deferredExpressions: [deferredExpression] })],
    source: `${validSource()}<div data-count-provenance="entity-local">{catalog.count} entity-local skills</div>\n`,
  });
  equal(check(root).allow, true);
  equal(check(root).deferred, 1);

  const malformed = makeFixture({
    surfaces: [enforcedSurface({ deferredExpressions: [{ ...deferredExpression, owner: '' }] })],
    source: `${validSource()}<div data-count-provenance="entity-local">{catalog.count} entity-local skills</div>\n`,
  });
  equal(findingCode(check(malformed)), 'INVALID_REGISTRY');

  const nonExecutableCommand = makeFixture({
    surfaces: [
      enforcedSurface({
        deferredExpressions: [{ ...deferredExpression, command: 'browser resolver prose' }],
      }),
    ],
    source: `${validSource()}<div data-count-provenance="entity-local">{catalog.count} entity-local skills</div>\n`,
  });
  equal(findingCode(check(nonExecutableCommand)), 'INVALID_LOCAL_COMMAND');

  const unboundContract = makeFixture({
    surfaces: [
      enforcedSurface({
        deferredExpressions: [{ ...deferredExpression, contract: 'not rendered here' }],
      }),
    ],
    source: `${validSource()}<div data-count-provenance="entity-local">{catalog.count} entity-local skills</div>\n`,
  });
  equal(findingCode(check(unboundContract)), 'LOCAL_CONTRACT_MISMATCH');

  const missingContract = { ...deferredExpression };
  delete missingContract.contract;
  const missingContractFixture = makeFixture({
    surfaces: [enforcedSurface({ deferredExpressions: [missingContract] })],
    source: `${validSource()}<div data-count-provenance="entity-local">{catalog.count} entity-local skills</div>\n`,
  });
  equal(findingCode(check(missingContractFixture)), 'INVALID_REGISTRY');

  const unlabeledContract = makeFixture({
    surfaces: [
      enforcedSurface({
        deferredExpressions: [
          {
            ...deferredExpression,
            contract: '<span>{catalog.count} skills</span>',
          },
        ],
      }),
    ],
    source: `${validSource()}<span>{catalog.count} skills</span>\n`,
  });
  equal(findingCode(check(unlabeledContract)), 'LOCAL_CONTRACT_MISMATCH');

  const nonRenderedContract = makeFixture({
    surfaces: [
      enforcedSurface({
        deferredExpressions: [
          {
            ...deferredExpression,
            sink: 'el.innerHTML',
            function: 'updateCount',
            call: 'updateCount',
          },
        ],
      }),
    ],
    source: [
      '---',
      'const deadContract = `data-count-provenance="entity-local">{catalog.count} entity-local skills`;',
      '---',
      '<div>{catalog.count} skills</div>',
      '',
    ].join('\n'),
  });
  equal(findingCode(check(nonRenderedContract)), 'INVALID_LOCAL_CONTRACT');

  const runtimeContract = makeFixture({
    surfaces: [
      enforcedSurface({
        deferredExpressions: [
          {
            ...deferredExpression,
            sink: 'el.innerHTML',
            function: 'updateCount',
            call: 'updateCount',
          },
        ],
      }),
    ],
    source: [
      validSource().trimEnd(),
      '<div>{catalog.count} skills</div>',
      '<script>',
      '  const el = document.querySelector("#count");',
      '  function updateCount() {',
      '    el.innerHTML = `<span data-count-provenance="entity-local">{catalog.count} entity-local skills</span>`;',
      '  }',
      '  updateCount();',
      '</script>',
      '',
    ].join('\n'),
  });
  equal(check(runtimeContract).allow, true);

  const discardedPush = makeFixture({
    surfaces: [
      enforcedSurface({
        deferredExpressions: [deferredExpression],
      }),
    ],
    source: [
      validSource().trimEnd(),
      '<script>',
      '  const discarded = [];',
      '  discarded.push(`<span data-count-provenance="entity-local">{catalog.count} entity-local skills</span>`);',
      '</script>',
      '',
    ].join('\n'),
  });
  equal(findingCode(check(discardedPush)), 'INVALID_LOCAL_CONTRACT');

  const deadExactSink = makeFixture({
    surfaces: [
      enforcedSurface({
        deferredExpressions: [deferredExpression],
      }),
    ],
    source: [
      validSource().trimEnd(),
      '<script>',
      '  function renderCard() {',
      '    metaParts.push(`<span data-count-provenance="entity-local">{catalog.count} entity-local skills</span>`);',
      '  }',
      '  // renderCard();',
      '  const text = "renderCard()";',
      '  notrenderCard();',
      '  other.renderCard();',
      '</script>',
      '',
    ].join('\n'),
  });
  equal(findingCode(check(deadExactSink)), 'INVALID_LOCAL_CONTRACT');
});

test('every expression in a combined shown-of-total skill count needs registration', () => {
  const root = makeFixture({
    surfaces: [
      enforcedSurface({
        deferredExpressions: [
          {
            expression: 'total',
            classification: 'query-result-local',
            owner: 'fixture owner',
            reason: 'The total belongs to the query-result cohort.',
            label: 'query-result-local skills',
            provenance: 'query-result-local',
            command: 'node scripts/check-published-count-cohorts.mjs --json',
            contract:
              '<span data-count-provenance="query-result-local">Showing ${shown} of ${total} query-result-local skills</span>',
            sink: 'el.innerHTML',
            function: 'updateResultsCount',
            call: 'updateResultsCount',
          },
        ],
      }),
    ],
    source: `${validSource()}<span data-count-provenance="query-result-local">Showing \${shown} of \${total} query-result-local skills</span><p>{shown} skills</p>\n`,
  });
  equal(findingCode(check(root)), 'UNREGISTERED_PUBLIC_COUNT_EXPRESSION');
});

test('Agent Skills is a skill label, not an intervening agent population', () => {
  const root = makeFixture({
    surfaces: [enforcedSurface({ expression: 'stats.totalSkills', label: 'marketplace-visible' })],
    source: [
      '---',
      '---',
      '<span>{stats.totalSkills}</span>',
      '<span>marketplace-visible Agent Skills</span>',
      '<span>{stats.totalAgents}</span>',
      '<span>Custom Agents</span>',
      '<CountProvenance cohort="marketplace-visible" />',
      '',
    ].join('\n'),
  });
  const report = check(root);
  equal(report.allow, true, JSON.stringify(report));
});

test('a generic Skills title cannot capture a count across a script declaration boundary', () => {
  const root = makeFixture();
  fs.writeFileSync(
    path.join(root, 'marketplace/src/pages/explore.astro'),
    [
      "const pageTitle = 'Explore Plugins & Skills';",
      'const pageDescription = `Search all ${stats.totalPlugins} catalog plugins`;',
      '',
    ].join('\n'),
  );
  equal(check(root).allow, true);
});

test('identifier-independent discovery refuses catalog counts, collection lengths, and literals', () => {
  for (const source of [
    '<strong>{_rawCatalog.count}</strong> skills\n',
    '<strong>{skills.length}</strong> skills\n',
    '<strong>{skillQuantity}</strong> skills\n',
    '<strong>{widgetsAvailable}</strong>\n<span>skills</span>\n',
    '<span>Skills</span>\n<strong>{widgetsAvailable}</strong>\n',
    '<h2><strong>{widgetsAvailable}</strong>\nSkills</h2>\n',
    '<strong>{widgetsAvailable}</strong>\n<h2>Skills</h2>\n',
    '<strong>{widgetsAvailable}</strong>\n<h2>Community-maintained Skills</h2>\n',
    '<strong>{quantumWidgets}</strong>\n<span>community-maintained skills</span>\n',
    '<span>Skills currently indexed:</span>\n<strong>{quantumWidgets}</strong>\n',
    '<strong>{\n  quantumWidgets\n}</strong>\n<span>skills</span>\n',
    '<span>Skills</span>\n<strong>{\n  quantumWidgets\n}</strong>\n',
    '<BaseLayout\n  description={`${seoQuantity}\n    marketplace-visible skills`}\n/>\n',
    '<p>Research across 1,372 skills.</p>\n',
    '<p>Skills: 9,999</p>\n',
  ]) {
    const root = makeFixture();
    fs.writeFileSync(path.join(root, 'marketplace/src/pages/legacy.astro'), source);
    equal(findingCode(check(root)), 'UNREGISTERED_PUBLIC_COUNT', source);
  }

  for (const source of [
    '<a href={`/skills/${item.slug}/`}>Skill detail</a>\n',
    '<a href="https://github.com/example/plugins-plus-skills">{starsDisplay} stars</a>\n',
    '<a href="https://github.com/skills">GitHub Skills</a>\n<span>{starsDisplay}</span> stars\n',
    '<BaseLayout\n  description={pageDescription}\n  title="Skills"\n/>\n',
    '<CrossProperty current="skills" />\n<p>{eyebrow}</p>\n',
    '<p>{eyebrow}</p>\n<h2>Where these skills come from</h2>\n',
    '<p>{eyebrow}</p><h2>Where these skills come from</h2>\n',
    '<p>{eyebrow}</p>\n<h2>Discover Skills</h2>\n',
    '<p>{eyebrow}</p>\n<h2>Build Real-world Skills</h2>\n',
    '<p>Learn what plugins and skills are, install in 60 seconds.</p>\n',
    '<p>Skills: 2 hours to complete this workshop.</p>\n',
    '<h2>Skills</h2>\n<span>{durationHours}</span> hours of training\n',
    '<h2>Skills</h2>\n<span>{notebookTotal}</span> notebooks\n',
    '<h2>Agent Skills</h2>\n<span>{stats.totalAgents}</span> custom agents\n',
    '<h2>Related Skills</h2>\n<div>{relatedSkills.map((skill) => (\n<a>{skill.name}</a>\n))}</div>\n',
    '<h2>Related Skills</h2><div>{relatedSkills.map((skill) => (<a>{skill.name}</a>))}</div>\n',
    '<h3>Agent Skills (5 notebooks)</h3>\n',
  ]) {
    const root = makeFixture();
    fs.writeFileSync(path.join(root, 'marketplace/src/pages/relationship.astro'), source);
    equal(check(root).allow, true, source);
  }

  const nestedRenderedCount = makeFixture();
  fs.writeFileSync(
    path.join(nestedRenderedCount, 'marketplace/src/components/NestedCount.astro'),
    '{skill.skillCount && (<span>{skill.skillCount} skills</span>)}\n',
  );
  equal(findingCode(check(nestedRenderedCount)), 'UNREGISTERED_PUBLIC_COUNT');
});

test('count-like sources in public Astro components require registration', () => {
  const root = makeFixture();
  fs.writeFileSync(
    path.join(root, 'marketplace/src/components/LegacyCard.astro'),
    '<span>{item.skillCount} skills</span>\n',
  );
  equal(findingCode(check(root)), 'UNREGISTERED_PUBLIC_COUNT');
});

test('count and label split across adjacent markup still require registration', () => {
  const root = makeFixture();
  fs.writeFileSync(
    path.join(root, 'marketplace/src/pages/legacy.astro'),
    [
      '<div>{catalog.count}</div>',
      '<div class="stat-label">Marketplace-visible skills</div>',
      '',
    ].join('\n'),
  );
  equal(findingCode(check(root)), 'UNREGISTERED_PUBLIC_COUNT');
});

test('symlinked entries inside the discovery tree fail closed', () => {
  const root = makeFixture();
  fs.symlinkSync(
    path.join(root, 'marketplace/src/pages/index.astro'),
    path.join(root, 'marketplace/src/pages/linked.astro'),
  );
  equal(findingCode(check(root)), 'SYMLINK_PATH');
});

test('missing cohort label near an expression is refused', () => {
  const root = makeFixture({
    source: validSource().replace('marketplace-visible skills', 'skills'),
  });
  equal(findingCode(check(root)), 'MISSING_COHORT_LABEL');
});

test('comment-only labels and provenance do not satisfy the visible contract', () => {
  const root = makeFixture({
    source: [
      '---',
      'const totalSkills = 3068;',
      '---',
      '<!-- marketplace-visible skills -->',
      '<strong>{fmt(totalSkills)}</strong>',
      '<!-- <CountProvenance cohort="marketplace-visible" /> -->',
      '',
    ].join('\n'),
  });
  equal(findingCode(check(root)), 'MISSING_COHORT_LABEL');
});

test('comment-only provenance is refused even when the visible label is valid', () => {
  const root = makeFixture({
    source: validSource().replace(
      '<CountProvenance cohort="marketplace-visible" />',
      '<!-- <CountProvenance cohort="marketplace-visible" /> -->',
    ),
  });
  equal(findingCode(check(root)), 'INVALID_PROVENANCE_COUNT');
});

test('frontmatter and script strings cannot satisfy the visible label or provenance contract', () => {
  const frontmatterOnly = makeFixture({
    source: [
      '---',
      "const label = 'marketplace-visible skills';",
      'const marker = `<CountProvenance cohort="marketplace-visible" />`;',
      '---',
      '<strong>{fmt(totalSkills)}</strong> skills',
      '',
    ].join('\n'),
  });
  equal(findingCode(check(frontmatterOnly)), 'MISSING_COHORT_LABEL');

  const scriptOnly = makeFixture({
    source: [
      '---',
      '---',
      '<strong>{fmt(totalSkills)}</strong> skills',
      '<script>',
      "const label = 'marketplace-visible skills';",
      'const marker = `<CountProvenance cohort="marketplace-visible" />`;',
      '</script>',
      '',
    ].join('\n'),
  });
  equal(findingCode(check(scriptOnly)), 'MISSING_COHORT_LABEL');

  const quotedSelfClosingText = makeFixture({
    source: [
      '---',
      '---',
      '<strong>{fmt(totalSkills)}</strong> skills',
      '<script data-x="/>">',
      "const label = 'marketplace-visible skills';",
      'const marker = `<CountProvenance cohort="marketplace-visible" />`;',
      '</script>',
      '',
    ].join('\n'),
  });
  equal(findingCode(check(quotedSelfClosingText)), 'MISSING_COHORT_LABEL');

  const hiddenExpression = makeFixture({
    source: [
      '---',
      'const hidden = fmt(totalSkills);',
      '---',
      '<p>marketplace-visible skills</p>',
      '<CountProvenance cohort="marketplace-visible" />',
      '',
    ].join('\n'),
  });
  equal(findingCode(check(hiddenExpression)), 'MISSING_EXPRESSION');

  const selfClosingHeadScript = makeFixture({
    source: validSource().replace(
      '<strong>{fmt(totalSkills)}</strong>',
      '<script type="application/ld+json" set:html={JSON.stringify({})} />\n<strong>{fmt(totalSkills)}</strong>',
    ),
  });
  equal(check(selfClosingHeadScript).allow, true);

  const unclosedScript = makeFixture({
    source: validSource().replace(
      '<CountProvenance cohort="marketplace-visible" />',
      '<script>const value = 1;',
    ),
  });
  equal(findingCode(check(unclosedScript)), 'MALFORMED_ASTRO_RAW_TEXT');
});

test('markup attributes cannot impersonate rendered count labels or provenance', () => {
  const attributeLabel = makeFixture({
    source: validSource().replace(
      '<strong>{fmt(totalSkills)}</strong> marketplace-visible skills',
      '<strong data-label="marketplace-visible skills">{fmt(totalSkills)}</strong> skills',
    ),
  });
  equal(findingCode(check(attributeLabel)), 'MISSING_COHORT_LABEL');

  const attributeExpression = makeFixture({
    source: validSource().replace(
      '<strong>{fmt(totalSkills)}</strong> marketplace-visible skills',
      '<strong data-count={fmt(totalSkills)}>marketplace-visible skills</strong>',
    ),
  });
  equal(findingCode(check(attributeExpression)), 'MISSING_EXPRESSION');

  const quotedGreaterThanLabel = makeFixture({
    source: validSource().replace(
      '<strong>{fmt(totalSkills)}</strong> marketplace-visible skills',
      '<strong title=">" data-label="marketplace-visible skills">{fmt(totalSkills)}</strong> skills',
    ),
  });
  equal(findingCode(check(quotedGreaterThanLabel)), 'MISSING_COHORT_LABEL');

  const quotedGreaterThanExpression = makeFixture({
    source: validSource().replace(
      '<strong>{fmt(totalSkills)}</strong> marketplace-visible skills',
      '<strong title=">" data-count={fmt(totalSkills)}>marketplace-visible skills</strong>',
    ),
  });
  equal(findingCode(check(quotedGreaterThanExpression)), 'MISSING_EXPRESSION');

  const attributeProvenance = makeFixture({
    source: validSource().replace(
      '<CountProvenance cohort="marketplace-visible" />',
      '<div data-marker=\'<CountProvenance cohort="marketplace-visible" />\'></div>',
    ),
  });
  equal(findingCode(check(attributeProvenance)), 'INVALID_PROVENANCE_COUNT');

  const multilineAttributeProvenance = makeFixture({
    source: validSource().replace(
      '<CountProvenance cohort="marketplace-visible" />',
      ['<div data-marker="', '<CountProvenance cohort="marketplace-visible" />', '"></div>'].join(
        '\n',
      ),
    ),
  });
  equal(findingCode(check(multilineAttributeProvenance)), 'INVALID_PROVENANCE_COUNT');

  const expressionStringProvenance = makeFixture({
    source: validSource().replace(
      '<CountProvenance cohort="marketplace-visible" />',
      '{`<CountProvenance cohort="marketplace-visible" />`}',
    ),
  });
  equal(findingCode(check(expressionStringProvenance)), 'INVALID_PROVENANCE_COUNT');
});

test('malformed Astro frontmatter fails closed', () => {
  const root = makeFixture({
    source: ['---', '<strong>{fmt(totalSkills)}</strong> marketplace-visible skills'].join('\n'),
  });
  equal(findingCode(check(root)), 'MALFORMED_ASTRO_FRONTMATTER');
});

test('trailing line comments cannot supply the visible label or provenance', () => {
  const labelOnly = makeFixture({
    source: [
      '---',
      'const totalSkills = 3068;',
      '---',
      '<strong>{fmt(totalSkills)}</strong> skills // marketplace-visible skills',
      '<div /> // <CountProvenance cohort="marketplace-visible" />',
      '',
    ].join('\n'),
  });
  equal(findingCode(check(labelOnly)), 'MISSING_COHORT_LABEL');

  const compactLabelOnly = makeFixture({
    source: [
      '---',
      'const totalSkills = 3068;',
      '---',
      '<strong>{fmt(totalSkills)}</strong> skills;// marketplace-visible skills',
      '<div />;// <CountProvenance cohort="marketplace-visible" />',
      '',
    ].join('\n'),
  });
  equal(findingCode(check(compactLabelOnly)), 'MISSING_COHORT_LABEL');

  const provenanceOnly = makeFixture({
    source: validSource().replace(
      '<CountProvenance cohort="marketplace-visible" />',
      '<div /> // <CountProvenance cohort="marketplace-visible" />',
    ),
  });
  equal(findingCode(check(provenanceOnly)), 'INVALID_PROVENANCE_COUNT');
});

test('URL slashes are preserved while stripping trailing line comments', () => {
  const root = makeFixture({
    source: validSource().replace(
      '<strong>{fmt(totalSkills)}</strong> marketplace-visible skills',
      '<a href="https://example.com/skills"><strong>{fmt(totalSkills)}</strong> marketplace-visible skills</a>',
    ),
  });
  equal(check(root).allow, true);
});

test('the branded project name is not mistaken for a numeric skill count', () => {
  const root = makeFixture();
  fs.writeFileSync(
    path.join(root, 'marketplace/src/pages/not-found.astro'),
    '<BaseLayout title="404 — Page Not Found · Tons of Skills" />\n',
  );
  equal(check(root).allow, true);
  equal(check(root).discovered, 1);
});

test('missing or duplicated provenance is refused', () => {
  const missing = makeFixture({
    source: validSource().replace('<CountProvenance cohort="marketplace-visible" />', ''),
  });
  equal(findingCode(check(missing)), 'INVALID_PROVENANCE_COUNT');

  const duplicated = makeFixture({ source: `${validSource()}${validSource().split('\n')[4]}\n` });
  equal(findingCode(check(duplicated)), 'INVALID_PROVENANCE_COUNT');
});

test('unknown cohorts fail closed for enforced and deferred surfaces', () => {
  const enforced = makeFixture({ surfaces: [enforcedSurface({ cohort: 'everything' })] });
  equal(findingCode(check(enforced)), 'UNKNOWN_COHORT');

  const deferred = makeFixture({
    surfaces: [
      {
        path: 'marketplace/src/pages/index.astro',
        classification: 'historical',
        cohort: 'everything',
        status: 'deferred',
        owner: 'E1.6',
        reason: 'Awaiting classification.',
      },
    ],
  });
  equal(findingCode(check(deferred)), 'UNKNOWN_COHORT');
});

test('exact duplicate and NFC/casefold-colliding surface paths are refused', () => {
  const duplicate = makeFixture({ surfaces: [enforcedSurface(), enforcedSurface()] });
  equal(findingCode(check(duplicate)), 'DUPLICATE_SURFACE_PATH');

  const collision = makeFixture({
    surfaces: [
      enforcedSurface({ path: 'marketplace/src/pages/INDEX.astro' }),
      enforcedSurface({
        path: 'marketplace/src/pages/index.astro',
        expression: 'other(totalSkills)',
      }),
    ],
  });
  fs.copyFileSync(
    path.join(collision, 'marketplace/src/pages/index.astro'),
    path.join(collision, 'marketplace/src/pages/INDEX.astro'),
  );
  equal(findingCode(check(collision)), 'CASEFOLD_SURFACE_COLLISION');

  const composedPath = 'marketplace/src/pages/caf\u00e9.astro';
  const decomposedPath = 'marketplace/src/pages/cafe\u0301.astro';
  const deferred = (surfacePath) => ({
    path: surfacePath,
    classification: 'historical',
    status: 'deferred',
    owner: 'E1.6',
    reason: 'Unicode collision fixture.',
  });
  const unicode = makeFixture({ surfaces: [deferred(composedPath), deferred(decomposedPath)] });
  fs.writeFileSync(path.join(unicode, composedPath), '<p>Composed</p>\n');
  fs.writeFileSync(path.join(unicode, decomposedPath), '<p>Decomposed</p>\n');
  equal(findingCode(check(unicode)), 'CASEFOLD_SURFACE_COLLISION');
});

test('malformed registry JSON is refused', () => {
  const root = makeFixture();
  fs.writeFileSync(path.join(root, 'scripts/published-count-cohorts.json'), '{ nope');
  equal(findingCode(check(root)), 'MALFORMED_JSON');
});

test('absolute paths, traversal, and non-normal paths are refused', () => {
  for (const unsafePath of [
    '/tmp/index.astro',
    '../index.astro',
    'marketplace/src/pages/../index.astro',
    'C:\\index.astro',
  ]) {
    const root = makeFixture({ surfaces: [enforcedSurface({ path: unsafePath })] });
    equal(findingCode(check(root)), 'UNSAFE_PATH', unsafePath);
  }
});

test('symlinked registry, surface, and surface ancestor are refused', () => {
  const registryRoot = makeFixture();
  const externalRegistry = path.join(registryRoot, 'registry-outside.json');
  fs.renameSync(path.join(registryRoot, 'scripts/published-count-cohorts.json'), externalRegistry);
  fs.symlinkSync(externalRegistry, path.join(registryRoot, 'scripts/published-count-cohorts.json'));
  equal(findingCode(check(registryRoot)), 'SYMLINK_PATH');

  const surfaceRoot = makeFixture();
  const externalSurface = path.join(surfaceRoot, 'surface-outside.astro');
  fs.renameSync(path.join(surfaceRoot, 'marketplace/src/pages/index.astro'), externalSurface);
  fs.symlinkSync(externalSurface, path.join(surfaceRoot, 'marketplace/src/pages/index.astro'));
  equal(findingCode(check(surfaceRoot)), 'SYMLINK_PATH');

  const ancestorRoot = makeFixture();
  const pages = path.join(ancestorRoot, 'marketplace/src/pages');
  const externalPages = path.join(ancestorRoot, 'external-pages');
  fs.renameSync(pages, externalPages);
  fs.symlinkSync(externalPages, pages, 'dir');
  equal(findingCode(check(ancestorRoot)), 'SYMLINK_PATH');
});

test('deterministically injected EACCES refuses an unreadable surface', () => {
  const root = makeFixture();
  const blocked = path.join(root, 'marketplace/src/pages/index.astro');
  const io = {
    ...fs,
    readFileSync(candidate, encoding) {
      if (candidate === blocked) {
        const error = new Error('injected EACCES');
        error.code = 'EACCES';
        throw error;
      }
      return fs.readFileSync(candidate, encoding);
    },
  };
  const report = check(root, io);
  equal(findingCode(report), 'UNREADABLE_FILE');
  match(report.findings[0].message, /injected EACCES/);
});

test('deferred surfaces require an owner and reason and never count as enforced', () => {
  for (const omitted of ['owner', 'reason']) {
    const deferred = {
      path: 'marketplace/src/pages/index.astro',
      classification: 'historical',
      status: 'deferred',
      owner: 'E1.6',
      reason: 'Frozen historical evidence.',
    };
    delete deferred[omitted];
    const root = makeFixture({ surfaces: [deferred], source: '<p>Historical</p>\n' });
    equal(findingCode(check(root)), 'INVALID_REGISTRY', omitted);
  }
});

test('deferred groups require exact owned paths and share duplicate protection', () => {
  const root = makeFixture();
  const registryPath = path.join(root, 'scripts/published-count-cohorts.json');
  const registry = JSON.parse(fs.readFileSync(registryPath, 'utf8'));
  registry.deferredGroups = [
    {
      classification: 'local-entity',
      owner: 'E1.6 follow-up',
      reason: 'Fixture deferral.',
      paths: ['marketplace/src/pages/index.astro'],
    },
  ];
  fs.writeFileSync(registryPath, JSON.stringify(registry));
  equal(findingCode(check(root)), 'DUPLICATE_SURFACE_PATH');

  const missing = makeFixture();
  const missingRegistryPath = path.join(missing, 'scripts/published-count-cohorts.json');
  const missingRegistry = JSON.parse(fs.readFileSync(missingRegistryPath, 'utf8'));
  missingRegistry.deferredGroups = [
    {
      classification: 'local-entity',
      owner: 'E1.6 follow-up',
      reason: 'Fixture deferral.',
      paths: [],
    },
  ];
  fs.writeFileSync(missingRegistryPath, JSON.stringify(missingRegistry));
  equal(findingCode(check(missing)), 'INVALID_DEFERRED_GROUP');
});

test('deferred-group claims enforce exact rendered contracts and fail closed', () => {
  const claim = {
    path: 'marketplace/src/pages/group-claim.astro',
    expression: 'catalog.count',
    classification: 'local-entity',
    owner: 'E1.6 follow-up',
    reason: 'The count belongs to one local entity.',
    label: 'local-entity skills',
    provenance: 'data-count-provenance="local-entity"',
    command: 'node scripts/check-published-count-cohorts.mjs --json',
    contract:
      '<span data-count-provenance="local-entity">{catalog.count} local-entity skills</span>',
    sink: 'metaParts.push',
    function: 'renderCard',
    call: 'renderCard',
  };
  const group = {
    classification: 'local-entity',
    owner: 'E1.6 follow-up',
    reason: 'Fixture deferred group.',
    claims: [claim],
  };
  const source = validSource();
  const claimSource =
    '<span data-count-provenance="local-entity">{catalog.count} local-entity skills</span>\n';

  const valid = makeFixture({
    deferredGroups: [group],
    source,
    files: { [claim.path]: claimSource },
  });
  equal(check(valid).allow, true);
  equal(check(valid).deferred, 1);
  equal(check(valid).discovered, 2);

  const duplicateRenderedExpression = makeFixture({
    deferredGroups: [group],
    source,
    files: {
      [claim.path]: `${claimSource}<span>{catalog.count} unlabelled skills</span>\n`,
    },
  });
  equal(findingCode(check(duplicateRenderedExpression)), 'AMBIGUOUS_LOCAL_EXPRESSION');

  const missingExpression = makeFixture({
    deferredGroups: [
      {
        ...group,
        claims: [
          {
            ...claim,
            expression: 'missing.count',
            contract: claim.contract.replace('catalog.count', 'missing.count'),
          },
        ],
      },
    ],
    source,
    files: { [claim.path]: claimSource },
  });
  equal(findingCode(check(missingExpression)), 'MISSING_EXPRESSION');

  const labelMismatch = makeFixture({
    deferredGroups: [{ ...group, claims: [{ ...claim, label: 'other skills' }] }],
    source,
    files: { [claim.path]: claimSource },
  });
  equal(findingCode(check(labelMismatch)), 'LOCAL_LABEL_MISMATCH');

  const provenanceMismatch = makeFixture({
    deferredGroups: [{ ...group, claims: [{ ...claim, provenance: 'other-provenance' }] }],
    source,
    files: { [claim.path]: claimSource },
  });
  equal(findingCode(check(provenanceMismatch)), 'LOCAL_PROVENANCE_MISMATCH');

  const duplicateClaim = makeFixture({
    deferredGroups: [{ ...group, claims: [claim, { ...claim }] }],
    source,
    files: { [claim.path]: claimSource },
  });
  equal(findingCode(check(duplicateClaim)), 'DUPLICATE_SURFACE_EXPRESSION');

  const deadContract = makeFixture({
    deferredGroups: [group],
    source: [
      validSource().trimEnd(),
      '<script>',
      'const dead = `<span data-count-provenance="local-entity">{catalog.count} local-entity skills</span>`;',
      '</script>',
      '',
    ].join('\n'),
    files: {
      [claim.path]: [
        '<script>',
        'const dead = `<span data-count-provenance="local-entity">{catalog.count} local-entity skills</span>`;',
        '</script>',
        '',
      ].join('\n'),
    },
  });
  equal(findingCode(check(deadContract)), 'INVALID_LOCAL_CONTRACT');

  const malformedClaim = makeFixture({
    deferredGroups: [{ ...group, claims: [null] }],
    source,
    files: { [claim.path]: claimSource },
  });
  equal(findingCode(check(malformedClaim)), 'INVALID_DEFERRED_GROUP_CLAIM');

  const missingRequiredField = { ...claim };
  delete missingRequiredField.function;
  const missingField = makeFixture({
    deferredGroups: [{ ...group, claims: [missingRequiredField] }],
    source,
    files: { [claim.path]: claimSource },
  });
  equal(findingCode(check(missingField)), 'INVALID_REGISTRY');

  const unsafeClaim = makeFixture({
    deferredGroups: [{ ...group, claims: [{ ...claim, path: '../group-claim.astro' }] }],
    source,
    files: { [claim.path]: claimSource },
  });
  equal(findingCode(check(unsafeClaim)), 'UNSAFE_PATH');
});

test('canonical cohort shape and resolver commands fail closed on contradiction', () => {
  const root = makeFixture();
  const registryPath = path.join(root, 'scripts/published-count-cohorts.json');
  const registry = JSON.parse(fs.readFileSync(registryPath, 'utf8'));
  registry.cohorts.graded.command =
    'node scripts/corpus-resolver.mjs --cohort marketplace-visible --json';
  fs.writeFileSync(registryPath, JSON.stringify(registry));
  equal(findingCode(check(root)), 'INVALID_COHORT_COMMAND');
});

test('CLI rejects unknown arguments and emits JSON for a fixture root', () => {
  const root = makeFixture();
  const unknown = spawnSync(process.execPath, [script, '--wat'], { encoding: 'utf8' });
  equal(unknown.status, 1);
  match(unknown.stderr, /UNKNOWN_ARGUMENT: unknown argument: --wat/);

  const result = spawnSync(process.execPath, [script, '--root', root, '--json'], {
    encoding: 'utf8',
  });
  equal(result.status, 0, result.stderr);
  const report = JSON.parse(result.stdout);
  equal(report.decision, 'ALLOW');
  equal(report.enforced, 1);
  deepEqual(parseArguments(['--root', root, '--json']), { root, json: true });
});

test('live vendor-pack pages use explicit local claims for pack and category counts', () => {
  const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
  const registry = JSON.parse(
    fs.readFileSync(path.join(repositoryRoot, 'scripts/published-count-cohorts.json'), 'utf8'),
  );
  const group = registry.deferredGroups.find(
    (candidate) => candidate.classification === 'vendor-pack-local',
  );
  equal(group.paths.length, 0);
  equal(group.claims.length, 56);
  equal(new Set(group.claims.map((claim) => claim.path)).size, 28);
  equal(group.claims.filter((claim) => claim.expression === 'vendor.skillCount').length, 28);
  equal(group.claims.filter((claim) => claim.expression === 'category.skills.length').length, 28);

  const report = check(repositoryRoot);
  equal(report.allow, true);
  equal(report.deferred >= 56, true);
  equal(report.findings.length, 0);
});

test('learning hub separates aggregate and vendor-pack-local claims', () => {
  const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
  const registry = JSON.parse(
    fs.readFileSync(path.join(repositoryRoot, 'scripts/published-count-cohorts.json'), 'utf8'),
  );
  const group = registry.deferredGroups.find(
    (candidate) => candidate.classification === 'learning-hub-aggregate',
  );
  equal(group.paths.length, 0);
  equal(group.claims.length, 4);
  equal(new Set(group.claims.map((claim) => claim.expression)).size, 4);
  equal(
    group.claims.filter((claim) => claim.classification === 'learning-hub-aggregate').length,
    2,
  );
  equal(group.claims.filter((claim) => claim.classification === 'vendor-pack-local').length, 2);
  equal(check(repositoryRoot).allow, true);
});

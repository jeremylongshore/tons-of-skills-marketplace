import assert from 'node:assert/strict';
import test from 'node:test';

import {
  IDENTITY,
  LIVE_REDIRECTS,
  checkIdentityCompatibility,
  checkLiveRedirects,
  hasExportedString,
  loadIdentitySnapshot,
} from './check-identity-compatibility.mjs';

const LIVE = loadIdentitySnapshot();

function snapshot(overrides = {}) {
  return JSON.parse(JSON.stringify({ ...LIVE, ...overrides }));
}

test('the repository satisfies the complete post-rename identity contract', () => {
  assert.deepEqual(checkIdentityCompatibility(LIVE), []);
});

test('renaming the published CLI package is rejected', () => {
  const candidate = snapshot();
  candidate.cliPackage.name = '@intentsolutionsio/tons';
  assert.match(checkIdentityCompatibility(candidate).join('\n'), /package identity/);
});

test('both ccpi and tons must remain aliases for one executable', () => {
  for (const bin of ['ccpi', 'tons']) {
    const candidate = snapshot();
    delete candidate.cliPackage.bin[bin];
    assert.match(checkIdentityCompatibility(candidate).join('\n'), /binary aliases/);
  }
  const split = snapshot();
  split.cliPackage.bin.tons = './dist/tons.js';
  assert.match(checkIdentityCompatibility(split).join('\n'), /binary aliases/);
});

test('the marketplace slug is frozen in both source and generated catalogs', () => {
  for (const catalog of ['extendedCatalog', 'generatedCatalog']) {
    const candidate = snapshot();
    candidate[catalog].name = 'tons-of-skills-marketplace';
    assert.match(checkIdentityCompatibility(candidate).join('\n'), /install identity/);
  }
});

test('the legacy install command and canonical skills.sh route are both required', () => {
  const commandDrift = snapshot({
    readme: LIVE.readme.replace(
      IDENTITY.installCommand,
      '/plugin marketplace add jeremylongshore/tons-of-skills-marketplace',
    ),
  });
  assert.match(checkIdentityCompatibility(commandDrift).join('\n'), /frozen install command/);

  const routeDrift = snapshot({
    readme: LIVE.readme.replace(IDENTITY.skillsRoute, 'https://skills.sh/example/drift'),
  });
  assert.match(checkIdentityCompatibility(routeDrift).join('\n'), /skills\.sh route/);
});

test('canonical repository and catalog endpoints cannot regress', () => {
  const rootDrift = snapshot();
  rootDrift.rootPackage.repository.url = 'git+https://github.com/example/drift.git';
  assert.match(checkIdentityCompatibility(rootDrift).join('\n'), /root package repository/);

  const cliDrift = snapshot();
  cliDrift.cliConstantsSource = cliDrift.cliConstantsSource.replace(
    IDENTITY.canonicalRepository,
    'example/drift',
  );
  assert.match(checkIdentityCompatibility(cliDrift).join('\n'), /repository constant/);

  const catalogDrift = snapshot();
  catalogDrift.cliConstantsSource = catalogDrift.cliConstantsSource.replace(
    IDENTITY.catalogUrl,
    'https://example.com/catalog.json',
  );
  assert.match(checkIdentityCompatibility(catalogDrift).join('\n'), /catalog URL/);

  const commentedRelic = snapshot();
  commentedRelic.cliConstantsSource = commentedRelic.cliConstantsSource
    .replace(IDENTITY.marketplaceSlug, 'tons-of-skills-marketplace')
    .concat(`\n// export const MARKETPLACE_SLUG = '${IDENTITY.marketplaceSlug}';\n`);
  assert.match(checkIdentityCompatibility(commentedRelic).join('\n'), /marketplace slug/);
});

test('exported URL checks compare literal values without compiling them as regular expressions', () => {
  const source = [
    "export const CATALOG_URL = 'https://raw.githubusercontent.com/owner/repo/main/catalog.json';",
    "export const LOOKALIKE = 'https://rawXgithubusercontent.com/owner/repo/main/catalog.json';",
  ].join('\n');
  assert.equal(
    hasExportedString(
      source,
      'CATALOG_URL',
      'https://raw.githubusercontent.com/owner/repo/main/catalog.json',
    ),
    true,
  );
  assert.equal(
    hasExportedString(
      source,
      'CATALOG_URL',
      'https://rawXgithubusercontent.com/owner/repo/main/catalog.json',
    ),
    false,
  );
});

test('exported URL checks ignore declaration-shaped comments and template contents', () => {
  const malicious = [
    `/* export const CATALOG_URL = '${IDENTITY.catalogUrl}'; */`,
    `const documentation = \`export const CATALOG_URL = '${IDENTITY.catalogUrl}';\`;`,
    "export const CATALOG_URL = 'https://attacker.invalid/catalog.json';",
  ].join('\n');
  assert.equal(hasExportedString(malicious, 'CATALOG_URL', IDENTITY.catalogUrl), false);

  const duplicated = [
    `export const CATALOG_URL = '${IDENTITY.catalogUrl}';`,
    "export const CATALOG_URL = 'https://attacker.invalid/catalog.json';",
  ].join('\n');
  assert.equal(hasExportedString(duplicated, 'CATALOG_URL', IDENTITY.catalogUrl), false);
});

test('the ccpi program identity and portable skills family remain registered', () => {
  const missingCcpi = snapshot({
    cliProgramSource: LIVE.cliProgramSource.replace(".name('ccpi')", ".name('tons')"),
  });
  assert.match(checkIdentityCompatibility(missingCcpi).join('\n'), /ccpi program identity/);

  const missingSkills = snapshot({
    cliProgramSource: LIVE.cliProgramSource.replace(".command('skills')", ".command('portable')"),
  });
  assert.match(checkIdentityCompatibility(missingSkills).join('\n'), /tons skills/);

  const templateSpoof = snapshot({
    cliProgramSource: LIVE.cliProgramSource
      .replace(".name('ccpi')", ".name('attacker')")
      .replace(".command('skills')", ".command('portable')")
      .replace(
        'export function buildProgram() {',
        "export function buildProgram() {\n  const documentation = `.name('ccpi') .command('skills')`;",
      ),
  });
  const spoofViolations = checkIdentityCompatibility(templateSpoof).join('\n');
  assert.match(spoofViolations, /ccpi program identity/);
  assert.match(spoofViolations, /tons skills/);
});

test('unreachable nested functions cannot satisfy the program identity contract', () => {
  const nestedFunctionSpoof = snapshot({
    cliProgramSource: [
      'export function buildProgram() {',
      '  const program = new Command();',
      "  function decoyName() { program.name('ccpi'); }",
      '  const skills = function decoyCommand() {',
      "    return program.command('skills');",
      '  };',
      '  return program;',
      '}',
    ].join('\n'),
  });

  const violations = checkIdentityCompatibility(nestedFunctionSpoof).join('\n');
  assert.match(violations, /ccpi program identity/);
  assert.match(violations, /tons skills/);
});

test('shadowed and unreachable calls cannot satisfy the program identity contract', () => {
  const controlFlowSpoof = snapshot({
    cliProgramSource: [
      'export function buildProgram() {',
      '  const program = new Command();',
      "  { const program = { name() {}, command() {} }; program.name('ccpi'); }",
      "  const skills = false && program.command('skills');",
      '  return program;',
      '}',
    ].join('\n'),
  });

  const violations = checkIdentityCompatibility(controlFlowSpoof).join('\n');
  assert.match(violations, /ccpi program identity/);
  assert.match(violations, /tons skills/);
});

test('the registered command instance must be returned from buildProgram', () => {
  const wrongReturn = snapshot({
    cliProgramSource: LIVE.cliProgramSource.replace('return program;', 'return new Command();'),
  });
  const violations = checkIdentityCompatibility(wrongReturn).join('\n');
  assert.match(violations, /ccpi program identity/);
  assert.match(violations, /tons skills/);
});

test('live redirect verifier follows every legacy route to the canonical destination', async () => {
  const seen = [];
  const results = await checkLiveRedirects(async (url) => {
    seen.push(url);
    const contract = LIVE_REDIRECTS.find((item) => item.source === url);
    const destination = new URL(contract.destination);
    if (destination.hostname === 'skills.sh') destination.hostname = 'www.skills.sh';
    return { status: 200, url: destination.toString(), body: null };
  });

  assert.deepEqual(
    seen,
    LIVE_REDIRECTS.map((item) => item.source),
  );
  assert.deepEqual(
    results.flatMap((result) => result.violations),
    [],
  );
});

test('live redirect verifier rejects errors and destinations outside the contract', async () => {
  const results = await checkLiveRedirects(async () => ({
    status: 404,
    url: 'https://example.com/wrong',
    body: null,
  }));
  const violations = results.flatMap((result) => result.violations).join('\n');
  assert.match(violations, /HTTP 404/);
  assert.match(violations, /resolved to/);
});

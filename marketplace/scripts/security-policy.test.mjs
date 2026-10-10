import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

import { renderCaddyHeaders } from './render-security-headers-caddy.mjs';
import {
  CHAT_CSP_DIRECTIVES,
  CSP_DIRECTIVES,
  CSP_INLINE_JUSTIFICATIONS,
  MARKETPLACE_CHAT_SECURITY_HEADERS,
  MARKETPLACE_SECURITY_HEADERS,
  securityHeadersForPath,
  serializeCsp,
  validateSecurityPolicy,
} from './security-policy.mjs';

const caddyPath = new URL('../ops/tonsofskills-security-headers.caddy', import.meta.url);
const workflowPath = new URL('../../.github/workflows/validate-plugins.yml', import.meta.url);
const packagePath = new URL('../../package.json', import.meta.url);
const marketplacePackagePath = new URL('../package.json', import.meta.url);
const policyModulePath = new URL('./security-policy.mjs', import.meta.url);

const REVIEWED_BASE_CSP =
  "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'self'; form-action 'self'; script-src 'self' https://analytics.intentsolutions.io https://www.googletagmanager.com https://cdn.jsdelivr.net https://gettermscdn.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data: https://github.com https://avatars.githubusercontent.com https://www.google-analytics.com https://www.googletagmanager.com; connect-src 'self' https://analytics.intentsolutions.io https://www.google-analytics.com https://analytics.google.com https://region1.google-analytics.com https://stats.g.doubleclick.net https://gettermscdn.com; frame-src 'self' https://gettermscdn.com; media-src 'self'; manifest-src 'self'; worker-src 'self' blob:";
const REVIEWED_CHAT_CSP = `${REVIEWED_BASE_CSP.replace(
  "; frame-src 'self'",
  " wss: ws:; frame-src 'self'",
)}`;

function assertSecurityHeaderCiWiring(workflow, packageJson) {
  assert.equal(
    workflow.split('run: pnpm run validate:security-headers').length - 1,
    1,
    'validate must invoke the security-header gate exactly once',
  );
  assert.match(workflow, /- name: Enforce marketplace response-security policy/);
  assert.match(
    packageJson.scripts['validate:security-headers'],
    /security-policy\.test\.mjs marketplace\/scripts\/install-security-headers\.test\.mjs/,
  );
  assert.match(
    packageJson.scripts['validate:security-headers'],
    /render-security-headers-caddy\.mjs --check/,
  );
}

test('policy fails closed on the high-value XSS boundaries', () => {
  const policy = serializeCsp();
  assert.equal(policy, REVIEWED_BASE_CSP, 'base CSP changed without an explicit ratchet review');
  assert.equal(
    serializeCsp(CHAT_CSP_DIRECTIVES),
    REVIEWED_CHAT_CSP,
    'chat CSP changed without an explicit ratchet review',
  );
  assert.match(policy, /default-src 'self'/);
  assert.match(policy, /object-src 'none'/);
  assert.match(policy, /base-uri 'self'/);
  assert.match(policy, /frame-ancestors 'self'/);
  assert.match(policy, /form-action 'self'/);
  assert.doesNotMatch(policy, /unsafe-eval/);
  assert.doesNotMatch(policy, /script-src[^;]*'unsafe-inline'/);
  assert.doesNotMatch(policy, /(?:^|\s)\*(?:\s|;|$)/);
  assert.doesNotMatch(policy, /(?:^|\s)wss?:/);
  assert.equal(MARKETPLACE_SECURITY_HEADERS['X-Content-Type-Options'], 'nosniff');
});

test('WebSocket schemes are scoped only to the chats route', () => {
  assert.deepEqual(CHAT_CSP_DIRECTIVES['connect-src'].slice(-2), ['wss:', 'ws:']);
  assert.equal(securityHeadersForPath('/'), MARKETPLACE_SECURITY_HEADERS);
  assert.equal(securityHeadersForPath('/plugins/example/'), MARKETPLACE_SECURITY_HEADERS);
  assert.equal(securityHeadersForPath('/chats'), MARKETPLACE_CHAT_SECURITY_HEADERS);
  assert.equal(securityHeadersForPath('/chats/'), MARKETPLACE_CHAT_SECURITY_HEADERS);
  assert.equal(securityHeadersForPath('/chats/session?id=1'), MARKETPLACE_CHAT_SECURITY_HEADERS);
  assert.equal(securityHeadersForPath('/%63hats/'), MARKETPLACE_CHAT_SECURITY_HEADERS);
  assert.equal(securityHeadersForPath('//evil.invalid/chats'), MARKETPLACE_SECURITY_HEADERS);
  assert.equal(securityHeadersForPath('http://evil.invalid/chats'), MARKETPLACE_SECURITY_HEADERS);
  assert.equal(securityHeadersForPath('/%E0%A4%A'), MARKETPLACE_SECURITY_HEADERS);
  assert.equal(securityHeadersForPath('/chats/../'), MARKETPLACE_SECURITY_HEADERS);
  assert.equal(securityHeadersForPath('/chats/%2e%2e/'), MARKETPLACE_SECURITY_HEADERS);
  assert.equal(securityHeadersForPath('/chats/../index.html'), MARKETPLACE_SECURITY_HEADERS);
  assert.equal(securityHeadersForPath('/chats-other'), MARKETPLACE_SECURITY_HEADERS);
});

test('every inline exception is explicit and justified', () => {
  for (const [directive, values] of Object.entries(CSP_DIRECTIVES)) {
    if (!values.includes("'unsafe-inline'")) continue;
    assert.ok(CSP_INLINE_JUSTIFICATIONS[directive], `${directive} needs a justification`);
  }
  assert.deepEqual(Object.keys(CSP_INLINE_JUSTIFICATIONS).sort(), ['style-src']);
});

test('tracked Caddy fragment is an exact projection of the preview policy', () => {
  assert.equal(readFileSync(caddyPath, 'utf8'), renderCaddyHeaders());
});

test('planted weakening is rejected by the policy assertions', () => {
  const missingBoundary = structuredClone(CSP_DIRECTIVES);
  delete missingBoundary['object-src'];
  assert.throws(() => validateSecurityPolicy(missingBoundary), /object-src/);

  const executableString = structuredClone(CSP_DIRECTIVES);
  executableString['script-src'] = [...executableString['script-src'], "'unsafe-eval'"];
  assert.throws(() => validateSecurityPolicy(executableString), /unsafe-eval/);

  const wildcard = structuredClone(CSP_DIRECTIVES);
  wildcard['connect-src'] = [...wildcard['connect-src'], '*'];
  assert.throws(() => validateSecurityPolicy(wildcard), /wildcard/);

  for (const [directive, source] of [
    ['object-src', 'https:'],
    ['script-src', 'https:'],
    ['base-uri', 'data:'],
  ]) {
    const broadSchemeSource = structuredClone(CSP_DIRECTIVES);
    broadSchemeSource[directive] = [...broadSchemeSource[directive], source];
    assert.throws(
      () => validateSecurityPolicy(broadSchemeSource),
      /reviewed singleton|broad scheme-only source/,
    );
  }

  assert.throws(
    () => validateSecurityPolicy(CSP_DIRECTIVES, {}),
    /style-src unsafe-inline requires/,
  );

  // A justification does not reopen script-src: inline script is refused outright.
  const inlineScript = structuredClone(CSP_DIRECTIVES);
  inlineScript['script-src'] = [...inlineScript['script-src'], "'unsafe-inline'"];
  assert.throws(
    () =>
      validateSecurityPolicy(inlineScript, {
        ...CSP_INLINE_JUSTIFICATIONS,
        'script-src': 'planted justification',
      }),
    /script-src may not allow unsafe-inline/,
  );
});

test('source-level CSP weakenings fail during module initialization', async () => {
  const source = readFileSync(policyModulePath, 'utf8');

  const broadScheme = source.replace(
    `  'script-src': [\n    "'self'",`,
    `  'script-src': [\n    "'self'",\n    'https:',`,
  );
  assert.notEqual(broadScheme, source, 'broad-scheme mutation must alter the module source');
  await assert.rejects(
    import(`data:text/javascript;base64,${Buffer.from(broadScheme).toString('base64')}`),
    /script-src may not contain the broad scheme-only source https:/,
  );

  const inlineScript = source.replace(
    `  'script-src': [\n    "'self'",`,
    `  'script-src': [\n    "'self'",\n    "'unsafe-inline'",`,
  );
  assert.notEqual(inlineScript, source, 'inline-script mutation must alter the module source');
  await assert.rejects(
    import(`data:text/javascript;base64,${Buffer.from(inlineScript).toString('base64')}`),
    /script-src may not allow unsafe-inline/,
  );

  const insecureUpgrade = source.replace(
    `  'script-src': [`,
    `  'upgrade-insecure-requests': [],\n  'script-src': [`,
  );
  assert.notEqual(insecureUpgrade, source, 'upgrade mutation must alter the module source');
  await assert.rejects(
    import(`data:text/javascript;base64,${Buffer.from(insecureUpgrade).toString('base64')}`),
    /upgrade-insecure-requests is forbidden/,
  );
});

test('required validation keeps the security policy and projection gate wired', () => {
  const workflow = readFileSync(workflowPath, 'utf8');
  const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'));
  const marketplacePackageJson = JSON.parse(readFileSync(marketplacePackagePath, 'utf8'));
  assertSecurityHeaderCiWiring(workflow, packageJson);
  assert.equal(marketplacePackageJson.scripts.preview, 'node scripts/preview.mjs');
  assert.match(
    packageJson.scripts['validate:security-headers'],
    /marketplace\/scripts\/preview\.test\.mjs/,
  );

  const plantedDisappearance = workflow.replace(
    'run: pnpm run validate:security-headers',
    'run: echo planted-security-header-gate-removal',
  );
  assert.throws(
    () => assertSecurityHeaderCiWiring(plantedDisappearance, packageJson),
    /security-header gate exactly once/,
  );
});

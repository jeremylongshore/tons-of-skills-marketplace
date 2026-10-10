import { expect, test } from '@playwright/test';

// The policy module is plain ESM and intentionally shared with Astro config.
// @ts-expect-error JavaScript policy module has no separate declaration file.
import { securityHeadersForPath } from '../scripts/security-policy.mjs';

const pages = [
  '/',
  '/skills/',
  '/plugins/skill-creator/',
  '/docs/',
  '/explore/',
  '/chats/',
  '/terms/',
  '/privacy/',
  '/acceptable-use/',
  // Pages whose scripts moved out of inline <script> and onclick (bead claude-i076).
  '/compare/',
  '/collections/',
  '/cowork/',
  '/community/',
  '/skills/abridge-ci-integration/',
];

// Third-party requests (analytics, Google Tag Manager, Google Fonts) are answered
// locally so the test never waits on hosts outside our control. This does not weaken
// the CSP check: the browser evaluates the policy before a request is issued, so a
// blocked resource never reaches the route handler and still fires a
// securitypolicyviolation event; an allowed one gets an empty, correctly typed body.
const EMPTY_BY_RESOURCE: Record<string, { contentType: string; body: string }> = {
  script: { contentType: 'application/javascript', body: '' },
  stylesheet: { contentType: 'text/css', body: '' },
  font: { contentType: 'font/woff2', body: '' },
  image: { contentType: 'image/gif', body: '' },
};

for (const path of pages) {
  test(`${path} emits the reviewed CSP without runtime violations`, async ({ page, baseURL }) => {
    const ownHost = new URL(baseURL ?? 'http://localhost:4321').host;
    await page.route('**/*', (route) => {
      const request = route.request();
      if (new URL(request.url()).host === ownHost) return route.continue();
      const empty = EMPTY_BY_RESOURCE[request.resourceType()];
      return empty
        ? route.fulfill({ status: 200, ...empty })
        : route.fulfill({ status: 204, body: '' });
    });
    await page.addInitScript(() => {
      const violations: string[] = [];
      Object.defineProperty(window, '__cspViolations', { value: violations });
      document.addEventListener('securitypolicyviolation', (event) => {
        violations.push(`${event.effectiveDirective}: ${event.blockedURI}`);
      });
    });
    const response = await page.goto(path, { waitUntil: 'networkidle' });
    expect(response?.status()).toBe(200);
    expect(response?.headers()['content-security-policy']).toBe(
      securityHeadersForPath(path)['Content-Security-Policy'],
    );
    const violations = await page.evaluate(
      // @ts-expect-error test-only property installed above.
      () => window.__cspViolations as string[],
    );
    expect(violations).toEqual([]);
  });
}

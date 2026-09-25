import { test, expect } from '@playwright/test';

/**
 * P7: Performance — Basic performance checks on production
 */

test.describe('P7: Performance', () => {
  const criticalPages = ['/', '/explore', '/cowork', '/skills/', '/plugins/'];

  for (const path of criticalPages) {
    test(`${path} loads within budget`, async ({ page }, testInfo) => {
      const isMobile = testInfo.project.name.includes('mobile');
      const budget = isMobile ? 8000 : 5000;

      const start = Date.now();
      const response = await page.goto(path, { waitUntil: 'domcontentloaded' });
      const duration = Date.now() - start;

      expect(response?.status()).toBe(200);
      expect(duration).toBeLessThan(budget);
    });
  }

  test('Homepage does not have excessively long HTML lines (iOS Safari compat)', async ({ request }) => {
    const response = await request.get('https://tonsofskills.com');
    const html = await response.text();
    const lines = html.split('\n');

    // iOS Safari fails on lines > 5000 chars
    const longLines = lines.filter(line => line.length > 5000);
    expect(longLines.length).toBe(0);
  });

  test('No broken first-party images on homepage', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    // Scope to assets we own. Third-party avatars (github.com/*.png — sponsor
    // logos, contributor avatars) are out of our control and rate-limit during
    // CI; failing on those is noise, not signal. If a third-party CDN ever
    // becomes a reliability concern, mirror the asset to /assets/.
    const images = page.locator('img');
    const count = await images.count();

    for (let i = 0; i < count; i++) {
      const img = images.nth(i);
      const src = await img.getAttribute('src');
      if (!src || src.startsWith('data:')) continue;
      if (/^https?:\/\/(?:[^/]+\.)?github(?:usercontent)?\.com\//i.test(src)) continue;

      // Skip display:none images. With loading="lazy" the browser never
      // initiates the request for hidden imgs, so naturalWidth stays 0 —
      // a false-positive. The user can't see them; their src can't be
      // "broken" from a visitor's POV. If a hidden img matters, the
      // component should preload it (loading="eager") and we'd catch it.
      const isHidden = await img.evaluate((el: HTMLImageElement) => {
        const cs = getComputedStyle(el);
        return cs.display === 'none' || cs.visibility === 'hidden';
      });
      if (isHidden) continue;

      // A loading="lazy" image below the fold is never fetched, so its
      // naturalWidth stays 0 on short viewports. Bring it into view and wait
      // for it to settle before judging it.
      await img.scrollIntoViewIfNeeded();
      await img.evaluate(
        (el: HTMLImageElement) =>
          el.complete
            ? undefined
            : new Promise((resolve) => {
                el.addEventListener('load', resolve, { once: true });
                el.addEventListener('error', resolve, { once: true });
              }),
      );
      const naturalWidth = await img.evaluate((el: HTMLImageElement) => el.naturalWidth);
      expect(naturalWidth, `Broken image: ${src}`).toBeGreaterThan(0);
    }
  });

  test('No console errors on homepage', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Filter out common third-party noise
    const realErrors = errors.filter(e =>
      !e.includes('favicon') &&
      !e.includes('third-party') &&
      !e.includes('Failed to load resource: net::ERR_BLOCKED_BY_CLIENT') &&
      !e.includes('X-Frame-Options')
    );

    expect(realErrors).toEqual([]);
  });

  test('No console errors on explore page', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('/explore');
    await page.waitForLoadState('networkidle');

    const realErrors = errors.filter(e =>
      !e.includes('favicon') &&
      !e.includes('third-party') &&
      !e.includes('Failed to load resource: net::ERR_BLOCKED_BY_CLIENT') &&
      !e.includes('X-Frame-Options')
    );

    expect(realErrors).toEqual([]);
  });
});

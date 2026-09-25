import { test, expect } from '@playwright/test';

/**
 * P6: Mobile Responsive — Tests mobile viewport rendering on key pages
 * Only runs on webkit-mobile project
 */

test.describe('P6: Mobile Responsive', () => {
  test('Homepage renders properly on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/');

    const heading = page.locator('h1').first();
    await expect(heading).toBeVisible();

    // The homepage's one action and its path to search both fit on mobile
    await expect(page.locator('button.install-copy').first()).toBeVisible();
    await expect(page.locator('a.btn-browse').first()).toBeVisible();

    // No horizontal overflow
    const body = page.locator('body');
    const bodyWidth = await body.evaluate(el => el.scrollWidth);
    const viewportWidth = 390;
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 5); // 5px tolerance
  });

  test('Explore page renders on mobile without overflow', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/explore');

    const searchInput = page.locator('.hero-search-input').first();
    await expect(searchInput).toBeVisible();

    const body = page.locator('body');
    const bodyWidth = await body.evaluate(el => el.scrollWidth);
    expect(bodyWidth).toBeLessThanOrEqual(395);
  });

  test('Cowork page renders on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/cowork');

    const heading = page.locator('h1').first();
    await expect(heading).toBeVisible();

    const megaBtn = page.locator('.mega-download-btn');
    await expect(megaBtn).toBeVisible();
  });

  test('Skills page renders on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/skills/');

    const heading = page.locator('h1').first();
    await expect(heading).toBeVisible();
  });

  test('Navigation is accessible on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/');

    // Check nav is present (may be hamburger menu)
    const nav = page.locator('nav, header, [role="navigation"]').first();
    await expect(nav).toBeVisible();
  });

  test('Plugin detail page renders on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/plugins/');

    const pluginLink = page.locator('a[href*="/plugins/"]').first();
    const isVisible = await pluginLink.isVisible().catch(() => false);

    if (isVisible) {
      const href = await pluginLink.getAttribute('href');
      if (href) {
        await page.goto(href);
        const title = await page.title();
        expect(title).not.toContain('404');
      }
    }
  });
});

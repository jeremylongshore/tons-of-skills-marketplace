import { test, expect, type Page } from '@playwright/test';

/**
 * P2: Search Flow — Tests search from homepage through explore page results
 */

/**
 * The explore page loads fuse.js from jsdelivr (top-level ESM import) and
 * fetches the ~2.9MB /data/unified-search-index.json before any result can
 * render (measured 1.4–3.5s against production). When the index is ready the
 * page sets #results-grid aria-busy="false" and removes #explore-loading —
 * wait on that deterministic signal instead of sleeping.
 */
async function waitForSearchIndex(page: Page): Promise<void> {
  await page.locator('#results-grid[aria-busy="false"]').waitFor({ timeout: 20_000 });
}

const RESULTS_INFO_PATTERN = /Showing \d+ of \d+/;

test.describe('P2: Search Flow', () => {
  // Search is reached from the homepage through Browse since the #1152
  // redesign removed the homepage search box.
  test('Homepage Browse reaches a working explore search', async ({ page }) => {
    await page.goto('/');

    await Promise.all([
      page.waitForURL(/\/explore\/?$/),
      page.locator('a.btn-browse').first().click(),
    ]);

    await expect(page.locator('.hero-search-input').first()).toBeVisible();
  });

  test('Explore page search input is functional', async ({ page }) => {
    await page.goto('/explore');

    const searchInput = page.locator('.hero-search-input').first();
    await expect(searchInput).toBeVisible();

    await searchInput.fill('security');
    await expect(searchInput).toHaveValue('security');
  });

  test('Search returns results for known plugin', async ({ page }) => {
    await page.goto('/explore');
    await waitForSearchIndex(page);

    const searchInput = page.locator('.hero-search-input').first();
    await searchInput.fill('prettier');

    // Should have at least one result card visible — scoped to the results
    // grid so the (mobile-hidden) header nav links can never satisfy this
    const resultCards = page
      .locator('#results-grid')
      .locator('a[href*="/plugins/"], a[href*="/skills/"]');
    await expect(resultCards.first()).toBeVisible({ timeout: 10_000 });
    await expect.poll(() => resultCards.count(), { timeout: 10_000 }).toBeGreaterThan(0);

    // Secondary signal: the client-side render updated the results counter
    await expect(page.locator('#results-info')).toHaveText(RESULTS_INFO_PATTERN);
  });

  test('Search returns results for known skill', async ({ page }) => {
    await page.goto('/explore');
    await waitForSearchIndex(page);

    const searchInput = page.locator('.hero-search-input').first();
    await searchInput.fill('genkit');

    // Scoped to the results grid so the (mobile-hidden) header nav /cowork
    // link can never satisfy this
    const resultCards = page
      .locator('#results-grid')
      .locator('a[href*="/plugins/"], a[href*="/skills/"], a[href*="/cowork"]');
    await expect(resultCards.first()).toBeVisible({ timeout: 10_000 });
    await expect.poll(() => resultCards.count(), { timeout: 10_000 }).toBeGreaterThan(0);

    // Secondary signal: the client-side render updated the results counter
    await expect(page.locator('#results-info')).toHaveText(RESULTS_INFO_PATTERN);
  });

  test('Empty search query shows no-results state gracefully', async ({ page }) => {
    await page.goto('/explore');
    await waitForSearchIndex(page);

    const searchInput = page.locator('.hero-search-input').first();
    await searchInput.fill('xyznonexistent999zzz');

    // Page should not crash — the results counter still renders
    await expect(page.locator('#results-info')).toHaveText(RESULTS_INFO_PATTERN);
    await expect(page).toHaveTitle(/Explore/);
  });

  test('Search results link to valid pages', async ({ page }) => {
    await page.goto('/explore');
    await waitForSearchIndex(page);

    const searchInput = page.locator('.hero-search-input').first();
    await searchInput.fill('security');

    // Scoped to the results grid so the (mobile-hidden) header nav /cowork
    // link can never satisfy this
    const firstResult = page
      .locator('#results-grid')
      .locator('a[href*="/plugins/"], a[href*="/skills/"], a[href*="/cowork"]')
      .first();
    await expect(firstResult).toBeVisible({ timeout: 10_000 });

    // Secondary signal: the client-side render updated the results counter
    await expect(page.locator('#results-info')).toHaveText(RESULTS_INFO_PATTERN);

    const href = await firstResult.getAttribute('href');
    expect(href).toBeTruthy();

    await firstResult.click();
    await page.waitForLoadState('networkidle');
    // Should land on a valid page (not 404)
    const title = await page.title();
    expect(title).not.toContain('404');
  });
});

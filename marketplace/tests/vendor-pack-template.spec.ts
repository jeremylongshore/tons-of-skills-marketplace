import { readFileSync } from 'node:fs';
import { expect, test } from '@playwright/test';

const { vendors }: typeof import('../src/data/vendor-packs.json') = JSON.parse(
  readFileSync(new URL('../src/data/vendor-packs.json', import.meta.url), 'utf8'),
);
const countOnly = new Set(['cursor', 'klingai', 'openrouter', 'sentry', 'supabase', 'vercel']);
const normalize = (text: string) => text.replace(/\s+/g, ' ').trim();

test('every vendor route retains its own content and local count provenance', async ({ page }) => {
  test.setTimeout(120_000);
  const pageErrors: string[] = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
  expect(vendors).toHaveLength(28);
  for (const vendor of vendors) {
    await test.step(vendor.id, async () => {
      const response = await page.goto(`/learn/${vendor.id}/`);
      expect(response?.status()).toBe(200);
      await expect(page).toHaveTitle(
        new RegExp(`${vendor.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')} Skill Pack`),
      );
      await expect(page.locator('.pack-title')).toHaveText(`${vendor.name} Pack`);
      await expect(page.locator('.pack-subtitle')).toHaveText(vendor.description);
      await expect(page.locator('#install-cmd')).toHaveText(vendor.installCommand);
      await expect(page.locator('meta[name="description"]')).toHaveAttribute(
        'content',
        `Complete ${vendor.name} integration covering ${vendor.description.toLowerCase()}.`,
      );

      const tier = countOnly.has(vendor.id) ? '' : `${vendor.tier} - `;
      const counts = page.locator('[data-count-provenance="vendor-pack-local"]');
      expect((await counts.allTextContents()).map(normalize)).toEqual([
        `${tier}${vendor.skillCount} vendor-pack-local skills`,
        ...vendor.categories.map(
          (category) => `${category.skills.length} vendor-pack-local skills`,
        ),
      ]);
      expect((await page.locator('.category-title').allTextContents()).map(normalize)).toEqual(
        vendor.categories.map(
          (category) => `${category.name} ${category.skills.length} vendor-pack-local skills`,
        ),
      );
      expect((await page.locator('.skill-slot').allTextContents()).map(normalize)).toEqual(
        vendor.categories.flatMap((category) => category.skills),
      );
      const links = page.locator('.links-section a');
      await expect(links).toHaveCount(2);
      for (const [index, url] of [vendor.docsUrl, vendor.dashboardUrl].entries()) {
        await expect(links.nth(index)).toHaveAttribute('href', url);
        await expect(links.nth(index)).toHaveAttribute('target', '_blank');
        await expect(links.nth(index)).toHaveAttribute('rel', /\bnoopener\b/);
      }
      expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
        page.viewportSize()!.width,
      );
    });
  }
  expect(pageErrors).toEqual([]);
});

// Includes both badge modes and every incumbent presentation variant.
for (const id of ['apollo', 'supabase', 'cursor', 'klingai', 'openrouter', 'vercel']) {
  test(`${id}: the copy control writes its own command once and restores its label`, async ({
    page,
  }) => {
    const vendor = vendors.find((entry) => entry.id === id)!;
    await page.addInitScript(() => {
      const state = window as unknown as { __vendorCopies: string[] };
      state.__vendorCopies = [];
      Object.defineProperty(navigator, 'clipboard', {
        configurable: true,
        value: {
          writeText: async (text: string) => {
            state.__vendorCopies.push(text);
          },
        },
      });
    });
    await page.goto(`/learn/${id}/`);
    await expect(page.getByRole('button', { name: 'Copy', exact: true })).toBeVisible();
    const copy = page.locator('.copy-btn');
    await copy.click();
    await expect(copy).toHaveText('Copied!');
    expect(
      await page.evaluate(() => (window as unknown as { __vendorCopies: string[] }).__vendorCopies),
    ).toEqual([vendor.installCommand]);
    await expect(copy).toHaveText('Copy');
    expect(
      await page.evaluate(() => (window as unknown as { __vendorCopies: string[] }).__vendorCopies),
    ).toEqual([vendor.installCommand]);
  });
}

test('clipboard rejection reports failure and restores an actionable copy control', async ({
  page,
}) => {
  const pageErrors: string[] = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {
        writeText: async () => {
          throw new Error('Synthetic clipboard denial');
        },
      },
    });
  });
  await page.goto('/learn/supabase/');
  const copy = page.locator('.copy-btn');
  await copy.click();
  await expect(copy).toHaveText('Copy failed');
  await expect(copy).toHaveAttribute('aria-live', 'polite');
  await expect(copy).toHaveAttribute('aria-label', /copy it manually/);
  await expect(copy).toHaveText('Copy');
  expect(pageErrors).toEqual([]);
});

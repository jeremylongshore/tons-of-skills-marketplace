import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { expect, test } from '@playwright/test';

const { vendors }: typeof import('../src/data/vendor-packs.json') = JSON.parse(
  readFileSync(new URL('../src/data/vendor-packs.json', import.meta.url), 'utf8'),
);
const countOnly = new Set(['cursor', 'klingai', 'openrouter', 'sentry', 'supabase', 'vercel']);
const normalize = (text: string) => text.replace(/\s+/g, ' ').trim();

test('vendor curricula and install commands resolve to the published local packs', () => {
  const { plugins } = JSON.parse(
    readFileSync(
      new URL('../../.claude-plugin/marketplace.extended.json', import.meta.url),
      'utf8',
    ),
  );
  for (const vendor of vendors) {
    const install = /^\/plugin install ([a-z0-9-]+)@claude-code-plugins-plus$/.exec(
      vendor.installCommand,
    );
    expect(install, vendor.id).not.toBeNull();
    const plugin = plugins.find((entry: { name: string }) => entry.name === install![1]);
    expect(plugin, `${vendor.id}: registered install identity`).toBeDefined();
    const root = new URL(`../../${plugin.source.replace(/^\.\//, '')}/skills/`, import.meta.url);
    const actual = readdirSync(root, { withFileTypes: true })
      .filter((entry) => entry.isDirectory() && existsSync(new URL(`${entry.name}/SKILL.md`, root)))
      .map((entry) => entry.name)
      .sort();
    const listed = vendor.categories.flatMap((category) => category.skills).sort();
    expect(listed, vendor.id).toEqual(actual);
    expect(new Set(listed).size, `${vendor.id}: no repeated skills`).toBe(listed.length);
    expect(vendor.skillCount, vendor.id).toBe(actual.length);
  }
});

test('the hub reports actual per-pack ranges and Sentry uses the shared theme', async ({
  page,
}) => {
  await page.goto('/learn/');
  const tiers = await page.locator('.tier-section').allTextContents();
  for (const [index, tier] of ['flagship+', 'flagship', 'pro', 'standard']
    .filter((name) => vendors.some((vendor) => vendor.tier === name))
    .entries()) {
    const counts = vendors
      .filter((vendor) => vendor.tier === tier)
      .map((vendor) => vendor.skillCount);
    const low = Math.min(...counts);
    const high = Math.max(...counts);
    const label = low === high ? `${low}` : `${low}–${high}`;
    expect(normalize(tiers[index])).toContain(`${label} vendor-pack-local skills per pack`);
  }
  await test.info().attach('learning-hub-counts', {
    body: await page.screenshot({ fullPage: false }),
    contentType: 'image/png',
  });
  await page.goto('/learn/sentry/');
  await expect(page.locator('.pack-hero')).toHaveClass(/vendor-default/);
  await expect(page.locator('.vendor-purple')).toHaveCount(0);
  await test.info().attach('sentry-shared-theme', {
    body: await page.screenshot({ fullPage: false }),
    contentType: 'image/png',
  });
});

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
      await expect(links.nth(1).locator('.link-title')).toHaveText(
        vendor.dashboardLabel ?? 'Dashboard',
      );
      for (const [index, url] of [vendor.docsUrl, vendor.dashboardUrl].entries()) {
        await expect(links.nth(index)).toHaveAttribute('href', url);
        await expect(links.nth(index)).toHaveAttribute('target', '_blank');
        await expect(links.nth(index)).toHaveAttribute('rel', /\bnoopener\b/);
      }
      expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
        page.viewportSize()!.width,
      );
      if (vendor.id === 'langchain') {
        await test.info().attach('langchain-python-curriculum', {
          body: await page.screenshot({ fullPage: false }),
          contentType: 'image/png',
        });
      }
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

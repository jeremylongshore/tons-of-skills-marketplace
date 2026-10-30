import { expect, test } from '@playwright/test';
import { readFileSync } from 'node:fs';

const searchIndex = JSON.parse(
  readFileSync(new URL('../src/data/unified-search-index.json', import.meta.url), 'utf8'),
);
import { buildComparisonLookup, comparisonKey, resolveComparison } from '../src/lib/comparison.mjs';

const lookup = buildComparisonLookup(searchIndex.items);
const collision = 'agency-os';

test('every real cross-type collision resolves both artifacts without shadowing', () => {
  const original = Object.fromEntries(
    searchIndex.items.map((item) => [item.id || item.name, item]),
  );
  const groups = new Map<string, string[]>();
  for (const item of searchIndex.items.filter((item) => ['plugin', 'skill'].includes(item.type))) {
    const id = item.id || item.name;
    groups.set(id, [...(groups.get(id) || []), item.type]);
  }
  expect(lookup.ambiguous.sort()).toEqual(
    [...groups]
      .filter(([, types]) => types.length > 1)
      .map(([id]) => id)
      .sort(),
  );
  expect(lookup.ambiguous).toContain(collision);
  expect(original[collision].type).toBe('skill');
  for (const id of lookup.ambiguous) {
    const rows = searchIndex.items.filter((item) => (item.id || item.name) === id);
    expect(rows.map((item) => item.type).sort()).toEqual(['plugin', 'skill']);
    expect(resolveComparison(rows.map(comparisonKey), lookup).items).toEqual(rows);
    expect(resolveComparison([id], lookup).rejected).toEqual([
      { reference: id, reason: 'ambiguous' },
    ]);
  }
});

test('typed URL keeps same-ID plugin and skill distinct when removing and sharing', async ({
  page,
}) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {
        writeText: (text: string) => {
          (window as unknown as { copied: string }).copied = text;
          return Promise.resolve();
        },
      },
    });
  });
  await page.goto(
    `/compare/?items=${encodeURIComponent(`plugin:${collision},skill:${collision}`)}`,
  );
  await expect(page.locator('#type-1')).toHaveText('plugin');
  await expect(page.locator('#type-2')).toHaveText('skill');
  await expect(page.locator('#header-1 a')).toHaveAttribute('href', `/plugins/${collision}/`);
  await page.locator('#header-1 [data-remove-id]').click();
  await expect(page.locator('#type-1')).toHaveText('skill');
  expect(new URL(page.url()).searchParams.get('items')).toBe(`skill:${collision}`);
  await page.locator('#share-comparison').click();
  expect(await page.evaluate(() => (window as unknown as { copied: string }).copied)).toBe(
    page.url(),
  );
  await page.reload();
  await expect(page.locator('#type-1')).toHaveText('skill');
});

test('typed saved selections generate distinct share references', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem(
      'compare-items',
      JSON.stringify([
        { id: 'agency-os', type: 'plugin', name: 'Agency plugin' },
        { id: 'agency-os', type: 'skill', name: 'Agency skill' },
      ]),
    );
  });
  await page.goto('/compare/');
  await expect(page.locator('#type-1')).toHaveText('plugin');
  await expect(page.locator('#type-2')).toHaveText('skill');
  expect(new URL(page.url()).searchParams.get('items')).toBe(
    `plugin:${collision},skill:${collision}`,
  );
  await page.goto('/explore/');
  await expect(page.locator('#compare-items .compare-item')).toHaveCount(2);
  await expect(page.locator('#compare-go')).toHaveAttribute(
    'href',
    `/compare/?items=${encodeURIComponent(`plugin:${collision},skill:${collision}`)}`,
  );
  await page.locator('[data-remove-id="agency-os"][data-remove-type="plugin"]').click();
  await expect(page.locator('#compare-items .compare-item')).toHaveCount(1);
  expect(await page.evaluate(() => JSON.parse(localStorage.getItem('compare-items')!))).toEqual([
    { id: 'agency-os', type: 'skill', name: 'Agency skill' },
  ]);
});

test('ambiguous legacy URL is explicit and never silently replaced by saved selection', async ({
  page,
}, testInfo) => {
  await page.addInitScript(() =>
    localStorage.setItem(
      'compare-items',
      JSON.stringify([{ id: 'agency-os', type: 'plugin', name: 'Agency plugin' }]),
    ),
  );
  await page.goto(`/compare/?items=${collision}`);
  await expect(page.locator('#comparison-notice')).toContainText('shared by a plugin and a skill');
  await expect(page.locator('#compare-content')).toBeHidden();
  await testInfo.attach('ambiguous-link-recovery', {
    body: await page.screenshot(),
    contentType: 'image/png',
  });
  for (const type of ['plugin', 'skill']) {
    await page.goto(`/compare/?items=${collision}`);
    await page.getByRole('button', { name: new RegExp(`^Use ${type}:`) }).click();
    await expect(page.locator('#type-1')).toHaveText(type);
    await expect(page.locator('#comparison-notice')).toBeHidden();
    expect(new URL(page.url()).searchParams.get('items')).toBe(`${type}:${collision}`);
  }
});

test('unambiguous legacy links keep their artifact; unknown references are explicit', async ({
  page,
}) => {
  const row = searchIndex.items.find(
    (item) => item.type === 'plugin' && !lookup.ambiguous.includes(item.id || item.name),
  )!;
  const id = row.id || row.name;
  await page.goto(`/compare/?items=${encodeURIComponent(id)}`);
  await expect(page.locator('#header-1 a')).toHaveAttribute('href', `/plugins/${row.name}/`);
  await expect(page.locator('#comparison-notice')).toBeHidden();
  await page.goto('/compare/?items=unknown-artifact,__proto__,constructor');
  await expect(page.locator('#comparison-notice')).toContainText('could not be found');
  await expect(page.locator('#compare-content')).toBeHidden();
});

test('malformed storage is ignored rather than crashing the comparison', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('compare-items', '{"not":"an array"}'));
  await page.goto('/compare/');
  await expect(page.locator('#empty-state')).toBeVisible();
  await page.goto('/explore/');
  await expect(page.locator('#compare-items .compare-item')).toHaveCount(0);
});

test('comparison manager accepts both types and refuses only the same typed item', async ({
  page,
}) => {
  await page.goto('/explore/');
  await expect
    .poll(() => page.evaluate(() => typeof (window as any).CompareManager?.add))
    .toBe('function');
  const result = await page.evaluate(() => {
    const manager = (window as any).CompareManager;
    const plugin = { id: 'agency-os', name: 'Agency plugin', type: 'plugin' };
    const skill = { id: 'agency-os', name: 'Agency skill', type: 'skill' };
    return [manager.add(plugin), manager.add(skill), manager.add(plugin)];
  });
  expect(result).toEqual([true, true, false]);
  await expect(page.locator('#compare-items .compare-item')).toHaveCount(2);
});

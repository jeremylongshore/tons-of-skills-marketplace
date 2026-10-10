import { expect, test, type Page } from '@playwright/test';

// Buttons that used inline onclick attributes now bind by event delegation,
// so script-src can drop 'unsafe-inline' (bead claude-i076). Each test clicks
// a converted button and checks the behavior, including buttons rendered into
// the page at runtime.

// Record clipboard writes instead of depending on clipboard permissions.
async function recordClipboard(page: Page) {
  await page.addInitScript(() => {
    (window as unknown as { __copied: string[] }).__copied = [];
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {
        writeText: (text: string) => {
          (window as unknown as { __copied: string[] }).__copied.push(text);
          return Promise.resolve();
        },
      },
    });
  });
}

const copied = (page: Page) =>
  page.evaluate(() => (window as unknown as { __copied: string[] }).__copied);

test.describe('delegated click handlers', () => {
  test('collections: Copy Install copies the collection install commands', async ({ page }) => {
    await recordClipboard(page);
    await page.goto('/collections/');
    const btn = page.locator('.collection-card .install-btn[data-plugins]').first();
    const plugins = (await btn.getAttribute('data-plugins'))!.split(',');
    await btn.click();
    await expect.poll(() => copied(page)).toEqual([
      plugins.map((p) => `/plugin install ${p}@claude-code-plugins-plus`).join('\n'),
    ]);
  });

  test('explore: runtime "Clear All Filters" button resets the search', async ({ page }) => {
    await page.goto('/explore/');
    // The grid renders after the catalog fetch; wait for it before searching.
    await expect(page.locator('.pcard').first()).toBeVisible();
    await page.locator('#main-search').fill('qxjvqxjvqxjvqxjv');
    const clear = page.locator('[data-action="clear-all-filters"]');
    await expect(clear).toBeVisible();
    await clear.click();
    await expect(page.locator('#main-search')).toHaveValue('');
    await expect(clear).toHaveCount(0);
    await expect(page.locator('.pcard').first()).toBeVisible();
    await expect(page.locator('.author-toggle .type-btn[data-author="all"]')).toHaveClass(/active/);
  });

  test('skills: both "Clear Filters" buttons reset the search', async ({ page }) => {
    await page.goto('/skills/');
    // Filtering is a no-op until the skills catalog fetch completes.
    await page.waitForLoadState('networkidle');
    const search = page.locator('#search-input');
    await search.fill('qxjvqxjvqxjvqxjv');
    const runtime = page.locator('.no-results [data-action="clear-filters"]');
    await expect(runtime).toBeVisible();
    await runtime.click();
    await expect(search).toHaveValue('');
    await expect(runtime).toHaveCount(0);

    await search.fill('qxjvqxjvqxjvqxjv');
    await page.locator('.clear-filters-btn[data-action="clear-filters"]').click();
    await expect(search).toHaveValue('');
  });

  test('compare bar: remove button drops the item, and item text is escaped', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem(
        'compare-items',
        JSON.stringify([
          { id: 'a-item', name: '<img src=x onerror="window.__xss=1">', type: 'plugin' },
          { id: "b'item", name: 'second', type: 'skill' },
        ]),
      );
    });
    await page.goto('/explore/');
    const items = page.locator('#compare-items .compare-item');
    await expect(items).toHaveCount(2);
    await expect(page.locator('#compare-items img')).toHaveCount(0);
    await expect(items.first().locator('.compare-item-name')).toHaveText('<img src=x onerror="window.__xss=1">');

    // An id with a quote broke the old onclick string; delegation handles it.
    await page.locator('#compare-items [data-remove-id="b\'item"]').click();
    await expect(items).toHaveCount(1);
    const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('compare-items')!));
    expect(saved.map((i: { id: string }) => i.id)).toEqual(['a-item']);
    expect(await page.evaluate(() => (window as unknown as { __xss?: number }).__xss)).toBeUndefined();
  });

  test('compare page: Copy and Remove buttons work', async ({ page }) => {
    await recordClipboard(page);
    await page.goto('/compare/');
    const ids = await page.evaluate(() =>
      Object.keys(JSON.parse(document.getElementById('compare-items-data')!.textContent!)).slice(0, 2),
    );
    await page.goto(`/compare/?items=${encodeURIComponent(ids.join(','))}`);

    const copy = page.locator('#install-1 [data-copy-cmd]');
    const cmd = await copy.getAttribute('data-copy-cmd');
    expect(cmd).toMatch(/^\/plugin install .+@claude-code-plugins-plus$/);
    await copy.click();
    await expect.poll(() => copied(page)).toEqual([cmd]);

    await page.locator('#header-1 [data-remove-id]').click();
    await expect.poll(() => new URL(page.url()).searchParams.get('items')).toBe(ids[1]);
  });

  test('community: hall-of-fame author link is not nested in the card link', async ({ page }) => {
    await page.goto('/community/');
    const card = page.locator('.hof-card').first();
    await expect(card.locator('.hof-card-link')).toHaveAttribute('href', /.+/);
    const author = card.locator('a.hof-author-link');
    await expect(author).toHaveAttribute('href', /^https:\/\/github\.com\//);
    expect(await author.evaluate((a) => a.parentElement!.closest('a'))).toBeNull();

    // The headline link stretches over the card: a point on the card body
    // hit-tests to that link, while the author link stays clickable above it.
    await card.scrollIntoViewIfNeeded();
    const hit = await card.evaluate((el) => {
      const r = el.getBoundingClientRect();
      const top = document.elementFromPoint(r.left + r.width / 2, r.bottom - 8);
      return top?.closest('a')?.className;
    });
    expect(hit).toBe('hof-card-link');
    const authorHit = await author.evaluate((a) => {
      const r = a.getBoundingClientRect();
      return document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2)?.closest('a') === a;
    });
    expect(authorHit).toBe(true);
  });
});

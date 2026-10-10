import { expect, test, type Page } from '@playwright/test';

// Behavior of the page- and component-scoped scripts that moved from
// is:inline <script> blocks to bundled modules, so script-src can drop
// 'unsafe-inline' (bead claude-i076). Each test exercises one script and
// passes on both the inline and the bundled build.

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

test.describe('page scripts', () => {
  test('skill page: install command copies its data-copy text', async ({ page }) => {
    await recordClipboard(page);
    await page.goto('/skills/');
    const href = await page.locator('.skills-grid a[href^="/skills/"]').first().getAttribute('href');
    await page.goto(href!);
    const cmd = page.locator('.install-command[data-copy]').first();
    const text = await cmd.getAttribute('data-copy');
    await cmd.click();
    await expect(cmd).toHaveText('Copied to clipboard!');
    expect(await page.evaluate(() => (window as unknown as { __copied: string[] }).__copied)).toEqual([text]);
  });

  test('cowork: plugin search filters the list and updates the count', async ({ page }) => {
    await page.goto('/cowork/');
    const items = page.locator('#plugin-list .plugin-item');
    const total = await items.count();
    expect(total).toBeGreaterThan(1);
    const name = await items.first().getAttribute('data-name');
    await page.locator('#plugin-search').fill(name!);
    await expect(page.locator('#plugin-count')).toContainText('Showing');
    await expect(page.locator('#plugin-count')).not.toContainText(`Showing all`);
    const visible = await items.evaluateAll((els) => els.filter((e) => (e as HTMLElement).style.display !== 'none').length);
    expect(visible).toBeGreaterThan(0);
    expect(visible).toBeLessThan(total);
  });

  test('cowork: download button shows the download toast', async ({ page }) => {
    await page.route('**/downloads/**', (route) => route.abort());
    await page.goto('/cowork/');
    const btn = page.locator('.download-btn[data-category]').first();
    const category = await btn.getAttribute('data-category');
    // Fire the click without following the download link.
    await btn.evaluate((a) => a.addEventListener('click', (e) => e.preventDefault(), { once: true }));
    await btn.click();
    await expect(page.getByText(`Downloading ${category} pack...`)).toBeVisible();
  });

  test('community: contributor card expands and collapses', async ({ page }) => {
    await page.goto('/community/');
    const card = page.locator('.contributor-card').first();
    await card.scrollIntoViewIfNeeded();
    const before = await card.getAttribute('aria-expanded');
    await card.locator('.contributor-name').click();
    await expect(card).toHaveAttribute('aria-expanded', before === 'true' ? 'false' : 'true');
    await card.press('Enter');
    await expect(card).toHaveAttribute('aria-expanded', before === 'true' ? 'true' : 'false');
  });

  test('collections: killer skill card opens its link', async ({ page, context }) => {
    await page.goto('/collections/');
    const card = page.locator('.killer-card');
    const href = await card.getAttribute('data-href');
    const external = (await card.getAttribute('data-external')) === 'true';
    await context.route(/github\.com/, (route) => route.fulfill({ status: 200, body: 'ok' }));
    if (external) {
      const popup = context.waitForEvent('page');
      await card.locator('.killer-headline').click();
      expect((await popup).url()).toBe(href);
    } else {
      await card.locator('.killer-headline').click();
      await expect(page).toHaveURL(new RegExp(href!.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
    }
  });

  test('legal pages: GetTerms embed loader is present', async ({ page }) => {
    await page.route('**/gettermscdn.com/**', (route) => route.abort());
    for (const path of ['/privacy/', '/terms/', '/acceptable-use/']) {
      await page.goto(path);
      await expect(page.locator('script#getterms-embed-js')).toHaveAttribute(
        'src',
        'https://gettermscdn.com/dist/js/embed.js',
      );
    }
  });
});

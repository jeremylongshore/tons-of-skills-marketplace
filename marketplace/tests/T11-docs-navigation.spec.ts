import { expect, test } from '@playwright/test';

// claude-4ntw: exercise the published docs UI, including server-rendered metadata.
const firstPlugin = '/docs/getting-started/first-plugin';

test.describe('Documentation navigation', () => {
  test('the docs hub leads to a readable getting-started guide', async ({ page }) => {
    const response = await page.goto('/docs/');
    expect(response?.status()).toBe(200);
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Learn Claude Code Plugins');
    const cards = page.locator('.doc-card');
    expect(await cards.count()).toBeGreaterThan(0);
    await expect(cards.first()).toBeVisible();

    await page.getByRole('main').getByRole('link', { name: 'Get Started', exact: true }).click();
    await expect(page).toHaveURL(/\/docs\/getting-started\/installation\/?$/);
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    await expect(page.locator('#docs-content')).toContainText('Claude Code');
  });

  test('the desktop sidebar changes articles and marks the current page', async ({ page }) => {
    // Exercise the desktop layout in each browser, including mobile WebKit.
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto(firstPlugin);
    const sidebar = page.locator('#docs-sidebar');
    await expect(sidebar).toBeVisible();
    const skillsLink = sidebar.locator('a[href="/docs/concepts/skills"]');
    const title = await skillsLink.innerText();
    await skillsLink.click();

    await expect(page).toHaveURL(/\/docs\/concepts\/skills\/?$/);
    await expect(page.getByRole('heading', { level: 1 })).toHaveText(title);
    await expect(sidebar.locator('.sidebar-link.active')).toHaveCount(1);
    await expect(sidebar.locator('.sidebar-link.active')).toHaveAttribute(
      'href',
      '/docs/concepts/skills',
    );
    await expect(page.locator('#docs-content')).toContainText('SKILL.md');

    await sidebar.getByRole('link', { name: 'Documentation', exact: true }).click();
    await expect(page).toHaveURL(/\/docs\/?$/);
    await expect(page.locator('.doc-card').first()).toBeVisible();
  });

  test('breadcrumbs and previous/next links navigate between readable articles', async ({
    page,
  }) => {
    await page.goto(firstPlugin);
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Install Your First Plugin');
    const breadcrumbs = page.getByRole('navigation', { name: 'Breadcrumb' });
    await expect(breadcrumbs).toContainText('Getting Started');
    await expect(breadcrumbs).toContainText('Install Your First Plugin');
    await expect(
      page.locator('#docs-content').getByRole('heading', { name: 'Overview', exact: true }),
    ).toBeVisible();
    await expect(page.locator('#docs-content')).toContainText('ccpi install api-test-automation');

    await page.locator('.nav-prev').click();
    await expect(page).toHaveURL(/\/docs\/getting-started\/installation\/?$/);
    await expect(page.locator('#docs-content')).toBeVisible();
    await page.locator('.nav-next').click();
    await expect(page).toHaveURL(/\/docs\/getting-started\/first-plugin\/?$/);
    await page.locator('.nav-next').click();
    await expect(page).toHaveURL(/\/docs\/getting-started\/first-skill\/?$/);
    await expect(page.locator('#docs-content')).toContainText('SKILL.md');

    await breadcrumbs.getByRole('link', { name: 'Docs', exact: true }).click();
    await expect(page).toHaveURL(/\/docs\/?$/);
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Learn Claude Code Plugins');
  });

  test('the sidebar collapses on mobile while article navigation remains usable', async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(firstPlugin);
    const sidebar = page.locator('#docs-sidebar');
    await expect(sidebar).toBeHidden();
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    await expect(page.locator('#docs-content')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
      390,
    );

    await page.locator('.nav-next').click();
    await expect(page).toHaveURL(/\/docs\/getting-started\/first-skill\/?$/);
    await expect(page.locator('#docs-content')).toContainText('SKILL.md');
    await expect(sidebar).toBeHidden();

    await page.setViewportSize({ width: 1280, height: 900 });
    await expect(sidebar).toBeVisible();
    await expect(sidebar.locator('.sidebar-link.active')).toHaveAttribute(
      'href',
      '/docs/getting-started/first-skill',
    );
  });

  test('the HTML response contains TechArticle metadata matching the article', async ({ page }) => {
    const response = await page.goto(firstPlugin);
    expect(response?.status()).toBe(200);
    const html = await response!.text();
    // Inspect the response, so client-side insertion cannot masquerade as SSR.
    const schemas = [
      ...html.matchAll(/<script\b[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g),
    ].map((match) => JSON.parse(match[1]));
    const articles = schemas.filter((schema) => schema['@type'] === 'TechArticle');
    expect(articles).toHaveLength(1);
    const article = articles[0];
    expect(article['@context']).toBe('https://schema.org');
    expect(article.headline).toBe(await page.getByRole('heading', { level: 1 }).innerText());
    expect(article.description).toBe(await page.locator('.docs-description').innerText());
    expect(article.url).toBe(`https://tonsofskills.com${firstPlugin}`);
    expect(article.mainEntityOfPage['@id']).toBe(article.url);
  });

  test('official documentation opens externally without replacing the article', async ({
    page,
    context,
  }) => {
    // Verify browser navigation without depending on the vendor's availability.
    await context.route('https://code.claude.com/**', (route) =>
      route.fulfill({
        contentType: 'text/html',
        body: '<h1>Official documentation destination</h1>',
      }),
    );
    await page.goto(firstPlugin);
    const link = page.locator('.official-links').getByRole('link', {
      name: 'Claude Code Plugins Documentation',
      exact: true,
    });
    await expect(link).toHaveAttribute('href', 'https://code.claude.com/docs/en/plugins');
    await expect(link).toHaveAttribute('target', '_blank');
    await expect(link).toHaveAttribute('rel', /\bnoopener\b/);
    await expect(link).toHaveAttribute('rel', /\bnoreferrer\b/);
    const popupPromise = page.waitForEvent('popup');
    await link.click();
    const popup = await popupPromise;
    await expect(popup).toHaveURL('https://code.claude.com/docs/en/plugins');
    await expect(popup.getByRole('heading')).toHaveText('Official documentation destination');
    expect(await popup.evaluate(() => window.opener === null)).toBe(true);
    await expect(page).toHaveURL(/\/docs\/getting-started\/first-plugin\/?$/);
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Install Your First Plugin');
    await popup.close();
  });
});

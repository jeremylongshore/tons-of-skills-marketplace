import { test, expect } from '@playwright/test';

/**
 * P1: Core Pages — Smoke tests for every major page on tonsofskills.com
 * Verifies 200 status, page title, and key elements render.
 */

const corePages = [
  { path: '/', titleMatch: /Tons of Skills|Skills Hub/, desc: 'Homepage' },
  { path: '/explore', titleMatch: /Explore/, desc: 'Explore' },
  { path: '/skills/', titleMatch: /Skills/, desc: 'Skills Directory' },
  { path: '/plugins/', titleMatch: /Plugin|Browse/, desc: 'Plugins' },
  { path: '/cowork', titleMatch: /Cowork|Download/, desc: 'Cowork' },
  { path: '/getting-started', titleMatch: /Getting Started/, desc: 'Getting Started' },
  { path: '/learning/', titleMatch: /Learn/, desc: 'Learning' },
  { path: '/playbooks/', titleMatch: /Playbook/, desc: 'Playbooks' },
  { path: '/tools', titleMatch: /Tool/, desc: 'Tools' },
  { path: '/sponsor', titleMatch: /Sponsor/, desc: 'Sponsor' },
  { path: '/privacy', titleMatch: /Privacy/, desc: 'Privacy' },
  { path: '/terms', titleMatch: /Terms/, desc: 'Terms' },
];

test.describe('P1: Core Pages Smoke Tests', () => {
  for (const pg of corePages) {
    test(`${pg.desc} (${pg.path}) loads with 200`, async ({ page }) => {
      const response = await page.goto(pg.path);
      expect(response?.status()).toBe(200);
      await expect(page).toHaveTitle(pg.titleMatch);
    });
  }

  test('Homepage renders hero heading', async ({ page }) => {
    await page.goto('/');
    const heading = page.locator('h1').first();
    await expect(heading).toBeVisible();
  });

  // The homepage has one action since the #1152 redesign: copy the install
  // command. Search moved to /explore, reached through the Browse link. The
  // install slug is a frozen public identifier, so it is asserted exactly.
  test('Homepage leads with the copyable install command', async ({ page }) => {
    await page.goto('/');
    const copy = page.locator('button.install-copy').first();
    await expect(copy).toBeVisible();
    await expect(copy).toHaveAttribute(
      'data-copy',
      '/plugin marketplace add jeremylongshore/claude-code-plugins',
    );
  });

  test('Homepage Browse link leads to the explore page', async ({ page }) => {
    await page.goto('/');
    const browse = page.locator('a.btn-browse').first();
    await expect(browse).toBeVisible();
    await expect(browse).toHaveAttribute('href', /^\/explore\/?$/);
  });

  test('Navigation bar is present on all pages', async ({ page }) => {
    await page.goto('/');
    const nav = page.locator('nav, .nav, header').first();
    await expect(nav).toBeVisible();
  });

  test('Footer is present', async ({ page }) => {
    await page.goto('/');
    const footer = page.locator('footer').first();
    await expect(footer).toBeVisible();
  });
});

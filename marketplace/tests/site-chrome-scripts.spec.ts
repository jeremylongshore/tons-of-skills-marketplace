import { expect, test } from '@playwright/test';

// Behavior of the site-wide scripts loaded by BaseLayout from public/scripts/
// (externalized from inline <script> blocks so script-src can drop
// 'unsafe-inline', bead claude-i076). Each test exercises one script.

test.describe('site-wide scripts', () => {
  test('theme-init applies a saved theme before first paint', async ({ page }) => {
    await page.addInitScript(() => localStorage.setItem('theme', 'light'));
    await page.goto('/');
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
  });

  test('theme-toggle flips the theme and persists the choice', async ({ page, isMobile }) => {
    test.skip(isMobile, 'the toggle sits in the desktop nav');
    await page.addInitScript(() => localStorage.setItem('theme', 'dark'));
    await page.goto('/');
    await page.locator('.theme-toggle').click();
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
    expect(await page.evaluate(() => localStorage.getItem('theme'))).toBe('light');
  });

  test('nav-scroll marks the nav once the page scrolls', async ({ page }) => {
    await page.goto('/skills/');
    const nav = page.locator('nav').first();
    await expect(nav).not.toHaveClass(/scrolled/);
    await page.evaluate(() => window.scrollTo(0, 400));
    await expect(nav).toHaveClass(/scrolled/);
  });

  test('mobile-menu opens and closes the nav links', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'the menu toggle is only visible on mobile');
    await page.goto('/');
    const links = page.locator('.nav-links');
    await page.locator('.mobile-menu-toggle').click();
    await expect(links).toHaveClass(/active/);
    // The open menu covers the toggle (a pre-existing layout issue, tracked
    // separately), so dispatch the click to the toggle to exercise the script.
    await page.locator('.mobile-menu-toggle').dispatchEvent('click');
    await expect(links).not.toHaveClass(/active/);
  });

  test('site-forms validates the footer signup without a network call', async ({ page }) => {
    let posted = false;
    await page.route('**/api/forms/**', (route) => {
      posted = true;
      return route.abort();
    });
    await page.goto('/');
    const form = page.locator('form[data-signup-form="footer"]');
    // Bypass the browser's own type=email check so the submit reaches the
    // script's validator, which is the code under test.
    await form.evaluate((el) => ((el as HTMLFormElement).noValidate = true));
    await form.locator('input[type="email"]').fill('not-an-email');
    await form.locator('button[type="submit"]').click();
    await expect(form.locator('button[type="submit"]')).toHaveText('Invalid email');
    expect(posted).toBe(false);
  });
});

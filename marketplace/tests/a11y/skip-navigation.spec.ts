import { test, expect } from '@playwright/test';

for (const path of ['/', '/grading/']) {
  test(`keyboard users can bypass shared navigation on ${path}`, async ({ page }, testInfo) => {
    await page.goto(path);
    const skip = page.getByRole('link', { name: 'Skip to content', exact: true });
    await page.keyboard.press('Tab');
    await expect(skip).toBeFocused();
    await expect(skip).toBeInViewport();
    await testInfo.attach('Focused skip link', {
      body: await page.screenshot(),
      contentType: 'image/png',
    });
    await page.keyboard.press('Enter');
    const main = page.getByRole('main');
    await expect(main).toBeFocused();
    await page.keyboard.press('Tab');
    await expect(main.locator('a, button, input, select, textarea').first()).toBeFocused();
  });
}

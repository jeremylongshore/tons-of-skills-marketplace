import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

for (const theme of ['light', 'dark'] as const) {
  test(`grading introduction links are readable in ${theme} mode`, async ({ page }, testInfo) => {
    await page.emulateMedia({ colorScheme: theme });
    await page.addInitScript((value: string) => localStorage.setItem('theme', value), theme);
    await page.goto('/grading/');
    await expect(page.locator('html')).toHaveAttribute('data-theme', theme);
    const links = page.locator('.grading__subtitle a');
    await expect(links).toHaveCount(3);
    const checkContrast = async () => {
      const result = await new AxeBuilder({ page })
        .include('.grading__subtitle')
        .withRules(['color-contrast'])
        .analyze();
      expect(result.violations).toEqual([]);
      expect(result.incomplete).toEqual([]);
      expect(result.passes.some((rule) => rule.id === 'color-contrast')).toBe(true);
    };
    await checkContrast();
    for (const link of await links.all()) {
      await link.hover();
      await checkContrast();
    }
    await page.mouse.move(0, 0);
    await page.keyboard.press('Tab');
    await page.keyboard.press('Enter');
    for (const link of await links.all()) {
      await page.keyboard.press('Tab');
      await expect(link).toBeFocused();
      const outline = await link.evaluate((element) => getComputedStyle(element).outlineWidth);
      expect(parseFloat(outline)).toBeGreaterThan(0);
    }
    await testInfo.attach(`Grading introduction (${theme})`, {
      body: await page.screenshot(),
      contentType: 'image/png',
    });
  });
}

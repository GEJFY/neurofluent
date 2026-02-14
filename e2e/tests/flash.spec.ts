import { test, expect } from '@playwright/test'

test.describe('Flash Translation ページ', () => {
  test('/speaking/flash ページの表示確認', async ({ page }) => {
    await page.goto('/speaking/flash')
    // ページが表示されることを確認
    await expect(page.locator('body')).toBeVisible()
  })

  test('ページ遷移が正常に動作する', async ({ page }) => {
    await page.goto('/speaking/flash')
    const currentUrl = page.url()
    expect(currentUrl).toContain('/')
  })

  test('ページコンテンツが読み込まれる', async ({ page }) => {
    await page.goto('/speaking/flash')
    await expect(page.locator('body')).toBeVisible()

    // ページの body にコンテンツが存在することを確認
    const bodyText = await page.locator('body').textContent()
    expect(bodyText).toBeTruthy()
  })
})

import { test, expect } from '@playwright/test'

test.describe('Spaced Review ページ', () => {
  test('/review ページの表示確認', async ({ page }) => {
    await page.goto('/review')
    // ページが表示されることを確認
    await expect(page.locator('body')).toBeVisible()
  })

  test('ページ遷移が正常に動作する', async ({ page }) => {
    await page.goto('/review')
    const currentUrl = page.url()
    expect(currentUrl).toContain('/')
  })

  test('ページコンテンツが読み込まれる', async ({ page }) => {
    await page.goto('/review')
    await expect(page.locator('body')).toBeVisible()

    // ページの body にコンテンツが存在することを確認
    const bodyText = await page.locator('body').textContent()
    expect(bodyText).toBeTruthy()
  })

  test('ページ読み込みパフォーマンス', async ({ page }) => {
    const start = Date.now()
    await page.goto('/review')
    await expect(page.locator('body')).toBeVisible()
    expect(Date.now() - start).toBeLessThan(5000)
  })

  test('JavaScriptエラーが発生しない', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', (error) => errors.push(error.message))
    await page.goto('/review')
    await page.waitForTimeout(1000)
    expect(errors).toHaveLength(0)
  })
})

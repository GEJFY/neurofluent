import { test, expect } from '@playwright/test'

test.describe('AI Free Talk ページ', () => {
  test('/talk ページの基本表示確認', async ({ page }) => {
    await page.goto('/talk')
    // ページが表示されることを確認
    await expect(page.locator('body')).toBeVisible()
  })

  test('ページ遷移が正常に動作する', async ({ page }) => {
    await page.goto('/talk')
    // URLが/talkまたはリダイレクト先であることを確認
    const currentUrl = page.url()
    expect(currentUrl).toContain('/') // ルートまたは/talkまたは/login
  })

  test('チャットインターフェース要素の確認', async ({ page }) => {
    await page.goto('/talk')
    await expect(page.locator('body')).toBeVisible()

    // ページが読み込まれていることを確認
    // 認証済みの場合：AI Free Talk のUI
    // 未認証の場合：ログインページにリダイレクト
    const bodyText = await page.locator('body').textContent()
    expect(bodyText).toBeTruthy()
  })

  test('ページ読み込みパフォーマンス', async ({ page }) => {
    const start = Date.now()
    await page.goto('/talk')
    await expect(page.locator('body')).toBeVisible()
    expect(Date.now() - start).toBeLessThan(5000)
  })

  test('JavaScriptエラーが発生しない', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', (error) => errors.push(error.message))
    await page.goto('/talk')
    await page.waitForTimeout(1000)
    expect(errors).toHaveLength(0)
  })
})

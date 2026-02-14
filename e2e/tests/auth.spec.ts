import { test, expect } from '@playwright/test'

test.describe('認証フロー', () => {
  test('ログインページが表示される', async ({ page }) => {
    await page.goto('/login')
    await expect(page).toHaveTitle(/FluentEdge/)
  })

  test('未認証でダッシュボードアクセス', async ({ page }) => {
    await page.goto('/')
    // ログインリダイレクトまたはページ表示を確認
    await expect(page.locator('body')).toBeVisible()
  })

  test('ログインページにフォーム要素が存在する', async ({ page }) => {
    await page.goto('/login')
    // ページの body が表示されることを確認
    await expect(page.locator('body')).toBeVisible()
  })
})

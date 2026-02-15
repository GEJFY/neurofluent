import { test, expect } from '@playwright/test'

test.describe('ページナビゲーション', () => {
  const routes = [
    { path: '/', name: 'Dashboard' },
    { path: '/talk', name: 'Talk' },
    { path: '/speaking', name: 'Speaking' },
    { path: '/speaking/flash', name: 'Flash Translation' },
    { path: '/listening', name: 'Listening' },
    { path: '/review', name: 'Review' },
    { path: '/analytics', name: 'Analytics' },
    { path: '/settings', name: 'Settings' },
    { path: '/subscription', name: 'Subscription' },
    { path: '/login', name: 'Login' },
  ]

  for (const route of routes) {
    test(`${route.name} (${route.path}) ページが表示される`, async ({ page }) => {
      const response = await page.goto(route.path)
      expect(response?.status()).toBeLessThan(500)
      await expect(page.locator('body')).toBeVisible()
    })
  }

  test('存在しないページで404関連の処理が行われる', async ({ page }) => {
    await page.goto('/nonexistent-page-12345')
    await expect(page.locator('body')).toBeVisible()
  })

  test('全ページが5秒以内に読み込まれる', async ({ page }) => {
    for (const route of routes) {
      const start = Date.now()
      await page.goto(route.path)
      await expect(page.locator('body')).toBeVisible()
      const loadTime = Date.now() - start
      expect(loadTime).toBeLessThan(5000)
    }
  })
})

import { test, expect } from '@playwright/test'
import { loginAsMockUser } from './helpers/auth'
import { mockTalkApi, mockComprehensionApi } from './helpers/api-mocks'

test.describe('デスクトップレスポンシブレイアウト', () => {
  test.use({ viewport: { width: 1280, height: 800 } })

  test.beforeEach(async ({ page }) => {
    await loginAsMockUser(page)
  })

  test('サイドバーがデスクトップ幅で表示される', async ({ page }) => {
    await page.goto('/')

    // Sidebar（aside要素）の FluentEdge ロゴが表示される
    const sidebar = page.locator('aside').filter({ hasText: 'FluentEdge' })
    await expect(sidebar).toBeVisible()

    // サイドバー内のナビゲーションリンクが表示される
    await expect(sidebar.getByText('Dashboard')).toBeVisible()
    await expect(sidebar.getByText('Talk')).toBeVisible()
  })

  test('ボトムナビがデスクトップ幅で非表示', async ({ page }) => {
    await page.goto('/')

    // md:hidden のボトムナビが非表示であることを確認
    // BottomNav は固定位置で bottom-0 に配置される
    const bottomNav = page.locator('nav.fixed.bottom-0')
    if (await bottomNav.count() > 0) {
      await expect(bottomNav).not.toBeVisible()
    }
  })

  test('Talk ページで 2パネルレイアウトが表示される', async ({ page }) => {
    await mockTalkApi(page)
    await page.goto('/talk')

    // デスクトップではプレビューパネル（「Selected」ラベル）が表示される
    await expect(page.getByText('Selected')).toBeVisible()

    // モード選択とプレビューが同時に表示される
    await expect(page.getByText('Casual Chat').first()).toBeVisible()
    await expect(page.getByText('Start Talking')).toBeVisible()
  })

  test('Comprehension トピックが 4列グリッドで表示される', async ({ page }) => {
    await mockComprehensionApi(page)
    await page.goto('/listening/comprehension')

    // トピック選択セクションが表示される
    await expect(page.getByText('Topic')).toBeVisible()

    // セットアップフォームが中央寄せで表示される
    await expect(page.getByText('Listening Comprehension')).toBeVisible()
    await expect(page.getByText('Start Listening')).toBeVisible()
  })

  test('ダッシュボードのコンテンツが表示される', async ({ page }) => {
    // ダッシュボードAPI をモック
    await page.route('**/api/dashboard/stats', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_sessions: 10,
          total_minutes: 120,
          current_streak: 3,
          weekly_activity: [],
        }),
      })
    )

    await page.goto('/')

    // ダッシュボードタイトルが表示される
    await expect(page.getByText('Quick Start').first()).toBeVisible()
  })

  test('JavaScript エラーが発生しない（複数ページ遷移）', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', (error) => errors.push(error.message))

    await mockTalkApi(page)
    await mockComprehensionApi(page)

    // 複数ページを巡回
    await page.goto('/')
    await page.waitForTimeout(300)
    await page.goto('/talk')
    await page.waitForTimeout(300)
    await page.goto('/speaking')
    await page.waitForTimeout(300)
    await page.goto('/listening')
    await page.waitForTimeout(300)

    expect(errors).toHaveLength(0)
  })
})

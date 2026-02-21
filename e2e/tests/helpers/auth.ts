import { Page } from '@playwright/test'

/**
 * テスト用認証ヘルパー
 * localStorage にモックトークンを設定し、/api/auth/me をモックする
 */
export async function loginAsMockUser(page: Page) {
  // localStorage にトークンを事前設定
  await page.addInitScript(() => {
    localStorage.setItem('fluentedge_token', 'test-mock-token-12345')
  })

  // /api/auth/me をモック（認証済みユーザーを返す）
  await page.route('**/api/auth/me', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'test-user-001',
        email: 'test@example.com',
        name: 'Test User',
        native_language: 'ja',
        target_language: 'en',
        proficiency_level: 'intermediate',
      }),
    })
  )
}

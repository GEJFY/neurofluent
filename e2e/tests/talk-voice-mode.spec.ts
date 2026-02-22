import { test, expect } from '@playwright/test'
import { loginAsMockUser } from './helpers/auth'
import { mockTalkApi } from './helpers/api-mocks'

test.describe('Talk ページ - セッション開始と Voice UI', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsMockUser(page)
    await mockTalkApi(page)
  })

  test('セッション開始後、Voice mode がデフォルトで有効', async ({ page }) => {
    await page.goto('/talk')

    // セッション開始
    await page.getByRole('button', { name: /start talking/i }).click()

    // Voice/Text 切り替えボタンが表示される
    // Voice mode有効時は「Text」トグルが表示される
    await expect(page.getByText('Text', { exact: true }).first()).toBeVisible()
  })

  test('セッション中に New Session ボタンが表示される', async ({ page }) => {
    await page.goto('/talk')
    await page.getByRole('button', { name: /start talking/i }).click()

    await expect(page.getByRole('button', { name: /new session/i })).toBeVisible()
  })

  test('セッション中にテキスト入力エリアが表示される', async ({ page }) => {
    await page.goto('/talk')
    await page.getByRole('button', { name: /start talking/i }).click()

    // テキスト入力エリア（Voice/Text両モードで常に表示）
    await expect(page.getByPlaceholder(/type your message/i)).toBeVisible()
  })

  test('JavaScript エラーが発生しない（セッション開始）', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', (error) => errors.push(error.message))

    await page.goto('/talk')
    await page.waitForTimeout(500)

    // セッション開始
    await page.getByRole('button', { name: /start talking/i }).click()
    await page.waitForTimeout(1000)

    expect(errors).toHaveLength(0)
  })
})

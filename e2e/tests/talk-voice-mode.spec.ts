import { test, expect } from '@playwright/test'
import { loginAsMockUser } from './helpers/auth'
import { mockTalkApi } from './helpers/api-mocks'

test.describe('Talk ページ - Voice/Text モード切り替え', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsMockUser(page)
    await mockTalkApi(page)
  })

  test('セッション開始後、Voice mode がデフォルトで有効', async ({ page }) => {
    await page.goto('/talk')

    // セッション開始
    await page.getByRole('button', { name: /start talking/i }).click()

    // Voice mode有効時は「Text」トグルが表示される（切替先を表示するため）
    await expect(page.getByRole('button', { name: /text/i }).first()).toBeVisible()

    // VoiceChat の「End」ボタンが表示されることで音声UIが表示されていることを確認
    await expect(page.getByRole('button', { name: /end/i })).toBeVisible()
  })

  test('Text ボタンクリックでテキストモードに切り替わる', async ({ page }) => {
    await page.goto('/talk')
    await page.getByRole('button', { name: /start talking/i }).click()
    await expect(page.getByRole('button', { name: /text/i }).first()).toBeVisible()

    // Text ボタンをクリック
    await page.locator('button').filter({ hasText: /^Text$/ }).click()

    // テキストモードでは「Voice」トグルが表示される
    await expect(page.locator('button').filter({ hasText: /^Voice$/ })).toBeVisible()

    // テキスト入力エリアが表示される
    await expect(page.getByPlaceholder(/type your message/i)).toBeVisible()
  })

  test('Voice ボタンで音声モードに戻れる', async ({ page }) => {
    await page.goto('/talk')
    await page.getByRole('button', { name: /start talking/i }).click()

    // テキストモードに切り替え
    await page.locator('button').filter({ hasText: /^Text$/ }).click()
    await expect(page.locator('button').filter({ hasText: /^Voice$/ })).toBeVisible()

    // Voiceボタンで戻す
    await page.locator('button').filter({ hasText: /^Voice$/ }).click()

    // 再び「Text」トグルが表示 = Voice mode
    await expect(page.locator('button').filter({ hasText: /^Text$/ })).toBeVisible()
    await expect(page.getByRole('button', { name: /end/i })).toBeVisible()
  })

  test('セッション中に New Session ボタンが表示される', async ({ page }) => {
    await page.goto('/talk')
    await page.getByRole('button', { name: /start talking/i }).click()

    await expect(page.getByRole('button', { name: /new session/i })).toBeVisible()
  })

  test('JavaScript エラーが発生しない', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', (error) => errors.push(error.message))

    await page.goto('/talk')
    await page.getByRole('button', { name: /start talking/i }).click()

    // Voice → Text → Voice 切り替え
    await page.locator('button').filter({ hasText: /^Text$/ }).click()
    await page.locator('button').filter({ hasText: /^Voice$/ }).click()
    await page.waitForTimeout(500)

    expect(errors).toHaveLength(0)
  })
})

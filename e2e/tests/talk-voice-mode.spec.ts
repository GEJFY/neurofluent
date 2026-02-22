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

    // VoiceChat の「End」ボタンが表示されることで音声UIが表示されていることを確認
    await expect(page.getByRole('button', { name: /end/i })).toBeVisible()

    // Voice mode有効時は「Text」トグルボタンが表示される
    await expect(page.getByText('Text', { exact: true }).first()).toBeVisible()
  })

  test('Text ボタンクリックでテキストモードに切り替わる', async ({ page }) => {
    await page.goto('/talk')
    await page.getByRole('button', { name: /start talking/i }).click()
    await expect(page.getByRole('button', { name: /end/i })).toBeVisible()

    // Text トグルボタンをクリック
    await page.getByText('Text', { exact: true }).first().click()

    // テキスト入力エリアが表示される
    await expect(page.getByPlaceholder(/type your message/i)).toBeVisible()
  })

  test('Voice ボタンで音声モードに戻れる', async ({ page }) => {
    await page.goto('/talk')
    await page.getByRole('button', { name: /start talking/i }).click()
    await expect(page.getByRole('button', { name: /end/i })).toBeVisible()

    // テキストモードに切り替え
    await page.getByText('Text', { exact: true }).first().click()
    await expect(page.getByPlaceholder(/type your message/i)).toBeVisible()

    // Voiceボタンで戻す
    await page.getByText('Voice', { exact: true }).first().click()

    // VoiceChat の End ボタンが再表示される = Voice mode
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
    await expect(page.getByRole('button', { name: /end/i })).toBeVisible()

    // Voice → Text 切り替え
    await page.getByText('Text', { exact: true }).first().click()
    await page.waitForTimeout(300)

    // Text → Voice 切り替え
    await page.getByText('Voice', { exact: true }).first().click()
    await page.waitForTimeout(300)

    expect(errors).toHaveLength(0)
  })
})

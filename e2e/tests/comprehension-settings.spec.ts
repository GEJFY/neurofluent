import { test, expect } from '@playwright/test'
import { loginAsMockUser } from './helpers/auth'
import { mockComprehensionApi } from './helpers/api-mocks'

// Comprehension ページは項目が多く、デスクトップでは固定サイドバーとボタンが重なるため
// モバイルビューポートでテストする
test.use({ viewport: { width: 390, height: 844 } })

test.describe('Comprehension ページ - セットアップ画面', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsMockUser(page)
    await mockComprehensionApi(page)
  })

  // --- トピック ---
  test('6つのトピックが表示される', async ({ page }) => {
    await page.goto('/listening/comprehension')
    const topics = ['Business Meeting', 'Presentation', 'Job Interview', 'News Report', 'Casual Conversation', 'Academic Lecture']
    for (const topic of topics) {
      await expect(page.getByText(topic).first()).toBeVisible()
    }
  })

  // --- アクセント ---
  test('Accentセクションが表示される', async ({ page }) => {
    await page.goto('/listening/comprehension')
    await expect(page.getByText('Accent')).toBeVisible()
  })

  test('6つのアクセントボタンが表示される', async ({ page }) => {
    await page.goto('/listening/comprehension')
    const accents = ['Any', 'US', 'UK', 'India', 'Singapore', 'Australia']
    for (const accent of accents) {
      await expect(page.getByRole('button', { name: accent, exact: true })).toBeVisible()
    }
  })

  test('Any がデフォルトのアクセント選択', async ({ page }) => {
    await page.goto('/listening/comprehension')
    const anyButton = page.getByRole('button', { name: 'Any', exact: true })
    await expect(anyButton).toHaveClass(/border-primary/)
  })

  test('アクセントを UK に切り替えできる', async ({ page }) => {
    await page.goto('/listening/comprehension')
    const ukButton = page.getByRole('button', { name: 'UK', exact: true })
    await ukButton.click()
    await expect(ukButton).toHaveClass(/border-primary/)
    // Any は非選択状態
    const anyButton = page.getByRole('button', { name: 'Any', exact: true })
    await expect(anyButton).not.toHaveClass(/border-primary/)
  })

  // --- マルチスピーカー ---
  test('Speakersセクションが表示される', async ({ page }) => {
    await page.goto('/listening/comprehension')
    await expect(page.getByText('Speakers')).toBeVisible()
  })

  test('Single がデフォルトのスピーカー選択', async ({ page }) => {
    await page.goto('/listening/comprehension')
    const singleButton = page.getByRole('button', { name: 'Single', exact: true })
    await expect(singleButton).toHaveClass(/border-primary/)
  })

  test('Multi-Speaker に切り替えできる', async ({ page }) => {
    await page.goto('/listening/comprehension')
    const multiButton = page.getByRole('button', { name: 'Multi-Speaker', exact: true })
    await multiButton.click()
    await expect(multiButton).toHaveClass(/border-primary/)
    // Single は非選択状態
    const singleButton = page.getByRole('button', { name: 'Single', exact: true })
    await expect(singleButton).not.toHaveClass(/border-primary/)
  })

  // --- 環境 ---
  test('Environmentセクションが表示される', async ({ page }) => {
    await page.goto('/listening/comprehension')
    await expect(page.getByText('Environment')).toBeVisible()
  })

  test('5つの環境ボタンが表示される', async ({ page }) => {
    await page.goto('/listening/comprehension')
    const environments = ['Clean', 'Phone Call', 'Video Call', 'Office', 'Cafe']
    for (const env of environments) {
      await expect(page.getByRole('button', { name: env, exact: true })).toBeVisible()
    }
  })

  test('Clean がデフォルトの環境選択', async ({ page }) => {
    await page.goto('/listening/comprehension')
    const cleanButton = page.getByRole('button', { name: 'Clean', exact: true })
    await expect(cleanButton).toHaveClass(/border-primary/)
  })

  test('環境を Cafe に切り替えできる', async ({ page }) => {
    await page.goto('/listening/comprehension')
    const cafeButton = page.getByRole('button', { name: 'Cafe', exact: true })
    await cafeButton.click()
    await expect(cafeButton).toHaveClass(/border-primary/)
  })

  // --- 難易度 ---
  test('3段階の難易度が表示される', async ({ page }) => {
    await page.goto('/listening/comprehension')
    for (const diff of ['Easy', 'Intermediate', 'Advanced']) {
      await expect(page.getByRole('button', { name: diff, exact: true })).toBeVisible()
    }
  })

  // --- Duration ---
  test('3つの長さオプションが表示される', async ({ page }) => {
    await page.goto('/listening/comprehension')
    for (const dur of ['Short', 'Medium', 'Long']) {
      await expect(page.getByRole('button', { name: new RegExp(dur) })).toBeVisible()
    }
  })

  // --- 開始ボタン ---
  test('Start Listening ボタンが存在する', async ({ page }) => {
    await page.goto('/listening/comprehension')
    await expect(page.getByRole('button', { name: /start listening/i })).toBeVisible()
  })

  // --- JSエラーチェック ---
  test('JavaScriptエラーが発生しない', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', (error) => errors.push(error.message))
    await page.goto('/listening/comprehension')
    await page.waitForTimeout(1000)
    expect(errors).toHaveLength(0)
  })
})

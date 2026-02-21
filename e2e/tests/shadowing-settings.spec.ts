import { test, expect } from '@playwright/test'
import { loginAsMockUser } from './helpers/auth'
import { mockShadowingApi } from './helpers/api-mocks'

test.describe('Shadowing ページ - アクセント&環境セレクター', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsMockUser(page)
    await mockShadowingApi(page)
  })

  test('セットアップ画面にAccentセクションが表示される', async ({ page }) => {
    await page.goto('/listening/shadowing')
    await expect(page.getByText('Accent')).toBeVisible()
  })

  test('6つのアクセントボタンが表示される', async ({ page }) => {
    await page.goto('/listening/shadowing')
    const accents = ['Any', 'US', 'UK', 'India', 'Singapore', 'Australia']
    for (const accent of accents) {
      await expect(page.getByRole('button', { name: accent, exact: true })).toBeVisible()
    }
  })

  test('アクセントボタンをクリックして選択できる', async ({ page }) => {
    await page.goto('/listening/shadowing')
    const ukButton = page.getByRole('button', { name: 'UK', exact: true })
    await ukButton.click()
    // 選択状態: border-primary クラスが付与される
    await expect(ukButton).toHaveClass(/border-primary/)
  })

  test('セットアップ画面にEnvironmentセクションが表示される', async ({ page }) => {
    await page.goto('/listening/shadowing')
    await expect(page.getByText('Environment')).toBeVisible()
  })

  test('5つの環境ボタンが表示される', async ({ page }) => {
    await page.goto('/listening/shadowing')
    const environments = ['Clean', 'Phone Call', 'Video Call', 'Office', 'Cafe']
    for (const env of environments) {
      await expect(page.getByRole('button', { name: env, exact: true })).toBeVisible()
    }
  })

  test('環境ボタンをクリックして切り替えできる', async ({ page }) => {
    await page.goto('/listening/shadowing')

    // デフォルト: Clean が選択済み
    const cleanButton = page.getByRole('button', { name: 'Clean', exact: true })
    await expect(cleanButton).toHaveClass(/border-primary/)

    // Office に切り替え
    const officeButton = page.getByRole('button', { name: 'Office', exact: true })
    await officeButton.click()
    await expect(officeButton).toHaveClass(/border-primary/)
  })

  test('難易度セレクターが3段階表示される', async ({ page }) => {
    await page.goto('/listening/shadowing')
    const difficulties = ['Beginner', 'Intermediate', 'Advanced']
    for (const diff of difficulties) {
      await expect(page.getByRole('button', { name: diff, exact: true })).toBeVisible()
    }
  })

  test('トピック選択が存在する', async ({ page }) => {
    await page.goto('/listening/shadowing')
    await expect(page.getByText('Topic')).toBeVisible()
    await expect(page.getByText('Business Meeting')).toBeVisible()
  })

  test('Start Shadowing ボタンが存在する', async ({ page }) => {
    await page.goto('/listening/shadowing')
    await expect(page.getByRole('button', { name: /start shadowing/i })).toBeVisible()
  })

  test('JavaScriptエラーが発生しない', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', (error) => errors.push(error.message))
    await page.goto('/listening/shadowing')
    await page.waitForTimeout(1000)
    expect(errors).toHaveLength(0)
  })
})

import { test, expect } from '@playwright/test'
import { loginAsMockUser } from './helpers/auth'
import { mockTalkApi, MOCK_SCENARIOS } from './helpers/api-mocks'

test.describe('Talk ページ - モード&シナリオ選択', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsMockUser(page)
    await mockTalkApi(page)
  })

  test('6つの会話モードが表示される', async ({ page }) => {
    await page.goto('/talk')
    const modes = ['Casual Chat', 'Business Meeting', 'Interview', 'Presentation', 'Negotiation', 'Phone Call']
    for (const mode of modes) {
      await expect(page.getByText(mode, { exact: false }).first()).toBeVisible()
    }
  })

  test('Casual Chat がデフォルト選択されている', async ({ page }) => {
    await page.goto('/talk')
    // Casual Chat のラジオドットが表示されていることを確認（bg-primary の内側ドット）
    const casualChatButton = page.locator('button').filter({ hasText: 'Casual Chat' })
    await expect(casualChatButton).toBeVisible()
    // 選択状態: border-primary bg-primary/5 クラスが付与されている
    await expect(casualChatButton).toHaveClass(/border-primary/)
  })

  test('Casual Chat 選択時はシナリオセクションが表示されない', async ({ page }) => {
    await page.goto('/talk')
    // Scenario ラベルが存在しないことを確認
    await expect(page.getByText('Scenario', { exact: false })).not.toBeVisible()
  })

  test('Business Meeting 選択でシナリオカードが表示される', async ({ page }) => {
    await page.goto('/talk')
    // Business Meeting をクリック
    await page.locator('button').filter({ hasText: 'Business Meeting' }).click()

    // シナリオセクションが表示される
    await expect(page.getByText('Scenario')).toBeVisible()

    // モックの3シナリオが表示される
    for (const scenario of MOCK_SCENARIOS) {
      await expect(page.getByText(scenario.title)).toBeVisible()
    }
  })

  test('シナリオカードに難易度バッジが表示される', async ({ page }) => {
    await page.goto('/talk')
    await page.locator('button').filter({ hasText: 'Business Meeting' }).click()
    await expect(page.getByText('Scenario')).toBeVisible()

    // 各難易度ラベルが存在する
    await expect(page.getByText('intermediate').first()).toBeVisible()
    await expect(page.getByText('advanced')).toBeVisible()
    await expect(page.getByText('beginner')).toBeVisible()
  })

  test('シナリオカードをクリックして選択・解除できる', async ({ page }) => {
    await page.goto('/talk')
    await page.locator('button').filter({ hasText: 'Business Meeting' }).click()
    await expect(page.getByText('Scenario')).toBeVisible()

    // シナリオを選択
    const scenarioButton = page.locator('button').filter({ hasText: 'Budget Overrun Explanation' })
    await scenarioButton.click()
    await expect(scenarioButton).toHaveClass(/border-primary/)

    // 再クリックで解除
    await scenarioButton.click()
    await expect(scenarioButton).not.toHaveClass(/border-primary bg-primary/)
  })

  test('モード切替でシナリオがリセットされる', async ({ page }) => {
    await page.goto('/talk')

    // Meeting を選択してシナリオ表示
    await page.locator('button').filter({ hasText: 'Business Meeting' }).click()
    await expect(page.getByText('Scenario')).toBeVisible()

    // Casual Chat に戻すとシナリオが消える
    await page.locator('button').filter({ hasText: 'Casual Chat' }).click()
    await expect(page.getByText('Scenario', { exact: false })).not.toBeVisible()
  })

  test('Start Talking ボタンが存在する', async ({ page }) => {
    await page.goto('/talk')
    await expect(page.getByRole('button', { name: /start talking/i })).toBeVisible()
  })

  test('JavaScriptエラーが発生しない', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', (error) => errors.push(error.message))
    await page.goto('/talk')
    await page.locator('button').filter({ hasText: 'Business Meeting' }).click()
    await page.waitForTimeout(1000)
    expect(errors).toHaveLength(0)
  })
})

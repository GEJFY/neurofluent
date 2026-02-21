import { Page } from '@playwright/test'

/** Talk シナリオ mock データ */
export const MOCK_SCENARIOS = [
  {
    id: 'mtg-budget-overrun',
    mode: 'meeting',
    title: 'Budget Overrun Explanation',
    description: 'Explain and discuss a project that has exceeded its budget.',
    difficulty: 'intermediate',
    accent_context: null,
  },
  {
    id: 'mtg-quarterly-review',
    mode: 'meeting',
    title: 'Quarterly Performance Review',
    description: 'Present and discuss quarterly results with the management team.',
    difficulty: 'advanced',
    accent_context: null,
  },
  {
    id: 'mtg-new-member',
    mode: 'meeting',
    title: 'New Team Member Onboarding',
    description: 'Welcome and orient a new team member in a meeting setting.',
    difficulty: 'beginner',
    accent_context: null,
  },
]

/** Accent / Environment mock データ */
export const MOCK_ACCENTS_RESPONSE = {
  accents: [
    { id: 'us', label: 'American English', label_ja: 'アメリカ英語' },
    { id: 'uk', label: 'British English', label_ja: 'イギリス英語' },
    { id: 'india', label: 'Indian English', label_ja: 'インド英語' },
    { id: 'singapore', label: 'Singapore English', label_ja: 'シンガポール英語' },
    { id: 'australia', label: 'Australian English', label_ja: 'オーストラリア英語' },
  ],
  environments: [
    { id: 'clean', label: 'Clean', description: 'No background noise' },
    { id: 'phone_call', label: 'Phone Call', description: 'Phone call quality audio' },
    { id: 'video_call', label: 'Video Call', description: 'Video conference quality' },
    { id: 'office', label: 'Office', description: 'Office background noise' },
    { id: 'cafe', label: 'Cafe', description: 'Cafe ambient noise' },
  ],
}

/**
 * Talk ページ用 API モック設定
 */
export async function mockTalkApi(page: Page) {
  // シナリオ一覧
  await page.route('**/api/talk/scenarios*', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_SCENARIOS),
    })
  )

  // セッション開始
  await page.route('**/api/talk/start', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        session_id: 'test-session-001',
        mode: 'meeting',
        ai_message: 'Hello! Welcome to the meeting simulation.',
      }),
    })
  )
}

/**
 * Shadowing ページ用 API モック設定
 */
export async function mockShadowingApi(page: Page) {
  // アクセント一覧
  await page.route('**/api/listening/accents', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_ACCENTS_RESPONSE),
    })
  )

  // シャドーイング素材取得
  await page.route('**/api/listening/shadowing/material*', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        exercise_id: 'test-exercise-001',
        text: 'The quarterly report shows a significant increase in revenue.',
        translation: '四半期報告書は収益の大幅な増加を示しています。',
        audio_url: null,
        difficulty: 'intermediate',
        topic: 'business_meeting',
      }),
    })
  )
}

/**
 * Comprehension ページ用 API モック設定
 */
export async function mockComprehensionApi(page: Page) {
  // アクセント一覧
  await page.route('**/api/listening/accents', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_ACCENTS_RESPONSE),
    })
  )

  // 素材取得
  await page.route('**/api/listening/comprehension/material*', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        material_id: 'test-material-001',
        title: 'Quarterly Business Review',
        transcript: 'Welcome to the quarterly review meeting...',
        audio_url: null,
        questions: [
          {
            question_id: 'q1',
            question_text: 'What was the main topic?',
            options: ['Revenue growth', 'Budget cuts', 'New hires', 'Office relocation'],
            correct_answer: 'Revenue growth',
          },
        ],
        key_points: ['Revenue increased by 15%'],
        vocabulary: [{ word: 'revenue', definition: '収益', context: 'Revenue grew by 15%.' }],
        difficulty: 'intermediate',
        duration_seconds: 180,
      }),
    })
  )
}

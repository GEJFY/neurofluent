import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import DashboardPage from '@/app/page'

// AppShellモック（認証チェックをバイパス）
vi.mock('@/components/layout/AppShell', () => ({
  default: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="app-shell">{children}</div>
  ),
}))

// auth-storeモック
vi.mock('@/lib/stores/auth-store', () => ({
  useAuthStore: (selector: (state: Record<string, unknown>) => unknown) =>
    selector({ user: { name: 'TestUser', email: 'test@example.com' } }),
}))

// APIモック
vi.mock('@/lib/api', () => ({
  api: {
    getDashboard: vi.fn().mockResolvedValue({
      streak_days: 5,
      total_practice_minutes: 120,
      total_sessions: 15,
      total_reviews_completed: 30,
      total_expressions_learned: 45,
      avg_grammar_accuracy: 0.85,
      avg_pronunciation_score: null,
      recent_daily_stats: [],
      pending_reviews: 3,
    }),
  },
}))

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('ダッシュボードのメインレイアウトが表示される', async () => {
    render(<DashboardPage />)

    // ローディング中はスピナーが表示される
    // データ読み込み後にコンテンツが表示される
    await waitFor(() => {
      expect(screen.getByText(/TestUser/)).toBeInTheDocument()
    })
  })

  it('挨拶テキストが表示される', async () => {
    render(<DashboardPage />)

    await waitFor(() => {
      // 時間帯に応じた挨拶（Good morning / afternoon / evening / night）
      expect(
        screen.getByText(
          /Good (morning|afternoon|evening|night)/
        )
      ).toBeInTheDocument()
    })
  })

  it('学習統計セクションが表示される', async () => {
    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('Learning Stats')).toBeInTheDocument()
      expect(screen.getByText('120')).toBeInTheDocument() // total_practice_minutes
      expect(screen.getByText('Total Minutes')).toBeInTheDocument()
    })
  })

  it('ストリークカウンターが表示される', async () => {
    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('5')).toBeInTheDocument() // streak_days
      expect(screen.getByText('Day Streak')).toBeInTheDocument()
    })
  })

  it('Quick Startメニューが表示される', async () => {
    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('Quick Start')).toBeInTheDocument()
      expect(screen.getByText('Spaced Review')).toBeInTheDocument()
      expect(screen.getByText('Flash Translation')).toBeInTheDocument()
      expect(screen.getByText('AI Free Talk')).toBeInTheDocument()
    })
  })

  it('pending reviewsのバッジが表示される', async () => {
    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('3 due')).toBeInTheDocument()
    })
  })

  it('日本語サブテキストが表示される', async () => {
    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('今日も英語力を磨きましょう')).toBeInTheDocument()
    })
  })
})

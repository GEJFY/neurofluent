import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ReviewPage from '@/app/review/page'

// AppShellモック
vi.mock('@/components/layout/AppShell', () => ({
  default: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="app-shell">{children}</div>
  ),
}))

// ReviewCardモック
vi.mock('@/components/drill/ReviewCard', () => ({
  default: () => <div data-testid="review-card">ReviewCard</div>,
}))

// APIモック（復習アイテムなし）
vi.mock('@/lib/api', () => ({
  api: {
    getDueReviews: vi.fn().mockResolvedValue([]),
    completeReview: vi.fn(),
  },
}))

describe('ReviewPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('Spaced Reviewのタイトルが表示される', () => {
    render(<ReviewPage />)

    expect(screen.getByText('Spaced Review')).toBeInTheDocument()
  })

  it('説明テキストが表示される', () => {
    render(<ReviewPage />)

    expect(
      screen.getByText('間隔反復法で効率的に記憶を定着させましょう')
    ).toBeInTheDocument()
  })

  it('復習アイテムがない場合、完了メッセージが表示される', async () => {
    render(<ReviewPage />)

    await waitFor(() => {
      expect(screen.getByText('All caught up!')).toBeInTheDocument()
    })
  })

  it('復習アイテムがない場合、日本語完了メッセージが表示される', async () => {
    render(<ReviewPage />)

    await waitFor(() => {
      expect(
        screen.getByText('今日の復習アイテムはすべて完了です')
      ).toBeInTheDocument()
    })
  })

  it('再チェックボタンが表示される（アイテムなし時）', async () => {
    render(<ReviewPage />)

    await waitFor(() => {
      expect(screen.getByText('再チェック')).toBeInTheDocument()
    })
  })
})

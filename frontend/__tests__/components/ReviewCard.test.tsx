import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ReviewCard from '@/components/drill/ReviewCard'
import type { ReviewItemResponse } from '@/lib/api'

/** テスト用の復習アイテムデータ（flash_translation タイプ） */
const mockFlashItem: ReviewItemResponse = {
  id: 'review-1',
  item_type: 'flash_translation',
  content: {
    target: 'He runs every day.',
    corrected: 'He runs every day.',
    user_answer: 'He run every day.',
    explanation: 'Use third-person singular form.',
  },
  next_review_at: '2026-02-15T10:00:00Z',
  ease_factor: 2.5,
  interval_days: 1,
  repetitions: 2,
}

/** テスト用の復習アイテムデータ（expression_upgrade タイプ） */
const mockExpressionItem: ReviewItemResponse = {
  id: 'review-2',
  item_type: 'expression_upgrade',
  content: {
    original: 'I want to eat pizza.',
    upgraded: 'I feel like having some pizza.',
    explanation: 'More natural expression for cravings.',
  },
  next_review_at: '2026-02-16T10:00:00Z',
  ease_factor: 2.5,
  interval_days: 3,
  repetitions: 1,
}

describe('ReviewCard', () => {
  const mockOnRate = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('復習アイテムの表面（問題テキスト）が表示される', () => {
    render(
      <ReviewCard
        item={mockFlashItem}
        onRate={mockOnRate}
        currentIndex={0}
        totalItems={5}
      />
    )

    // flash_translation タイプの場合、targetが表面に表示される
    expect(screen.getByText('He runs every day.')).toBeInTheDocument()
  })

  it('アイテムタイプのバッジが表示される', () => {
    render(
      <ReviewCard
        item={mockFlashItem}
        onRate={mockOnRate}
        currentIndex={0}
        totalItems={5}
      />
    )

    // "flash_translation" -> "flash translation" に変換されて表示
    expect(screen.getByText('flash translation')).toBeInTheDocument()
  })

  it('進捗表示が正しい', () => {
    render(
      <ReviewCard
        item={mockFlashItem}
        onRate={mockOnRate}
        currentIndex={2}
        totalItems={5}
      />
    )

    expect(screen.getByText('3 / 5')).toBeInTheDocument()
    expect(screen.getByText('Rep #2')).toBeInTheDocument()
  })

  it('「Show Answer」ボタンが表示される', () => {
    render(
      <ReviewCard
        item={mockFlashItem}
        onRate={mockOnRate}
        currentIndex={0}
        totalItems={5}
      />
    )

    expect(screen.getByText('Show Answer')).toBeInTheDocument()
  })

  it('「Show Answer」クリック後に回答と評価ボタンが表示される', async () => {
    const user = userEvent.setup()

    render(
      <ReviewCard
        item={mockFlashItem}
        onRate={mockOnRate}
        currentIndex={0}
        totalItems={5}
      />
    )

    // Show Answerをクリック
    await user.click(screen.getByText('Show Answer'))

    // 評価ボタン4つが表示される
    expect(screen.getByText('Again')).toBeInTheDocument()
    expect(screen.getByText('Hard')).toBeInTheDocument()
    expect(screen.getByText('Good')).toBeInTheDocument()
    expect(screen.getByText('Easy')).toBeInTheDocument()
  })

  it('評価ボタンのクリックでonRateが呼ばれる', async () => {
    const user = userEvent.setup()

    render(
      <ReviewCard
        item={mockFlashItem}
        onRate={mockOnRate}
        currentIndex={0}
        totalItems={5}
      />
    )

    // Show Answerをクリック
    await user.click(screen.getByText('Show Answer'))

    // Goodボタンをクリック
    await user.click(screen.getByText('Good'))

    expect(mockOnRate).toHaveBeenCalledWith(3)
  })

  it('Again(1)ボタンのクリックで正しいratingが渡される', async () => {
    const user = userEvent.setup()

    render(
      <ReviewCard
        item={mockFlashItem}
        onRate={mockOnRate}
        currentIndex={0}
        totalItems={5}
      />
    )

    await user.click(screen.getByText('Show Answer'))
    await user.click(screen.getByText('Again'))

    expect(mockOnRate).toHaveBeenCalledWith(1)
  })

  it('isSubmitting中は評価ボタンが無効化される', async () => {
    const user = userEvent.setup()

    render(
      <ReviewCard
        item={mockFlashItem}
        onRate={mockOnRate}
        isSubmitting={true}
        currentIndex={0}
        totalItems={5}
      />
    )

    await user.click(screen.getByText('Show Answer'))

    const goodButton = screen.getByText('Good').closest('button')
    expect(goodButton).toBeDisabled()
  })

  it('expression_upgradeタイプのアイテムが正しく表示される', () => {
    render(
      <ReviewCard
        item={mockExpressionItem}
        onRate={mockOnRate}
        currentIndex={0}
        totalItems={3}
      />
    )

    expect(screen.getByText('I want to eat pizza.')).toBeInTheDocument()
    expect(screen.getByText('expression upgrade')).toBeInTheDocument()
  })

  it('Show Answer後に解説が表示される', async () => {
    const user = userEvent.setup()

    render(
      <ReviewCard
        item={mockFlashItem}
        onRate={mockOnRate}
        currentIndex={0}
        totalItems={5}
      />
    )

    await user.click(screen.getByText('Show Answer'))

    expect(screen.getByText('Use third-person singular form.')).toBeInTheDocument()
  })
})

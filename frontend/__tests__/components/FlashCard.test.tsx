import { render, screen, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import FlashCard from '@/components/drill/FlashCard'
import type { FlashExercise, FlashCheckResponse } from '@/lib/api'

/** テスト用のFlash問題データ */
const mockExercise: FlashExercise = {
  exercise_id: 'ex-1',
  japanese: '彼は毎日走っています。',
  english_target: 'He runs every day.',
  acceptable_alternatives: ['He jogs every day.'],
  key_pattern: 'present continuous',
  difficulty: 'intermediate',
  time_limit_seconds: 30,
  hints: ['present tense', 'daily routine'],
}

/** テスト用の正解レスポンス */
const mockCorrectResult: FlashCheckResponse = {
  is_correct: true,
  score: 0.95,
  corrected: 'He runs every day.',
  explanation: 'Great job! Your answer is correct.',
  review_item_created: false,
}

/** テスト用の不正解レスポンス */
const mockIncorrectResult: FlashCheckResponse = {
  is_correct: false,
  score: 0.3,
  corrected: 'He runs every day.',
  explanation: 'The verb form should be simple present for daily routines.',
  review_item_created: true,
}

/** カウントダウン (3→2→1→0) を完了させるヘルパー。チェーンされたsetTimeoutをact()で順に実行 */
async function advanceCountdown() {
  for (let i = 0; i < 4; i++) {
    await act(async () => {
      vi.advanceTimersByTime(1000)
    })
  }
}

describe('FlashCard', () => {
  const mockOnSubmit = vi.fn()
  const mockOnNext = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers({ shouldAdvanceTime: true })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('日本語テキスト（問題文）が表示される', () => {
    render(
      <FlashCard
        exercise={mockExercise}
        onSubmit={mockOnSubmit}
        onNext={mockOnNext}
        questionNumber={1}
        totalQuestions={10}
      />
    )

    expect(screen.getByText('彼は毎日走っています。')).toBeInTheDocument()
    expect(screen.getByText('Translate to English')).toBeInTheDocument()
  })

  it('進捗表示（問題番号/全問数）が表示される', () => {
    render(
      <FlashCard
        exercise={mockExercise}
        onSubmit={mockOnSubmit}
        onNext={mockOnNext}
        questionNumber={3}
        totalQuestions={10}
      />
    )

    expect(screen.getByText('3 / 10')).toBeInTheDocument()
  })

  it('キーパターンが表示される', () => {
    render(
      <FlashCard
        exercise={mockExercise}
        onSubmit={mockOnSubmit}
        onNext={mockOnNext}
        questionNumber={1}
        totalQuestions={10}
      />
    )

    expect(screen.getByText('Pattern: present continuous')).toBeInTheDocument()
  })

  it('カウントダウン後に入力フィールドが表示される', async () => {
    render(
      <FlashCard
        exercise={mockExercise}
        onSubmit={mockOnSubmit}
        onNext={mockOnNext}
        questionNumber={1}
        totalQuestions={10}
      />
    )

    // カウントダウン中（初期値 3）
    expect(screen.getByText('3')).toBeInTheDocument()

    // カウントダウンを完了させる
    await advanceCountdown()

    // 入力フィールドが表示される
    expect(screen.getByPlaceholderText('Type your answer in English...')).toBeInTheDocument()
  })

  it('回答送信後に結果が表示される（正解）', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    mockOnSubmit.mockResolvedValue(mockCorrectResult)

    render(
      <FlashCard
        exercise={mockExercise}
        onSubmit={mockOnSubmit}
        onNext={mockOnNext}
        questionNumber={1}
        totalQuestions={10}
      />
    )

    // カウントダウンを完了させる
    await advanceCountdown()

    expect(screen.getByPlaceholderText('Type your answer in English...')).toBeInTheDocument()

    // 回答を入力して送信
    const input = screen.getByPlaceholderText('Type your answer in English...')
    await user.type(input, 'He runs every day.')
    await user.keyboard('{Enter}')

    // 結果表示
    await waitFor(() => {
      expect(screen.getByText('Correct!')).toBeInTheDocument()
    })
  })

  it('回答送信後に結果が表示される（不正解）', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    mockOnSubmit.mockResolvedValue(mockIncorrectResult)

    render(
      <FlashCard
        exercise={mockExercise}
        onSubmit={mockOnSubmit}
        onNext={mockOnNext}
        questionNumber={1}
        totalQuestions={10}
      />
    )

    // カウントダウンを完了させる
    await advanceCountdown()

    expect(screen.getByPlaceholderText('Type your answer in English...')).toBeInTheDocument()

    // 回答を入力して送信
    const input = screen.getByPlaceholderText('Type your answer in English...')
    await user.type(input, 'He is run every day.')
    await user.keyboard('{Enter}')

    // 不正解の結果表示
    await waitFor(() => {
      expect(screen.getByText('Not quite...')).toBeInTheDocument()
      expect(screen.getByText(/review list/)).toBeInTheDocument()
    })
  })

  it('最終問題では「See Results」ボタンが表示される', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    mockOnSubmit.mockResolvedValue(mockCorrectResult)

    render(
      <FlashCard
        exercise={mockExercise}
        onSubmit={mockOnSubmit}
        onNext={mockOnNext}
        questionNumber={10}
        totalQuestions={10}
      />
    )

    await advanceCountdown()

    expect(screen.getByPlaceholderText('Type your answer in English...')).toBeInTheDocument()

    const input = screen.getByPlaceholderText('Type your answer in English...')
    await user.type(input, 'He runs every day.')
    await user.keyboard('{Enter}')

    await waitFor(() => {
      expect(screen.getByText('See Results')).toBeInTheDocument()
    })
  })

  it('途中の問題では「Next Question」ボタンが表示される', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    mockOnSubmit.mockResolvedValue(mockCorrectResult)

    render(
      <FlashCard
        exercise={mockExercise}
        onSubmit={mockOnSubmit}
        onNext={mockOnNext}
        questionNumber={5}
        totalQuestions={10}
      />
    )

    await advanceCountdown()

    expect(screen.getByPlaceholderText('Type your answer in English...')).toBeInTheDocument()

    const input = screen.getByPlaceholderText('Type your answer in English...')
    await user.type(input, 'He runs every day.')
    await user.keyboard('{Enter}')

    await waitFor(() => {
      expect(screen.getByText('Next Question')).toBeInTheDocument()
    })
  })
})

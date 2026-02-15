import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import MessageBubble from '@/components/chat/MessageBubble'
import type { TalkMessageResponse } from '@/lib/api'

// FeedbackPanel のモック
vi.mock('@/components/chat/FeedbackPanel', () => ({
  default: ({ feedback }: { feedback: unknown }) => (
    <div data-testid="feedback-panel">Feedback: {JSON.stringify(feedback)}</div>
  ),
}))

/** テスト用ユーザーメッセージ */
const userMessage: TalkMessageResponse = {
  id: 'msg-user-1',
  role: 'user',
  content: 'I go to school yesterday.',
  feedback: {
    grammar_errors: [
      {
        original: 'go',
        corrected: 'went',
        explanation: '過去形が必要です',
      },
    ],
    expression_upgrades: [],
    pronunciation_notes: [],
    positive_feedback: '',
    vocabulary_level: 'B1',
  },
  created_at: '2026-01-15T14:30:00Z',
}

/** テスト用AIメッセージ */
const assistantMessage: TalkMessageResponse = {
  id: 'msg-ai-1',
  role: 'assistant',
  content: 'That sounds great! What did you study?',
  feedback: null,
  created_at: '2026-01-15T14:30:05Z',
}

describe('MessageBubble', () => {
  it('ユーザーメッセージが表示される', () => {
    render(<MessageBubble message={userMessage} />)

    expect(screen.getByText('I go to school yesterday.')).toBeInTheDocument()
  })

  it('AIメッセージが表示される', () => {
    render(<MessageBubble message={assistantMessage} />)

    expect(
      screen.getByText('That sounds great! What did you study?')
    ).toBeInTheDocument()
  })

  it('ユーザーメッセージは右寄せスタイルを持つ', () => {
    const { container } = render(<MessageBubble message={userMessage} />)

    const wrapper = container.firstChild as HTMLElement
    expect(wrapper).toHaveClass('justify-end')
  })

  it('AIメッセージは左寄せスタイルを持つ', () => {
    const { container } = render(<MessageBubble message={assistantMessage} />)

    const wrapper = container.firstChild as HTMLElement
    expect(wrapper).toHaveClass('justify-start')
  })

  it('タイムスタンプが表示される', () => {
    render(<MessageBubble message={userMessage} />)

    // toLocaleTimeString の結果はロケール依存だが、時刻文字列が存在することを確認
    const timeElements = screen.getAllByText(/\d{1,2}:\d{2}/)
    expect(timeElements.length).toBeGreaterThanOrEqual(1)
  })

  it('ユーザーメッセージにフィードバックがある場合、FeedbackPanelが表示される', () => {
    render(<MessageBubble message={userMessage} />)

    expect(screen.getByTestId('feedback-panel')).toBeInTheDocument()
  })

  it('AIメッセージにはFeedbackPanelが表示されない', () => {
    render(<MessageBubble message={assistantMessage} />)

    expect(screen.queryByTestId('feedback-panel')).not.toBeInTheDocument()
  })
})

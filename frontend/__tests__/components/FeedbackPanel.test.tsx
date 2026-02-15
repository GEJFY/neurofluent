import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect } from 'vitest'
import FeedbackPanel from '@/components/chat/FeedbackPanel'
import type { FeedbackData } from '@/lib/api'

/** 文法エラー・表現アップグレード・ポジティブフィードバックを含むデータ */
const fullFeedback: FeedbackData = {
  grammar_errors: [
    {
      original: 'I go to school yesterday',
      corrected: 'I went to school yesterday',
      explanation: '過去の出来事には過去形を使います',
    },
  ],
  expression_upgrades: [
    {
      original: 'very good',
      upgraded: 'excellent',
      context: 'よりフォーマルで洗練された表現です',
    },
  ],
  pronunciation_notes: [],
  positive_feedback: 'Great sentence structure!',
  vocabulary_level: 'B1',
}

/** コンテンツが空のフィードバック */
const emptyFeedback: FeedbackData = {
  grammar_errors: [],
  expression_upgrades: [],
  pronunciation_notes: [],
  positive_feedback: '',
  vocabulary_level: '',
}

describe('FeedbackPanel', () => {
  it('フィードバックアイテムが表示される（展開時）', () => {
    render(<FeedbackPanel feedback={fullFeedback} defaultExpanded={true} />)

    // Grammarセクション
    expect(screen.getByText('Grammar')).toBeInTheDocument()
    expect(screen.getByText('I go to school yesterday')).toBeInTheDocument()
    expect(screen.getByText('I went to school yesterday')).toBeInTheDocument()

    // Expression Upgradeセクション
    expect(screen.getByText('Expression Upgrade')).toBeInTheDocument()
    expect(screen.getByText('very good')).toBeInTheDocument()
    expect(screen.getByText('excellent')).toBeInTheDocument()
  })

  it('文法修正が表示される', () => {
    render(<FeedbackPanel feedback={fullFeedback} defaultExpanded={true} />)

    expect(
      screen.getByText('過去の出来事には過去形を使います')
    ).toBeInTheDocument()
  })

  it('表現アップグレードが表示される', () => {
    render(<FeedbackPanel feedback={fullFeedback} defaultExpanded={true} />)

    expect(
      screen.getByText('よりフォーマルで洗練された表現です')
    ).toBeInTheDocument()
  })

  it('ポジティブフィードバックが表示される', () => {
    render(<FeedbackPanel feedback={fullFeedback} defaultExpanded={true} />)

    expect(screen.getByText('Good Points')).toBeInTheDocument()
    expect(screen.getByText('Great sentence structure!')).toBeInTheDocument()
  })

  it('語彙レベルバッジが表示される', () => {
    render(<FeedbackPanel feedback={fullFeedback} defaultExpanded={true} />)

    expect(screen.getByText('B1')).toBeInTheDocument()
  })

  it('折りたたみ/展開がトグルできる', async () => {
    const user = userEvent.setup()
    render(<FeedbackPanel feedback={fullFeedback} defaultExpanded={false} />)

    // 初期状態では文法セクションが非表示
    expect(screen.queryByText('Grammar')).not.toBeInTheDocument()

    // Feedbackボタンをクリックして展開
    const toggleButton = screen.getByText('Feedback')
    await user.click(toggleButton)

    // 展開後は表示される
    expect(screen.getByText('Grammar')).toBeInTheDocument()
  })

  it('コンテンツが空の場合はnullを返す', () => {
    const { container } = render(
      <FeedbackPanel feedback={emptyFeedback} />
    )

    expect(container.firstChild).toBeNull()
  })
})

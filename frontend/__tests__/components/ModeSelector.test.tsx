import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ModeSelector from '@/components/talk/ModeSelector'

describe('ModeSelector', () => {
  const mockOnSelectMode = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('全会話モードが表示される', () => {
    render(<ModeSelector onSelectMode={mockOnSelectMode} />)

    expect(screen.getByText('Casual Chat')).toBeInTheDocument()
    expect(screen.getByText('Meeting')).toBeInTheDocument()
    expect(screen.getByText('Debate')).toBeInTheDocument()
    expect(screen.getByText('Presentation Q&A')).toBeInTheDocument()
    expect(screen.getByText('Negotiation')).toBeInTheDocument()
    expect(screen.getByText('Small Talk')).toBeInTheDocument()
  })

  it('日本語ラベルが表示される', () => {
    render(<ModeSelector onSelectMode={mockOnSelectMode} />)

    expect(screen.getByText('カジュアルトーク')).toBeInTheDocument()
    expect(screen.getByText('ミーティング')).toBeInTheDocument()
    expect(screen.getByText('ディベート')).toBeInTheDocument()
  })

  it('利用可能モードのクリックでコールバックが呼ばれる', async () => {
    const user = userEvent.setup()
    render(<ModeSelector onSelectMode={mockOnSelectMode} />)

    const casualButton = screen.getByText('Casual Chat').closest('button')
    await user.click(casualButton!)

    expect(mockOnSelectMode).toHaveBeenCalledWith(
      expect.objectContaining({ id: 'casual_chat', available: true })
    )
  })

  it('利用不可モードのクリックではコールバックが呼ばれない', async () => {
    const user = userEvent.setup()
    render(<ModeSelector onSelectMode={mockOnSelectMode} />)

    const presentationButton = screen.getByText('Presentation Q&A').closest('button')
    await user.click(presentationButton!)

    expect(mockOnSelectMode).not.toHaveBeenCalled()
  })

  it('選択中モードがハイライトされる', () => {
    render(<ModeSelector onSelectMode={mockOnSelectMode} selectedMode="meeting" />)

    const meetingButton = screen.getByText('Meeting').closest('button')
    expect(meetingButton).toHaveClass('border-primary')
  })

  it('Phase 3ラベルが表示される', () => {
    render(<ModeSelector onSelectMode={mockOnSelectMode} />)

    const phaseLabels = screen.getAllByText('Phase 3')
    expect(phaseLabels.length).toBe(3) // Presentation Q&A, Negotiation, Small Talk
  })

  it('ヘッダーテキストが表示される', () => {
    render(<ModeSelector onSelectMode={mockOnSelectMode} />)

    expect(screen.getByText('Select Conversation Mode')).toBeInTheDocument()
  })
})

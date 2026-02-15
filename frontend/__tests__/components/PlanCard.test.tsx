import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import PlanCard from '@/components/subscription/PlanCard'

const freePlan = {
  id: 'free',
  name: 'Free',
  nameJa: '無料プラン',
  price: 0,
  priceLabel: 'Free',
  description: '基本機能が使えます',
  features: [
    { text: 'AI Free Talk (3回/日)', included: true },
    { text: '瞬間英作文 (5問/日)', included: true },
    { text: '音声会話', included: false },
  ],
}

const standardPlan = {
  id: 'standard',
  name: 'Standard',
  nameJa: 'スタンダード',
  price: 980,
  priceLabel: '¥980/月',
  description: '全機能が使えます',
  features: [
    { text: 'AI Free Talk (無制限)', included: true },
    { text: '瞬間英作文 (無制限)', included: true },
    { text: '音声会話', included: true },
  ],
  popular: true,
}

describe('PlanCard', () => {
  const mockOnSelect = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('プラン名が表示される', () => {
    render(<PlanCard plan={freePlan} isCurrent={false} onSelect={mockOnSelect} />)
    expect(screen.getByText('Free')).toBeInTheDocument()
    expect(screen.getByText('無料プラン')).toBeInTheDocument()
  })

  it('機能リストが表示される', () => {
    render(<PlanCard plan={freePlan} isCurrent={false} onSelect={mockOnSelect} />)
    expect(screen.getByText('AI Free Talk (3回/日)')).toBeInTheDocument()
    expect(screen.getByText('音声会話')).toBeInTheDocument()
  })

  it('現在のプランでCurrent Planバッジが表示される', () => {
    render(<PlanCard plan={freePlan} isCurrent={true} onSelect={mockOnSelect} />)
    const currentLabels = screen.getAllByText('Current Plan')
    expect(currentLabels.length).toBeGreaterThanOrEqual(1)
  })

  it('人気プランでMost Popularバッジが表示される', () => {
    render(<PlanCard plan={standardPlan} isCurrent={false} onSelect={mockOnSelect} />)
    expect(screen.getByText('Most Popular')).toBeInTheDocument()
  })

  it('有料プランでUpgrade Nowボタンが表示される', () => {
    render(<PlanCard plan={standardPlan} isCurrent={false} onSelect={mockOnSelect} />)
    expect(screen.getByText('Upgrade Now')).toBeInTheDocument()
  })

  it('選択ボタンクリックでコールバックが呼ばれる', async () => {
    const user = userEvent.setup()
    render(<PlanCard plan={standardPlan} isCurrent={false} onSelect={mockOnSelect} />)
    await user.click(screen.getByText('Upgrade Now'))
    expect(mockOnSelect).toHaveBeenCalled()
  })

  it('現在のプランは選択ボタンが無効', () => {
    render(<PlanCard plan={freePlan} isCurrent={true} onSelect={mockOnSelect} />)
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })
})

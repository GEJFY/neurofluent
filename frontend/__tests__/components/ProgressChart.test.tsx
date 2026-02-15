import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import ProgressChart from '@/components/analytics/ProgressChart'

describe('ProgressChart', () => {
  const mockData = [
    { date: 'Mon', value: 30 },
    { date: 'Tue', value: 45 },
    { date: 'Wed', value: 20 },
    { date: 'Thu', value: 60 },
    { date: 'Fri', value: 35 },
  ]

  it('ラベルが表示される', () => {
    render(<ProgressChart data={mockData} label="Practice Minutes" />)
    expect(screen.getByText('Practice Minutes')).toBeInTheDocument()
  })

  it('合計値が表示される', () => {
    render(<ProgressChart data={mockData} label="Practice Minutes" />)
    // Total: 30+45+20+60+35 = 190
    expect(screen.getByText('Total: 190')).toBeInTheDocument()
  })

  it('平均値が表示される', () => {
    render(<ProgressChart data={mockData} label="Practice Minutes" />)
    // Avg: 190/5 = 38
    expect(screen.getByText('Avg: 38')).toBeInTheDocument()
  })

  it('日付ラベルが表示される', () => {
    render(<ProgressChart data={mockData} label="Practice Minutes" />)
    expect(screen.getByText('Mon')).toBeInTheDocument()
    expect(screen.getByText('Fri')).toBeInTheDocument()
  })

  it('バーが描画される', () => {
    const { container } = render(<ProgressChart data={mockData} label="Sessions" />)
    // flex-1クラスのバーグループ要素が5つ
    const bars = container.querySelectorAll('.flex-1.flex.flex-col')
    expect(bars.length).toBe(5)
  })
})

import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import FlashPage from '@/app/speaking/flash/page'

// AppShellモック
vi.mock('@/components/layout/AppShell', () => ({
  default: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="app-shell">{children}</div>
  ),
}))

// FlashCardモック
vi.mock('@/components/drill/FlashCard', () => ({
  default: () => <div data-testid="flash-card">FlashCard</div>,
}))

// APIモック
vi.mock('@/lib/api', () => ({
  api: {
    getFlashExercises: vi.fn(),
    checkFlashAnswer: vi.fn(),
  },
}))

describe('FlashPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('Flash Translationのタイトルが表示される', () => {
    render(<FlashPage />)

    expect(screen.getByText('Flash Translation')).toBeInTheDocument()
  })

  it('説明テキストが表示される', () => {
    render(<FlashPage />)

    expect(
      screen.getByText('日本語を見て、瞬時に英語に訳す練習です')
    ).toBeInTheDocument()
  })

  it('開始ボタンが表示される', () => {
    render(<FlashPage />)

    expect(
      screen.getByRole('button', { name: /Start/ })
    ).toBeInTheDocument()
  })

  it('開始ボタンに「10 Questions」と表示される', () => {
    render(<FlashPage />)

    expect(screen.getByText(/10 Questions/)).toBeInTheDocument()
  })
})

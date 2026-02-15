import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import TalkPage from '@/app/talk/page'

// AppShellモック
vi.mock('@/components/layout/AppShell', () => ({
  default: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="app-shell">{children}</div>
  ),
}))

// ChatWindowモック
vi.mock('@/components/chat/ChatWindow', () => ({
  default: () => <div data-testid="chat-window">ChatWindow</div>,
}))

// talk-storeモック（セッション未開始状態）
vi.mock('@/lib/stores/talk-store', () => ({
  useTalkStore: () => ({
    currentSession: null,
    messages: [],
    isLoading: false,
    isSending: false,
    error: null,
    startSession: vi.fn(),
    sendMessage: vi.fn(),
    reset: vi.fn(),
    clearError: vi.fn(),
  }),
}))

describe('TalkPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('AI Free Talkのタイトルが表示される', () => {
    render(<TalkPage />)

    expect(screen.getByText('AI Free Talk')).toBeInTheDocument()
  })

  it('説明テキストが表示される', () => {
    render(<TalkPage />)

    expect(
      screen.getByText(/AIと英語で自由に会話しましょう/)
    ).toBeInTheDocument()
  })

  it('モード選択肢が表示される', () => {
    render(<TalkPage />)

    expect(screen.getByText('Casual Chat')).toBeInTheDocument()
    expect(screen.getByText('Business')).toBeInTheDocument()
    expect(screen.getByText('Interview')).toBeInTheDocument()
  })

  it('Coming Soonラベルが非対応モードに表示される', () => {
    render(<TalkPage />)

    const comingSoonLabels = screen.getAllByText('(Coming Soon)')
    expect(comingSoonLabels.length).toBe(2) // Business と Interview
  })

  it('Start Talkingボタンが表示される', () => {
    render(<TalkPage />)

    expect(
      screen.getByRole('button', { name: /Start Talking/ })
    ).toBeInTheDocument()
  })

  it('Select Modeラベルが表示される', () => {
    render(<TalkPage />)

    expect(screen.getByText('Select Mode')).toBeInTheDocument()
  })
})

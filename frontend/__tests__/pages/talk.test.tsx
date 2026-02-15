import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
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
const mockStartSession = vi.fn()
const mockSendMessage = vi.fn()
const mockReset = vi.fn()
const mockClearError = vi.fn()

vi.mock('@/lib/stores/talk-store', () => ({
  useTalkStore: () => ({
    currentSession: null,
    messages: [],
    isLoading: false,
    isSending: false,
    error: null,
    startSession: mockStartSession,
    sendMessage: mockSendMessage,
    reset: mockReset,
    clearError: mockClearError,
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

  it('全モード選択肢が表示される', () => {
    render(<TalkPage />)

    expect(screen.getByText('Casual Chat')).toBeInTheDocument()
    expect(screen.getByText('Business Meeting')).toBeInTheDocument()
    expect(screen.getByText('Interview')).toBeInTheDocument()
  })

  it('全モードが有効でComing Soonラベルがない', () => {
    render(<TalkPage />)

    expect(screen.queryByText('(Coming Soon)')).not.toBeInTheDocument()
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

  it('モード選択ボタンがクリックできる', async () => {
    const user = userEvent.setup()
    render(<TalkPage />)

    const meetingButton = screen.getByText('Business Meeting').closest('button')
    expect(meetingButton).not.toBeDisabled()
    await user.click(meetingButton!)
  })

  it('Start TalkingクリックでstartSessionが呼ばれる', async () => {
    const user = userEvent.setup()
    render(<TalkPage />)

    const startButton = screen.getByRole('button', { name: /Start Talking/ })
    await user.click(startButton)

    expect(mockStartSession).toHaveBeenCalledWith('casual_chat')
  })
})

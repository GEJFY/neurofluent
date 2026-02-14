import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ChatWindow from '@/components/chat/ChatWindow'
import type { TalkMessageResponse } from '@/lib/api'

// MessageBubble のモック（ChatWindowの責務に集中するため）
vi.mock('@/components/chat/MessageBubble', () => ({
  default: ({ message }: { message: TalkMessageResponse }) => (
    <div data-testid={`message-${message.id}`}>{message.content}</div>
  ),
}))

/** テスト用メッセージデータ */
const mockMessages: TalkMessageResponse[] = [
  {
    id: 'msg-1',
    role: 'user',
    content: 'Hello, how are you?',
    feedback: null,
    created_at: '2026-01-15T10:00:00Z',
  },
  {
    id: 'msg-2',
    role: 'assistant',
    content: 'I am fine, thank you!',
    feedback: null,
    created_at: '2026-01-15T10:00:05Z',
  },
]

describe('ChatWindow', () => {
  it('チャットメッセージが表示される', () => {
    render(<ChatWindow messages={mockMessages} />)

    expect(screen.getByText('Hello, how are you?')).toBeInTheDocument()
    expect(screen.getByText('I am fine, thank you!')).toBeInTheDocument()
  })

  it('メッセージが空の場合、プレースホルダーが表示される', () => {
    render(<ChatWindow messages={[]} />)

    expect(screen.getByText('Start a conversation')).toBeInTheDocument()
    expect(screen.getByText('英語で何でも話してみましょう')).toBeInTheDocument()
  })

  it('送信中のインジケーターが表示される', () => {
    const { container } = render(
      <ChatWindow messages={mockMessages} isSending={true} />
    )

    // ローディングドットアニメーションが表示される
    const bounceDots = container.querySelectorAll('.animate-bounce')
    expect(bounceDots.length).toBeGreaterThanOrEqual(3)
  })

  it('送信中でない場合、インジケーターが非表示', () => {
    const { container } = render(
      <ChatWindow messages={mockMessages} isSending={false} />
    )

    const bounceDots = container.querySelectorAll('.animate-bounce')
    expect(bounceDots.length).toBe(0)
  })

  it('メッセージが空で送信中の場合、プレースホルダーは非表示', () => {
    render(<ChatWindow messages={[]} isSending={true} />)

    expect(screen.queryByText('Start a conversation')).not.toBeInTheDocument()
  })
})

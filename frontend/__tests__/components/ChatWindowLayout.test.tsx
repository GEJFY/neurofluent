import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeAll } from 'vitest'
import ChatWindow from '@/components/chat/ChatWindow'
import MessageBubble from '@/components/chat/MessageBubble'
import type { TalkMessageResponse } from '@/lib/api'

// jsdom に scrollIntoView が無いためモック
beforeAll(() => {
  Element.prototype.scrollIntoView = vi.fn()
})

const mockMessage: TalkMessageResponse = {
  id: 'msg-1',
  role: 'assistant',
  content: 'Hello there!',
  feedback: null,
  created_at: '2026-01-15T10:00:00Z',
}

describe('ChatWindow - デスクトップレイアウト', () => {
  it('コンテナに px-4 クラスが存在する', () => {
    const { container } = render(<ChatWindow messages={[]} />)
    const scrollContainer = container.querySelector('.overflow-y-auto')
    expect(scrollContainer).toHaveClass('px-4')
  })

  it('コンテナに lg:px-8 クラスが存在する', () => {
    const { container } = render(<ChatWindow messages={[]} />)
    const scrollContainer = container.querySelector('.overflow-y-auto')
    expect(scrollContainer?.className).toContain('lg:px-8')
  })
})

describe('MessageBubble - デスクトップレイアウト', () => {
  it('メッセージ幅に lg:max-w-[60%] が適用される', () => {
    const { container } = render(<MessageBubble message={mockMessage} />)
    // max-w-[85%] md:max-w-[70%] lg:max-w-[60%] を持つ要素を検索
    const bubble = container.querySelector('[class*="lg:max-w-"]')
    expect(bubble).not.toBeNull()
    expect(bubble?.className).toContain('lg:max-w-[60%]')
  })

  it('基本の max-w が設定されている', () => {
    const { container } = render(<MessageBubble message={mockMessage} />)
    const bubble = container.querySelector('[class*="max-w-"]')
    expect(bubble).not.toBeNull()
    expect(bubble?.className).toContain('max-w-[85%]')
    expect(bubble?.className).toContain('md:max-w-[70%]')
  })
})

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import VoiceChat from '@/components/talk/VoiceChat'

// api モック
vi.mock('@/lib/api', () => ({
  api: {
    sendMessage: vi.fn(),
    requestTTS: vi.fn(),
  },
}))

describe('VoiceChat', () => {
  const defaultProps = {
    sessionId: 'test-session-001',
    mode: 'casual_chat',
    onEnd: vi.fn(),
  }

  it('ブラウザ非対応時に案内メッセージが表示される', () => {
    // jsdom には SpeechRecognition がないため非対応表示になる
    render(<VoiceChat {...defaultProps} />)

    expect(screen.getByText('Voice Chat is not available')).toBeInTheDocument()
    expect(
      screen.getByText(/このブラウザは音声認識/)
    ).toBeInTheDocument()
  })

  it('ブラウザ非対応時に「テキストモードに切り替え」ボタンが表示される', () => {
    render(<VoiceChat {...defaultProps} />)

    expect(screen.getByText('テキストモードに切り替え')).toBeInTheDocument()
  })

  it('「テキストモードに切り替え」クリックで onEnd が呼ばれる', async () => {
    const user = userEvent.setup()
    const onEnd = vi.fn()
    render(<VoiceChat {...defaultProps} onEnd={onEnd} />)

    await user.click(screen.getByText('テキストモードに切り替え'))
    expect(onEnd).toHaveBeenCalledTimes(1)
  })

  it('Chrome/Edge ラベルが案内に含まれる', () => {
    render(<VoiceChat {...defaultProps} />)

    expect(
      screen.getByText(/Chrome、Edge、または Safari/)
    ).toBeInTheDocument()
  })
})

describe('VoiceChat (SpeechRecognition対応環境)', () => {
  const defaultProps = {
    sessionId: 'test-session-001',
    mode: 'casual_chat',
    onEnd: vi.fn(),
  }

  // SpeechRecognition をモック
  const MockSpeechRecognition = vi.fn(() => ({
    lang: '',
    interimResults: false,
    continuous: false,
    maxAlternatives: 1,
    start: vi.fn(),
    stop: vi.fn(),
    abort: vi.fn(),
    onresult: null,
    onerror: null,
    onend: null,
  }))

  beforeEach(() => {
    // SpeechRecognition をグローバルに設定
    Object.defineProperty(window, 'SpeechRecognition', {
      value: MockSpeechRecognition,
      writable: true,
      configurable: true,
    })
  })

  afterEach(() => {
    // クリーンアップ
    Object.defineProperty(window, 'SpeechRecognition', {
      value: undefined,
      writable: true,
      configurable: true,
    })
  })

  it('End ボタンが表示される', () => {
    render(<VoiceChat {...defaultProps} />)

    expect(screen.getByText('End')).toBeInTheDocument()
  })

  it('End ボタンクリックで onEnd が呼ばれる', async () => {
    const user = userEvent.setup()
    const onEnd = vi.fn()
    render(<VoiceChat {...defaultProps} onEnd={onEnd} />)

    await user.click(screen.getByText('End'))
    expect(onEnd).toHaveBeenCalledTimes(1)
  })

  it('メッセージカウントとモードが表示される', () => {
    render(<VoiceChat {...defaultProps} />)

    expect(screen.getByText('Messages: 0')).toBeInTheDocument()
    expect(screen.getByText('Mode: casual_chat')).toBeInTheDocument()
  })

  it('idle 状態で "Tap to speak" が表示される', () => {
    render(<VoiceChat {...defaultProps} />)

    expect(screen.getByText('Tap to speak')).toBeInTheDocument()
  })
})

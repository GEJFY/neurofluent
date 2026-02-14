import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act } from '@testing-library/react'

// APIモック
vi.mock('@/lib/api', () => ({
  api: {
    login: vi.fn(),
    register: vi.fn(),
    getMe: vi.fn(),
    clearToken: vi.fn(),
    startTalk: vi.fn(),
    sendMessage: vi.fn(),
    getSession: vi.fn(),
  },
  ApiError: class ApiError extends Error {
    status: number
    statusText: string
    detail?: string
    constructor(status: number, statusText: string, detail?: string) {
      super(detail || `API Error: ${status} ${statusText}`)
      this.name = 'ApiError'
      this.status = status
      this.statusText = statusText
      this.detail = detail
    }
  },
}))

describe('AuthStore', () => {
  // 各テスト前にモジュールキャッシュをリセットしてストアを初期化
  beforeEach(async () => {
    vi.clearAllMocks()
    // zustandストアのリセットのため、モジュールを再インポート
    vi.resetModules()
  })

  it('初期状態が正しい', async () => {
    const { useAuthStore } = await import('@/lib/stores/auth-store')
    const state = useAuthStore.getState()

    expect(state.user).toBeNull()
    expect(state.isInitialized).toBe(false)
    expect(state.isLoading).toBe(false)
    expect(state.error).toBeNull()
  })

  it('clearErrorでエラーがクリアされる', async () => {
    const { useAuthStore } = await import('@/lib/stores/auth-store')

    // エラーを直接セット（内部テスト用）
    useAuthStore.setState({ error: 'テストエラー' })
    expect(useAuthStore.getState().error).toBe('テストエラー')

    // clearErrorを実行
    act(() => {
      useAuthStore.getState().clearError()
    })

    expect(useAuthStore.getState().error).toBeNull()
  })

  it('logoutでユーザーがクリアされる', async () => {
    const { useAuthStore } = await import('@/lib/stores/auth-store')
    const { api } = await import('@/lib/api')

    // ユーザーがログイン中の状態をセット
    useAuthStore.setState({
      user: {
        id: 'user-1',
        email: 'test@example.com',
        name: 'Test User',
        target_level: 'intermediate',
        subscription_plan: 'free',
        daily_goal_minutes: 30,
        native_language: 'ja',
        created_at: '2026-01-01T00:00:00Z',
      },
    })

    // logout実行
    act(() => {
      useAuthStore.getState().logout()
    })

    expect(useAuthStore.getState().user).toBeNull()
    expect(api.clearToken).toHaveBeenCalled()
  })

  it('initializeメソッドが存在する', async () => {
    const { useAuthStore } = await import('@/lib/stores/auth-store')

    expect(typeof useAuthStore.getState().initialize).toBe('function')
  })

  it('loginメソッドが存在する', async () => {
    const { useAuthStore } = await import('@/lib/stores/auth-store')

    expect(typeof useAuthStore.getState().login).toBe('function')
  })

  it('registerメソッドが存在する', async () => {
    const { useAuthStore } = await import('@/lib/stores/auth-store')

    expect(typeof useAuthStore.getState().register).toBe('function')
  })
})

describe('TalkStore', () => {
  beforeEach(async () => {
    vi.clearAllMocks()
    vi.resetModules()
  })

  it('初期状態が正しい', async () => {
    const { useTalkStore } = await import('@/lib/stores/talk-store')
    const state = useTalkStore.getState()

    expect(state.currentSession).toBeNull()
    expect(state.messages).toEqual([])
    expect(state.isLoading).toBe(false)
    expect(state.isSending).toBe(false)
    expect(state.error).toBeNull()
  })

  it('resetでストアが初期化される', async () => {
    const { useTalkStore } = await import('@/lib/stores/talk-store')

    // ストアにデータをセット
    useTalkStore.setState({
      currentSession: {
        id: 'session-1',
        mode: 'casual_chat',
        scenario_description: null,
        started_at: '2026-01-15T10:00:00Z',
        ended_at: null,
        duration_seconds: null,
        overall_score: null,
        messages: [],
      },
      messages: [
        {
          id: 'msg-1',
          role: 'user',
          content: 'Hello',
          feedback: null,
          created_at: '2026-01-15T10:00:00Z',
        },
      ],
      isLoading: true,
      isSending: true,
      error: 'some error',
    })

    // reset実行
    act(() => {
      useTalkStore.getState().reset()
    })

    const state = useTalkStore.getState()
    expect(state.currentSession).toBeNull()
    expect(state.messages).toEqual([])
    expect(state.isLoading).toBe(false)
    expect(state.isSending).toBe(false)
    expect(state.error).toBeNull()
  })

  it('clearErrorでエラーがクリアされる', async () => {
    const { useTalkStore } = await import('@/lib/stores/talk-store')

    useTalkStore.setState({ error: 'テストエラー' })
    expect(useTalkStore.getState().error).toBe('テストエラー')

    act(() => {
      useTalkStore.getState().clearError()
    })

    expect(useTalkStore.getState().error).toBeNull()
  })

  it('startSessionメソッドが存在する', async () => {
    const { useTalkStore } = await import('@/lib/stores/talk-store')

    expect(typeof useTalkStore.getState().startSession).toBe('function')
  })

  it('sendMessageメソッドが存在する', async () => {
    const { useTalkStore } = await import('@/lib/stores/talk-store')

    expect(typeof useTalkStore.getState().sendMessage).toBe('function')
  })

  it('loadSessionメソッドが存在する', async () => {
    const { useTalkStore } = await import('@/lib/stores/talk-store')

    expect(typeof useTalkStore.getState().loadSession).toBe('function')
  })

  it('startSessionでisLoadingがtrueになる', async () => {
    const { useTalkStore } = await import('@/lib/stores/talk-store')
    const { api } = await import('@/lib/api')

    // APIが未解決のPromiseを返す（ローディング状態を確認するため）
    ;(api.startTalk as ReturnType<typeof vi.fn>).mockReturnValue(
      new Promise(() => {}) // 永遠に解決しない
    )

    // 非同期でstartSessionを開始（awaitしない）
    act(() => {
      useTalkStore.getState().startSession('casual_chat')
    })

    expect(useTalkStore.getState().isLoading).toBe(true)
  })
})

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { api, ApiError } from '@/lib/api'

/** fetchのモック */
const mockFetch = vi.fn()

describe('ApiClient', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // global.fetchをモック
    global.fetch = mockFetch
    // localStorageモック
    Storage.prototype.getItem = vi.fn()
    Storage.prototype.setItem = vi.fn()
    Storage.prototype.removeItem = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('インスタンス', () => {
    it('apiインスタンスが存在する', () => {
      expect(api).toBeDefined()
    })

    it('setTokenメソッドが存在する', () => {
      expect(typeof api.setToken).toBe('function')
    })

    it('clearTokenメソッドが存在する', () => {
      expect(typeof api.clearToken).toBe('function')
    })
  })

  describe('認証API', () => {
    it('login メソッドが存在する', () => {
      expect(typeof api.login).toBe('function')
    })

    it('register メソッドが存在する', () => {
      expect(typeof api.register).toBe('function')
    })

    it('getMe メソッドが存在する', () => {
      expect(typeof api.getMe).toBe('function')
    })
  })

  describe('Talk API', () => {
    it('startTalk メソッドが存在する', () => {
      expect(typeof api.startTalk).toBe('function')
    })

    it('sendMessage メソッドが存在する', () => {
      expect(typeof api.sendMessage).toBe('function')
    })

    it('getSessions メソッドが存在する', () => {
      expect(typeof api.getSessions).toBe('function')
    })

    it('getSession メソッドが存在する', () => {
      expect(typeof api.getSession).toBe('function')
    })
  })

  describe('Flash Translation API', () => {
    it('getFlashExercises メソッドが存在する', () => {
      expect(typeof api.getFlashExercises).toBe('function')
    })

    it('checkFlashAnswer メソッドが存在する', () => {
      expect(typeof api.checkFlashAnswer).toBe('function')
    })
  })

  describe('Review API', () => {
    it('getDueReviews メソッドが存在する', () => {
      expect(typeof api.getDueReviews).toBe('function')
    })

    it('completeReview メソッドが存在する', () => {
      expect(typeof api.completeReview).toBe('function')
    })
  })

  describe('Dashboard API', () => {
    it('getDashboard メソッドが存在する', () => {
      expect(typeof api.getDashboard).toBe('function')
    })
  })

  describe('トークン管理', () => {
    it('setTokenでlocalStorageに保存される', () => {
      api.setToken('test-token-123')

      expect(localStorage.setItem).toHaveBeenCalledWith(
        'fluentedge_token',
        'test-token-123'
      )
    })

    it('clearTokenでlocalStorageから削除される', () => {
      api.clearToken()

      expect(localStorage.removeItem).toHaveBeenCalledWith('fluentedge_token')
    })
  })

  describe('エラーハンドリング', () => {
    it('ApiErrorクラスが正しく動作する', () => {
      const error = new ApiError(404, 'Not Found', 'Resource not found')

      expect(error).toBeInstanceOf(Error)
      expect(error).toBeInstanceOf(ApiError)
      expect(error.status).toBe(404)
      expect(error.statusText).toBe('Not Found')
      expect(error.detail).toBe('Resource not found')
      expect(error.name).toBe('ApiError')
    })

    it('ApiErrorのdetailがundefinedの場合、デフォルトメッセージ', () => {
      const error = new ApiError(500, 'Internal Server Error')

      expect(error.message).toBe('API Error: 500 Internal Server Error')
    })

    it('APIエラーレスポンス時にApiErrorがスローされる', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: async () => ({ detail: 'Invalid credentials' }),
      })

      await expect(api.getMe()).rejects.toThrow(ApiError)
    })

    it('login成功時にトークンが保存される', async () => {
      mockFetch
        // login リクエスト
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({
            access_token: 'new-token-abc',
            token_type: 'bearer',
          }),
        })
        // getMe リクエスト（login内部でsetToken後に自動呼び出しはされないが、
        // login自体がsetTokenを呼ぶ）

      // loginはsetTokenを内部で呼ぶ
      const result = await api.login('test@example.com', 'password123')

      expect(result.access_token).toBe('new-token-abc')
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'fluentedge_token',
        'new-token-abc'
      )
    })
  })

  describe('Phase 2-4 APIメソッド', () => {
    it('getShadowingMaterials メソッドが存在する', () => {
      expect(typeof api.getShadowingMaterials).toBe('function')
    })

    it('getPatternExercises メソッドが存在する', () => {
      expect(typeof api.getPatternExercises).toBe('function')
    })

    it('startRealtimeSession メソッドが存在する', () => {
      expect(typeof api.startRealtimeSession).toBe('function')
    })

    it('getRealtimeWebSocketUrl メソッドが存在する', () => {
      expect(typeof api.getRealtimeWebSocketUrl).toBe('function')
    })

    it('getAdvancedAnalytics メソッドが存在する', () => {
      expect(typeof api.getAdvancedAnalytics).toBe('function')
    })

    it('getSubscription メソッドが存在する', () => {
      expect(typeof api.getSubscription).toBe('function')
    })

    it('getPronunciationExercises メソッドが存在する', () => {
      expect(typeof api.getPronunciationExercises).toBe('function')
    })

    it('getComprehensionExercises メソッドが存在する', () => {
      expect(typeof api.getComprehensionExercises).toBe('function')
    })
  })

  describe('WebSocket URL生成', () => {
    it('getRealtimeWebSocketUrlが正しいURLを生成する', () => {
      ;(localStorage.getItem as ReturnType<typeof vi.fn>).mockReturnValue(
        'test-token'
      )

      const url = api.getRealtimeWebSocketUrl('session-123')

      expect(url).toContain('ws')
      expect(url).toContain('session-123')
      expect(url).toContain('token=test-token')
    })
  })
})

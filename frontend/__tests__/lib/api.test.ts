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
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          access_token: 'new-token-abc',
          token_type: 'bearer',
        }),
      })

      const result = await api.login('test@example.com', 'password123')

      expect(result.access_token).toBe('new-token-abc')
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'fluentedge_token',
        'new-token-abc'
      )
    })
  })

  describe('Phase 2-4 APIメソッド', () => {
    it('getShadowingMaterial メソッドが存在する', () => {
      expect(typeof api.getShadowingMaterial).toBe('function')
    })

    it('getPatternExercises メソッドが存在する', () => {
      expect(typeof api.getPatternExercises).toBe('function')
    })

    it('createRealtimeSession メソッドが存在する', () => {
      expect(typeof api.createRealtimeSession).toBe('function')
    })

    it('getConversationModes メソッドが存在する', () => {
      expect(typeof api.getConversationModes).toBe('function')
    })

    it('getSkillBreakdown メソッドが存在する', () => {
      expect(typeof api.getSkillBreakdown).toBe('function')
    })

    it('getCurrentSubscription メソッドが存在する', () => {
      expect(typeof api.getCurrentSubscription).toBe('function')
    })

    it('getPronunciationExercises メソッドが存在する', () => {
      expect(typeof api.getPronunciationExercises).toBe('function')
    })

    it('getComprehensionMaterial メソッドが存在する', () => {
      expect(typeof api.getComprehensionMaterial).toBe('function')
    })
  })

  describe('新規APIメソッド', () => {
    it('getPhonemes メソッドが存在する', () => {
      expect(typeof api.getPhonemes).toBe('function')
    })

    it('getMogomogoExercises メソッドが存在する', () => {
      expect(typeof api.getMogomogoExercises).toBe('function')
    })

    it('checkDictation メソッドが存在する', () => {
      expect(typeof api.checkDictation).toBe('function')
    })

    it('getWeeklyReport メソッドが存在する', () => {
      expect(typeof api.getWeeklyReport).toBe('function')
    })

    it('getRecommendations メソッドが存在する', () => {
      expect(typeof api.getRecommendations).toBe('function')
    })

    it('getSubscriptionPlans メソッドが存在する', () => {
      expect(typeof api.getSubscriptionPlans).toBe('function')
    })

    it('createCheckout メソッドが存在する', () => {
      expect(typeof api.createCheckout).toBe('function')
    })
  })
})

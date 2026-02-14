/**
 * FluentEdge AI - APIクライアント
 * バックエンド (FastAPI) との通信を管理
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ===== 型定義（バックエンドスキーマ準拠） =====

/** JWTトークンレスポンス */
export interface Token {
  access_token: string;
  token_type: string;
}

/** ユーザー情報 */
export interface User {
  id: string;
  email: string;
  name: string;
  target_level: string;
  subscription_plan: string;
  daily_goal_minutes: number;
  native_language: string;
  created_at: string;
}

/** フィードバックデータ */
export interface FeedbackData {
  grammar_errors: { original: string; corrected: string; explanation: string }[];
  expression_upgrades: { original: string; upgraded: string; context: string }[];
  pronunciation_notes: string[];
  positive_feedback: string;
  vocabulary_level: string;
}

/** チャットメッセージレスポンス */
export interface TalkMessageResponse {
  id: string;
  role: "user" | "assistant";
  content: string;
  feedback: FeedbackData | null;
  created_at: string;
}

/** セッション詳細レスポンス */
export interface SessionResponse {
  id: string;
  mode: string;
  scenario_description: string | null;
  started_at: string;
  ended_at: string | null;
  duration_seconds: number | null;
  overall_score: Record<string, unknown> | null;
  messages: TalkMessageResponse[];
}

/** セッション一覧レスポンス */
export interface SessionListResponse {
  id: string;
  mode: string;
  started_at: string;
  duration_seconds: number | null;
}

/** Flash Translation 問題 */
export interface FlashExercise {
  exercise_id: string;
  japanese: string;
  english_target: string;
  acceptable_alternatives: string[];
  key_pattern: string;
  difficulty: string;
  time_limit_seconds: number;
  hints: string[];
}

/** Flash Translation 回答結果 */
export interface FlashCheckResponse {
  is_correct: boolean;
  score: number;
  corrected: string;
  explanation: string;
  review_item_created: boolean;
}

/** 復習アイテムレスポンス */
export interface ReviewItemResponse {
  id: string;
  item_type: string;
  content: Record<string, unknown>;
  next_review_at: string | null;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
}

/** 復習完了レスポンス */
export interface ReviewCompleteResponse {
  next_review_at: string;
  new_interval_days: number;
  new_ease_factor: number;
}

/** ダッシュボードレスポンス */
export interface DashboardData {
  streak_days: number;
  total_practice_minutes: number;
  total_sessions: number;
  total_reviews_completed: number;
  total_expressions_learned: number;
  avg_grammar_accuracy: number | null;
  avg_pronunciation_score: number | null;
  recent_daily_stats: {
    date: string;
    practice_minutes: number;
    sessions_completed: number;
    reviews_completed: number;
    new_expressions_learned: number;
    grammar_accuracy: number | null;
    pronunciation_avg_score: number | null;
  }[];
  pending_reviews: number;
}

// ===== Phase 2: 音声統合 型定義 =====

/** シャドーイング素材 */
export interface ShadowingMaterial {
  id: string;
  title: string;
  audio_url: string;
  transcript: string;
  segments: { start: number; end: number; text: string }[];
  difficulty: string;
  duration_seconds: number;
  category: string;
}

/** シャドーイング結果 */
export interface ShadowingResult {
  overall_score: number;
  accuracy: number;
  fluency: number;
  timing_score: number;
  segment_scores: { segment_index: number; score: number; feedback: string }[];
  review_items_created: number;
}

/** パターン練習問題 */
export interface PatternExercise {
  id: string;
  pattern_name: string;
  pattern_description: string;
  japanese_prompt: string;
  example_answer: string;
  variations: string[];
  difficulty: number;
  category: string;
}

/** パターン練習結果 */
export interface PatternCheckResponse {
  is_correct: boolean;
  score: number;
  feedback: string;
  corrected: string;
  pattern_mastery_updated: boolean;
}

/** リアルタイム音声セッション情報 */
export interface RealtimeSession {
  session_id: string;
  websocket_url: string;
  mode: string;
  ice_servers?: { urls: string }[];
}

// ===== Phase 3: 学習最適化 型定義 =====

/** もごもごイングリッシュ素材 */
export interface MogomogoMaterial {
  id: string;
  title: string;
  original_text: string;
  connected_text: string;
  audio_url: string;
  audio_slow_url: string;
  pattern_type: string;
  difficulty: number;
  examples: { phrase: string; connected: string; explanation: string }[];
}

/** もごもご練習結果 */
export interface MogomogoResult {
  score: number;
  accuracy: number;
  detected_patterns: string[];
  feedback: string;
  next_difficulty: number;
}

/** 高度な分析レスポンス */
export interface AdvancedAnalytics {
  skill_radar: { skill: string; score: number; change: number }[];
  weekly_trend: { week: string; score: number; practice_minutes: number }[];
  pattern_mastery: { pattern: string; mastery: number; review_count: number }[];
  weak_areas: { area: string; description: string; recommended_exercise: string }[];
  curriculum_suggestion: string;
}

/** サブスクリプション情報 */
export interface SubscriptionInfo {
  plan: string;
  status: string;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  usage: { api_calls_today: number; api_calls_limit: number };
}

/** Stripe決済セッション */
export interface CheckoutSession {
  checkout_url: string;
  session_id: string;
}

/** 週次/月次レポート */
export interface LearningReport {
  period: string;
  total_minutes: number;
  sessions_count: number;
  streak_days: number;
  skills_improved: { skill: string; before: number; after: number }[];
  highlights: string[];
  recommendations: string[];
}

// ===== Phase 4: 高度な機能 型定義 =====

/** 発音練習素材 */
export interface PronunciationExercise {
  id: string;
  target_phoneme: string;
  word: string;
  ipa: string;
  audio_url: string;
  mouth_position_image: string | null;
  tips: string[];
  difficulty: number;
  minimal_pairs: { word1: string; word2: string }[];
}

/** 発音評価結果 */
export interface PronunciationResult {
  overall_score: number;
  phoneme_scores: { phoneme: string; score: number; feedback: string }[];
  spectral_analysis: { frequency: number; amplitude: number }[] | null;
  improvement_tips: string[];
}

/** リスニング理解度テスト問題 */
export interface ComprehensionExercise {
  id: string;
  audio_url: string;
  title: string;
  duration_seconds: number;
  difficulty: string;
  questions: {
    id: string;
    question: string;
    options: string[];
    type: string;
  }[];
}

/** リスニング理解度結果 */
export interface ComprehensionResult {
  score: number;
  total_questions: number;
  correct_answers: number;
  details: { question_id: string; correct: boolean; explanation: string }[];
}

// ===== APIエラーハンドリング =====

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public detail?: string
  ) {
    super(detail || `API Error: ${status} ${statusText}`);
    this.name = "ApiError";
  }
}

// ===== APIクライアント =====

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  /** 認証トークン取得 */
  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("fluentedge_token");
  }

  /** 認証トークン保存 */
  setToken(token: string): void {
    if (typeof window !== "undefined") {
      localStorage.setItem("fluentedge_token", token);
    }
  }

  /** 認証トークン削除 */
  clearToken(): void {
    if (typeof window !== "undefined") {
      localStorage.removeItem("fluentedge_token");
    }
  }

  /** 共通リクエストメソッド */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...((options.headers as Record<string, string>) || {}),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let detail: string | undefined;
      try {
        const errorBody = await response.json();
        detail = errorBody.detail || errorBody.message;
      } catch {
        // JSONパース失敗の場合は無視
      }
      throw new ApiError(response.status, response.statusText, detail);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  // ===== 認証 API =====

  /** ユーザー登録 */
  async register(
    email: string,
    password: string,
    name: string
  ): Promise<Token> {
    const response = await this.request<Token>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, name }),
    });
    this.setToken(response.access_token);
    return response;
  }

  /** ログイン */
  async login(email: string, password: string): Promise<Token> {
    const response = await this.request<Token>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    this.setToken(response.access_token);
    return response;
  }

  /** 現在のユーザー情報取得 */
  async getMe(): Promise<User> {
    return this.request<User>("/api/auth/me");
  }

  // ===== Talk API =====

  /** トークセッション開始 */
  async startTalk(
    mode: string = "casual_chat",
    scenarioDescription?: string
  ): Promise<SessionResponse> {
    return this.request<SessionResponse>("/api/talk/start", {
      method: "POST",
      body: JSON.stringify({
        mode,
        scenario_description: scenarioDescription,
      }),
    });
  }

  /** メッセージ送信 */
  async sendMessage(
    sessionId: string,
    content: string
  ): Promise<TalkMessageResponse> {
    return this.request<TalkMessageResponse>("/api/talk/message", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, content }),
    });
  }

  /** セッション一覧取得 */
  async getSessions(): Promise<SessionListResponse[]> {
    return this.request<SessionListResponse[]>("/api/talk/sessions");
  }

  /** セッション詳細取得（メッセージ含む） */
  async getSession(sessionId: string): Promise<SessionResponse> {
    return this.request<SessionResponse>(
      `/api/talk/sessions/${sessionId}`
    );
  }

  // ===== Flash Translation API =====

  /** Flash問題取得 */
  async getFlashExercises(
    count: number = 5,
    focus?: string
  ): Promise<FlashExercise[]> {
    const params = new URLSearchParams({ count: String(count) });
    if (focus) params.set("focus", focus);
    return this.request<FlashExercise[]>(
      `/api/speaking/flash?${params.toString()}`
    );
  }

  /** Flash回答チェック */
  async checkFlashAnswer(
    exerciseId: string,
    userAnswer: string,
    target: string
  ): Promise<FlashCheckResponse> {
    return this.request<FlashCheckResponse>("/api/speaking/flash/check", {
      method: "POST",
      body: JSON.stringify({
        exercise_id: exerciseId,
        user_answer: userAnswer,
        target,
      }),
    });
  }

  // ===== Review (SRS) API =====

  /** 今日の復習アイテム取得 */
  async getDueReviews(): Promise<ReviewItemResponse[]> {
    return this.request<ReviewItemResponse[]>("/api/review/due");
  }

  /** 復習完了（評価送信） - rating: 1=Again, 2=Hard, 3=Good, 4=Easy */
  async completeReview(
    itemId: string,
    rating: number
  ): Promise<ReviewCompleteResponse> {
    return this.request<ReviewCompleteResponse>("/api/review/complete", {
      method: "POST",
      body: JSON.stringify({ item_id: itemId, rating }),
    });
  }

  // ===== Dashboard API =====

  /** ダッシュボードデータ取得 */
  async getDashboard(): Promise<DashboardData> {
    return this.request<DashboardData>("/api/analytics/dashboard");
  }

  // ===== Phase 2: Listening (Shadowing) API =====

  /** シャドーイング素材一覧取得 */
  async getShadowingMaterials(
    difficulty?: string,
    category?: string
  ): Promise<ShadowingMaterial[]> {
    const params = new URLSearchParams();
    if (difficulty) params.set("difficulty", difficulty);
    if (category) params.set("category", category);
    const qs = params.toString();
    return this.request<ShadowingMaterial[]>(
      `/api/listening/shadowing${qs ? `?${qs}` : ""}`
    );
  }

  /** シャドーイング結果送信 */
  async submitShadowingResult(
    materialId: string,
    audioBlob: Blob
  ): Promise<ShadowingResult> {
    const formData = new FormData();
    formData.append("material_id", materialId);
    formData.append("audio", audioBlob, "recording.webm");

    const token = this.getToken();
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const response = await fetch(
      `${this.baseUrl}/api/listening/shadowing/evaluate`,
      { method: "POST", headers, body: formData }
    );
    if (!response.ok) {
      const detail = await response.text();
      throw new ApiError(response.status, response.statusText, detail);
    }
    return response.json();
  }

  // ===== Phase 2: Pattern Practice API =====

  /** パターン練習問題取得 */
  async getPatternExercises(
    count: number = 5,
    category?: string
  ): Promise<PatternExercise[]> {
    const params = new URLSearchParams({ count: String(count) });
    if (category) params.set("category", category);
    return this.request<PatternExercise[]>(
      `/api/speaking/pattern?${params.toString()}`
    );
  }

  /** パターン練習回答チェック */
  async checkPatternAnswer(
    exerciseId: string,
    userAnswer: string
  ): Promise<PatternCheckResponse> {
    return this.request<PatternCheckResponse>(
      "/api/speaking/pattern/check",
      {
        method: "POST",
        body: JSON.stringify({
          exercise_id: exerciseId,
          user_answer: userAnswer,
        }),
      }
    );
  }

  // ===== Phase 2: Realtime Voice API =====

  /** リアルタイム音声セッション開始 */
  async startRealtimeSession(
    mode: string = "casual_chat"
  ): Promise<RealtimeSession> {
    return this.request<RealtimeSession>("/api/talk/realtime/start", {
      method: "POST",
      body: JSON.stringify({ mode }),
    });
  }

  /** WebSocket URLを生成（リアルタイム音声用） */
  getRealtimeWebSocketUrl(sessionId: string): string {
    const wsBase = this.baseUrl
      .replace("http://", "ws://")
      .replace("https://", "wss://");
    const token = this.getToken();
    return `${wsBase}/api/talk/realtime/ws/${sessionId}?token=${token}`;
  }

  // ===== Phase 3: もごもごイングリッシュ API =====

  /** もごもご素材一覧取得 */
  async getMogomogoMaterials(
    patternType?: string,
    difficulty?: number
  ): Promise<MogomogoMaterial[]> {
    const params = new URLSearchParams();
    if (patternType) params.set("pattern_type", patternType);
    if (difficulty) params.set("difficulty", String(difficulty));
    const qs = params.toString();
    return this.request<MogomogoMaterial[]>(
      `/api/listening/mogomogo${qs ? `?${qs}` : ""}`
    );
  }

  /** もごもご練習結果送信 */
  async submitMogomogoResult(
    materialId: string,
    audioBlob: Blob
  ): Promise<MogomogoResult> {
    const formData = new FormData();
    formData.append("material_id", materialId);
    formData.append("audio", audioBlob, "recording.webm");

    const token = this.getToken();
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const response = await fetch(
      `${this.baseUrl}/api/listening/mogomogo/evaluate`,
      { method: "POST", headers, body: formData }
    );
    if (!response.ok) {
      const detail = await response.text();
      throw new ApiError(response.status, response.statusText, detail);
    }
    return response.json();
  }

  // ===== Phase 3: Advanced Analytics API =====

  /** 高度な分析データ取得 */
  async getAdvancedAnalytics(): Promise<AdvancedAnalytics> {
    return this.request<AdvancedAnalytics>("/api/analytics/advanced");
  }

  /** 週次レポート取得 */
  async getWeeklyReport(weekStart?: string): Promise<LearningReport> {
    const params = weekStart ? `?week_start=${weekStart}` : "";
    return this.request<LearningReport>(
      `/api/analytics/advanced/report/weekly${params}`
    );
  }

  /** 月次レポート取得 */
  async getMonthlyReport(month?: string): Promise<LearningReport> {
    const params = month ? `?month=${month}` : "";
    return this.request<LearningReport>(
      `/api/analytics/advanced/report/monthly${params}`
    );
  }

  // ===== Phase 3: Subscription API =====

  /** サブスクリプション情報取得 */
  async getSubscription(): Promise<SubscriptionInfo> {
    return this.request<SubscriptionInfo>("/api/subscription");
  }

  /** チェックアウトセッション作成 */
  async createCheckout(plan: string): Promise<CheckoutSession> {
    return this.request<CheckoutSession>("/api/subscription/checkout", {
      method: "POST",
      body: JSON.stringify({ plan }),
    });
  }

  /** サブスクリプション解約 */
  async cancelSubscription(): Promise<{ message: string }> {
    return this.request<{ message: string }>("/api/subscription/cancel", {
      method: "POST",
    });
  }

  // ===== Phase 4: Pronunciation API =====

  /** 発音練習素材取得 */
  async getPronunciationExercises(
    targetPhoneme?: string,
    difficulty?: number
  ): Promise<PronunciationExercise[]> {
    const params = new URLSearchParams();
    if (targetPhoneme) params.set("target_phoneme", targetPhoneme);
    if (difficulty) params.set("difficulty", String(difficulty));
    const qs = params.toString();
    return this.request<PronunciationExercise[]>(
      `/api/speaking/pronunciation${qs ? `?${qs}` : ""}`
    );
  }

  /** 発音評価送信 */
  async submitPronunciation(
    exerciseId: string,
    audioBlob: Blob
  ): Promise<PronunciationResult> {
    const formData = new FormData();
    formData.append("exercise_id", exerciseId);
    formData.append("audio", audioBlob, "recording.webm");

    const token = this.getToken();
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const response = await fetch(
      `${this.baseUrl}/api/speaking/pronunciation/evaluate`,
      { method: "POST", headers, body: formData }
    );
    if (!response.ok) {
      const detail = await response.text();
      throw new ApiError(response.status, response.statusText, detail);
    }
    return response.json();
  }

  // ===== Phase 4: Listening Comprehension API =====

  /** リスニング理解度テスト取得 */
  async getComprehensionExercises(
    difficulty?: string
  ): Promise<ComprehensionExercise[]> {
    const params = difficulty ? `?difficulty=${difficulty}` : "";
    return this.request<ComprehensionExercise[]>(
      `/api/listening/comprehension${params}`
    );
  }

  /** リスニング理解度回答送信 */
  async submitComprehensionAnswers(
    exerciseId: string,
    answers: { question_id: string; answer: string }[]
  ): Promise<ComprehensionResult> {
    return this.request<ComprehensionResult>(
      "/api/listening/comprehension/check",
      {
        method: "POST",
        body: JSON.stringify({ exercise_id: exerciseId, answers }),
      }
    );
  }
}

// シングルトンインスタンスをエクスポート
export const api = new ApiClient(BASE_URL);

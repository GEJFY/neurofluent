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
}

// シングルトンインスタンスをエクスポート
export const api = new ApiClient(BASE_URL);

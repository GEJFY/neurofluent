/**
 * FluentEdge AI - APIクライアント
 * バックエンド (FastAPI) との通信を管理
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8500";

// ===== 共通型定義 =====

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
  grammar_errors: {
    original: string;
    corrected: string;
    explanation: string;
  }[];
  expression_upgrades: {
    original: string;
    upgraded: string;
    context: string;
  }[];
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

// ===== Flash Translation 型定義 =====

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

export interface FlashCheckResponse {
  is_correct: boolean;
  score: number;
  corrected: string;
  explanation: string;
  review_item_created: boolean;
}

// ===== Review (SRS) 型定義 =====

export interface ReviewItemResponse {
  id: string;
  item_type: string;
  content: Record<string, unknown>;
  next_review_at: string | null;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
}

export interface ReviewCompleteResponse {
  next_review_at: string;
  new_interval_days: number;
  new_ease_factor: number;
}

// ===== Dashboard 型定義 =====

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

// ===== Shadowing 型定義 =====

export interface ShadowingMaterial {
  text: string;
  suggested_speeds: number[];
  key_phrases: string[];
  vocabulary_notes: { word: string; meaning: string; example: string }[];
  difficulty: string;
}

export interface PronunciationWordScore {
  word: string;
  accuracy_score: number;
  error_type: string | null;
}

export interface ShadowingResult {
  overall_score: number;
  accuracy: number;
  fluency: number;
  prosody: number;
  completeness: number;
  speed_achieved: number;
  word_scores: PronunciationWordScore[];
  areas_to_improve: string[];
}

// ===== Pattern Practice 型定義 =====

export interface PatternExercise {
  pattern_id: string;
  pattern_template: string;
  example_sentence: string;
  japanese_hint: string;
  category: string;
  difficulty: string;
  fill_in_blank: boolean;
}

export interface PatternCheckResult {
  is_correct: boolean;
  score: number;
  corrected: string;
  explanation: string;
  usage_tip: string;
}

export interface PatternCategory {
  category: string;
  name: string;
  description: string;
  pattern_count: number;
}

export interface PatternProgress {
  category: string;
  total_patterns: number;
  understood: number;
  drilling: number;
  acquired: number;
  average_accuracy: number;
  total_practice_count: number;
}

// ===== Realtime 型定義 =====

export interface RealtimeSessionConfig {
  ws_url: string;
  session_token: string;
  model: string;
  voice: string;
  mode: string;
  instructions_summary: string;
}

export interface ConversationMode {
  id: string;
  name: string;
  description: string;
  available: boolean;
  phase: string;
}

export interface ConversationModeList {
  modes: ConversationMode[];
  current_phase: string;
}

// ===== Mogomogo 型定義 =====

export interface MogomogoExercise {
  exercise_id: string;
  pattern_type: string;
  audio_text: string;
  ipa_original: string;
  ipa_modified: string;
  explanation: string;
  practice_sentence: string;
  difficulty: string;
}

export interface DictationResult {
  accuracy: number;
  missed_words: string[];
  identified_patterns: string[];
  score: number;
  feedback: string;
}

export interface SoundPatternInfo {
  type: string;
  name_en: string;
  name_ja: string;
  description: string;
  examples: string[];
  ipa_examples: { original: string; modified: string; word: string }[];
}

export interface MogomogoProgressItem {
  pattern_type: string;
  pattern_name: string;
  accuracy: number;
  practice_count: number;
  mastery_level: string;
}

export interface MogomogoProgress {
  overall_accuracy: number;
  total_practice_count: number;
  patterns: MogomogoProgressItem[];
}

// ===== Comprehension 型定義 =====

export interface VocabularyItem {
  word: string;
  definition: string;
  example: string;
  level: string;
}

export interface ComprehensionMaterial {
  material_id: string;
  topic: string;
  text: string;
  difficulty: string;
  duration_seconds: number;
  vocabulary: VocabularyItem[];
  key_points: string[];
}

export interface ComprehensionQuestion {
  question_id: string;
  question_text: string;
  question_type: string;
  options: string[] | null;
  correct_answer: string;
}

export interface ComprehensionResult {
  is_correct: boolean;
  score: number;
  explanation: string;
  correct_answer: string;
}

export interface SummaryResult {
  score: number;
  feedback: string;
  key_points_covered: string[];
  key_points_missed: string[];
}

export interface ComprehensionHistoryItem {
  material_id: string;
  topic: string;
  difficulty: string;
  score: number;
  completed_at: string;
  questions_correct: number;
  questions_total: number;
}

export interface ComprehensionHistory {
  items: ComprehensionHistoryItem[];
  total_sessions: number;
  avg_score: number;
}

// ===== Pronunciation 型定義 =====

export interface PronunciationExercise {
  exercise_id: string;
  target_phoneme: string;
  exercise_type: string;
  word_a: string;
  word_b: string | null;
  sentence: string;
  ipa: string;
  audio_url: string | null;
  difficulty: string;
  tip: string;
}

export interface PhonemeResult {
  target_phoneme: string;
  accuracy: number;
  is_correct: boolean;
  feedback: string;
  common_error_pattern: string;
}

export interface ProsodyExercise {
  exercise_id: string;
  sentence: string;
  stress_pattern: string;
  intonation_type: string;
  audio_url: string | null;
  explanation: string;
  context: string;
}

export interface JapaneseSpeakerPhoneme {
  phoneme_pair: string;
  description_ja: string;
  description_en: string;
  examples: string[];
  practice_words: string[];
  common_mistake: string;
  tip: string;
}

export interface PronunciationProgressItem {
  phoneme: string;
  accuracy: number;
  practice_count: number;
  trend: string;
}

export interface PronunciationOverallProgress {
  overall_accuracy: number;
  total_evaluations: number;
  phoneme_progress: PronunciationProgressItem[];
  strongest_phonemes: string[];
  weakest_phonemes: string[];
}

// ===== Analytics 型定義 =====

export interface DailyBreakdown {
  date: string;
  practice_minutes: number;
  sessions_completed: number;
  reviews_completed: number;
  new_expressions_learned: number;
  grammar_accuracy: number | null;
  pronunciation_avg_score: number | null;
}

export interface WeeklyReport {
  period_start: string;
  period_end: string;
  total_minutes: number;
  total_sessions: number;
  total_reviews: number;
  new_expressions: number;
  avg_grammar_accuracy: number | null;
  avg_pronunciation: number | null;
  streak_days: number;
  daily_breakdown: DailyBreakdown[];
  improvement_vs_last_week: Record<string, number>;
}

export interface MonthlyReport {
  period_start: string;
  period_end: string;
  total_minutes: number;
  total_sessions: number;
  total_reviews: number;
  new_expressions: number;
  avg_grammar_accuracy: number | null;
  avg_pronunciation: number | null;
  streak_best: number;
  monthly_trend_chart_data: Record<string, unknown>[];
  skill_radar_data: Record<string, number>;
  top_achievements: {
    title: string;
    description: string;
    achieved_at: string | null;
    icon: string;
  }[];
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

export interface SkillBreakdown {
  speaking: {
    response_time: { avg_ms: number; trend: string; target_ms: number };
    filler_words: {
      avg_per_minute: number;
      common_fillers: string[];
      trend: string;
    };
    grammar: { accuracy: number; weak_patterns: string[]; trend: string };
    expression_level: {
      current_level: string;
      sophistication_score: number;
      recently_mastered: string[];
    };
  };
  listening: {
    comprehension_by_speed: {
      slow: number;
      normal: number;
      fast: number;
      native: number;
    };
    weak_patterns: {
      pattern_type: string;
      pattern_name: string;
      accuracy: number;
      practice_count: number;
    }[];
    dictation_accuracy: {
      overall_accuracy: number;
      by_pattern: Record<string, number>;
    };
  };
  vocabulary: {
    range: { total_words: number; active_words: number; passive_words: number };
    sophistication: {
      level: string;
      score: number;
      advanced_word_ratio: number;
    };
    new_per_week: {
      current_week: number;
      avg_last_4_weeks: number;
      target: number;
    };
  };
}

export interface Recommendation {
  category: string;
  title: string;
  description: string;
  priority: number;
  suggested_exercise_type: string;
}

export interface DailyMenu {
  time_of_day: string;
  recommended_activities: {
    activity_type: string;
    title: string;
    description: string;
    estimated_minutes: number;
    priority: number;
    params: Record<string, unknown>;
  }[];
  focus_message: string;
  estimated_minutes: number;
}

export interface FocusArea {
  skill: string;
  current_level: number;
  target_level: number;
  priority: number;
  suggested_exercises: string[];
}

// ===== Subscription 型定義 =====

export interface PlanFeature {
  name: string;
  description: string;
  included: boolean;
}

export interface PlanLimits {
  daily_sessions: number;
  monthly_api_calls: number;
  flash_exercises_per_day: number;
  conversation_minutes_per_day: number;
  pronunciation_evaluations_per_day: number;
  advanced_analytics: boolean;
  ai_curriculum: boolean;
  priority_support: boolean;
}

export interface PlanInfo {
  id: string;
  name: string;
  price_monthly: number;
  price_yearly: number;
  features: PlanFeature[];
  limits: PlanLimits;
  is_current: boolean;
}

export interface SubscriptionInfo {
  plan: string;
  status: string;
  current_period_start: string | null;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  stripe_customer_id: string | null;
}

export interface CheckoutSessionResponse {
  checkout_url: string;
  session_id: string;
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

  /** マルチパートFormDataリクエスト（音声アップロード用） */
  private async requestFormData<T>(
    endpoint: string,
    formData: FormData
  ): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: "POST",
      headers,
      body: formData,
    });

    if (!response.ok) {
      let detail: string | undefined;
      try {
        const errorBody = await response.json();
        detail = errorBody.detail || errorBody.message;
      } catch {
        detail = await response.text();
      }
      throw new ApiError(response.status, response.statusText, detail);
    }

    return response.json();
  }

  // ===== 認証 API =====

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

  async login(email: string, password: string): Promise<Token> {
    const response = await this.request<Token>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    this.setToken(response.access_token);
    return response;
  }

  async getMe(): Promise<User> {
    return this.request<User>("/api/auth/me");
  }

  // ===== Talk API =====

  async startTalk(
    mode: string = "casual_chat",
    scenarioDescription?: string,
    scenarioId?: string
  ): Promise<SessionResponse> {
    return this.request<SessionResponse>("/api/talk/start", {
      method: "POST",
      body: JSON.stringify({
        mode,
        scenario_description: scenarioDescription,
        scenario_id: scenarioId,
      }),
    });
  }

  async getScenarios(
    mode?: string
  ): Promise<
    {
      id: string;
      mode: string;
      title: string;
      description: string;
      difficulty: string;
      accent_context?: string;
    }[]
  > {
    const params = new URLSearchParams();
    if (mode) params.set("mode", mode);
    return this.request(`/api/talk/scenarios?${params.toString()}`);
  }

  async sendMessage(
    sessionId: string,
    content: string
  ): Promise<TalkMessageResponse> {
    return this.request<TalkMessageResponse>("/api/talk/message", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, content }),
    });
  }

  async getSessions(): Promise<SessionListResponse[]> {
    return this.request<SessionListResponse[]>("/api/talk/sessions");
  }

  async getSession(sessionId: string): Promise<SessionResponse> {
    return this.request<SessionResponse>(
      `/api/talk/sessions/${sessionId}`
    );
  }

  // ===== Realtime Voice API =====

  async createRealtimeSession(
    mode: string = "casual_chat",
    scenarioDescription?: string
  ): Promise<RealtimeSessionConfig> {
    return this.request<RealtimeSessionConfig>(
      "/api/talk/realtime/session",
      {
        method: "POST",
        body: JSON.stringify({
          mode,
          scenario_description: scenarioDescription,
        }),
      }
    );
  }

  async getConversationModes(): Promise<ConversationModeList> {
    return this.request<ConversationModeList>("/api/talk/realtime/modes");
  }

  // ===== Flash Translation API =====

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

  // ===== Pattern Practice API =====

  async getPatternCategories(): Promise<PatternCategory[]> {
    return this.request<PatternCategory[]>(
      "/api/speaking/pattern/categories"
    );
  }

  async getPatternExercises(
    count: number = 10,
    category?: string
  ): Promise<PatternExercise[]> {
    const params = new URLSearchParams({ count: String(count) });
    if (category) params.set("category", category);
    return this.request<PatternExercise[]>(
      `/api/speaking/pattern/exercises?${params.toString()}`
    );
  }

  async checkPatternAnswer(
    patternId: string,
    userAnswer: string,
    expected: string
  ): Promise<PatternCheckResult> {
    return this.request<PatternCheckResult>(
      "/api/speaking/pattern/check",
      {
        method: "POST",
        body: JSON.stringify({
          pattern_id: patternId,
          user_answer: userAnswer,
          expected,
        }),
      }
    );
  }

  async getPatternProgress(): Promise<PatternProgress[]> {
    return this.request<PatternProgress[]>(
      "/api/speaking/pattern/progress"
    );
  }

  // ===== Pronunciation API =====

  async getPhonemes(): Promise<JapaneseSpeakerPhoneme[]> {
    return this.request<JapaneseSpeakerPhoneme[]>(
      "/api/speaking/pronunciation/phonemes"
    );
  }

  async getPronunciationExercises(
    phonemes: string = "/r/-/l/",
    type?: string,
    count: number = 10
  ): Promise<PronunciationExercise[]> {
    const params = new URLSearchParams({
      phonemes,
      count: String(count),
    });
    if (type) params.set("type", type);
    return this.request<PronunciationExercise[]>(
      `/api/speaking/pronunciation/exercises?${params.toString()}`
    );
  }

  async evaluatePronunciation(
    audioBlob: Blob,
    targetPhoneme: string,
    referenceText: string,
    exerciseId?: string
  ): Promise<PhonemeResult> {
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.wav");
    formData.append("target_phoneme", targetPhoneme);
    formData.append("reference_text", referenceText);
    if (exerciseId) formData.append("exercise_id", exerciseId);
    return this.requestFormData<PhonemeResult>(
      "/api/speaking/pronunciation/evaluate",
      formData
    );
  }

  async getProsodyExercises(
    pattern: string = "stress",
    count: number = 5
  ): Promise<ProsodyExercise[]> {
    const params = new URLSearchParams({
      pattern,
      count: String(count),
    });
    return this.request<ProsodyExercise[]>(
      `/api/speaking/pronunciation/prosody/exercises?${params.toString()}`
    );
  }

  async getPronunciationProgress(): Promise<PronunciationOverallProgress> {
    return this.request<PronunciationOverallProgress>(
      "/api/speaking/pronunciation/progress"
    );
  }

  // ===== Shadowing API =====

  async getShadowingMaterial(
    topic?: string,
    difficulty: string = "intermediate",
    mode: string = "standard",
    accent?: string,
    environment?: string
  ): Promise<ShadowingMaterial> {
    const params = new URLSearchParams({ difficulty, mode });
    if (topic) params.set("topic", topic);
    if (accent) params.set("accent", accent);
    if (environment && environment !== "clean")
      params.set("environment", environment);
    return this.request<ShadowingMaterial>(
      `/api/listening/shadowing/material?${params.toString()}`
    );
  }

  async getAccents(): Promise<{
    accents: { id: string; label: string; label_ja: string }[];
    environments: { id: string; label: string; description: string }[];
  }> {
    return this.request("/api/listening/accents");
  }

  async evaluateShadowing(
    audioBlob: Blob,
    referenceText: string,
    speed: number = 1.0
  ): Promise<ShadowingResult> {
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.wav");
    formData.append("reference_text", referenceText);
    formData.append("speed", String(speed));
    return this.requestFormData<ShadowingResult>(
      "/api/listening/shadowing/evaluate",
      formData
    );
  }

  async requestTTS(
    text: string,
    voice: string = "en-US-JennyMultilingualNeural",
    speed: number = 1.0
  ): Promise<Blob> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const response = await fetch(`${this.baseUrl}/api/listening/tts`, {
      method: "POST",
      headers,
      body: JSON.stringify({ text, voice, speed }),
    });

    if (!response.ok) {
      throw new ApiError(response.status, response.statusText);
    }

    return response.blob();
  }

  // ===== Mogomogo API =====

  async getMogomogoPatterns(): Promise<SoundPatternInfo[]> {
    return this.request<SoundPatternInfo[]>(
      "/api/listening/mogomogo/patterns"
    );
  }

  async getMogomogoExercises(
    patternTypes: string = "linking,reduction",
    count: number = 10,
    difficulty?: string
  ): Promise<MogomogoExercise[]> {
    const params = new URLSearchParams({
      pattern_types: patternTypes,
      count: String(count),
    });
    if (difficulty) params.set("difficulty", difficulty);
    return this.request<MogomogoExercise[]>(
      `/api/listening/mogomogo/exercises?${params.toString()}`
    );
  }

  async checkDictation(
    exerciseId: string,
    userText: string,
    originalText: string
  ): Promise<DictationResult> {
    return this.request<DictationResult>(
      "/api/listening/mogomogo/dictation/check",
      {
        method: "POST",
        body: JSON.stringify({
          exercise_id: exerciseId,
          user_text: userText,
          original_text: originalText,
        }),
      }
    );
  }

  async getMogomogoProgress(): Promise<MogomogoProgress> {
    return this.request<MogomogoProgress>(
      "/api/listening/mogomogo/progress"
    );
  }

  // ===== Comprehension API =====

  async getComprehensionMaterial(
    topic?: string,
    difficulty: string = "intermediate",
    duration: number = 3,
    accent?: string,
    multiSpeaker?: boolean,
    environment?: string
  ): Promise<ComprehensionMaterial> {
    const params = new URLSearchParams({
      difficulty,
      duration: String(duration),
    });
    if (topic) params.set("topic", topic);
    if (accent) params.set("accent", accent);
    if (multiSpeaker) params.set("multi_speaker", "true");
    if (environment && environment !== "clean")
      params.set("environment", environment);
    return this.request<ComprehensionMaterial>(
      `/api/listening/comprehension/material?${params.toString()}`
    );
  }

  async getComprehensionQuestions(
    text: string,
    count: number = 5
  ): Promise<ComprehensionQuestion[]> {
    const params = new URLSearchParams({
      text,
      count: String(count),
    });
    return this.request<ComprehensionQuestion[]>(
      `/api/listening/comprehension/material/questions?${params.toString()}`
    );
  }

  async getComprehensionTopics(): Promise<
    { id: string; name: string; description: string }[]
  > {
    return this.request<
      { id: string; name: string; description: string }[]
    >("/api/listening/comprehension/topics");
  }

  async checkComprehensionAnswer(
    questionId: string,
    userAnswer: string,
    correctAnswer: string
  ): Promise<ComprehensionResult> {
    return this.request<ComprehensionResult>(
      "/api/listening/comprehension/answer",
      {
        method: "POST",
        body: JSON.stringify({
          question_id: questionId,
          user_answer: userAnswer,
          correct_answer: correctAnswer,
        }),
      }
    );
  }

  async checkSummary(
    materialId: string,
    userSummary: string
  ): Promise<SummaryResult> {
    return this.request<SummaryResult>(
      "/api/listening/comprehension/summary",
      {
        method: "POST",
        body: JSON.stringify({
          material_id: materialId,
          user_summary: userSummary,
        }),
      }
    );
  }

  async getComprehensionHistory(
    limit: number = 20
  ): Promise<ComprehensionHistory> {
    return this.request<ComprehensionHistory>(
      `/api/listening/comprehension/history?limit=${limit}`
    );
  }

  // ===== Review (SRS) API =====

  async getDueReviews(): Promise<ReviewItemResponse[]> {
    return this.request<ReviewItemResponse[]>("/api/review/due");
  }

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

  async getDashboard(): Promise<DashboardData> {
    return this.request<DashboardData>("/api/analytics/dashboard");
  }

  // ===== Advanced Analytics API =====

  async getWeeklyReport(): Promise<WeeklyReport> {
    return this.request<WeeklyReport>(
      "/api/analytics/advanced/weekly-report"
    );
  }

  async getMonthlyReport(): Promise<MonthlyReport> {
    return this.request<MonthlyReport>(
      "/api/analytics/advanced/monthly-report"
    );
  }

  async getSkillBreakdown(): Promise<SkillBreakdown> {
    return this.request<SkillBreakdown>("/api/analytics/advanced/skills");
  }

  async getRecommendations(): Promise<Recommendation[]> {
    return this.request<Recommendation[]>(
      "/api/analytics/advanced/recommendations"
    );
  }

  async getDailyMenu(): Promise<DailyMenu> {
    return this.request<DailyMenu>("/api/analytics/advanced/daily-menu");
  }

  async getFocusAreas(): Promise<FocusArea[]> {
    return this.request<FocusArea[]>(
      "/api/analytics/advanced/focus-areas"
    );
  }

  // ===== Subscription API =====

  async getSubscriptionPlans(): Promise<PlanInfo[]> {
    return this.request<PlanInfo[]>("/api/subscription/plans");
  }

  async getCurrentSubscription(): Promise<SubscriptionInfo> {
    return this.request<SubscriptionInfo>("/api/subscription/current");
  }

  async createCheckout(
    plan: string,
    billingCycle: string = "monthly"
  ): Promise<CheckoutSessionResponse> {
    const successUrl = typeof window !== "undefined"
      ? `${window.location.origin}/subscription?status=success`
      : "";
    const cancelUrl = typeof window !== "undefined"
      ? `${window.location.origin}/subscription?status=cancel`
      : "";
    return this.request<CheckoutSessionResponse>(
      "/api/subscription/checkout",
      {
        method: "POST",
        body: JSON.stringify({
          plan,
          success_url: successUrl,
          cancel_url: cancelUrl,
          billing_cycle: billingCycle,
        }),
      }
    );
  }

  async cancelSubscription(): Promise<{
    success: boolean;
    message: string;
  }> {
    return this.request<{ success: boolean; message: string }>(
      "/api/subscription/cancel",
      { method: "POST" }
    );
  }
}

// シングルトンインスタンスをエクスポート
export const api = new ApiClient(BASE_URL);

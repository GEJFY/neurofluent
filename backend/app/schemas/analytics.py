"""アナリティクス（Analytics）スキーマ - 学習分析・カリキュラム最適化"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


# --- 日次詳細 ---

class DailyBreakdown(BaseModel):
    """日次統計の詳細データ"""

    date: date
    practice_minutes: int = 0
    sessions_completed: int = 0
    reviews_completed: int = 0
    new_expressions_learned: int = 0
    grammar_accuracy: float | None = None
    pronunciation_avg_score: float | None = None


# --- 週次レポート ---

class WeeklyReport(BaseModel):
    """週次学習レポート - 7日間の集計・前週比較"""

    period_start: date
    period_end: date
    total_minutes: int = Field(description="合計学習時間（分）")
    total_sessions: int = Field(description="合計セッション数")
    total_reviews: int = Field(description="合計復習数")
    new_expressions: int = Field(description="新規習得表現数")
    avg_grammar_accuracy: float | None = Field(default=None, description="平均文法精度")
    avg_pronunciation: float | None = Field(default=None, description="平均発音スコア")
    streak_days: int = Field(default=0, description="連続学習日数")
    daily_breakdown: list[DailyBreakdown] = Field(default_factory=list, description="日別詳細データ")
    improvement_vs_last_week: dict = Field(
        default_factory=dict,
        description="前週比改善率 (例: {'minutes': 15.2, 'accuracy': 3.5})"
    )

    model_config = {"from_attributes": True}


# --- 月次レポート ---

class Achievement(BaseModel):
    """学習実績アチーブメント"""

    title: str
    description: str
    achieved_at: date | None = None
    icon: str = "star"


class MonthlyReport(BaseModel):
    """月次学習レポート - 月間集計・トレンド・レーダーチャート"""

    period_start: date
    period_end: date
    total_minutes: int = 0
    total_sessions: int = 0
    total_reviews: int = 0
    new_expressions: int = 0
    avg_grammar_accuracy: float | None = None
    avg_pronunciation: float | None = None
    streak_best: int = Field(default=0, description="月内最長ストリーク")
    monthly_trend_chart_data: list[dict] = Field(
        default_factory=list,
        description="月次トレンドチャートデータ [{'week': 1, 'minutes': 120, ...}]"
    )
    skill_radar_data: dict = Field(
        default_factory=dict,
        description="スキルレーダーチャートデータ {'speaking': 0.7, 'listening': 0.6, ...}"
    )
    top_achievements: list[Achievement] = Field(
        default_factory=list,
        description="月間トップアチーブメント"
    )
    strengths: list[str] = Field(default_factory=list, description="強み分野")
    weaknesses: list[str] = Field(default_factory=list, description="弱み分野")
    recommendations: list[str] = Field(default_factory=list, description="推奨アクション")

    model_config = {"from_attributes": True}


# --- スキルブレイクダウン ---

class SpeakingResponseTime(BaseModel):
    """スピーキング応答速度"""

    avg_ms: int = 0
    trend: str = "stable"
    target_ms: int = 3000


class SpeakingFillerWords(BaseModel):
    """フィラーワード使用状況"""

    avg_per_minute: float = 0.0
    common_fillers: list[str] = Field(default_factory=list)
    trend: str = "stable"


class SpeakingGrammar(BaseModel):
    """スピーキング文法精度"""

    accuracy: float = 0.0
    weak_patterns: list[str] = Field(default_factory=list)
    trend: str = "stable"


class SpeakingExpressionLevel(BaseModel):
    """表現レベル"""

    current_level: str = "B2"
    sophistication_score: float = 0.0
    recently_mastered: list[str] = Field(default_factory=list)


class SpeakingSkill(BaseModel):
    """スピーキングスキル詳細"""

    response_time: SpeakingResponseTime = Field(default_factory=SpeakingResponseTime)
    filler_words: SpeakingFillerWords = Field(default_factory=SpeakingFillerWords)
    grammar: SpeakingGrammar = Field(default_factory=SpeakingGrammar)
    expression_level: SpeakingExpressionLevel = Field(default_factory=SpeakingExpressionLevel)


class ListeningComprehensionBySpeed(BaseModel):
    """速度別リスニング理解度"""

    slow: float = Field(default=0.0, description="ゆっくり（0.75x）での理解度")
    normal: float = Field(default=0.0, description="通常速度での理解度")
    fast: float = Field(default=0.0, description="速い（1.25x）での理解度")
    native: float = Field(default=0.0, description="ネイティブ速度（1.5x）での理解度")


class ListeningWeakPatterns(BaseModel):
    """リスニング弱点パターン"""

    pattern_type: str
    pattern_name: str
    accuracy: float = 0.0
    practice_count: int = 0


class ListeningDictationAccuracy(BaseModel):
    """ディクテーション精度"""

    overall_accuracy: float = 0.0
    by_pattern: dict = Field(default_factory=dict, description="パターン別精度")


class ListeningSkill(BaseModel):
    """リスニングスキル詳細"""

    comprehension_by_speed: ListeningComprehensionBySpeed = Field(
        default_factory=ListeningComprehensionBySpeed
    )
    weak_patterns: list[ListeningWeakPatterns] = Field(default_factory=list)
    dictation_accuracy: ListeningDictationAccuracy = Field(
        default_factory=ListeningDictationAccuracy
    )


class VocabularyRange(BaseModel):
    """語彙範囲"""

    total_words: int = 0
    active_words: int = 0
    passive_words: int = 0


class VocabularySophistication(BaseModel):
    """語彙の洗練度"""

    level: str = "intermediate"
    score: float = 0.0
    advanced_word_ratio: float = 0.0


class VocabularyNewPerWeek(BaseModel):
    """週あたり新規語彙"""

    current_week: int = 0
    avg_last_4_weeks: float = 0.0
    target: int = 20


class VocabularySkill(BaseModel):
    """語彙スキル詳細"""

    range: VocabularyRange = Field(default_factory=VocabularyRange)
    sophistication: VocabularySophistication = Field(default_factory=VocabularySophistication)
    new_per_week: VocabularyNewPerWeek = Field(default_factory=VocabularyNewPerWeek)


class SkillBreakdown(BaseModel):
    """スキル分類別の詳細分析"""

    speaking: SpeakingSkill = Field(default_factory=SpeakingSkill)
    listening: ListeningSkill = Field(default_factory=ListeningSkill)
    vocabulary: VocabularySkill = Field(default_factory=VocabularySkill)

    model_config = {"from_attributes": True}


# --- 発音進捗 ---

class PhonemeTrend(BaseModel):
    """音素別トレンドポイント"""

    date: date
    score: float


class PronunciationProgress(BaseModel):
    """発音進捗データ"""

    overall_trend: list[PhonemeTrend] = Field(default_factory=list, description="全体トレンド")
    phoneme_scores: dict = Field(
        default_factory=dict,
        description="音素別スコア {'θ': 0.65, 'r': 0.72, ...}"
    )
    weak_phonemes: list[str] = Field(
        default_factory=list,
        description="弱点音素リスト"
    )

    model_config = {"from_attributes": True}


# --- 推奨事項 ---

class Recommendation(BaseModel):
    """AI生成の学習推奨事項"""

    category: str = Field(description="カテゴリ: speaking, listening, vocabulary, grammar")
    title: str = Field(description="推奨タイトル")
    description: str = Field(description="推奨詳細")
    priority: int = Field(default=1, ge=1, le=5, description="優先度（1=最高, 5=最低）")
    suggested_exercise_type: str = Field(description="推奨エクササイズ種別")


# --- カリキュラム ---

class ActivityItem(BaseModel):
    """推奨アクティビティ"""

    activity_type: str = Field(description="アクティビティ種別")
    title: str = Field(description="アクティビティタイトル")
    description: str = Field(description="説明")
    estimated_minutes: int = Field(description="推定所要時間（分）")
    priority: int = Field(default=1, ge=1, le=5)
    params: dict = Field(default_factory=dict, description="アクティビティ固有パラメータ")


class DailyMenu(BaseModel):
    """日次学習メニュー - 概日リズム最適化"""

    time_of_day: str = Field(description="時間帯: morning, afternoon, evening, night")
    recommended_activities: list[ActivityItem] = Field(
        default_factory=list,
        description="推奨アクティビティリスト"
    )
    focus_message: str = Field(description="本日のフォーカスメッセージ")
    estimated_minutes: int = Field(description="推定合計時間（分）")

    model_config = {"from_attributes": True}


class FocusArea(BaseModel):
    """フォーカスエリア - ベイジアン知識モデルに基づく"""

    skill: str = Field(description="スキル名")
    current_level: float = Field(description="現在のレベル（0.0-1.0）")
    target_level: float = Field(description="目標レベル（0.0-1.0）")
    priority: int = Field(default=1, ge=1, le=5, description="優先度")
    suggested_exercises: list[str] = Field(default_factory=list, description="推奨エクササイズ")

    model_config = {"from_attributes": True}

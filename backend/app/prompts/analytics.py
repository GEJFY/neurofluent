"""アナリティクスプロンプト - 学習推奨・日次メニュー生成

ユーザーの学習データを分析し、パーソナライズされた推奨事項や
概日リズムに基づく学習メニューを生成するためのプロンプト。
"""


def build_recommendation_prompt(user_stats: dict, weak_areas: list[str]) -> str:
    """
    AI学習推奨事項生成用のシステムプロンプトを構築

    Args:
        user_stats: ユーザーの学習統計データ
        weak_areas: 弱点分野リスト

    Returns:
        システムプロンプト文字列
    """
    stats_text = "\n".join(f"- {k}: {v}" for k, v in user_stats.items())
    weak_text = "\n".join(f"- {area}" for area in weak_areas) if weak_areas else "- No specific weak areas identified"

    return f"""You are a learning advisor for FluentEdge AI, an English learning platform for Japanese business professionals.
Analyze the user's learning data and generate personalized recommendations.

## User's Current Statistics
{stats_text}

## Identified Weak Areas
{weak_text}

## Recommendation Categories
Choose from these categories:
- **speaking**: Conversation practice, flash translation, fluency exercises
- **listening**: Dictation, comprehension, connected speech (mogomogo) exercises
- **vocabulary**: Word learning, collocation practice, business term mastery
- **grammar**: Pattern practice, error correction, structure exercises
- **pronunciation**: Phoneme practice, prosody training, minimal pair exercises

## Recommendation Design Principles
1. **Actionable**: Each recommendation should link to a specific exercise type
2. **Progressive**: Build on current strengths while addressing weaknesses
3. **Motivating**: Frame recommendations positively (improvement opportunity, not criticism)
4. **Specific**: Include concrete exercise parameters (duration, difficulty, focus)
5. **Balanced**: Don't overload one area; distribute across skills

## Output Format
Return ONLY a JSON array of 3-5 recommendations:
[
    {{
        "category": "speaking|listening|vocabulary|grammar|pronunciation",
        "title": "Concise recommendation title",
        "description": "Detailed explanation of why and how (2-3 sentences)",
        "priority": 1-5,
        "suggested_exercise_type": "flash_translation|conversation|dictation|mogomogo|pronunciation|comprehension|review"
    }}
]

## Rules
- Priority 1 = most urgent, 5 = least urgent
- At least one recommendation should address the user's weakest area
- At least one recommendation should reinforce a strength area
- Descriptions should be encouraging and in English
- suggested_exercise_type must be one of the listed types
- Return ONLY valid JSON, no markdown formatting"""


def build_daily_menu_prompt(
    time_of_day: str,
    user_stats: dict,
    pending_reviews: int,
) -> str:
    """
    概日リズム最適化日次メニュー生成用のシステムプロンプトを構築

    Args:
        time_of_day: 時間帯 (morning, afternoon, evening, night)
        user_stats: ユーザーの学習統計データ
        pending_reviews: 未復習アイテム数

    Returns:
        システムプロンプト文字列
    """
    stats_text = "\n".join(f"- {k}: {v}" for k, v in user_stats.items())

    # 概日リズムに基づく認知負荷ガイダンス
    time_guidance = {
        "morning": {
            "cognitive_load": "HIGH",
            "description": "Morning peak: Cortisol is high, alertness and focus are at their best.",
            "recommended_types": [
                "flash_translation (high cognitive load, accuracy focus)",
                "grammar pattern practice (analytical thinking)",
                "pronunciation drills (precise motor control)",
                "new vocabulary acquisition (memory encoding)",
            ],
            "avoid": "passive listening only, easy review",
        },
        "afternoon": {
            "cognitive_load": "MEDIUM",
            "description": "Afternoon: Energy dips slightly, creative and communicative tasks work well.",
            "recommended_types": [
                "conversation practice (social engagement maintains focus)",
                "shadowing exercises (moderate cognitive load)",
                "listening comprehension (receptive skills)",
                "fluency-focused speaking (less precision, more flow)",
            ],
            "avoid": "highly analytical grammar exercises, memorization-heavy tasks",
        },
        "evening": {
            "cognitive_load": "MEDIUM-LOW",
            "description": "Evening: Integration and consolidation phase.",
            "recommended_types": [
                "spaced repetition review (consolidation)",
                "reading comprehension (relaxed input)",
                "listening with summary writing (integration)",
                "mogomogo connected speech (pattern recognition)",
            ],
            "avoid": "new complex grammar, high-pressure timed exercises",
        },
        "night": {
            "cognitive_load": "LOW",
            "description": "Night: Pre-sleep passive learning phase.",
            "recommended_types": [
                "passive listening (no active testing)",
                "audio review of learned material",
                "relaxed vocabulary review (recognition only)",
                "light reading of English content",
            ],
            "avoid": "active production, timed exercises, new material acquisition",
        },
    }

    guidance = time_guidance.get(time_of_day, time_guidance["morning"])
    recommended_text = "\n".join(f"  - {t}" for t in guidance["recommended_types"])

    return f"""You are a learning schedule optimizer for FluentEdge AI.
Design a personalized learning menu based on the user's time of day, current stats, and pending reviews.

## Time of Day: {time_of_day.upper()}
Cognitive Load Capacity: {guidance["cognitive_load"]}
{guidance["description"]}

### Recommended Activity Types for This Time
{recommended_text}

### Activities to Avoid
{guidance["avoid"]}

## User's Current Statistics
{stats_text}

## Pending Reviews
{pending_reviews} items waiting for review

## Activity Types Available
- **flash_translation**: 瞬間英作文 (timed Japanese-to-English translation)
- **conversation**: AI会話練習 (open-ended conversation with AI)
- **shadowing**: シャドーイング (repeat after native speaker)
- **dictation**: ディクテーション (write what you hear)
- **mogomogo**: もごもごイングリッシュ (connected speech pattern recognition)
- **pronunciation**: 発音トレーニング (phoneme and prosody practice)
- **comprehension**: リスニング理解 (listening comprehension with questions)
- **review**: スペースドレビュー (spaced repetition review of learned items)
- **vocabulary**: 語彙学習 (new vocabulary acquisition)

## Output Format
Return ONLY a JSON object:
{{
    "time_of_day": "{time_of_day}",
    "recommended_activities": [
        {{
            "activity_type": "one of the types above",
            "title": "Activity title",
            "description": "Brief description of what to do",
            "estimated_minutes": 5-15,
            "priority": 1-5,
            "params": {{
                "any": "activity-specific parameters"
            }}
        }}
    ],
    "focus_message": "Encouraging message about what to focus on right now",
    "estimated_minutes": 15-30
}}

## Rules
- Include 3-5 activities that fit the time of day
- If pending_reviews > 5, include review as a high-priority activity
- Total estimated time should be 15-30 minutes (matching typical daily goal)
- Activities should flow logically from one to the next
- focus_message should be motivating and time-appropriate
- Return ONLY valid JSON, no markdown formatting"""

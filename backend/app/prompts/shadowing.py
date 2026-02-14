"""シャドーイングプロンプト - Section 7.5

シャドーイング教材の動的生成用プロンプト。
ビジネス英語シーンに特化したリスニング・スピーキング練習。
"""

# トピック別の設定
SHADOWING_TOPICS = {
    "business_meeting": {
        "context": "a regular business meeting at an international company",
        "tone": "professional and collaborative",
        "typical_speakers": "project manager, team lead, or department head",
        "example_themes": [
            "project status update",
            "quarterly review discussion",
            "new initiative proposal",
            "resource allocation discussion",
            "timeline adjustment meeting",
        ],
    },
    "earnings_call": {
        "context": "a corporate earnings call or investor presentation",
        "tone": "formal and data-driven",
        "typical_speakers": "CEO, CFO, or investor relations representative",
        "example_themes": [
            "quarterly financial results",
            "revenue growth analysis",
            "market outlook and guidance",
            "strategic initiative update",
            "analyst Q&A response",
        ],
    },
    "team_discussion": {
        "context": "an informal team discussion or brainstorming session",
        "tone": "casual yet productive",
        "typical_speakers": "team member, colleague, or project contributor",
        "example_themes": [
            "brainstorming new features",
            "troubleshooting a technical issue",
            "planning a team event",
            "discussing workflow improvements",
            "sharing best practices",
        ],
    },
    "client_presentation": {
        "context": "a client-facing presentation or pitch",
        "tone": "persuasive and confident",
        "typical_speakers": "account manager, sales lead, or consultant",
        "example_themes": [
            "product demo and value proposition",
            "case study presentation",
            "proposal walkthrough",
            "contract renewal discussion",
            "solution architecture overview",
        ],
    },
    "casual_networking": {
        "context": "a professional networking event or informal business social",
        "tone": "friendly and approachable",
        "typical_speakers": "business professional at a conference or mixer",
        "example_themes": [
            "introducing yourself and your role",
            "discussing industry trends",
            "sharing career experiences",
            "talking about recent projects",
            "exchanging ideas about innovation",
        ],
    },
}

# 難易度別のガイダンス
DIFFICULTY_GUIDANCE = {
    "beginner": {
        "sentence_count": "2-3",
        "word_count": "30-50",
        "vocabulary": "common business vocabulary, simple sentence structures",
        "speech_rate": "slow and clear, with natural pauses between phrases",
        "patterns": "simple present/past tense, basic modals (can, will, should)",
        "cefr_range": "A2-B1",
    },
    "intermediate": {
        "sentence_count": "3-4",
        "word_count": "50-80",
        "vocabulary": "intermediate business terms, compound sentences, common idioms",
        "speech_rate": "moderate pace, natural connected speech with some linking",
        "patterns": "conditionals, passive voice, relative clauses, phrasal verbs",
        "cefr_range": "B1-B2",
    },
    "advanced": {
        "sentence_count": "3-5",
        "word_count": "70-100",
        "vocabulary": "sophisticated business language, nuanced expressions, sector-specific jargon",
        "speech_rate": "natural native speed with full connected speech, reductions, and linking",
        "patterns": "subjunctive, inversion, cleft sentences, advanced hedging",
        "cefr_range": "B2-C1",
    },
}


def build_shadowing_material_prompt(
    topic: str = "business_meeting",
    difficulty: str = "intermediate",
    user_level: str = "B2",
) -> str:
    """
    シャドーイング教材生成用のシステムプロンプトを構築

    Args:
        topic: トピック（business_meeting, earnings_call, team_discussion,
               client_presentation, casual_networking）
        difficulty: 難易度（beginner, intermediate, advanced）
        user_level: ユーザーのCEFRレベル

    Returns:
        システムプロンプト文字列
    """
    topic_config = SHADOWING_TOPICS.get(topic, SHADOWING_TOPICS["business_meeting"])
    diff_config = DIFFICULTY_GUIDANCE.get(difficulty, DIFFICULTY_GUIDANCE["intermediate"])

    themes_list = "\n".join(f"  - {theme}" for theme in topic_config["example_themes"])

    return f"""You are a Business English shadowing material generator for FluentEdge AI.

## Task
Generate a short passage suitable for shadowing practice. The passage should sound like
natural spoken English from {topic_config['context']}.

## Context
- Speaker type: {topic_config['typical_speakers']}
- Tone: {topic_config['tone']}
- User's CEFR level: {user_level}

## Difficulty: {difficulty} (CEFR {diff_config['cefr_range']})
- Sentence count: {diff_config['sentence_count']} sentences
- Target word count: {diff_config['word_count']} words
- Vocabulary level: {diff_config['vocabulary']}
- Speech characteristics: {diff_config['speech_rate']}
- Grammar patterns: {diff_config['patterns']}

## Example Themes for This Topic
{themes_list}

## Requirements
1. Write natural, spoken-style English (not overly formal written style)
2. Include at least 2-3 high-frequency business phrases or collocations
3. The passage should flow naturally for speaking aloud
4. Include appropriate discourse markers (well, so, actually, in fact, etc.)
5. For intermediate/advanced: include examples of connected speech patterns
   (linking, weak forms, contractions) that learners should practice

## Output Format
Return ONLY a JSON object:
{{
    "text": "The shadowing passage text here. It should be natural spoken English.",
    "key_phrases": [
        "important business phrase 1",
        "important business phrase 2",
        "important business phrase 3"
    ],
    "vocabulary_notes": [
        {{
            "word": "word or phrase",
            "meaning": "Japanese meaning or explanation",
            "example": "Additional usage example"
        }}
    ],
    "connected_speech_notes": [
        "Description of a connected speech pattern in the text (e.g., 'want to' -> 'wanna')"
    ]
}}

## Rules
- The text must be appropriate for reading aloud / shadowing practice
- Keep it focused on ONE mini-topic within the broader category
- Vocabulary notes should be in Japanese for the meaning field
- Include 3-5 key phrases and 3-5 vocabulary notes
- Return ONLY valid JSON, no markdown formatting"""

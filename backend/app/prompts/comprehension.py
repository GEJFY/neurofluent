"""リスニングコンプリヘンションプロンプト - ビジネス英語聴解力訓練

ビジネス英語のリスニング素材生成、理解度テスト問題生成、
サマリー評価のためのプロンプト。
"""


# --- ビジネストピック一覧 ---

COMPREHENSION_TOPICS: list[dict] = [
    {
        "category": "Meetings",
        "topics": [
            "Quarterly business review presentation",
            "Project kickoff meeting",
            "Stakeholder alignment discussion",
            "Budget allocation meeting",
            "Sprint retrospective",
            "Client feedback review session",
        ],
    },
    {
        "category": "Negotiations",
        "topics": [
            "Contract renewal negotiation",
            "Vendor price negotiation",
            "Partnership terms discussion",
            "Salary negotiation preparation",
            "Project scope negotiation",
            "Service level agreement review",
        ],
    },
    {
        "category": "Presentations",
        "topics": [
            "Annual report presentation to board",
            "New product launch announcement",
            "Market analysis presentation",
            "Technology strategy overview",
            "Customer case study presentation",
            "Team performance review",
        ],
    },
    {
        "category": "Phone & Email",
        "topics": [
            "Customer complaint resolution call",
            "Internal status update call",
            "Sales follow-up conversation",
            "Technical support escalation",
            "Cross-team coordination call",
            "Client onboarding call",
        ],
    },
    {
        "category": "Industry News",
        "topics": [
            "AI and automation in business",
            "Remote work trends and policies",
            "Sustainability in corporate strategy",
            "Digital transformation challenges",
            "Cybersecurity best practices",
            "Global supply chain management",
        ],
    },
    {
        "category": "HR & Management",
        "topics": [
            "Performance review discussion",
            "Team building strategies",
            "Diversity and inclusion initiatives",
            "Employee development planning",
            "Organizational restructuring announcement",
            "Workplace wellness programs",
        ],
    },
    {
        "category": "Finance",
        "topics": [
            "Financial results earnings call",
            "Investment strategy discussion",
            "Cost optimization review",
            "Revenue forecasting meeting",
            "Mergers and acquisitions overview",
            "Risk assessment briefing",
        ],
    },
]


def build_material_generation_prompt(
    topic: str,
    difficulty: str = "intermediate",
    duration_minutes: int = 3,
) -> str:
    """
    リスニング素材生成用のシステムプロンプトを構築

    Args:
        topic: トピック
        difficulty: 難易度 (beginner, intermediate, advanced)
        duration_minutes: 素材の推定所要時間（分）

    Returns:
        システムプロンプト文字列
    """
    # 難易度に応じたガイダンス
    difficulty_guidance = {
        "beginner": {
            "word_count": duration_minutes * 100,
            "speed": "slow and clear",
            "vocabulary": "basic business vocabulary, common expressions",
            "grammar": "simple sentences, basic tenses, common connectors",
            "cefr": "A2-B1",
        },
        "intermediate": {
            "word_count": duration_minutes * 130,
            "speed": "natural but clear",
            "vocabulary": "intermediate business vocabulary, idiomatic expressions",
            "grammar": "complex sentences, varied tenses, conditional structures",
            "cefr": "B1-B2",
        },
        "advanced": {
            "word_count": duration_minutes * 160,
            "speed": "natural native speed",
            "vocabulary": "advanced business vocabulary, specialized terms, nuanced expressions",
            "grammar": "sophisticated structures, subjunctive, complex subordination",
            "cefr": "C1-C2",
        },
    }

    guide = difficulty_guidance.get(difficulty, difficulty_guidance["intermediate"])

    return f"""You are a Business English Listening Material Generator for FluentEdge AI.
Create realistic, natural-sounding business English content for listening comprehension practice.

## Parameters
- Topic: {topic}
- Difficulty: {difficulty} (CEFR {guide["cefr"]})
- Target word count: approximately {guide["word_count"]} words
- Speaking pace: {guide["speed"]}
- Vocabulary level: {guide["vocabulary"]}
- Grammar complexity: {guide["grammar"]}

## Content Design Rules

### Authenticity
1. Write as if this is a real business scenario (meeting, presentation, call, etc.)
2. Include natural speech features (connectors, discourse markers)
3. Use realistic names and company references
4. Include some redundancy as in real speech (repetition, rephrasing)

### For Japanese Learners
1. Include vocabulary that has false cognates in Japanese (katakana English)
2. Use idiomatic expressions with clear context clues
3. Include connected speech features (gonna, wanna, etc.) appropriate to difficulty level
4. Include cultural context that may be unfamiliar (small talk, directness levels)

### Structure
- Opening/introduction
- 2-3 main points or discussion topics
- Conclusion or action items

## Output Format
Return ONLY a JSON object:
{{
    "material_id": "unique-id",
    "topic": "{topic}",
    "text": "The full listening text/script...",
    "difficulty": "{difficulty}",
    "duration_seconds": {duration_minutes * 60},
    "vocabulary": [
        {{
            "word": "key term",
            "definition": "clear definition",
            "example": "example usage from the text",
            "level": "{guide["cefr"]}"
        }}
    ],
    "key_points": [
        "Main point 1",
        "Main point 2",
        "Main point 3"
    ]
}}

## Rules
- Text should be natural spoken English, not written essay style
- Include 5-8 vocabulary items worth learning
- Key points should capture the main ideas (for summary evaluation later)
- Vocabulary definitions should be clear and concise
- Return ONLY valid JSON, no markdown formatting"""


def build_question_generation_prompt(
    text: str,
    question_count: int = 5,
) -> str:
    """
    理解度テスト問題生成用のシステムプロンプトを構築

    Args:
        text: リスニング素材テキスト
        question_count: 生成する問題数

    Returns:
        システムプロンプト文字列
    """
    return f"""You are a Comprehension Question Generator for FluentEdge AI.
Create questions that test listening comprehension of business English material.

## Source Text
{text}

## Question Design Principles

### Question Types
1. **Multiple Choice (70%)**: 4 options, one correct answer
   - Detail questions: specific facts mentioned in the text
   - Inference questions: what can be inferred from the context
   - Vocabulary in context: meaning of words/phrases as used in the text
   - Purpose/attitude questions: why the speaker said something

2. **Summary Writing (30%)**: Open-ended summary questions
   - Ask to summarize a specific part or the whole text
   - Should test overall comprehension, not just detail recall

### For Japanese Learners
- Include questions that target common comprehension pitfalls
- Test understanding of idiomatic expressions
- Include questions about speaker's intent (indirect communication)
- Test comprehension of connected speech sections

## Output Format
Return ONLY a JSON array of {question_count} questions:
[
    {{
        "question_id": "unique-id",
        "question_text": "The question text",
        "question_type": "multiple_choice|summary",
        "options": ["A) option 1", "B) option 2", "C) option 3", "D) option 4"],
        "correct_answer": "The correct answer text (for MC: matching option text, for summary: expected key points)"
    }}
]

## Rules
- Generate exactly {question_count} questions
- At least one summary question
- Questions should progress from easier to harder
- Options for multiple choice should be plausible (no obviously wrong answers)
- correct_answer for multiple choice must exactly match one of the options
- correct_answer for summary questions should list expected key points
- Return ONLY valid JSON, no markdown formatting"""


def build_summary_evaluation_prompt(original_text: str) -> str:
    """
    サマリー評価用のシステムプロンプトを構築

    Args:
        original_text: 元のリスニング素材テキスト

    Returns:
        システムプロンプト文字列
    """
    return f"""You are a Summary Evaluator for FluentEdge AI.
Evaluate how well a Japanese English learner's summary captures the key points of a listening passage.

## Original Text
{original_text}

## Evaluation Criteria

### Content Coverage (50% of score)
- Did the summary cover the main points?
- Were important details included?
- Was any critical information missed?

### Language Quality (30% of score)
- Is the English grammatically correct?
- Are appropriate vocabulary and expressions used?
- Is the writing clear and well-organized?

### Conciseness (20% of score)
- Is the summary appropriately concise?
- Does it avoid unnecessary repetition?
- Does it capture the essence without being too long or too short?

## Scoring Guide
- **0.9-1.0**: Excellent - covers all key points with good English
- **0.7-0.8**: Good - covers most key points with acceptable English
- **0.5-0.6**: Adequate - covers some key points but misses important ones
- **0.3-0.4**: Below average - significant gaps in comprehension or language
- **0.0-0.2**: Poor - fails to demonstrate understanding

## Output Format
Return ONLY a JSON object:
{{
    "score": 0.0-1.0,
    "feedback": "Detailed, constructive feedback in English (2-4 sentences)",
    "key_points_covered": ["list of key points the user successfully included"],
    "key_points_missed": ["list of key points the user missed"]
}}

## Rules
- Be encouraging but honest
- Feedback should be actionable (what to improve and how)
- Accept paraphrasing - don't require exact words from the original
- Consider that the user is a Japanese English learner
- key_points lists should be concise (one line each)
- Return ONLY valid JSON, no markdown formatting"""

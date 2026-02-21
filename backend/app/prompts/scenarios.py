"""詳細シナリオDB - 100+ リアルビジネスシナリオ

単なる「meeting」「negotiation」ではなく、
具体的な状況・人物・目標・チャレンジを定義した
没入型ロールプレイシナリオ。
"""

import random

# --- シナリオデータベース ---

SCENARIOS: dict[str, list[dict]] = {
    "meeting": [
        {
            "id": "mtg-budget-overrun",
            "title": "Budget Overrun Explanation",
            "description": "Q3の予算が15%超過。CFOが厳しい質問をしてくる緊急ミーティング。"
            "あなたはプロジェクトマネージャーとして状況を説明し、対策案を提示する必要がある。",
            "ai_role": "the CFO who is concerned about the budget overrun and demands clear answers",
            "learner_goal": "Explain the reasons for budget overrun, present mitigation plans, and maintain credibility",
            "key_phrases": [
                "I'd like to walk you through the factors that contributed to...",
                "While I understand your concern, let me clarify that...",
                "We've already implemented the following corrective measures...",
                "Going forward, our plan is to...",
            ],
            "challenges": [
                "CFO interrupts and asks 'How did you not see this coming?'",
                "CFO demands specific numbers and timelines for recovery",
                "CFO asks if the team needs to be restructured",
            ],
            "accent_context": None,
            "difficulty": "B2-C1",
        },
        {
            "id": "mtg-cross-cultural",
            "title": "Cross-Cultural Team Alignment",
            "description": "東京・バンガロール・ロンドンの3拠点合同ミーティング。"
            "タイムゾーンの問題と文化の違いでプロジェクトが遅延している。",
            "ai_role": "the London team lead who is frustrated with communication delays",
            "learner_goal": "Mediate between teams, propose a new communication framework, and get buy-in",
            "key_phrases": [
                "I appreciate the challenges each team is facing...",
                "Could we explore a compromise where...?",
                "Let me propose a structured approach to bridge the gap...",
                "What if we set up a rotating meeting schedule that works for all time zones?",
            ],
            "challenges": [
                "London team complains they always have to attend late meetings",
                "Someone suggests switching to async communication only",
                "A team member raises cultural misunderstandings as the real issue",
            ],
            "accent_context": "uk",
            "difficulty": "B2-C1",
        },
        {
            "id": "mtg-product-pivot",
            "title": "Product Strategy Pivot",
            "description": "競合が同じ機能をリリースした。CEO がプロダクト方針の転換を検討。"
            "エンジニアチームとマーケティングチームの意見が対立している。",
            "ai_role": "the CEO who wants to hear different perspectives before making a decision",
            "learner_goal": "Present your team's recommendation with supporting data and handle counterarguments",
            "key_phrases": [
                "Based on our analysis, we recommend...",
                "The data suggests that our competitive advantage lies in...",
                "I understand the concern, but here's why we think...",
                "Rather than competing head-on, we could differentiate by...",
            ],
            "challenges": [
                "CEO plays devil's advocate and challenges your assumption",
                "Another department's VP disagrees with your approach",
                "CEO asks for a 30-second elevator pitch version",
            ],
            "accent_context": None,
            "difficulty": "C1",
        },
        {
            "id": "mtg-sprint-retro",
            "title": "Sprint Retrospective with Offshore Team",
            "description": "2週間スプリントの振り返り。インドのオフショアチームとの合同。"
            "品質問題とコミュニケーション齟齬について建設的に話し合う。",
            "ai_role": "the offshore team lead in Bangalore who is defensive about quality issues",
            "learner_goal": "Address quality concerns diplomatically while maintaining team morale",
            "key_phrases": [
                "I think we can all agree that the goal is...",
                "Rather than assigning blame, let's focus on...",
                "What if we tried a different approach to code reviews?",
                "I appreciate the effort your team has put in, and I think we can improve by...",
            ],
            "challenges": [
                "Offshore lead says the specs were unclear",
                "Someone suggests adding more QA resources (budget issue)",
                "Cultural tension arises around direct vs indirect feedback",
            ],
            "accent_context": "india",
            "difficulty": "B2",
        },
        {
            "id": "mtg-quarterly-review",
            "title": "Quarterly Business Review",
            "description": "四半期レビューで部門の成果を報告。数字は良いが人員不足が深刻。"
            "追加予算とヘッドカウントの承認を得る必要がある。",
            "ai_role": "the VP of Operations who controls budgets and is skeptical about headcount requests",
            "learner_goal": "Present strong results, then make a compelling case for additional resources",
            "key_phrases": [
                "Our Q3 results demonstrate that...",
                "To sustain this growth trajectory, we need to...",
                "The ROI on additional headcount would be...",
                "Without these resources, we risk...",
            ],
            "challenges": [
                "VP asks why you can't do more with existing team",
                "VP suggests using contractors instead of full-time hires",
                "VP asks you to prioritize: if you could only get 2 of 5 positions, which ones?",
            ],
            "accent_context": None,
            "difficulty": "B2-C1",
        },
    ],
    "negotiation": [
        {
            "id": "neg-vendor-price",
            "title": "Vendor Price Negotiation (India)",
            "description": "インドのITベンダーとの年間契約更新。相手は20%値上げを主張。"
            "あなたは5%以内に抑えたい。長期パートナーシップの維持も重要。",
            "ai_role": "the vendor account manager from Bangalore who firmly believes the price increase is justified",
            "learner_goal": "Negotiate the price increase down while preserving the relationship",
            "key_phrases": [
                "We value our partnership, and that's exactly why...",
                "I understand your cost pressures, however...",
                "Would you be open to a phased approach where...?",
                "What if we commit to a longer term in exchange for...?",
            ],
            "challenges": [
                "Vendor threatens to reduce service level at current price",
                "Vendor mentions a competitor offered them a better deal",
                "Vendor asks for immediate decision (time pressure)",
            ],
            "accent_context": "india",
            "difficulty": "B2-C1",
        },
        {
            "id": "neg-salary",
            "title": "Salary Negotiation",
            "description": "昇進後の給与交渉。HR担当者と1対1。"
            "市場相場より低いオファーを受けたが、会社には留まりたい。",
            "ai_role": "the HR compensation specialist who has a tight budget but wants to retain you",
            "learner_goal": "Negotiate a fair compensation package using market data and your value proposition",
            "key_phrases": [
                "Based on market research, the typical range for this role is...",
                "I'm excited about this opportunity, and I'd like to discuss...",
                "Beyond base salary, could we explore options like...?",
                "What I bring to this role that's unique is...",
            ],
            "challenges": [
                "HR says the budget is fixed for this fiscal year",
                "HR offers non-monetary benefits instead",
                "HR asks what's the minimum you'd accept (don't give a specific number!)",
            ],
            "accent_context": None,
            "difficulty": "B2",
        },
        {
            "id": "neg-contract-scope",
            "title": "Project Scope Negotiation",
            "description": "クライアントがスコープ外の機能追加を要求。追加料金なし。"
            "リレーション維持しつつ、適切な境界線を引く。",
            "ai_role": "the client project sponsor who sees the additional features as 'minor' and 'obvious'",
            "learner_goal": "Professionally decline scope creep while offering acceptable alternatives",
            "key_phrases": [
                "I want to make sure we deliver the best result within our agreed scope...",
                "We could certainly include that as a Phase 2 enhancement...",
                "Let me outline what's involved so we can make an informed decision...",
                "One option would be to reprioritize existing items to accommodate...",
            ],
            "challenges": [
                "Client says 'I thought this was included' with frustration",
                "Client mentions they have other vendors who would do it",
                "Client asks to speak to your manager",
            ],
            "accent_context": None,
            "difficulty": "C1",
        },
        {
            "id": "neg-partnership-sg",
            "title": "Partnership Terms (Singapore)",
            "description": "シンガポールのテック企業とのアジア太平洋地域パートナーシップ交渉。"
            "利益配分、独占権、サポート責任の3点が争点。",
            "ai_role": "the VP of Partnerships from a Singapore-based company who is experienced and shrewd",
            "learner_goal": "Reach a mutually beneficial agreement on the three key terms",
            "key_phrases": [
                "Let's take these one at a time, starting with...",
                "I see your point, and here's what we can offer in return...",
                "This could be a win-win if we structure it as...",
                "Shall we park that for now and come back to it after discussing...?",
            ],
            "challenges": [
                "Partner insists on exclusive rights for APAC",
                "Partner asks for a larger revenue share citing local market knowledge",
                "Partner introduces a new term not previously discussed",
            ],
            "accent_context": "singapore",
            "difficulty": "C1",
        },
    ],
    "presentation": [
        {
            "id": "prs-product-launch",
            "title": "New Product Launch to Distributors",
            "description": "日本の代理店向けに新製品をプレゼン。"
            "質疑で技術的な突っ込みと価格の質問が来る。",
            "ai_role": "a senior distributor representative who asks tough questions about pricing, timeline, and competitive advantage",
            "learner_goal": "Present the product compellingly and handle tough Q&A with confidence",
            "key_phrases": [
                "Let me walk you through the key differentiators...",
                "That's an excellent question. The short answer is...",
                "Compared to alternatives in the market, our solution...",
                "I'd be happy to provide detailed specifications after the session...",
            ],
            "challenges": [
                "Audience asks about a specific competitor's product",
                "Someone questions the price-to-value ratio",
                "Technical question you might not know the exact answer to",
            ],
            "accent_context": None,
            "difficulty": "B2",
        },
        {
            "id": "prs-quarterly-board",
            "title": "Board Presentation (Australian Context)",
            "description": "オーストラリア支社の取締役会でQ3業績報告。"
            "数字は良いが、今後のリスク要因について質問が予想される。",
            "ai_role": "a board member with an Australian accent who is detail-oriented and asks probing questions",
            "learner_goal": "Present results confidently and address risk factors proactively",
            "key_phrases": [
                "I'm pleased to report that our Q3 performance...",
                "Looking ahead, we've identified the following risk factors...",
                "Our mitigation strategy includes...",
                "To put this in perspective...",
            ],
            "challenges": [
                "Board member asks about worst-case scenarios",
                "Board member challenges your optimistic projections",
                "Board member wants to know the contingency plan",
            ],
            "accent_context": "australia",
            "difficulty": "B2-C1",
        },
    ],
    "small_talk": [
        {
            "id": "st-london-taxi",
            "title": "London Taxi Conversation",
            "description": "ロンドン出張。ヒースロー空港からホテルへのタクシーで運転手と会話。"
            "天気→最近のニュース→日本文化への興味と話が広がる。",
            "ai_role": "a chatty London taxi driver who loves talking about football, weather, and asking about Japan",
            "learner_goal": "Maintain natural small talk, show interest, and share about your culture",
            "key_phrases": [
                "Is it usually this [weather] at this time of year?",
                "That's interesting, I didn't know that about...",
                "Back in Japan, we actually have something similar...",
                "So what do you think about...?",
            ],
            "challenges": [
                "Driver uses British slang you might not understand",
                "Driver asks a sensitive cultural question",
                "Driver talks quickly about a topic you know nothing about",
            ],
            "accent_context": "uk",
            "difficulty": "B1-B2",
        },
        {
            "id": "st-conference-networking",
            "title": "Tech Conference Networking",
            "description": "サンフランシスコのテックカンファレンスのネットワーキングセッション。"
            "多国籍の参加者と自然に会話を始め、ビジネス機会を探る。",
            "ai_role": "a startup founder from India attending the same conference",
            "learner_goal": "Start conversations naturally, exchange business insights, and build connections",
            "key_phrases": [
                "Hi, I couldn't help but notice your badge says...",
                "What brings you to the conference?",
                "That sounds really interesting. How does it work?",
                "We should definitely stay in touch. Here's my card...",
            ],
            "challenges": [
                "The person asks deep technical questions about your product",
                "The person is very enthusiastic and talks fast with an Indian accent",
                "Someone else joins the conversation and you need to include them",
            ],
            "accent_context": "india",
            "difficulty": "B1-B2",
        },
        {
            "id": "st-business-dinner",
            "title": "Business Dinner in Singapore",
            "description": "シンガポールでのビジネスディナー。取引先の幹部と初めての食事。"
            "ビジネスの話と個人的な話のバランスが重要。",
            "ai_role": "a senior executive from a Singapore company who is evaluating you as a potential business partner",
            "learner_goal": "Build rapport through appropriate personal and business conversation",
            "key_phrases": [
                "Have you been to Japan before? What did you think of...?",
                "Speaking of which, I was curious about your company's approach to...",
                "That reminds me of a similar situation we had...",
                "On a different note, what do you enjoy doing outside of work?",
            ],
            "challenges": [
                "Executive subtly probes about your company's financial health",
                "Cultural faux pas opportunity (chopstick etiquette, etc.)",
                "Executive makes a joke with local references you don't understand",
            ],
            "accent_context": "singapore",
            "difficulty": "B2",
        },
    ],
    "interview": [
        {
            "id": "int-behavioral",
            "title": "Behavioral Interview at Global Firm",
            "description": "グローバルコンサル企業の面接。STAR method で回答が求められる。"
            "リーダーシップ・問題解決・異文化チームワークが問われる。",
            "ai_role": "a senior hiring manager who uses structured behavioral interview techniques",
            "learner_goal": "Answer using STAR method, demonstrate leadership and cross-cultural skills",
            "key_phrases": [
                "In that situation, my approach was to...",
                "The key challenge was..., and I addressed it by...",
                "As a result, we were able to achieve...",
                "Looking back, what I learned from that experience was...",
            ],
            "challenges": [
                "Interviewer asks for a specific example of failure",
                "Interviewer probes deeper: 'What would you do differently?'",
                "Interviewer asks a curveball question about your weaknesses",
            ],
            "accent_context": None,
            "difficulty": "B2-C1",
        },
    ],
    "phone_call": [
        {
            "id": "phone-conf-call",
            "title": "Multi-Party Conference Call",
            "description": "US・India・日本の3拠点が参加する電話会議。"
            "音声品質が悪い中で、議論を進行し結論を出す。",
            "ai_role": "the US team lead who is struggling with audio quality and has a packed schedule",
            "learner_goal": "Manage a conference call effectively despite audio issues",
            "key_phrases": [
                "Sorry, you're breaking up. Could you repeat that?",
                "Just to make sure I understood correctly, you're saying...",
                "Let me summarize what we've agreed so far...",
                "Before we wrap up, can everyone confirm the action items?",
            ],
            "challenges": [
                "Someone's audio cuts out mid-sentence",
                "Two people talk over each other",
                "US lead wants to end the call early but key decisions haven't been made",
            ],
            "accent_context": "us",
            "difficulty": "B2",
        },
        {
            "id": "phone-complaint",
            "title": "Client Complaint Call",
            "description": "クライアントがサービス障害について怒りの電話。"
            "まず感情を受け止め、事実確認し、具体的な解決策を提示する。",
            "ai_role": "an angry client whose service has been down for 6 hours causing business impact",
            "learner_goal": "De-escalate the situation, show empathy, and present a resolution plan",
            "key_phrases": [
                "I completely understand your frustration, and I'm sorry for...",
                "Let me look into this right now. Can you give me the details?",
                "Here's what I'm going to do to resolve this...",
                "To make sure this doesn't happen again, we will...",
            ],
            "challenges": [
                "Client demands to speak with management",
                "Client threatens to cancel the contract",
                "Client asks for compensation",
            ],
            "accent_context": None,
            "difficulty": "B2-C1",
        },
    ],
}


def get_scenario(mode: str, scenario_id: str | None = None) -> dict:
    """指定されたモード・IDのシナリオを取得（IDなしならランダム選択）"""
    mode_scenarios = SCENARIOS.get(mode, SCENARIOS.get("meeting", []))
    if not mode_scenarios:
        return _get_default_scenario(mode)

    if scenario_id:
        for s in mode_scenarios:
            if s["id"] == scenario_id:
                return s

    return random.choice(mode_scenarios)


def get_scenarios_for_mode(mode: str) -> list[dict]:
    """指定モードの全シナリオ一覧を取得"""
    return SCENARIOS.get(mode, [])


def get_all_scenario_ids() -> list[dict]:
    """全シナリオのID・タイトル一覧を取得"""
    result = []
    for mode, scenarios in SCENARIOS.items():
        for s in scenarios:
            result.append(
                {
                    "id": s["id"],
                    "mode": mode,
                    "title": s["title"],
                    "difficulty": s.get("difficulty", "B2"),
                    "accent_context": s.get("accent_context"),
                }
            )
    return result


def _get_default_scenario(mode: str) -> dict:
    """デフォルトのフォールバックシナリオ"""
    return {
        "id": f"default-{mode}",
        "title": f"General {mode.replace('_', ' ').title()} Practice",
        "description": f"A general {mode} scenario for practice.",
        "ai_role": "a professional counterpart in this business scenario",
        "learner_goal": "Practice effective business communication",
        "key_phrases": [
            "I'd like to suggest that...",
            "Could you elaborate on...?",
            "From my perspective...",
            "Let me summarize what we've discussed...",
        ],
        "challenges": [
            "Counterpart asks an unexpected question",
            "Counterpart disagrees with your point",
        ],
        "accent_context": None,
        "difficulty": "B2",
    }

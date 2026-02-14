"use client";

import { useState, useCallback } from "react";
import {
  Headphones,
  Play,
  Loader2,
  Trophy,
  RotateCcw,
  ChevronRight,
  Send,
  Volume2,
  Pause,
  FileText,
} from "lucide-react";
import AppShell from "@/components/layout/AppShell";
import ComprehensionQuiz from "@/components/listening/ComprehensionQuiz";

/**
 * リスニングコンプリヘンションページ
 * 音声を聞いて質問に答える総合リスニング訓練
 */

type PageState = "setup" | "listening" | "quiz" | "summary" | "result";
type Difficulty = "easy" | "intermediate" | "advanced";

interface Question {
  id: string;
  text: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

interface Answer {
  questionId: string;
  selectedIndex: number;
  isCorrect: boolean;
}

const TOPICS = [
  { id: "business_meeting", label: "Business Meeting", labelJa: "ビジネスミーティング" },
  { id: "presentation", label: "Presentation", labelJa: "プレゼンテーション" },
  { id: "interview", label: "Job Interview", labelJa: "面接" },
  { id: "news", label: "News Report", labelJa: "ニュース" },
  { id: "casual", label: "Casual Conversation", labelJa: "日常会話" },
  { id: "academic", label: "Academic Lecture", labelJa: "講義" },
];

const DURATIONS = [
  { id: "short", label: "Short", labelJa: "短い", minutes: "1-2 min" },
  { id: "medium", label: "Medium", labelJa: "中程度", minutes: "3-5 min" },
  { id: "long", label: "Long", labelJa: "長い", minutes: "5-10 min" },
];

// デモ用の問題データ
const DEMO_QUESTIONS: Question[] = [
  {
    id: "q1",
    text: "What was the main topic of the discussion?",
    options: [
      "Budget allocation for Q3",
      "New product launch timeline",
      "Team restructuring plan",
      "Customer feedback analysis",
    ],
    correctIndex: 1,
    explanation:
      "The speaker mentioned 'launching our new product line by September' as the primary agenda item.",
  },
  {
    id: "q2",
    text: "When is the deadline mentioned in the audio?",
    options: [
      "End of June",
      "Mid-July",
      "Early September",
      "Late October",
    ],
    correctIndex: 2,
    explanation:
      "The speaker clearly stated 'we need everything finalized by early September' as the key deadline.",
  },
  {
    id: "q3",
    text: "What concern did the second speaker raise?",
    options: [
      "Budget constraints",
      "Staffing shortages",
      "Supply chain delays",
      "Marketing timeline",
    ],
    correctIndex: 2,
    explanation:
      "The second speaker expressed worry about 'potential supply chain disruptions' affecting the timeline.",
  },
  {
    id: "q4",
    text: "What solution was proposed?",
    options: [
      "Delay the launch",
      "Hire more staff",
      "Work with multiple suppliers",
      "Reduce the product range",
    ],
    correctIndex: 2,
    explanation:
      "The team agreed to 'diversify our supplier base' as a mitigation strategy for supply chain risks.",
  },
  {
    id: "q5",
    text: "What is the next step agreed upon?",
    options: [
      "Schedule a follow-up meeting",
      "Send a progress report",
      "Contact new suppliers",
      "All of the above",
    ],
    correctIndex: 3,
    explanation:
      "The discussion concluded with agreement on all three actions: scheduling a follow-up, reporting progress, and supplier outreach.",
  },
];

const KEY_POINTS = [
  "New product launch planned for September",
  "Supply chain concerns identified",
  "Multiple supplier strategy agreed",
  "Follow-up meeting scheduled for next week",
  "Progress reports due bi-weekly",
];

const VOCABULARY_REVIEW = [
  { word: "finalize", definition: "最終的に決定する", context: "We need everything finalized by September." },
  { word: "disruption", definition: "混乱、中断", context: "Potential supply chain disruptions." },
  { word: "mitigation", definition: "軽減、緩和", context: "As a mitigation strategy." },
  { word: "diversify", definition: "多様化する", context: "Diversify our supplier base." },
];

export default function ComprehensionPage() {
  const [pageState, setPageState] = useState<PageState>("setup");
  const [selectedTopic, setSelectedTopic] = useState("business_meeting");
  const [difficulty, setDifficulty] = useState<Difficulty>("intermediate");
  const [selectedDuration, setSelectedDuration] = useState("medium");
  const [isPlaying, setIsPlaying] = useState(false);
  const [listeningProgress, setListeningProgress] = useState(0);
  const [notes, setNotes] = useState("");
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [summaryText, setSummaryText] = useState("");
  const [summaryScore, setSummaryScore] = useState<number | null>(null);

  // リスニング開始
  const handleStartListening = useCallback(() => {
    setPageState("listening");
    setListeningProgress(0);
    setNotes("");
  }, []);

  // 音声再生/一時停止
  const handleTogglePlay = useCallback(() => {
    if (isPlaying) {
      setIsPlaying(false);
    } else {
      setIsPlaying(true);
      // デモ：プログレスバーをアニメーション
      const interval = setInterval(() => {
        setListeningProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            setIsPlaying(false);
            return 100;
          }
          return prev + 2;
        });
      }, 200);
    }
  }, [isPlaying]);

  // クイズへ進む
  const handleProceedToQuiz = useCallback(() => {
    setPageState("quiz");
  }, []);

  // クイズ完了
  const handleQuizComplete = useCallback((quizAnswers: Answer[]) => {
    setAnswers(quizAnswers);
    setPageState("summary");
  }, []);

  // サマリー送信
  const handleSubmitSummary = useCallback(() => {
    // デモ：サマリースコア計算
    const words = summaryText.trim().split(/\s+/).length;
    const score = Math.min(100, Math.round(words * 3 + Math.random() * 20));
    setSummaryScore(score);
    setPageState("result");
  }, [summaryText]);

  // リスタート
  const handleRestart = useCallback(() => {
    setPageState("setup");
    setAnswers([]);
    setNotes("");
    setSummaryText("");
    setSummaryScore(null);
    setListeningProgress(0);
  }, []);

  // クイズスコア計算
  const correctAnswers = answers.filter((a) => a.isCorrect).length;
  const quizScore =
    answers.length > 0
      ? Math.round((correctAnswers / answers.length) * 100)
      : 0;

  return (
    <AppShell>
      <div className="min-h-[70vh] flex flex-col">
        {/* セットアップ画面 */}
        {pageState === "setup" && (
          <div className="space-y-6">
            <div className="space-y-1">
              <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
                Listening Comprehension
              </h1>
              <p className="text-sm text-[var(--color-text-muted)]">
                ビジネスシーンの音声を聞いて理解力を鍛えましょう
              </p>
            </div>

            {/* トピック選択 */}
            <div className="space-y-3">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Topic
              </p>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {TOPICS.map((topic) => (
                  <button
                    key={topic.id}
                    onClick={() => setSelectedTopic(topic.id)}
                    className={`p-3 rounded-xl text-left border transition-colors ${
                      selectedTopic === topic.id
                        ? "bg-primary/10 border-primary"
                        : "bg-[var(--color-bg-card)] border-[var(--color-border)] hover:border-primary/30"
                    }`}
                  >
                    <p
                      className={`text-sm font-medium ${
                        selectedTopic === topic.id
                          ? "text-primary"
                          : "text-[var(--color-text-primary)]"
                      }`}
                    >
                      {topic.label}
                    </p>
                    <p className="text-[11px] text-[var(--color-text-muted)]">
                      {topic.labelJa}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* 難易度選択 */}
            <div className="space-y-3">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Difficulty
              </p>
              <div className="flex gap-2">
                {(
                  [
                    { id: "easy", label: "Easy", color: "text-green-400" },
                    { id: "intermediate", label: "Intermediate", color: "text-warning" },
                    { id: "advanced", label: "Advanced", color: "text-red-400" },
                  ] as const
                ).map((d) => (
                  <button
                    key={d.id}
                    onClick={() => setDifficulty(d.id)}
                    className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors border ${
                      difficulty === d.id
                        ? "bg-primary/10 border-primary text-primary"
                        : "bg-[var(--color-bg-card)] border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-primary/30"
                    }`}
                  >
                    {d.label}
                  </button>
                ))}
              </div>
            </div>

            {/* 長さ選択 */}
            <div className="space-y-3">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Duration
              </p>
              <div className="flex gap-2">
                {DURATIONS.map((dur) => (
                  <button
                    key={dur.id}
                    onClick={() => setSelectedDuration(dur.id)}
                    className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors border ${
                      selectedDuration === dur.id
                        ? "bg-primary/10 border-primary text-primary"
                        : "bg-[var(--color-bg-card)] border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-primary/30"
                    }`}
                  >
                    <span>{dur.label}</span>
                    <span className="text-[10px] text-[var(--color-text-muted)] ml-1">
                      ({dur.minutes})
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* 開始ボタン */}
            <button
              onClick={handleStartListening}
              className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 transition-colors flex items-center justify-center gap-2"
            >
              <Headphones className="w-4 h-4" />
              Start Listening
            </button>
          </div>
        )}

        {/* リスニング画面 */}
        {pageState === "listening" && (
          <div className="flex-1 space-y-6">
            <div className="space-y-1">
              <h1 className="text-xl font-heading font-bold text-[var(--color-text-primary)]">
                Listen Carefully
              </h1>
              <p className="text-sm text-[var(--color-text-muted)]">
                音声を聞いてください。メモを取ることもできます。
              </p>
            </div>

            {/* オーディオプレーヤー */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-4">
              <div className="flex items-center gap-4">
                <button
                  onClick={handleTogglePlay}
                  className={`w-14 h-14 rounded-full flex items-center justify-center transition-all ${
                    isPlaying
                      ? "bg-primary/20 border-2 border-primary"
                      : "bg-primary/10 border-2 border-primary hover:bg-primary/20"
                  }`}
                >
                  {isPlaying ? (
                    <Pause className="w-6 h-6 text-primary" />
                  ) : (
                    <Play className="w-6 h-6 text-primary ml-0.5" />
                  )}
                </button>
                <div className="flex-1">
                  <div className="w-full h-2 bg-[var(--color-bg-input)] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all duration-200"
                      style={{ width: `${listeningProgress}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-[10px] text-[var(--color-text-muted)]">
                      {Math.round(listeningProgress * 0.03)}:
                      {String(Math.round((listeningProgress * 1.8) % 60)).padStart(2, "0")}
                    </span>
                    <span className="text-[10px] text-[var(--color-text-muted)]">
                      3:00
                    </span>
                  </div>
                </div>
                {isPlaying && (
                  <Volume2 className="w-5 h-5 text-primary animate-pulse" />
                )}
              </div>
            </div>

            {/* メモエリア */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-3">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-[var(--color-text-muted)]" />
                <p className="text-xs font-semibold text-[var(--color-text-secondary)]">
                  Notes (optional)
                </p>
              </div>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Take notes while listening..."
                rows={4}
                className="w-full px-4 py-3 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors resize-none"
              />
            </div>

            {/* クイズへ進む */}
            <button
              onClick={handleProceedToQuiz}
              disabled={listeningProgress < 50}
              className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
            >
              Proceed to Quiz
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* クイズ画面 */}
        {pageState === "quiz" && (
          <div className="flex-1">
            <div className="space-y-1 mb-6">
              <h1 className="text-xl font-heading font-bold text-[var(--color-text-primary)]">
                Comprehension Quiz
              </h1>
              <p className="text-sm text-[var(--color-text-muted)]">
                聞いた内容について答えてください
              </p>
            </div>
            <ComprehensionQuiz
              questions={DEMO_QUESTIONS}
              onComplete={handleQuizComplete}
            />
          </div>
        )}

        {/* サマリー画面 */}
        {pageState === "summary" && (
          <div className="flex-1 space-y-6">
            <div className="space-y-1">
              <h1 className="text-xl font-heading font-bold text-[var(--color-text-primary)]">
                Write a Summary
              </h1>
              <p className="text-sm text-[var(--color-text-muted)]">
                聞いた内容を英語で簡潔にまとめてください
              </p>
            </div>

            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-3">
              <textarea
                value={summaryText}
                onChange={(e) => setSummaryText(e.target.value)}
                placeholder="Write a brief summary of what you heard..."
                rows={6}
                className="w-full px-4 py-3 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors resize-none"
                autoFocus
              />
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-[var(--color-text-muted)]">
                  {summaryText.trim().split(/\s+/).filter(Boolean).length} words
                </span>
                <button
                  onClick={handleSubmitSummary}
                  disabled={summaryText.trim().length < 10}
                  className="px-6 py-2.5 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 disabled:opacity-50 transition-colors flex items-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  Submit
                </button>
              </div>
            </div>

            {/* スキップオプション */}
            <button
              onClick={() => {
                setSummaryScore(0);
                setPageState("result");
              }}
              className="w-full py-2 text-xs text-[var(--color-text-muted)] hover:text-primary transition-colors"
            >
              Skip summary and see results
            </button>
          </div>
        )}

        {/* 結果画面 */}
        {pageState === "result" && (
          <div className="space-y-6">
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-warning/10 flex items-center justify-center mx-auto mb-4">
                <Trophy className="w-8 h-8 text-warning" />
              </div>
              <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
                Comprehension Results
              </h1>
            </div>

            {/* クイズスコア */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6 space-y-4">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Quiz Score
              </p>
              <div className="text-center">
                <p className="text-4xl font-heading font-bold text-primary">
                  {correctAnswers}
                  <span className="text-lg text-[var(--color-text-muted)]">
                    /{answers.length}
                  </span>
                </p>
                <p className="text-sm text-[var(--color-text-muted)] mt-1">
                  {quizScore}% Accuracy
                </p>
              </div>
              <div className="w-full h-3 bg-[var(--color-bg-input)] rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    quizScore >= 80
                      ? "bg-green-400"
                      : quizScore >= 50
                        ? "bg-warning"
                        : "bg-red-400"
                  }`}
                  style={{ width: `${quizScore}%` }}
                />
              </div>
            </div>

            {/* サマリースコア */}
            {summaryScore !== null && summaryScore > 0 && (
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5">
                <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mb-2">
                  Summary Evaluation
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-[var(--color-text-primary)]">
                    Content Coverage
                  </span>
                  <span
                    className={`text-sm font-bold ${
                      summaryScore >= 70
                        ? "text-green-400"
                        : summaryScore >= 40
                          ? "text-warning"
                          : "text-red-400"
                    }`}
                  >
                    {summaryScore}%
                  </span>
                </div>
              </div>
            )}

            {/* Key Points */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-3">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Key Points
              </p>
              {KEY_POINTS.map((point, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 text-xs text-[var(--color-text-secondary)]"
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                  {point}
                </div>
              ))}
            </div>

            {/* Vocabulary Review */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-3">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Vocabulary Review
              </p>
              {VOCABULARY_REVIEW.map((item, i) => (
                <div
                  key={i}
                  className="p-3 rounded-xl bg-[var(--color-bg-primary)]/50 space-y-1"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-accent">
                      {item.word}
                    </span>
                    <span className="text-xs text-[var(--color-text-muted)]">
                      {item.definition}
                    </span>
                  </div>
                  <p className="text-[11px] text-[var(--color-text-secondary)] italic">
                    &ldquo;{item.context}&rdquo;
                  </p>
                </div>
              ))}
            </div>

            {/* アクション */}
            <button
              onClick={handleRestart}
              className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 transition-colors flex items-center justify-center gap-2"
            >
              <RotateCcw className="w-4 h-4" />
              Try Another
            </button>
          </div>
        )}
      </div>
    </AppShell>
  );
}

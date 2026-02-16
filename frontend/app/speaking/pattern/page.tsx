"use client";

import { useState, useCallback } from "react";
import {
  Loader2,
  Trophy,
  RotateCcw,
  Repeat2,
} from "lucide-react";
import AppShell from "@/components/layout/AppShell";
import PatternCard from "@/components/drill/PatternCard";
import { api } from "@/lib/api";
import { useToastStore } from "@/lib/stores/toast-store";
import { CardSkeleton } from "@/components/ui/Skeleton";

/**
 * パターンプラクティスページ
 * States: setup → playing → finished
 * APIに接続し、失敗時はフォールバックデモデータを使用
 */

type PageState = "setup" | "playing" | "finished";

/** パターン練習問題の型（ページ内部用） */
export interface PatternExercise {
  exercise_id: string;
  category: string;
  template: string;
  blank_prompt: string;
  japanese_hint: string;
  example_answer: string;
  difficulty: string;
}

/** パターン回答チェック結果の型 */
export interface PatternCheckResult {
  is_correct: boolean;
  score: number;
  corrected: string;
  explanation: string;
  usage_tip: string;
}

interface CategoryOption {
  id: string;
  label: string;
  labelJa: string;
  description: string;
}

const CATEGORIES: CategoryOption[] = [
  {
    id: "meeting",
    label: "Meeting",
    labelJa: "ミーティング",
    description: "会議で使う定型表現",
  },
  {
    id: "negotiation",
    label: "Negotiation",
    labelJa: "交渉",
    description: "交渉・折衝のフレーズ",
  },
  {
    id: "presentation",
    label: "Presentation",
    labelJa: "プレゼン",
    description: "プレゼンテーション表現",
  },
  {
    id: "email",
    label: "Email",
    labelJa: "メール",
    description: "ビジネスメール定型文",
  },
  {
    id: "discussion",
    label: "Discussion",
    labelJa: "議論",
    description: "意見交換・ディスカッション",
  },
  {
    id: "general",
    label: "General",
    labelJa: "一般",
    description: "汎用ビジネス表現",
  },
];

const COUNT_OPTIONS = [5, 10, 15, 20];

// フォールバック用のサンプルパターン練習問題（API失敗時に使用）
const FALLBACK_EXERCISES: Record<string, PatternExercise[]> = {
  meeting: [
    {
      exercise_id: "pat-m1",
      category: "meeting",
      template: "I'd like to _____ by discussing our quarterly results.",
      blank_prompt: "kick off / start",
      japanese_hint: "四半期の結果を議論するところから始めたいと思います。",
      example_answer: "kick off",
      difficulty: "intermediate",
    },
    {
      exercise_id: "pat-m2",
      category: "meeting",
      template: "Could you _____ on the progress of the project?",
      blank_prompt: "update us / give us an update",
      japanese_hint: "プロジェクトの進捗について教えていただけますか？",
      example_answer: "update us",
      difficulty: "beginner",
    },
    {
      exercise_id: "pat-m3",
      category: "meeting",
      template: "Let's _____ and come back to this topic later.",
      blank_prompt: "table this / put this on hold",
      japanese_hint: "これは一旦保留にして、後で戻りましょう。",
      example_answer: "table this",
      difficulty: "intermediate",
    },
    {
      exercise_id: "pat-m4",
      category: "meeting",
      template: "I think we're _____ here. Let me summarize the key takeaways.",
      blank_prompt: "running out of time / wrapping up",
      japanese_hint: "時間が残り少なくなってきました。主なポイントをまとめましょう。",
      example_answer: "running out of time",
      difficulty: "intermediate",
    },
    {
      exercise_id: "pat-m5",
      category: "meeting",
      template: "Does anyone have any _____ before we move on?",
      blank_prompt: "questions or concerns / objections",
      japanese_hint: "次に進む前に質問や懸念事項はありますか？",
      example_answer: "questions or concerns",
      difficulty: "beginner",
    },
  ],
  negotiation: [
    {
      exercise_id: "pat-n1",
      category: "negotiation",
      template: "We'd be willing to _____ if you could meet us halfway on the pricing.",
      blank_prompt: "make a concession / compromise",
      japanese_hint: "価格面で歩み寄っていただけるなら、譲歩する用意があります。",
      example_answer: "make a concession",
      difficulty: "advanced",
    },
    {
      exercise_id: "pat-n2",
      category: "negotiation",
      template: "That's a fair point, but _____ consider the long-term benefits.",
      blank_prompt: "let's also / we should also",
      japanese_hint: "おっしゃる通りですが、長期的なメリットも考慮しましょう。",
      example_answer: "let's also",
      difficulty: "intermediate",
    },
    {
      exercise_id: "pat-n3",
      category: "negotiation",
      template: "I'm afraid that's _____ our budget. Is there any flexibility on your end?",
      blank_prompt: "beyond / outside of",
      japanese_hint: "申し訳ないですが予算を超えています。そちらで柔軟に対応いただけますか？",
      example_answer: "beyond",
      difficulty: "intermediate",
    },
    {
      exercise_id: "pat-n4",
      category: "negotiation",
      template: "We can _____ a deal if we adjust the delivery timeline.",
      blank_prompt: "close / finalize",
      japanese_hint: "納期を調整すれば、取引をまとめることができます。",
      example_answer: "close",
      difficulty: "intermediate",
    },
    {
      exercise_id: "pat-n5",
      category: "negotiation",
      template: "Let me _____ with my team and get back to you by Friday.",
      blank_prompt: "check / consult",
      japanese_hint: "チームと確認して金曜日までにご連絡します。",
      example_answer: "check",
      difficulty: "beginner",
    },
  ],
  presentation: [
    {
      exercise_id: "pat-p1",
      category: "presentation",
      template: "Today, I'd like to _____ three key areas of our business strategy.",
      blank_prompt: "walk you through / cover",
      japanese_hint: "本日は、事業戦略の3つの重要な領域についてご説明します。",
      example_answer: "walk you through",
      difficulty: "intermediate",
    },
    {
      exercise_id: "pat-p2",
      category: "presentation",
      template: "As you can see from _____, there's been a significant upward trend.",
      blank_prompt: "this chart / the data",
      japanese_hint: "このチャートからお分かりのように、大幅な上昇傾向があります。",
      example_answer: "this chart",
      difficulty: "beginner",
    },
    {
      exercise_id: "pat-p3",
      category: "presentation",
      template: "This _____ us to the next point, which is our expansion plans.",
      blank_prompt: "brings / leads",
      japanese_hint: "これが次のポイント、つまり拡大計画に繋がります。",
      example_answer: "brings",
      difficulty: "intermediate",
    },
    {
      exercise_id: "pat-p4",
      category: "presentation",
      template: "To _____, our three priorities for next quarter are growth, efficiency, and innovation.",
      blank_prompt: "sum up / summarize",
      japanese_hint: "まとめると、来四半期の3つの優先事項は成長、効率、イノベーションです。",
      example_answer: "sum up",
      difficulty: "beginner",
    },
    {
      exercise_id: "pat-p5",
      category: "presentation",
      template: "I'd be happy to _____ any questions you might have.",
      blank_prompt: "take / address",
      japanese_hint: "ご質問があればお受けします。",
      example_answer: "take",
      difficulty: "beginner",
    },
  ],
  email: [
    {
      exercise_id: "pat-e1",
      category: "email",
      template: "I'm writing to _____ about the upcoming project deadline.",
      blank_prompt: "follow up / inquire",
      japanese_hint: "プロジェクトの締め切りについてフォローアップのためメールしています。",
      example_answer: "follow up",
      difficulty: "beginner",
    },
    {
      exercise_id: "pat-e2",
      category: "email",
      template: "Please find _____ the revised proposal for your review.",
      blank_prompt: "attached / enclosed",
      japanese_hint: "ご確認用に修正した提案書を添付いたします。",
      example_answer: "attached",
      difficulty: "beginner",
    },
    {
      exercise_id: "pat-e3",
      category: "email",
      template: "I would _____ it if you could respond by end of business today.",
      blank_prompt: "appreciate / value",
      japanese_hint: "本日中にご返信いただけると幸いです。",
      example_answer: "appreciate",
      difficulty: "intermediate",
    },
    {
      exercise_id: "pat-e4",
      category: "email",
      template: "Please don't _____ to reach out if you have any further questions.",
      blank_prompt: "hesitate / fail",
      japanese_hint: "さらにご質問がありましたら、遠慮なくご連絡ください。",
      example_answer: "hesitate",
      difficulty: "intermediate",
    },
    {
      exercise_id: "pat-e5",
      category: "email",
      template: "I look forward to _____ from you at your earliest convenience.",
      blank_prompt: "hearing / getting a response",
      japanese_hint: "お手すきの際にご返信をお待ちしています。",
      example_answer: "hearing",
      difficulty: "beginner",
    },
  ],
  discussion: [
    {
      exercise_id: "pat-d1",
      category: "discussion",
      template: "I see your point, but I'd like to _____ a different perspective.",
      blank_prompt: "offer / present",
      japanese_hint: "おっしゃることは分かりますが、別の視点を提示させてください。",
      example_answer: "offer",
      difficulty: "intermediate",
    },
    {
      exercise_id: "pat-d2",
      category: "discussion",
      template: "Building on what you just said, I think we should _____ our approach.",
      blank_prompt: "reconsider / rethink",
      japanese_hint: "今のご発言を踏まえて、アプローチを再考すべきだと思います。",
      example_answer: "reconsider",
      difficulty: "intermediate",
    },
    {
      exercise_id: "pat-d3",
      category: "discussion",
      template: "That's an interesting _____, but have we considered the risks?",
      blank_prompt: "idea / proposal",
      japanese_hint: "興味深いアイデアですが、リスクは検討しましたか？",
      example_answer: "idea",
      difficulty: "beginner",
    },
    {
      exercise_id: "pat-d4",
      category: "discussion",
      template: "I'm _____ in favor of this proposal, given the data we've seen.",
      blank_prompt: "strongly / fully",
      japanese_hint: "見たデータを踏まえると、この提案に強く賛成します。",
      example_answer: "strongly",
      difficulty: "beginner",
    },
    {
      exercise_id: "pat-d5",
      category: "discussion",
      template: "Let's _____ the pros and cons before making a final decision.",
      blank_prompt: "weigh / evaluate",
      japanese_hint: "最終決定の前にメリットとデメリットを比較しましょう。",
      example_answer: "weigh",
      difficulty: "intermediate",
    },
  ],
  general: [
    {
      exercise_id: "pat-g1",
      category: "general",
      template: "I'll _____ sure to keep you posted on any developments.",
      blank_prompt: "make / be",
      japanese_hint: "何か進展があれば必ずご報告します。",
      example_answer: "make",
      difficulty: "beginner",
    },
    {
      exercise_id: "pat-g2",
      category: "general",
      template: "Could we _____ a meeting for next Tuesday to discuss this further?",
      blank_prompt: "schedule / set up",
      japanese_hint: "来週の火曜日にこの件について更に議論する会議を設定できますか？",
      example_answer: "schedule",
      difficulty: "beginner",
    },
    {
      exercise_id: "pat-g3",
      category: "general",
      template: "I'd like to _____ your attention to an important update.",
      blank_prompt: "draw / bring",
      japanese_hint: "重要な更新についてご注意をお願いしたいと思います。",
      example_answer: "draw",
      difficulty: "intermediate",
    },
    {
      exercise_id: "pat-g4",
      category: "general",
      template: "We need to _____ this issue as soon as possible.",
      blank_prompt: "address / resolve",
      japanese_hint: "この問題にできるだけ早く対処する必要があります。",
      example_answer: "address",
      difficulty: "intermediate",
    },
    {
      exercise_id: "pat-g5",
      category: "general",
      template: "I'm _____ to report that we've met all our targets this quarter.",
      blank_prompt: "pleased / happy",
      japanese_hint: "今四半期の目標を全て達成したことをご報告できて嬉しく思います。",
      example_answer: "pleased",
      difficulty: "beginner",
    },
  ],
};

/**
 * APIレスポンスをページ内部の型にマッピング
 * api.getPatternExercises() → PatternExercise (ローカル)
 */
function mapApiExercise(
  apiEx: {
    pattern_id: string;
    pattern_template: string;
    example_sentence: string;
    japanese_hint: string;
    category: string;
    difficulty: string;
    fill_in_blank: boolean;
  }
): PatternExercise {
  return {
    exercise_id: apiEx.pattern_id,
    category: apiEx.category,
    template: apiEx.pattern_template,
    // fill_in_blank パターンでは blank_prompt はテンプレートから推測
    blank_prompt: "",
    japanese_hint: apiEx.japanese_hint,
    example_answer: apiEx.example_sentence,
    difficulty: apiEx.difficulty,
  };
}

export default function PatternPracticePage() {
  const [pageState, setPageState] = useState<PageState>("setup");
  const [selectedCategory, setSelectedCategory] = useState("meeting");
  const [selectedCount, setSelectedCount] = useState(5);
  const [exercises, setExercises] = useState<PatternExercise[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [results, setResults] = useState<PatternCheckResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addToast = useToastStore((s) => s.addToast);

  // 問題を取得して開始（API優先、フォールバックあり）
  const handleStart = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // APIから問題取得を試行
      const apiExercises = await api.getPatternExercises(selectedCount, selectedCategory);
      const mapped = apiExercises.map(mapApiExercise);

      if (mapped.length === 0) {
        throw new Error("APIから問題が返りませんでした");
      }

      setExercises(mapped);
      setCurrentIndex(0);
      setResults([]);
      setPageState("playing");
    } catch (err) {
      console.warn("Pattern exercises API failed, falling back to demo data:", err);
      // フォールバック：ローカルのデモデータを使用
      try {
        const categoryExercises = FALLBACK_EXERCISES[selectedCategory] || FALLBACK_EXERCISES.general;
        const selected = categoryExercises.slice(0, selectedCount);
        if (selected.length === 0) {
          setError("問題が見つかりませんでした。");
          return;
        }
        addToast("info", "オフラインモード：デモデータで練習を開始します");
        setExercises(selected);
        setCurrentIndex(0);
        setResults([]);
        setPageState("playing");
      } catch (fallbackErr) {
        console.error("Fallback also failed:", fallbackErr);
        setError("問題の読み込みに失敗しました");
      }
    } finally {
      setIsLoading(false);
    }
  }, [selectedCategory, selectedCount, addToast]);

  // 回答送信（API優先、フォールバックあり）
  const handleSubmit = useCallback(
    async (answer: string): Promise<PatternCheckResult> => {
      const exercise = exercises[currentIndex];

      try {
        // APIで回答チェックを試行
        const apiResult = await api.checkPatternAnswer(
          exercise.exercise_id,
          answer,
          exercise.example_answer
        );
        setResults((prev) => [...prev, apiResult]);
        return apiResult;
      } catch (err) {
        console.warn("Pattern answer check API failed, using local check:", err);
        // フォールバック：ローカルで回答チェック
        const isCorrect =
          answer.toLowerCase().trim() === exercise.example_answer.toLowerCase().trim() ||
          exercise.blank_prompt
            .toLowerCase()
            .split(" / ")
            .some((alt) => answer.toLowerCase().trim() === alt.trim());

        const result: PatternCheckResult = {
          is_correct: isCorrect,
          score: isCorrect ? 100 : 40 + Math.random() * 30,
          corrected: exercise.example_answer,
          explanation: isCorrect
            ? `Correct! "${exercise.example_answer}" is the natural phrasing for this context.`
            : `The expected answer is "${exercise.example_answer}". Alternatives: ${exercise.blank_prompt}.`,
          usage_tip: `This pattern is commonly used in ${exercise.category} situations. Practice using it in your daily conversations.`,
        };
        setResults((prev) => [...prev, result]);
        return result;
      }
    },
    [exercises, currentIndex]
  );

  // 次の問題へ
  const handleNext = useCallback(() => {
    if (currentIndex + 1 >= exercises.length) {
      setPageState("finished");
    } else {
      setCurrentIndex((prev) => prev + 1);
    }
  }, [currentIndex, exercises.length]);

  // リスタート
  const handleRestart = useCallback(() => {
    setPageState("setup");
    setExercises([]);
    setCurrentIndex(0);
    setResults([]);
  }, []);

  // 正解数・スコア計算
  const correctCount = results.filter((r) => r.is_correct).length;
  const totalScore = results.reduce((sum, r) => sum + r.score, 0);
  const avgScore = results.length > 0 ? totalScore / results.length : 0;

  return (
    <AppShell>
      <div className="min-h-[70vh] flex flex-col">
        {/* ===== セットアップ画面 ===== */}
        {pageState === "setup" && (
          <div className="flex-1 flex items-center justify-center">
            <div className="w-full max-w-md space-y-6">
              {/* ヘッダー */}
              <div className="text-center space-y-1">
                <div className="w-14 h-14 rounded-2xl bg-accent/10 flex items-center justify-center mx-auto mb-3">
                  <Repeat2 className="w-7 h-7 text-accent" />
                </div>
                <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
                  Pattern Practice
                </h1>
                <p className="text-sm text-[var(--color-text-muted)]">
                  ビジネスでよく使うフレーズパターンを身につけましょう
                </p>
              </div>

              {/* カテゴリー選択 */}
              <div className="space-y-2">
                <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                  Category
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {CATEGORIES.map((cat) => (
                    <button
                      key={cat.id}
                      onClick={() => setSelectedCategory(cat.id)}
                      className={`p-3 rounded-xl border text-left transition-colors ${
                        selectedCategory === cat.id
                          ? "border-accent bg-accent/5"
                          : "border-[var(--color-border)] hover:border-accent/30"
                      }`}
                    >
                      <p className="text-sm font-medium text-[var(--color-text-primary)]">
                        {cat.label}
                      </p>
                      <p className="text-[11px] text-[var(--color-text-muted)]">
                        {cat.labelJa}
                      </p>
                    </button>
                  ))}
                </div>
              </div>

              {/* 問題数選択 */}
              <div className="space-y-2">
                <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                  Number of Questions
                </p>
                <div className="flex gap-2">
                  {COUNT_OPTIONS.map((count) => (
                    <button
                      key={count}
                      onClick={() => setSelectedCount(count)}
                      className={`flex-1 py-2.5 rounded-xl text-sm font-semibold text-center transition-colors border ${
                        selectedCount === count
                          ? "border-accent bg-accent/10 text-accent"
                          : "border-[var(--color-border)] text-[var(--color-text-muted)] hover:border-accent/30"
                      }`}
                    >
                      {count}
                    </button>
                  ))}
                </div>
              </div>

              {/* エラー表示 */}
              {error && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-400">
                  {error}
                </div>
              )}

              {/* 開始ボタン */}
              <button
                onClick={handleStart}
                disabled={isLoading}
                className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
              >
                {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                Start Practice
              </button>
            </div>
          </div>
        )}

        {/* ===== プレイ中 ===== */}
        {pageState === "playing" && exercises[currentIndex] && (
          <div className="flex-1 flex flex-col items-center justify-center py-4">
            {/* 進捗トラッカー */}
            <div className="flex items-center gap-4 mb-6 text-sm">
              <span className="text-green-400 font-semibold">
                {correctCount} correct
              </span>
              <span className="text-[var(--color-text-muted)]">
                / {results.length} answered
              </span>
              {results.length > 0 && (
                <span className="text-accent text-xs">
                  Avg: {Math.round(avgScore)}%
                </span>
              )}
            </div>

            <PatternCard
              exercise={exercises[currentIndex]}
              onSubmit={handleSubmit}
              onNext={handleNext}
              questionNumber={currentIndex + 1}
              totalQuestions={exercises.length}
            />
          </div>
        )}

        {/* ===== ローディング中（playing遷移時） ===== */}
        {pageState === "playing" && !exercises[currentIndex] && (
          <div className="flex-1 flex items-center justify-center py-4">
            <div className="w-full max-w-lg space-y-4">
              <CardSkeleton />
              <CardSkeleton />
            </div>
          </div>
        )}

        {/* ===== リザルト画面 ===== */}
        {pageState === "finished" && (
          <div className="flex-1 flex items-center justify-center">
            <div className="w-full max-w-md space-y-6 text-center">
              <div className="w-16 h-16 rounded-2xl bg-warning/10 flex items-center justify-center mx-auto">
                <Trophy className="w-8 h-8 text-warning" />
              </div>
              <div>
                <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
                  Practice Complete!
                </h1>
                <p className="text-sm text-[var(--color-text-muted)] mt-1">
                  {CATEGORIES.find((c) => c.id === selectedCategory)?.label} -{" "}
                  {exercises.length} patterns
                </p>
              </div>

              {/* スコアカード */}
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6 space-y-4">
                <div className="text-center">
                  <p className="text-5xl font-heading font-bold text-primary">
                    {correctCount}
                    <span className="text-lg text-[var(--color-text-muted)]">
                      /{exercises.length}
                    </span>
                  </p>
                  <p className="text-sm text-[var(--color-text-muted)] mt-1">
                    Correct Answers
                  </p>
                </div>

                {/* プログレスバー */}
                <div className="w-full h-3 bg-[var(--color-bg-input)] rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      correctCount / exercises.length >= 0.8
                        ? "bg-green-400"
                        : correctCount / exercises.length >= 0.5
                          ? "bg-warning"
                          : "bg-red-400"
                    }`}
                    style={{
                      width: `${(correctCount / exercises.length) * 100}%`,
                    }}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div>
                    <p className="text-xl font-bold text-[var(--color-text-primary)]">
                      {Math.round(avgScore)}%
                    </p>
                    <p className="text-[11px] text-[var(--color-text-muted)]">
                      Average Score
                    </p>
                  </div>
                  <div>
                    <p className="text-xl font-bold text-[var(--color-text-primary)]">
                      {Math.round((correctCount / exercises.length) * 100)}%
                    </p>
                    <p className="text-[11px] text-[var(--color-text-muted)]">
                      Accuracy
                    </p>
                  </div>
                </div>
              </div>

              {/* 各問題の結果一覧 */}
              <div className="space-y-2 text-left">
                {results.map((result, i) => (
                  <div
                    key={i}
                    className={`p-3 rounded-xl text-xs ${
                      result.is_correct
                        ? "bg-green-500/5 border border-green-500/10"
                        : "bg-red-500/5 border border-red-500/10"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <span
                        className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 ${
                          result.is_correct
                            ? "bg-green-500/20 text-green-400"
                            : "bg-red-500/20 text-red-400"
                        }`}
                      >
                        {i + 1}
                      </span>
                      <div className="flex-1 min-w-0 space-y-1">
                        <p className="text-[var(--color-text-secondary)] line-clamp-1">
                          {exercises[i]?.template}
                        </p>
                        <p className="text-accent">
                          Answer: {result.corrected}
                        </p>
                        {!result.is_correct && (
                          <p className="text-[var(--color-text-muted)] text-[11px]">
                            {result.explanation}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* アクションボタン */}
              <button
                onClick={handleRestart}
                className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 transition-colors flex items-center justify-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Try Again
              </button>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}

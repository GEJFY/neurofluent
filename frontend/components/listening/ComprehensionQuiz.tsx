"use client";

import { useState, useCallback } from "react";
import { CheckCircle2, XCircle, ChevronRight } from "lucide-react";

/**
 * コンプリヘンションクイズ
 * 1問ずつ表示するマルチプルチョイスクイズ
 */

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

interface ComprehensionQuizProps {
  questions: Question[];
  onComplete: (answers: Answer[]) => void;
}

export default function ComprehensionQuiz({
  questions,
  onComplete,
}: ComprehensionQuizProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [answers, setAnswers] = useState<Answer[]>([]);

  const currentQuestion = questions[currentIndex];
  const isCorrect =
    selectedOption !== null &&
    selectedOption === currentQuestion?.correctIndex;
  const isLastQuestion = currentIndex === questions.length - 1;

  // 回答送信
  const handleSubmit = useCallback(() => {
    if (selectedOption === null || !currentQuestion) return;

    const answer: Answer = {
      questionId: currentQuestion.id,
      selectedIndex: selectedOption,
      isCorrect: selectedOption === currentQuestion.correctIndex,
    };

    setAnswers((prev) => [...prev, answer]);
    setIsSubmitted(true);
  }, [selectedOption, currentQuestion]);

  // 次の問題へ
  const handleNext = useCallback(() => {
    if (isLastQuestion) {
      // 最後の回答を含めてコールバック
      const finalAnswers = [
        ...answers,
        ...(isSubmitted && currentQuestion
          ? []
          : []),
      ];
      onComplete(finalAnswers.length > 0 ? finalAnswers : answers);
    } else {
      setCurrentIndex((prev) => prev + 1);
      setSelectedOption(null);
      setIsSubmitted(false);
    }
  }, [isLastQuestion, answers, onComplete, isSubmitted, currentQuestion]);

  if (!currentQuestion) return null;

  return (
    <div className="w-full max-w-lg mx-auto space-y-5">
      {/* 進捗バー */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-[var(--color-text-muted)]">
          <span>
            Question {currentIndex + 1} of {questions.length}
          </span>
          <span>
            {answers.filter((a) => a.isCorrect).length} correct
          </span>
        </div>
        <div className="w-full h-1.5 bg-[var(--color-bg-card)] rounded-full overflow-hidden">
          <div
            className="h-full bg-primary rounded-full transition-all duration-500"
            style={{
              width: `${((currentIndex + (isSubmitted ? 1 : 0)) / questions.length) * 100}%`,
            }}
          />
        </div>
      </div>

      {/* 質問カード */}
      <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-5">
        {/* 質問文 */}
        <p className="text-sm font-medium text-[var(--color-text-primary)] leading-relaxed">
          {currentQuestion.text}
        </p>

        {/* 選択肢 */}
        <div className="space-y-2">
          {currentQuestion.options.map((option, index) => {
            const isSelected = selectedOption === index;
            const isCorrectOption = index === currentQuestion.correctIndex;
            const showCorrectness = isSubmitted;

            let optionStyle = "";
            if (showCorrectness) {
              if (isCorrectOption) {
                optionStyle =
                  "border-green-500/30 bg-green-500/5";
              } else if (isSelected && !isCorrectOption) {
                optionStyle =
                  "border-red-500/30 bg-red-500/5";
              } else {
                optionStyle =
                  "border-[var(--color-border)] opacity-50";
              }
            } else {
              optionStyle = isSelected
                ? "border-primary bg-primary/5"
                : "border-[var(--color-border)] hover:border-primary/30";
            }

            return (
              <button
                key={index}
                onClick={() => {
                  if (!isSubmitted) setSelectedOption(index);
                }}
                disabled={isSubmitted}
                className={`w-full flex items-center gap-3 p-3 rounded-xl border text-left transition-colors ${optionStyle}`}
              >
                {/* ラジオボタン / 結果アイコン */}
                <div className="shrink-0">
                  {showCorrectness ? (
                    isCorrectOption ? (
                      <CheckCircle2 className="w-5 h-5 text-green-400" />
                    ) : isSelected ? (
                      <XCircle className="w-5 h-5 text-red-400" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border-2 border-[var(--color-border)]" />
                    )
                  ) : (
                    <div
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                        isSelected
                          ? "border-primary"
                          : "border-[var(--color-text-muted)]"
                      }`}
                    >
                      {isSelected && (
                        <div className="w-2.5 h-2.5 rounded-full bg-primary" />
                      )}
                    </div>
                  )}
                </div>

                {/* 選択肢テキスト */}
                <span
                  className={`text-sm ${
                    showCorrectness && isCorrectOption
                      ? "text-green-400 font-medium"
                      : showCorrectness && isSelected && !isCorrectOption
                        ? "text-red-400"
                        : "text-[var(--color-text-primary)]"
                  }`}
                >
                  {option}
                </span>
              </button>
            );
          })}
        </div>

        {/* 解説（送信後） */}
        {isSubmitted && (
          <div className="animate-fade-in p-3 rounded-xl bg-[var(--color-bg-primary)]/50">
            <p className="text-xs font-semibold text-[var(--color-text-secondary)] mb-1">
              Explanation
            </p>
            <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
              {currentQuestion.explanation}
            </p>
          </div>
        )}

        {/* アクションボタン */}
        {!isSubmitted ? (
          <button
            onClick={handleSubmit}
            disabled={selectedOption === null}
            className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Submit Answer
          </button>
        ) : (
          <button
            onClick={handleNext}
            className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 transition-colors flex items-center justify-center gap-2"
          >
            {isLastQuestion ? "See Summary" : "Next Question"}
            <ChevronRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}

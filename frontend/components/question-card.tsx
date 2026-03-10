"use client";

import {
  Bookmark,
  BookmarkCheck,
  ChevronDown,
  ChevronUp,
  LoaderCircle,
  RefreshCcw,
  Save,
  Sparkles
} from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { QuestionItem } from "@/types/api";

type QuestionCardProps = {
  item: QuestionItem;
  index: number;
  onToggleFavorite: (questionId: number, nextState: boolean) => void;
  onSaveAnswer: (questionId: number, answerText: string, hasExisting: boolean) => void;
  onGenerateFeedback: (questionId: number) => void;
  onRegenerate: (questionId: number) => void;
  favoritePending?: boolean;
  answerPending?: boolean;
  feedbackPending?: boolean;
  regeneratePending?: boolean;
};

export function QuestionCard({
  item,
  index,
  onToggleFavorite,
  onSaveAnswer,
  onGenerateFeedback,
  onRegenerate,
  favoritePending,
  answerPending,
  feedbackPending,
  regeneratePending
}: QuestionCardProps) {
  const savedAnswer = item.my_answer?.answer_text ?? "";
  const [draftAnswer, setDraftAnswer] = useState(savedAnswer);
  const [isReferenceVisible, setIsReferenceVisible] = useState(false);

  useEffect(() => {
    setDraftAnswer(savedAnswer);
    setIsReferenceVisible(false);
  }, [savedAnswer, item.answer, item.id, item.question]);

  const hasUnsavedChanges = draftAnswer.trim() !== savedAnswer.trim();
  const canSave = draftAnswer.trim().length >= 20;
  const feedback = item.my_answer?.feedback;

  return (
    <article className="paper-panel rounded-[28px] p-6">
      <div className="flex flex-col gap-4 border-b border-line pb-5 md:flex-row md:items-start md:justify-between">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full border border-line px-3 py-1 text-xs uppercase tracking-[0.18em]">
            Q{String(index + 1).padStart(2, "0")}
          </span>
          <span
            className={cn(
              "rounded-full px-3 py-1 text-xs font-medium",
              item.difficulty === "easy" && "difficulty-easy",
              item.difficulty === "medium" && "difficulty-medium",
              item.difficulty === "hard" && "difficulty-hard"
            )}
          >
            {item.difficulty}
          </span>
          <span className="rounded-full border border-line px-3 py-1 text-xs">{item.category}</span>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant={item.is_favorited ? "secondary" : "ghost"}
            disabled={favoritePending}
            onClick={() => onToggleFavorite(item.id, !item.is_favorited)}
          >
            {item.is_favorited ? (
              <BookmarkCheck className="mr-2 h-4 w-4 text-accent" />
            ) : (
              <Bookmark className="mr-2 h-4 w-4" />
            )}
            {item.is_favorited ? "已收藏" : "收藏"}
          </Button>
          <Button variant="ghost" disabled={regeneratePending} onClick={() => onRegenerate(item.id)}>
            {regeneratePending ? (
              <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <RefreshCcw className="mr-2 h-4 w-4" />
            )}
            重生成此题
          </Button>
        </div>
      </div>

      <h3 className="mt-5 text-xl font-semibold leading-8">{item.question}</h3>
      <p className="mt-3 text-sm leading-7 muted-text">{item.intent}</p>

      <div className="mt-6 grid gap-5 xl:grid-cols-[0.56fr_0.44fr]">
        <section className="rounded-[24px] border border-line bg-white/55 p-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="section-kicker">My Answer</p>
              <h4 className="mt-2 text-lg font-semibold">先自己回答，再看参考答案</h4>
            </div>
            {item.my_answer ? (
              <span className="rounded-full border border-line px-3 py-1 text-xs">已保存</span>
            ) : null}
          </div>

          <textarea
            value={draftAnswer}
            onChange={(event) => setDraftAnswer(event.target.value)}
            placeholder="在这里写下你的回答。建议先说明背景和目标，再讲方案、关键取舍和结果。"
            className="mt-4 min-h-[220px] w-full rounded-[22px] border border-line bg-[#fffdf7] px-4 py-4 text-sm leading-7 outline-none transition focus:border-accent"
          />

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <div className="text-xs muted-text">
              {canSave
                ? "建议先保存你的答案，再点击获取反馈。"
                : "至少写 20 个字符后才能保存。"}
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                variant="secondary"
                disabled={answerPending || !canSave || !hasUnsavedChanges}
                onClick={() => onSaveAnswer(item.id, draftAnswer, Boolean(item.my_answer))}
              >
                {answerPending ? (
                  <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Save className="mr-2 h-4 w-4" />
                )}
                保存我的回答
              </Button>
              <Button
                disabled={feedbackPending || !item.my_answer}
                onClick={() => onGenerateFeedback(item.id)}
              >
                {feedbackPending ? (
                  <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="mr-2 h-4 w-4" />
                )}
                获取 AI 反馈
              </Button>
            </div>
          </div>

          {feedback ? (
            <div className="mt-5 rounded-[22px] border border-line bg-[#fffaf0] p-5">
              <div className="grid gap-3 sm:grid-cols-4">
                {[
                  ["综合", feedback.score_json.overall],
                  ["相关性", feedback.score_json.relevance],
                  ["清晰度", feedback.score_json.clarity],
                  ["技术深度", feedback.score_json.technical_depth]
                ].map(([label, score]) => (
                  <div key={label} className="rounded-[18px] border border-line bg-white/70 p-4 text-center">
                    <p className="text-xs uppercase tracking-[0.18em] muted-text">{label}</p>
                    <p className="mt-2 text-3xl font-semibold">{score}</p>
                  </div>
                ))}
              </div>

              <div className="mt-5 grid gap-4 lg:grid-cols-3">
                <div className="rounded-[18px] border border-line bg-white/75 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] muted-text">亮点</p>
                  <div className="mt-3 space-y-2 text-sm leading-7">
                    {feedback.strengths.map((itemValue) => (
                      <p key={itemValue}>• {itemValue}</p>
                    ))}
                  </div>
                </div>
                <div className="rounded-[18px] border border-line bg-white/75 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] muted-text">不足</p>
                  <div className="mt-3 space-y-2 text-sm leading-7">
                    {feedback.weaknesses.map((itemValue) => (
                      <p key={itemValue}>• {itemValue}</p>
                    ))}
                  </div>
                </div>
                <div className="rounded-[18px] border border-line bg-white/75 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] muted-text">建议</p>
                  <div className="mt-3 space-y-2 text-sm leading-7">
                    {feedback.suggestions.map((itemValue) => (
                      <p key={itemValue}>• {itemValue}</p>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-4 rounded-[18px] border border-line bg-white/75 p-4">
                <p className="text-xs uppercase tracking-[0.18em] muted-text">优化版回答</p>
                <p className="mt-3 whitespace-pre-line text-sm leading-8">{feedback.improved_answer}</p>
              </div>
            </div>
          ) : null}
        </section>

        <section className="rounded-[24px] border border-line bg-white/55 p-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="section-kicker">Reference</p>
              <h4 className="mt-2 text-lg font-semibold">参考答案默认收起</h4>
            </div>
            <Button variant="ghost" onClick={() => setIsReferenceVisible((value) => !value)}>
              {isReferenceVisible ? (
                <ChevronUp className="mr-2 h-4 w-4" />
              ) : (
                <ChevronDown className="mr-2 h-4 w-4" />
              )}
              {isReferenceVisible ? "隐藏参考答案" : "显示参考答案"}
            </Button>
          </div>

          <div className="mt-4 rounded-[22px] border border-line bg-[#fffdf7] p-4">
            <p className="text-xs uppercase tracking-[0.18em] muted-text">简历依据</p>
            <p className="mt-3 text-sm leading-7">{item.reference_from_resume}</p>
          </div>

          <div className="mt-4 rounded-[22px] border border-line bg-[#fffdf7] p-4">
            {isReferenceVisible ? (
              <>
                <p className="text-xs uppercase tracking-[0.18em] muted-text">第一人称参考回答</p>
                <p className="mt-3 whitespace-pre-line text-sm leading-8">{item.answer}</p>
              </>
            ) : (
              <>
                <p className="text-xs uppercase tracking-[0.18em] muted-text">练习提示</p>
                <p className="mt-3 text-sm leading-7 muted-text">
                  先用自己的话回答，再点击“显示参考答案”对照结构、技术细节和工程取舍。
                </p>
              </>
            )}
          </div>
        </section>
      </div>
    </article>
  );
}

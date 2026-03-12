"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Layers3, RefreshCcw, Sparkles } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { EmptyState } from "@/components/empty-state";
import { LoadingPanel } from "@/components/loading-panel";
import { ProtectedShell } from "@/components/protected-shell";
import { QuestionCard } from "@/components/question-card";
import { Button } from "@/components/ui/button";
import { api, getApiErrorMessage } from "@/lib/api";
import { getOptionLabel, interviewStyleOptions, targetRoleOptions } from "@/lib/interview-options";
import { AnswerFeedback, InterviewSetDetail, QuestionItem, UserAnswer } from "@/types/api";

function updateQuestion(
  current: InterviewSetDetail | undefined,
  questionId: number,
  updater: (question: QuestionItem) => QuestionItem
) {
  if (!current) {
    return current;
  }
  return {
    ...current,
    questions: current.questions.map((question) =>
      question.id === questionId ? updater(question) : question
    )
  };
}

export default function InterviewDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const detailQuery = useQuery({
    queryKey: ["interview", params.id],
    queryFn: async () => (await api.get<InterviewSetDetail>(`/interviews/${params.id}`)).data
  });

  const favoriteMutation = useMutation({
    mutationFn: async ({ questionId, nextState }: { questionId: number; nextState: boolean }) => {
      if (nextState) {
        await api.post(`/questions/${questionId}/favorite`);
      } else {
        await api.delete(`/questions/${questionId}/favorite`);
      }
      return { questionId, nextState };
    },
    onMutate: async ({ questionId, nextState }) => {
      await queryClient.cancelQueries({ queryKey: ["interview", params.id] });
      const previous = queryClient.getQueryData<InterviewSetDetail>(["interview", params.id]);
      queryClient.setQueryData<InterviewSetDetail>(["interview", params.id], (current) =>
        updateQuestion(current, questionId, (question) => ({ ...question, is_favorited: nextState }))
      );
      return { previous };
    },
    onError: (_error, _variables, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["interview", params.id], context.previous);
      }
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["interview", params.id] });
      void queryClient.invalidateQueries({ queryKey: ["favorites"] });
    }
  });

  const saveAnswerMutation = useMutation({
    mutationFn: async ({
      questionId,
      answerText,
      hasExisting
    }: {
      questionId: number;
      answerText: string;
      hasExisting: boolean;
    }) => {
      const response = hasExisting
        ? await api.put<UserAnswer>(`/questions/${questionId}/my-answer`, {
            answer_text: answerText
          })
        : await api.post<UserAnswer>(`/questions/${questionId}/my-answer`, {
            answer_text: answerText
          });
      return { questionId, answer: response.data };
    },
    onSuccess: ({ questionId, answer }) => {
      queryClient.setQueryData<InterviewSetDetail>(["interview", params.id], (current) =>
        updateQuestion(current, questionId, (question) => ({ ...question, my_answer: answer }))
      );
      void queryClient.invalidateQueries({ queryKey: ["interview", params.id] });
    }
  });

  const feedbackMutation = useMutation({
    mutationFn: async (questionId: number) => {
      const response = await api.post<AnswerFeedback>(`/questions/${questionId}/feedback`);
      return { questionId, feedback: response.data };
    },
    onSuccess: ({ questionId, feedback }) => {
      queryClient.setQueryData<InterviewSetDetail>(["interview", params.id], (current) =>
        updateQuestion(current, questionId, (question) => ({
          ...question,
          my_answer: question.my_answer ? { ...question.my_answer, feedback } : question.my_answer
        }))
      );
      void queryClient.invalidateQueries({ queryKey: ["interview", params.id] });
    }
  });

  const regenerateQuestionMutation = useMutation({
    mutationFn: async (questionId: number) => {
      const response = await api.post<QuestionItem>(`/questions/${questionId}/regenerate`);
      return response.data;
    },
    onSuccess: (question) => {
      queryClient.setQueryData<InterviewSetDetail>(["interview", params.id], (current) =>
        updateQuestion(current, question.id, () => question)
      );
    }
  });

  const regenerateSetMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post<InterviewSetDetail>(`/interviews/${params.id}/regenerate`);
      return response.data;
    },
    onSuccess: (data) => {
      router.push(`/interviews/${data.id}`);
    }
  });

  const detail = detailQuery.data;

  return (
    <ProtectedShell
      title={detail?.title ?? "面试题集详情"}
      subtitle="这里是练习视图：先写自己的答案，再决定是否展开 AI 参考答案。每道题都支持收藏、反馈和原位重生成。"
      actions={
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" disabled={regenerateSetMutation.isPending} onClick={() => regenerateSetMutation.mutate()}>
            {regenerateSetMutation.isPending ? (
              <Sparkles className="mr-2 h-4 w-4 animate-pulse" />
            ) : (
              <RefreshCcw className="mr-2 h-4 w-4" />
            )}
            整套重生成
          </Button>
          <Link href="/upload">
            <Button>上传新简历</Button>
          </Link>
        </div>
      }
    >
      {detailQuery.isLoading ? <LoadingPanel text="正在加载题集详情..." /> : null}
      {detailQuery.isError ? (
        <div className="rounded-[24px] border border-[#d5a08b] bg-[#fff1eb] px-5 py-4 text-sm text-[#8d3411]">
          {getApiErrorMessage(detailQuery.error)}
        </div>
      ) : null}
      {!detailQuery.isLoading && !detailQuery.isError && !detail ? (
        <EmptyState title="题集不存在" description="该题集可能已删除，或不属于当前登录用户。" />
      ) : null}

      {detail ? (
        <div className="space-y-6">
          <section className="grid gap-5 xl:grid-cols-[0.5fr_0.5fr]">
            <div className="paper-panel rounded-[28px] p-6">
              <p className="section-kicker">Resume Summary</p>
              <h2 className="display-font mt-3 text-3xl">简历摘要</h2>
              <p className="mt-4 text-sm leading-8">{detail.resume_summary.summary}</p>
              <div className="mt-5 flex flex-wrap gap-2 text-xs">
                {detail.resume_summary.technical_stack.map((stack) => (
                  <span key={stack} className="rounded-full border border-line px-3 py-1">
                    {stack}
                  </span>
                ))}
              </div>
              {detail.resume_summary.resume_improvement_suggestions.length > 0 ? (
                <div className="mt-5 rounded-[20px] border border-line bg-white/50 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] muted-text">简历修改建议（基于 JD 对照）</p>
                  <div className="mt-3 space-y-2 text-sm leading-7">
                    {detail.resume_summary.resume_improvement_suggestions.map((suggestion) => (
                      <p key={suggestion}>• {suggestion}</p>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>

            <div className="paper-panel rounded-[28px] p-6">
              <p className="section-kicker">Practice Context</p>
              <h2 className="display-font mt-3 text-3xl">练习上下文</h2>
              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                <div className="rounded-[20px] border border-line bg-white/50 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] muted-text">目标岗位</p>
                  <p className="mt-3 text-sm font-medium">
                    {getOptionLabel(detail.target_role, targetRoleOptions)}
                  </p>
                </div>
                <div className="rounded-[20px] border border-line bg-white/50 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] muted-text">面试风格</p>
                  <p className="mt-3 text-sm font-medium">
                    {getOptionLabel(detail.interview_style, interviewStyleOptions)}
                  </p>
                </div>
                <div className="rounded-[20px] border border-line bg-white/50 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] muted-text">文本抽取状态</p>
                  <p className="mt-3 text-sm font-medium">{detail.extraction_status}</p>
                </div>
                <div className="rounded-[20px] border border-line bg-white/50 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] muted-text">抽取质量分</p>
                  <p className="mt-3 text-sm font-medium">
                    {detail.extraction_quality_score?.toFixed(1) ?? "N/A"}
                  </p>
                </div>
              </div>
              <div className="mt-5 rounded-[20px] border border-line bg-white/50 p-4">
                <div className="inline-flex items-center gap-2 text-sm font-medium">
                  <Layers3 className="h-4 w-4 text-accent" />
                  出题重点
                </div>
                <p className="mt-3 text-sm leading-7">
                  {detail.strategy.focus_areas.join("、")}，强调 {detail.strategy.emphasis.join("、")}
                </p>
              </div>
              <div className="mt-4 rounded-[20px] border border-line bg-white/50 p-4">
                <p className="text-xs uppercase tracking-[0.18em] muted-text">面试通过率评估</p>
                <div className="mt-3 grid gap-3 sm:grid-cols-3">
                  <div className="rounded-[16px] border border-line bg-white/70 p-3">
                    <p className="text-xs muted-text">通过率</p>
                    <p className="mt-1 text-xl font-semibold">{detail.assessment.pass_rate.toFixed(1)}%</p>
                  </div>
                  <div className="rounded-[16px] border border-line bg-white/70 p-3">
                    <p className="text-xs muted-text">已作答</p>
                    <p className="mt-1 text-xl font-semibold">{detail.assessment.answered_count}</p>
                  </div>
                  <div className="rounded-[16px] border border-line bg-white/70 p-3">
                    <p className="text-xs muted-text">平均分</p>
                    <p className="mt-1 text-xl font-semibold">
                      {detail.assessment.average_overall_score.toFixed(1)}
                    </p>
                  </div>
                </div>
                <p className="mt-3 text-xs muted-text">
                  通过率基于“你的回答 vs AI 参考答案”的评分结果自动估算；未生成反馈的答案会使用文本对齐评分兜底。
                </p>
              </div>
            </div>
          </section>

          {detail.job_description_text ? (
            <section className="paper-panel rounded-[28px] p-6">
              <p className="section-kicker">Job Description</p>
              <h2 className="display-font mt-3 text-3xl">岗位 JD</h2>
              <p className="mt-4 whitespace-pre-wrap text-sm leading-8">
                {detail.job_description_text}
              </p>
            </section>
          ) : null}

          <section className="space-y-5">
            {detail.questions.map((question, index) => (
              <QuestionCard
                key={question.id}
                item={question}
                index={index}
                favoritePending={
                  favoriteMutation.isPending && favoriteMutation.variables?.questionId === question.id
                }
                answerPending={
                  saveAnswerMutation.isPending && saveAnswerMutation.variables?.questionId === question.id
                }
                feedbackPending={
                  feedbackMutation.isPending && feedbackMutation.variables === question.id
                }
                regeneratePending={
                  regenerateQuestionMutation.isPending &&
                  regenerateQuestionMutation.variables === question.id
                }
                onToggleFavorite={(questionId, nextState) =>
                  favoriteMutation.mutate({ questionId, nextState })
                }
                onSaveAnswer={(questionId, answerText, hasExisting) =>
                  saveAnswerMutation.mutate({ questionId, answerText, hasExisting })
                }
                onGenerateFeedback={(questionId) => feedbackMutation.mutate(questionId)}
                onRegenerate={(questionId) => regenerateQuestionMutation.mutate(questionId)}
              />
            ))}
          </section>
        </div>
      ) : null}
    </ProtectedShell>
  );
}

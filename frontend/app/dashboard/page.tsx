"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { EmptyState } from "@/components/empty-state";
import { InterviewSetCard } from "@/components/interview-set-card";
import { LoadingPanel } from "@/components/loading-panel";
import { ProtectedShell } from "@/components/protected-shell";
import { Button } from "@/components/ui/button";
import { api, getApiErrorMessage } from "@/lib/api";
import { PaginatedInterviewSets } from "@/types/api";

export default function DashboardPage() {
  const query = useQuery({
    queryKey: ["interviews", "list"],
    queryFn: async () => (await api.get<PaginatedInterviewSets>("/interviews?page=1&page_size=12")).data
  });

  const items = query.data?.items ?? [];
  const totalQuestions = items.reduce((sum, item) => sum + item.total_question_count, 0);

  return (
    <ProtectedShell
      title="历史题集总览"
      subtitle="所有生成结果都会按用户隔离保存。你可以从这里回看每一次简历分析结果，并进入详情页收藏高价值问题。"
      actions={
        <Link href="/upload">
          <Button>上传新简历</Button>
        </Link>
      }
    >
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="paper-panel rounded-[26px] p-5">
          <p className="section-kicker">Total Sets</p>
          <p className="display-font mt-4 text-5xl">{query.data?.total ?? 0}</p>
          <p className="mt-3 text-sm muted-text">已持久化的面试题集数量</p>
        </div>
        <div className="paper-panel rounded-[26px] p-5">
          <p className="section-kicker">Total Questions</p>
          <p className="display-font mt-4 text-5xl">{totalQuestions}</p>
          <p className="mt-3 text-sm muted-text">当前页累计可复习题目数量</p>
        </div>
        <div className="paper-panel rounded-[26px] p-5">
          <p className="section-kicker">Coverage</p>
          <p className="display-font mt-4 text-5xl">
            {items[0]?.difficulty_breakdown.medium ?? 0}
          </p>
          <p className="mt-3 text-sm muted-text">最近题集中的中等难度题数量</p>
        </div>
      </div>

      <div className="mt-8">
        {query.isLoading ? <LoadingPanel text="正在加载历史题集..." /> : null}
        {query.isError ? (
          <div className="rounded-[24px] border border-[#d5a08b] bg-[#fff1eb] px-5 py-4 text-sm text-[#8d3411]">
            {getApiErrorMessage(query.error)}
          </div>
        ) : null}
        {!query.isLoading && !query.isError && items.length === 0 ? (
          <EmptyState
            title="还没有生成记录"
            description="上传一份程序员简历后，系统会生成 20 道主面试题，并在末尾附加 2 道随机 LeetCode 算法题。"
            action={
              <Link href="/upload">
                <Button>立即上传</Button>
              </Link>
            }
          />
        ) : null}
        <div className="grid gap-5 xl:grid-cols-2">
          {items.map((item) => (
            <InterviewSetCard key={item.id} item={item} />
          ))}
        </div>
      </div>
    </ProtectedShell>
  );
}

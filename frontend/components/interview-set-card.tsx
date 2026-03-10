import Link from "next/link";
import { ArrowRight, Clock3 } from "lucide-react";

import { InterviewSetListItem } from "@/types/api";

export function InterviewSetCard({ item }: { item: InterviewSetListItem }) {
  return (
    <Link
      href={`/interviews/${item.id}`}
      className="paper-panel group block rounded-[28px] p-6 transition hover:-translate-y-1"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="section-kicker">Interview Set</p>
          <h3 className="display-font mt-2 text-3xl">{item.title}</h3>
        </div>
        <ArrowRight className="h-5 w-5 transition group-hover:translate-x-1" />
      </div>
      <p className="mt-4 text-sm leading-7 muted-text">{item.resume_summary.summary}</p>
      <div className="mt-5 flex flex-wrap gap-2 text-xs">
        {item.resume_summary.technical_stack.slice(0, 4).map((stack) => (
          <span key={stack} className="rounded-full border border-line px-3 py-1">
            {stack}
          </span>
        ))}
      </div>
      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <div className="rounded-[22px] border border-line bg-white/45 p-4">
          <p className="text-xs uppercase tracking-[0.18em] muted-text">题目数量</p>
          <p className="mt-2 text-3xl font-semibold">{item.total_question_count}</p>
          <p className="mt-2 text-xs muted-text">
            简单 {item.difficulty_breakdown.easy} / 中等 {item.difficulty_breakdown.medium} / 困难 {item.difficulty_breakdown.hard}
          </p>
        </div>
        <div className="rounded-[22px] border border-line bg-white/45 p-4">
          <p className="text-xs uppercase tracking-[0.18em] muted-text">生成时间</p>
          <p className="mt-2 inline-flex items-center gap-2 text-sm">
            <Clock3 className="h-4 w-4 text-accent" />
            {new Date(item.created_at).toLocaleString("zh-CN")}
          </p>
          <p className="mt-2 text-xs muted-text">资历判断：{item.resume_summary.seniority}</p>
        </div>
      </div>
    </Link>
  );
}

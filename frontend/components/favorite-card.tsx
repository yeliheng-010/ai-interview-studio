import Link from "next/link";
import { ExternalLink, StarOff } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { FavoriteItem } from "@/types/api";

export function FavoriteCard({
  item,
  onRemove,
  isPending
}: {
  item: FavoriteItem;
  onRemove: (questionId: number) => void;
  isPending?: boolean;
}) {
  return (
    <article className="paper-panel rounded-[28px] p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div className="flex flex-wrap items-center gap-2">
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
          <span className="rounded-full border border-line px-3 py-1 text-xs muted-text">
            收藏于 {new Date(item.favorited_at).toLocaleDateString("zh-CN")}
          </span>
        </div>
        <Button variant="ghost" disabled={isPending} onClick={() => onRemove(item.question_id)}>
          <StarOff className="mr-2 h-4 w-4" />
          取消收藏
        </Button>
      </div>
      <h3 className="mt-5 text-xl font-semibold leading-8">{item.question}</h3>
      <p className="mt-4 text-sm leading-8">{item.answer}</p>
      <div className="mt-6 flex flex-wrap items-center justify-between gap-4 rounded-[22px] border border-line bg-white/50 p-4 text-sm">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] muted-text">来源题集</p>
          <p className="mt-2 font-medium">{item.source_question_set_title}</p>
        </div>
        <Link
          href={`/interviews/${item.source_question_set_id}`}
          className="inline-flex items-center gap-2 text-accent"
        >
          打开原题集
          <ExternalLink className="h-4 w-4" />
        </Link>
      </div>
    </article>
  );
}

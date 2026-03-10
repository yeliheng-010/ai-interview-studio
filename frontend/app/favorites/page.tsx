"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";

import { EmptyState } from "@/components/empty-state";
import { FavoriteCard } from "@/components/favorite-card";
import { LoadingPanel } from "@/components/loading-panel";
import { ProtectedShell } from "@/components/protected-shell";
import { Button } from "@/components/ui/button";
import { api, getApiErrorMessage } from "@/lib/api";
import { FavoriteItem } from "@/types/api";

export default function FavoritesPage() {
  const queryClient = useQueryClient();
  const favoritesQuery = useQuery({
    queryKey: ["favorites"],
    queryFn: async () => (await api.get<FavoriteItem[]>("/favorites")).data
  });

  const removeMutation = useMutation({
    mutationFn: async (questionId: number) => {
      await api.delete(`/questions/${questionId}/favorite`);
      return questionId;
    },
    onMutate: async (questionId) => {
      await queryClient.cancelQueries({ queryKey: ["favorites"] });
      const previous = queryClient.getQueryData<FavoriteItem[]>(["favorites"]);
      queryClient.setQueryData<FavoriteItem[]>(["favorites"], (current) =>
        current ? current.filter((item) => item.question_id !== questionId) : current
      );
      return { previous };
    },
    onError: (_error, _questionId, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["favorites"], context.previous);
      }
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["favorites"] });
    }
  });

  const favorites = favoritesQuery.data ?? [];

  return (
    <ProtectedShell
      title="收藏夹"
      subtitle="把值得反复推敲的题目收进这里，后续可以只针对高价值问题做强化训练。"
      actions={
        <Link href="/dashboard">
          <Button variant="secondary">返回仪表盘</Button>
        </Link>
      }
    >
      {favoritesQuery.isLoading ? <LoadingPanel text="正在加载收藏内容..." /> : null}
      {favoritesQuery.isError ? (
        <div className="rounded-[24px] border border-[#d5a08b] bg-[#fff1eb] px-5 py-4 text-sm text-[#8d3411]">
          {getApiErrorMessage(favoritesQuery.error)}
        </div>
      ) : null}
      {!favoritesQuery.isLoading && !favoritesQuery.isError && favorites.length === 0 ? (
        <EmptyState
          title="收藏夹还是空的"
          description="在题集详情页点击收藏后，这里会汇总展示所有高价值问题与参考回答。"
          action={
            <Link href="/dashboard">
              <Button>去浏览题集</Button>
            </Link>
          }
        />
      ) : null}
      <div className="space-y-5">
        {favorites.map((item) => (
          <FavoriteCard
            key={item.favorite_id}
            item={item}
            isPending={removeMutation.isPending}
            onRemove={(questionId) => removeMutation.mutate(questionId)}
          />
        ))}
      </div>
    </ProtectedShell>
  );
}

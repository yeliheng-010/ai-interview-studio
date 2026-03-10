"use client";

import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { AuthShell } from "@/components/auth-shell";
import { Button } from "@/components/ui/button";
import { api, getApiErrorMessage } from "@/lib/api";
import { getToken, setToken } from "@/lib/auth";
import { AuthResponse } from "@/types/api";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (getToken()) {
      router.replace("/dashboard");
    }
  }, [router]);

  const mutation = useMutation({
    mutationFn: async () => {
      const response = await api.post<AuthResponse>("/auth/register", { email, password });
      return response.data;
    },
    onSuccess: (data) => {
      setToken(data.access_token);
      router.push("/dashboard");
    },
    onError: (err) => setError(getApiErrorMessage(err))
  });

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    setError("");
    mutation.mutate();
  };

  return (
    <AuthShell
      title="注册"
      subtitle="创建账号后，你的题集、收藏和历史记录都会独立持久化保存，不会与其他用户混淆。"
    >
      <form className="paper-panel rounded-[30px] p-6" onSubmit={onSubmit}>
        <label className="block text-sm font-medium">邮箱</label>
        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="mt-2 w-full rounded-[18px] border border-line bg-white/80 px-4 py-3 outline-none transition focus:border-accent"
          placeholder="you@example.com"
          required
        />

        <label className="mt-5 block text-sm font-medium">密码</label>
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="mt-2 w-full rounded-[18px] border border-line bg-white/80 px-4 py-3 outline-none transition focus:border-accent"
          placeholder="至少 8 位"
          required
        />

        {error ? (
          <div className="mt-5 rounded-[18px] border border-[#d5a08b] bg-[#fff1eb] px-4 py-3 text-sm text-[#8d3411]">
            {error}
          </div>
        ) : null}

        <Button type="submit" className="mt-6 w-full" disabled={mutation.isPending}>
          {mutation.isPending ? "正在创建账号..." : "注册并开始生成"}
        </Button>

        <p className="mt-5 text-sm muted-text">
          已有账号？
          <Link href="/login" className="ml-2 text-accent">
            去登录
          </Link>
        </p>
      </form>
    </AuthShell>
  );
}

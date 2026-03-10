"use client";

import { useQuery } from "@tanstack/react-query";
import { BookOpen, LogOut, PanelTop, Upload } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect } from "react";

import { api } from "@/lib/api";
import { clearToken, getToken } from "@/lib/auth";
import { cn } from "@/lib/utils";
import { User } from "@/types/api";
import { LoadingPanel } from "@/components/loading-panel";
import { Button } from "@/components/ui/button";

const navItems = [
  { href: "/dashboard", label: "仪表盘", icon: PanelTop },
  { href: "/upload", label: "上传生成", icon: Upload },
  { href: "/favorites", label: "收藏夹", icon: BookOpen }
];

export function ProtectedShell({
  title,
  subtitle,
  actions,
  children
}: {
  title: string;
  subtitle: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const token = getToken();

  const userQuery = useQuery({
    queryKey: ["current-user"],
    queryFn: async () => (await api.get<User>("/auth/me")).data,
    enabled: Boolean(token),
    retry: false
  });

  useEffect(() => {
    if (!token) {
      router.replace("/login");
    }
  }, [router, token]);

  useEffect(() => {
    if (userQuery.isError) {
      clearToken();
      router.replace("/login");
    }
  }, [router, userQuery.isError]);

  if (!token || userQuery.isLoading || !userQuery.data) {
    return (
      <div className="mx-auto flex min-h-screen max-w-3xl items-center px-6">
        <LoadingPanel text="正在校验登录状态..." />
      </div>
    );
  }

  return (
    <div className="mx-auto min-h-screen max-w-[1400px] px-4 py-4 md:px-6 md:py-6">
      <div className="paper-panel rounded-[32px] p-4 md:p-6">
        <header className="flex flex-col gap-6 border-b border-line pb-6 lg:flex-row lg:items-start lg:justify-between">
          <div className="space-y-5">
            <div className="flex flex-wrap items-center gap-3">
              <Link href="/dashboard" className="display-font text-3xl tracking-wide">
                AI Interview Studio
              </Link>
              <span className="rounded-full border border-line px-3 py-1 text-xs uppercase tracking-[0.28em] text-accent">
                Resume-Based Practice
              </span>
            </div>
            <nav className="flex flex-wrap gap-2">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm transition",
                    pathname === item.href
                      ? "border-transparent bg-ink text-white"
                      : "border-line bg-white/50 hover:bg-white"
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
          <div className="flex flex-col gap-3 md:items-end">
            <div className="rounded-[20px] border border-line bg-white/50 px-4 py-3 text-sm">
              <div className="muted-text">当前账号</div>
              <div className="mt-1 font-medium">{userQuery.data.email}</div>
            </div>
            <Button
              variant="ghost"
              className="self-start md:self-auto"
              onClick={() => {
                clearToken();
                router.push("/login");
              }}
            >
              <LogOut className="mr-2 h-4 w-4" />
              退出登录
            </Button>
          </div>
        </header>

        <section className="grid gap-6 pt-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
          <div>
            <p className="section-kicker">Workbench</p>
            <h1 className="display-font mt-3 text-4xl md:text-5xl">{title}</h1>
            <p className="mt-4 max-w-2xl text-sm leading-7 muted-text">{subtitle}</p>
          </div>
          {actions ? <div className="justify-self-start lg:justify-self-end">{actions}</div> : null}
        </section>

        <main className="mt-8">{children}</main>
      </div>
    </div>
  );
}

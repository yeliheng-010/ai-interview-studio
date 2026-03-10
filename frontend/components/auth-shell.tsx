import Link from "next/link";
import { FileText, ShieldCheck, Sparkles } from "lucide-react";
import { ReactNode } from "react";

export function AuthShell({
  title,
  subtitle,
  children
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
}) {
  return (
    <div className="grid min-h-screen lg:grid-cols-[1.15fr_0.85fr]">
      <section className="grain-overlay relative overflow-hidden px-6 py-8 lg:px-12 lg:py-12">
        <div className="paper-panel relative flex h-full flex-col rounded-[36px] p-8 lg:p-12">
          <div className="flex items-center justify-between">
            <Link href="/" className="display-font text-3xl tracking-wide">
              AI Interview Studio
            </Link>
            <span className="rounded-full border border-line px-3 py-1 text-xs uppercase tracking-[0.28em] text-accent">
              AI 面试工作台
            </span>
          </div>
          <div className="mt-14 max-w-2xl">
            <p className="section-kicker">Interview Composer</p>
            <h1 className="display-font mt-4 text-5xl leading-tight lg:text-7xl">
              把简历变成一套可复盘的
              <span className="text-accent">程序员面试训练题库</span>
            </h1>
            <p className="mt-6 max-w-xl text-base leading-7 muted-text">{subtitle}</p>
          </div>
          <div className="mt-auto grid gap-4 pt-10 md:grid-cols-3">
            {[
              {
                icon: FileText,
                title: "PDF 简历解析",
                body: "上传后由 LangGraph 工作流完成抽取、分析、生成与修复。"
              },
              {
                icon: Sparkles,
                title: "双角色参考答案",
                body: "问题由 interviewer 提出，答案由第一人称 candidate 视角作答。"
              },
              {
                icon: ShieldCheck,
                title: "可回看可收藏",
                body: "历史记录、收藏夹、详情页全部持久化到数据库。"
              }
            ].map((item) => (
              <div key={item.title} className="rounded-[24px] border border-line bg-white/50 p-5">
                <item.icon className="h-5 w-5 text-accent" />
                <h3 className="mt-4 text-sm font-semibold">{item.title}</h3>
                <p className="mt-2 text-sm leading-6 muted-text">{item.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="flex items-center justify-center px-6 py-10 lg:px-12">
        <div className="w-full max-w-md">
          <p className="section-kicker">Access</p>
          <h2 className="display-font mt-3 text-4xl">{title}</h2>
          <div className="mt-8">{children}</div>
        </div>
      </section>
    </div>
  );
}

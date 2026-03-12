"use client";

import { useMutation } from "@tanstack/react-query";
import { FileText, FileUp, LoaderCircle, Sparkles } from "lucide-react";
import { useRouter } from "next/navigation";
import { ChangeEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { api, getApiErrorMessage } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { interviewStyleOptions, targetRoleOptions } from "@/lib/interview-options";
import { InterviewSetDetail } from "@/types/api";

type StreamQuestionPreview = {
  index: number;
  difficulty: string;
  category: string;
  question: string;
  isLeetcode: boolean;
};

export function UploadForm() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [jobDescriptionFile, setJobDescriptionFile] = useState<File | null>(null);
  const [targetRole, setTargetRole] = useState("software engineer");
  const [interviewStyle, setInterviewStyle] = useState("standard");
  const [jobDescriptionText, setJobDescriptionText] = useState("");
  const [error, setError] = useState<string>("");
  const [streamStage, setStreamStage] = useState("等待开始");
  const [streamQuestions, setStreamQuestions] = useState<StreamQuestionPreview[]>([]);
  const [resumeSuggestions, setResumeSuggestions] = useState<string[]>([]);

  const mutation = useMutation({
    mutationFn: async () => {
      if (!file) {
        throw new Error("请先选择 PDF 简历。");
      }

      const formData = new FormData();
      formData.append("file", file);
      if (jobDescriptionFile) {
        formData.append("jd_file", jobDescriptionFile);
      }
      formData.append("target_role", targetRole);
      formData.append("interview_style", interviewStyle);
      if (jobDescriptionText.trim()) {
        formData.append("job_description_text", jobDescriptionText.trim());
      }
      const token = getToken();

      const response = await fetch(`${api.defaults.baseURL ?? "http://localhost:8000/api"}/interviews/generate/stream`, {
        method: "POST",
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: formData
      });

      if (!response.ok) {
        let detail = `请求失败（${response.status}）`;
        try {
          const payload = await response.json();
          if (typeof payload?.detail === "string") {
            detail = payload.detail;
          }
        } catch {
          // Ignore JSON parse failures and use fallback detail.
        }
        throw new Error(detail);
      }

      if (!response.body) {
        throw new Error("当前环境不支持流式读取，请稍后重试。");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let interviewId: number | null = null;

      while (true) {
        const { value, done } = await reader.read();
        buffer += decoder.decode(value ?? new Uint8Array(), { stream: !done });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const rawLine of lines) {
          const line = rawLine.trim();
          if (!line) {
            continue;
          }
          let event: Record<string, unknown>;
          try {
            event = JSON.parse(line);
          } catch {
            continue;
          }

          if (event.event === "stage") {
            setStreamStage(typeof event.message === "string" ? event.message : "处理中");
            continue;
          }

          if (event.event === "resume_suggestions" && Array.isArray(event.suggestions)) {
            setResumeSuggestions(
              event.suggestions
                .map((item) => (typeof item === "string" ? item : ""))
                .filter(Boolean)
            );
            continue;
          }

          if (event.event === "question") {
            setStreamQuestions((current) => [
              ...current,
              {
                index: Number(event.index ?? current.length + 1),
                difficulty: String(event.difficulty ?? "unknown"),
                category: String(event.category ?? "未分类"),
                question: String(event.question ?? ""),
                isLeetcode: Boolean(event.is_leetcode)
              }
            ]);
            continue;
          }

          if (event.event === "completed" && typeof event.interview_id === "number") {
            interviewId = event.interview_id;
            continue;
          }

          if (event.event === "error") {
            throw new Error(typeof event.detail === "string" ? event.detail : "生成失败，请稍后重试。");
          }
        }

        if (done) {
          break;
        }
      }

      if (interviewId === null) {
        throw new Error("流式生成未返回题集 ID，请重试。");
      }

      const detail = await api.get<InterviewSetDetail>(`/interviews/${interviewId}`);
      return detail.data;
    },
    onMutate: () => {
      setError("");
      setStreamStage("开始上传与初始化...");
      setStreamQuestions([]);
      setResumeSuggestions([]);
    },
    onSuccess: (data) => {
      router.push(`/interviews/${data.id}`);
    },
    onError: (err) => {
      setError(getApiErrorMessage(err));
    }
  });

  const onFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setFile(event.target.files?.[0] ?? null);
    setError("");
  };

  const onJobDescriptionFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setJobDescriptionFile(event.target.files?.[0] ?? null);
    setError("");
  };

  return (
    <div className="space-y-6">
      <div className="paper-panel rounded-[30px] p-6 md:p-8">
        <div className="grid gap-6 xl:grid-cols-[0.62fr_0.38fr]">
          <div className="rounded-[24px] border border-dashed border-line bg-white/45 p-8 text-center">
            <FileUp className="mx-auto h-10 w-10 text-accent" />
            <h3 className="display-font mt-4 text-3xl">上传 PDF 简历</h3>
            <p className="mx-auto mt-3 max-w-xl text-sm leading-7 muted-text">
              系统会先在后端本地做 text-first 文本抽取、清洗和质量校验，确认质量足够后，才把纯文本发送给
              LLM 进行分析和出题。
            </p>
            <label className="mt-6 inline-flex cursor-pointer flex-col rounded-[22px] border border-line bg-white/70 px-5 py-4 text-left transition hover:bg-white">
              <span className="text-sm font-medium">选择文件</span>
              <span className="mt-1 text-xs muted-text">
                仅支持 PDF，默认不走 OCR，也不会把 PDF 页面转成图片送给模型。
              </span>
              <input type="file" accept=".pdf,application/pdf" className="hidden" onChange={onFileChange} />
            </label>
            <div className="mt-5 text-sm">
              {file ? (
                <span>
                  已选择：<strong>{file.name}</strong>
                </span>
              ) : (
                <span className="muted-text">尚未选择文件</span>
              )}
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-[24px] border border-line bg-white/55 p-5">
              <p className="section-kicker">Practice Setup</p>
              <h4 className="display-font mt-3 text-2xl">面试参数</h4>
              <div className="mt-5 space-y-4">
                <label className="block text-sm">
                  <span className="font-medium">目标岗位</span>
                  <select
                    value={targetRole}
                    onChange={(event) => setTargetRole(event.target.value)}
                    className="mt-2 w-full rounded-[18px] border border-line bg-white/80 px-4 py-3 outline-none transition focus:border-accent"
                  >
                    {targetRoleOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="block text-sm">
                  <span className="font-medium">面试风格</span>
                  <select
                    value={interviewStyle}
                    onChange={(event) => setInterviewStyle(event.target.value)}
                    className="mt-2 w-full rounded-[18px] border border-line bg-white/80 px-4 py-3 outline-none transition focus:border-accent"
                  >
                    {interviewStyleOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
                <div className="block text-sm">
                  <span className="font-medium">岗位 JD</span>
                  <label className="mt-2 flex cursor-pointer flex-col rounded-[18px] border border-dashed border-line bg-white/70 px-4 py-3 transition hover:bg-white">
                    <span className="text-sm font-medium">上传 JD 文件</span>
                    <span className="mt-1 text-xs muted-text">
                      支持 `.txt`、`.md`、`.pdf`。如果同时上传文件并粘贴文本，系统会合并两者一起出题。
                    </span>
                    <input
                      type="file"
                      accept=".txt,.md,.markdown,.pdf,text/plain,text/markdown,application/pdf"
                      className="hidden"
                      onChange={onJobDescriptionFileChange}
                    />
                  </label>
                  <div className="mt-2 text-xs muted-text">
                    {jobDescriptionFile ? `已选择 JD 文件：${jobDescriptionFile.name}` : "未上传 JD 文件"}
                  </div>
                  <textarea
                    value={jobDescriptionText}
                    onChange={(event) => setJobDescriptionText(event.target.value)}
                    className="mt-3 min-h-40 w-full rounded-[18px] border border-line bg-white/80 px-4 py-3 outline-none transition focus:border-accent"
                    placeholder="可选。也可以直接粘贴岗位职责、任职要求、技术栈要求等。"
                  />
                </div>
              </div>
            </div>

            <div className="rounded-[24px] border border-line bg-white/55 p-5 text-sm leading-7">
              <div className="flex items-center gap-3">
                <Sparkles className="h-4 w-4 text-accent" />
                <span className="font-medium">生成结果会持久化保存</span>
              </div>
              <p className="mt-3 muted-text">
                你可以回到历史题集继续练习，逐题写答案、获取反馈、收藏重点题，并在原题位上重生成新的问题。
              </p>
            </div>
          </div>
        </div>

        {error ? (
          <div className="mt-5 rounded-[20px] border border-[#d5a08b] bg-[#fff1eb] px-4 py-3 text-sm text-[#8d3411]">
            {error}
          </div>
        ) : null}

        {mutation.isPending ? (
          <section className="mt-5 rounded-[24px] border border-line bg-white/65 p-5">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="section-kicker">Streaming Generation</p>
                <h4 className="mt-2 text-xl font-semibold">题目正在流式生成</h4>
              </div>
              <span className="rounded-full border border-line px-3 py-1 text-xs">
                已到达 {streamQuestions.length} 题
              </span>
            </div>
            <p className="mt-3 text-sm muted-text">当前阶段：{streamStage}</p>

            {resumeSuggestions.length > 0 ? (
              <div className="mt-4 rounded-[18px] border border-line bg-white/70 p-4">
                <p className="text-xs uppercase tracking-[0.18em] muted-text">JD 对照简历修改建议</p>
                <div className="mt-3 space-y-2 text-sm leading-7">
                  {resumeSuggestions.map((suggestion) => (
                    <p key={suggestion}>• {suggestion}</p>
                  ))}
                </div>
              </div>
            ) : null}

            <div className="mt-4 max-h-[320px] space-y-3 overflow-y-auto pr-1">
              {streamQuestions.map((item) => (
                <div
                  key={`${item.index}-${item.question}`}
                  className="rounded-[18px] border border-line bg-white/75 px-4 py-3"
                >
                  <p className="text-xs muted-text">
                    Q{String(item.index).padStart(2, "0")} · {item.difficulty} · {item.category}
                    {item.isLeetcode ? " · LeetCode" : ""}
                  </p>
                  <p className="mt-1 text-sm leading-7">{item.question}</p>
                </div>
              ))}
            </div>
          </section>
        ) : null}

        <div className="mt-6 flex flex-wrap items-center justify-between gap-4">
          <div className="inline-flex items-center gap-2 text-sm muted-text">
            <FileText className="h-4 w-4 text-accent" />
            先本地抽文本，再调用模型，不上传图片版简历。
          </div>
          <Button onClick={() => mutation.mutate()} disabled={mutation.isPending || !file}>
            {mutation.isPending ? (
              <>
                <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
                正在流式生成
              </>
            ) : (
              "开始流式生成（20+2 题）"
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

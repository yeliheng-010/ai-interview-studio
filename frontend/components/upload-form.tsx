"use client";

import { useMutation } from "@tanstack/react-query";
import { FileText, FileUp, LoaderCircle, Sparkles } from "lucide-react";
import { useRouter } from "next/navigation";
import { ChangeEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { api, getApiErrorMessage } from "@/lib/api";
import { interviewStyleOptions, targetRoleOptions } from "@/lib/interview-options";
import { InterviewSetDetail } from "@/types/api";

export function UploadForm() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [targetRole, setTargetRole] = useState("software engineer");
  const [interviewStyle, setInterviewStyle] = useState("standard");
  const [error, setError] = useState<string>("");

  const mutation = useMutation({
    mutationFn: async () => {
      if (!file) {
        throw new Error("请先选择 PDF 简历。");
      }

      const formData = new FormData();
      formData.append("file", file);
      formData.append("target_role", targetRole);
      formData.append("interview_style", interviewStyle);

      const response = await api.post<InterviewSetDetail>("/interviews/generate", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      return response.data;
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

        <div className="mt-6 flex flex-wrap items-center justify-between gap-4">
          <div className="inline-flex items-center gap-2 text-sm muted-text">
            <FileText className="h-4 w-4 text-accent" />
            先本地抽文本，再调用模型，不上传图片版简历。
          </div>
          <Button onClick={() => mutation.mutate()} disabled={mutation.isPending || !file}>
            {mutation.isPending ? (
              <>
                <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
                正在生成
              </>
            ) : (
              "开始生成 20 题"
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

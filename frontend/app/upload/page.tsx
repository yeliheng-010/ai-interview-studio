"use client";

import { ProtectedShell } from "@/components/protected-shell";
import { UploadForm } from "@/components/upload-form";

export default function UploadPage() {
  return (
    <ProtectedShell
      title="上传并生成新题集"
      subtitle="这一版简历处理是明确的 text-first 工作流：后端先本地提取 PDF 纯文本，再清洗、校验质量，最后才把文本送入 LangGraph 做分析与生成。"
    >
      <UploadForm />
    </ProtectedShell>
  );
}

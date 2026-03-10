"use client";

import { ProtectedShell } from "@/components/protected-shell";
import { UploadForm } from "@/components/upload-form";

export default function UploadPage() {
  return (
    <ProtectedShell
      title="上传并生成新题集"
      subtitle="这一版支持简历和岗位 JD 联合出题：你可以上传 JD 文件或直接粘贴岗位要求，后端会与简历文本一起交给 LangGraph 做分析、策略规划和出题。"
    >
      <UploadForm />
    </ProtectedShell>
  );
}

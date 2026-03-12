"use client";

import { ProtectedShell } from "@/components/protected-shell";
import { UploadForm } from "@/components/upload-form";

export default function UploadPage() {
  return (
    <ProtectedShell
      title="上传并生成新题集"
      subtitle="这一版支持简历与岗位 JD 联合出题，并改为流式回传题目：生成过程中会实时看到题目和简历优化建议，最后附带 2 道随机 LeetCode 算法题。"
    >
      <UploadForm />
    </ProtectedShell>
  );
}

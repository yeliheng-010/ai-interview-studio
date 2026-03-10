export const targetRoleOptions = [
  { value: "software engineer", label: "软件工程师" },
  { value: "backend engineer", label: "后端工程师" },
  { value: "frontend engineer", label: "前端工程师" },
  { value: "full-stack engineer", label: "全栈工程师" },
  { value: "Java engineer", label: "Java 工程师" },
  { value: "Python engineer", label: "Python 工程师" },
  { value: "Go engineer", label: "Go 工程师" },
  { value: "test development engineer", label: "测试开发工程师" },
  { value: "DevOps engineer", label: "DevOps 工程师" },
  { value: "algorithm engineer", label: "算法工程师" },
  { value: "data engineer", label: "数据工程师" }
] as const;

export const interviewStyleOptions = [
  { value: "standard", label: "标准技术面" },
  { value: "fundamentals-heavy", label: "基础偏重" },
  { value: "project-deep-dive", label: "项目深挖" },
  { value: "system-design-heavy", label: "系统设计偏重" },
  { value: "algorithm-heavy", label: "算法偏重" },
  { value: "real-world-scenario", label: "真实场景题" },
  { value: "big-tech-style", label: "大厂风格" },
  { value: "startup-practical-style", label: "创业公司实战风格" }
] as const;

export function getOptionLabel(
  value: string,
  options: ReadonlyArray<{ value: string; label: string }>
) {
  return options.find((item) => item.value === value)?.label ?? value;
}

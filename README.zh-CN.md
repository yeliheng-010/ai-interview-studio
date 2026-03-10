# AI Interview Studio

<p align="center">
  <a href="./README.md"><strong>English</strong></a> |
  <a href="./README.zh-CN.md"><strong>Chinese</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python 3.11" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Next.js-App%20Router-000000?logo=nextdotjs&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/LangGraph-StateGraph-FF6B35" alt="LangGraph" />
  <img src="https://img.shields.io/badge/Agentic-Workflow%20Design-6C5CE7" alt="Agentic Workflow Design" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" alt="Docker Compose" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License" />
</p>

这是一个以 Agent 框架设计和工作流编排能力为主展示点的全栈 AI 面试训练平台。

它的重点不是“做了一个有上传、列表、详情页的功能型项目”，而是清楚地体现了我如何把一个 LLM 产品拆成显式状态、专职节点、结构化契约、修复环、评估环和业务持久化分层。

面试官如果只看一个项目，我希望他们从这个仓库里快速看到两件事：

1. 我不把 agent 理解成“多轮聊天”，而是理解成**有状态、有边界、有恢复能力的工作流系统**。
2. 我不仅会调模型接口，还会把 LangGraph、后端工程、前端产品化和数据库持久化组合成一个完整应用。

## 项目预览

![AI Interview Studio 首页截图](docs/images/github-homepage.png)

## 为什么这个项目适合放在作品集里

- 它把 Agent 系统建模成显式状态机，而不是一层 prompt 包装
- 它使用 LangGraph `StateGraph` 做真实工作流，而不是线性函数串联
- 它体现了验证、去重、修复、回退和评估，而不是“一次生成就结束”
- 它把工作流编排层、业务持久化层和前端交互层分开设计
- 它不是 Demo，而是有历史记录、收藏、反馈、重生成和持久化闭环的完整产品

## Agent 框架亮点

- **显式状态设计**：简历原文、清洗文本、简历摘要、面试策略、分难度题目、最终题集、错误信息都在共享 state 中流转
- **节点职责单一**：每个节点只处理一个明确问题，而不是把所有逻辑塞进一个超大 prompt
- **结构化契约**：每次 LLM 调用都要求输出结构化 JSON，并通过类型模型校验
- **修复环设计**：首次生成后还会做去重、字段修复、答案补全和缺量补齐
- **评估环设计**：用户答案反馈走独立图，说明系统不仅能“生成”，还能“评估与改写”
- **确定性护栏**：PDF 文本抽取、质量校验、字段规范化、本地 fallback 和持久化规则，保证系统不完全依赖模型侥幸输出
- **运行时与业务层分离**：LangGraph 负责编排，PostgreSQL 负责业务数据持久化，这种分层更符合真实工程实践

## 工作流架构

```mermaid
flowchart LR
    A[上传 PDF 简历] --> B[extract_pdf_text]
    B --> C[clean_resume_text]
    C --> D[validate_resume_text]
    D --> E[analyze_resume]
    E --> F[plan_interview_strategy]
    F --> G[generate_easy_questions_and_answers]
    G --> H[generate_medium_questions_and_answers]
    H --> I[generate_hard_questions_and_answers]
    I --> J[deduplicate_and_repair]
    J --> K[finalize_payload]
    K --> L[持久化到 PostgreSQL]
```

除此之外还有两个独立的 Agent 工作流：

- **单题重生成工作流**：准备上下文、生成替换题、校验质量、必要时安全回退
- **答案反馈工作流**：对比题目、用户答案和参考答案，输出结构化评分、优缺点和优化版回答

## 产品概览

用户上传 PDF 简历后，还可以额外粘贴岗位 JD，或直接上传 JD 文件。后端先在本地进行 text-first 的文本抽取与清洗，只把简历纯文本与 JD 上下文送入 LangGraph。系统随后完成简历分析、JD 对齐的面试策略规划、三档难度题目生成、答案生成、去重修复和最终落库。用户之后可以回看题集、收藏题目、隐藏或展开参考答案、提交自己的回答、获取 AI 反馈，并对整套题集或单题做重生成。

## JD 联合出题使用说明

当你希望系统同时参考“你的经历”和“目标岗位要求”时，可以按下面方式使用：

1. 上传 PDF 简历。
2. 通过两种方式之一补充岗位 JD：直接粘贴 JD 文本，或上传 `.txt`、`.md`、`.pdf` 格式的 JD 文件。
3. 如果同时提供 JD 文本和 JD 文件，后端会先合并两部分内容，再一起送入工作流。
4. 正常生成题集即可。
5. 系统会优先围绕简历证据与 JD 要求的交集提问，也会适度追问 JD 明确要求但简历体现较弱的能力点。
6. 这份 JD 上下文会随题集一起保存，并在整套重生成和单题重生成时继续复用。

## 这个项目体现了什么能力

1. 我能把一个 LLM 能力拆成有中间状态的多阶段工作流。
2. 我理解 Agent 系统必须有验证、修复、回退和评估，而不是“调用一次模型就结束”。
3. 我能把工作流编排、业务持久化和用户界面分层清楚。
4. 我做的不只是一个聊天式 Demo，而是一个具备复盘、重生成、反馈和持久化能力的完整 Agent 应用。

## Text-First 简历处理流程

本项目明确采用 text-first，而不是 vision-first。

默认情况下，系统不会：

- 把 PDF 页面转成图片发送给模型
- 把 PDF 二进制直接交给模型
- 把 OCR 作为默认路径

默认流程：

1. 上传 PDF 简历
2. 后端本地使用 `pypdf` 抽取文本
3. 清洗和归一化文本
4. 校验抽取质量
5. 只把纯文本送入 LLM
6. 执行 LangGraph 编排
7. 把业务结果持久化到 PostgreSQL

## 技术栈

### 后端

- Python 3.11
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Pydantic
- LangGraph
- httpx
- pypdf
- passlib
- python-jose

### 前端

- Next.js App Router
- TypeScript
- Tailwind CSS
- TanStack Query
- axios

### 基础设施

- Docker
- docker compose

## 快速开始

### 1. 配置环境变量

复制：

- `backend/.env.example` -> `backend/.env`
- `frontend/.env.example` -> `frontend/.env`

后端示例：

```env
APP_NAME=AI Interview Studio
APP_ENV=development
DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/interview_studio
SECRET_KEY=change-this-in-local-env
ACCESS_TOKEN_EXPIRE_MINUTES=10080
OPENAI_API_KEY=your_dashscope_api_key
OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
OPENAI_MODEL=qwen3.5-plus
OPENAI_TIMEOUT_SECONDS=180
CORS_ORIGINS=http://localhost:3000
SQL_ECHO=false
```

前端示例：

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

### 2. Docker 启动

```bash
docker compose up --build
```

### 3. 访问地址

- 前端：`http://localhost:3000`
- 后端 API：`http://localhost:8000/api`
- FastAPI 文档：`http://localhost:8000/docs`

## 安全说明

- 真实密钥只能保存在本地 `backend/.env` 与 `frontend/.env`
- `.env.example` 只能放占位值，不能放真实 secret
- 业务数据持久化在 PostgreSQL
- LangGraph 负责工作流编排，不替代业务数据层

## 许可证

本项目采用 [MIT License](./LICENSE)。

# AI Mock Interview Platform

<p align="center">
  <a href="./README.md"><strong>English</strong></a> |
  <a href="./README.zh-CN.md"><strong>Chinese</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python 3.11" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Next.js-App%20Router-000000?logo=nextdotjs&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/LangGraph-StateGraph-FF6B35" alt="LangGraph" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" alt="Docker Compose" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License" />
</p>

一个面向作品集展示的全栈 AI 模拟面试平台。用户上传 PDF 简历后，系统会先在后端本地抽取并清洗简历文本，再通过 LangGraph 编排简历分析、面试策略规划、题目生成、答案生成、去重修复与练习反馈流程，最终把完整结果持久化到 PostgreSQL，供后续复盘、收藏、重答和再生成使用。

这个项目不是一次性的脚本，而是完整产品形态，适合用于展示：

- FastAPI + PostgreSQL 的后端工程能力
- Next.js + TypeScript 的前端实现能力
- LangGraph 驱动的真实 LLM 工作流编排能力
- Docker 化本地开发与交付能力
- 面向用户练习场景的产品思维和数据持久化设计

## 项目预览

![AI Mock Interview Platform 首页截图](docs/images/github-homepage.png)

## 为什么它适合作为作品集项目

- 它是完整产品闭环，不是只做一次推理调用
- 同时覆盖前端、后端、数据库、AI 编排和部署
- 使用 LangGraph `StateGraph` 作为真实工作流层，而不是普通函数串联
- 支持历史记录、收藏、用户答案、AI 反馈和重生成
- 解决的是一个真实产品问题：把简历转化成可复盘、可练习、可长期保存的程序员模拟面试题库

## 核心能力

- JWT 注册 / 登录 / 当前用户信息
- PDF 简历上传
- 本地 `pypdf` 文本抽取
- 文本清洗与质量校验
- 简历分析与面试策略规划
- 固定 20 题生成
  - easy 6
  - medium 8
  - hard 6
- 题目与参考答案使用简体中文
- 参考答案默认折叠，适合练习
- 每题支持写“我的回答”
- 支持 AI 结构化反馈
- 支持收藏、历史复盘、整套重生成、单题重生成

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

## LangGraph 工作流

### 主生成图

主 `StateGraph` 包含：

1. `extract_pdf_text`
2. `clean_resume_text`
3. `validate_resume_text`
4. `analyze_resume`
5. `plan_interview_strategy`
6. `generate_easy_questions_and_answers`
7. `generate_medium_questions_and_answers`
8. `generate_hard_questions_and_answers`
9. `deduplicate_and_repair`
10. `finalize_payload`

### 练习相关图

- 单题重生成图
- 用户答案反馈图

这样生成链路和练习链路都具备明确状态、节点和边。

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

## 项目结构

```text
ai-mock-interview-platform/
|-- backend/
|   |-- app/
|   |   |-- core/
|   |   |-- graph/
|   |   |-- models/
|   |   |-- prompts/
|   |   |-- routers/
|   |   |-- schemas/
|   |   |-- services/
|   |   |-- utils/
|   |   |-- config.py
|   |   |-- db.py
|   |   `-- main.py
|   |-- alembic/
|   |-- tests/
|   |-- Dockerfile
|   |-- requirements.txt
|   `-- .env.example
|-- frontend/
|   |-- app/
|   |-- components/
|   |-- lib/
|   |-- types/
|   |-- __tests__/
|   |-- Dockerfile
|   |-- package.json
|   `-- .env.example
|-- docs/
|   `-- images/
|       `-- github-homepage.png
|-- docker-compose.yml
|-- LICENSE
|-- README.md
`-- README.zh-CN.md
```

## 快速开始

### 1. 配置环境变量

复制：

- `backend/.env.example` -> `backend/.env`
- `frontend/.env.example` -> `frontend/.env`

后端示例：

```env
APP_NAME=AI Mock Interview Platform
APP_ENV=development
DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/mock_interview
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

## 主要 API

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/interviews/generate`
- `GET /api/interviews`
- `GET /api/interviews/{id}`
- `POST /api/interviews/{id}/regenerate`
- `POST /api/questions/{id}/favorite`
- `POST /api/questions/{id}/my-answer`
- `POST /api/questions/{id}/feedback`
- `POST /api/questions/{id}/regenerate`
- `GET /api/favorites`

## 测试

后端：

```bash
cd backend
pytest
```

前端：

```bash
cd frontend
npm install
npm test
```

## 安全说明

- 真实密钥只能保存在本地 `backend/.env` 与 `frontend/.env`
- `.env.example` 只能放占位值，不能放真实 secret
- 业务数据持久化在 PostgreSQL
- LangGraph 负责工作流编排，不替代业务数据层

## 许可证

本项目采用 [MIT License](./LICENSE)。

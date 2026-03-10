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

An end-to-end AI interview practice platform built to showcase agent-framework design, explicit workflow orchestration, and production-style full-stack engineering.

The most important part of this project is not the CRUD surface area. It is the way the system models resume understanding, interview planning, question generation, repair, regeneration, and answer evaluation as explicit LangGraph workflows with structured state, typed contracts, deterministic post-processing, and persistent business data.

## Preview

![AI Interview Studio homepage](docs/images/github-homepage.png)

## Why This Project Stands Out to Interviewers

- It shows how I model agent systems as explicit state machines rather than prompt wrappers
- It uses LangGraph `StateGraph` for real orchestration instead of a linear function pipeline
- It separates workflow orchestration from business persistence, which keeps the system maintainable
- It demonstrates recovery-oriented design through validation, deduplication, repair, and regeneration nodes
- It includes evaluation loops, not just generation loops, through user-answer feedback workflows
- It is still a complete product, so the agent architecture is grounded in real user-facing behavior

## Product Overview

Users upload a PDF resume, optionally paste a job description or upload a JD file, and the backend extracts resume text locally, validates text quality, then sends the cleaned resume text plus JD context into a LangGraph workflow. The system analyzes the resume, aligns interview strategy with both the resume and target JD, generates 20 programmer-focused interview questions across easy, medium, and hard difficulty levels, and writes reference answers in first-person candidate voice. Everything is persisted for later review and practice.

## Agent Framework Highlights

This repository is designed to communicate agentic-system thinking clearly:

- **Explicit graph state**: resume extraction, cleaned text, resume summary, strategy, per-difficulty items, final items, and errors are modeled as shared workflow state
- **Specialized nodes**: each graph node owns one responsibility instead of bundling the whole workflow into one oversized prompt
- **Structured contracts**: every LLM hop is validated with typed schemas before downstream nodes consume the result
- **Repair loop**: the workflow does not stop at first-pass generation; it deduplicates, repairs, and fills missing items automatically
- **Evaluation loop**: user-written answers are evaluated through a separate LangGraph path, showing that the system supports both generation and critique
- **Deterministic guardrails**: local PDF extraction, text validation, normalization, fallback behavior, and persistence rules make the workflow more robust than a naive prompt chain
- **Business/runtime separation**: PostgreSQL stores product data while LangGraph handles runtime orchestration

## Workflow Architecture

```mermaid
flowchart LR
    A[Upload PDF Resume] --> B[extract_pdf_text]
    B --> C[clean_resume_text]
    C --> D[validate_resume_text]
    D --> E[analyze_resume]
    E --> F[plan_interview_strategy]
    F --> G[generate_easy_questions_and_answers]
    G --> H[generate_medium_questions_and_answers]
    H --> I[generate_hard_questions_and_answers]
    I --> J[deduplicate_and_repair]
    J --> K[finalize_payload]
    K --> L[Persist to PostgreSQL]
```

Additional agent workflows:

- **Question regeneration workflow**: prepare local context, generate a replacement question, validate it, and fall back safely if needed
- **Answer feedback workflow**: compare the question, the user answer, and the reference answer, then produce structured scoring and an improved answer

## Core Features

- JWT-based authentication
- Resume upload with text-first PDF extraction
- Optional job description text or file input for JD-aligned questioning
- Resume analysis and interview strategy planning
- 20 generated interview questions per set
- Difficulty distribution: 6 easy, 8 medium, 6 hard
- Simplified Chinese question and answer generation
- Reference answers hidden by default for practice
- User-written answers per question
- AI feedback on user-written answers
- Favorites and historical review
- Full interview set regeneration
- Single-question regeneration

## Text-First Resume Workflow

This project is intentionally text-first.

The system does **not** send PDF screenshots or page images to the LLM.

Default flow:

1. Upload PDF
2. Extract text locally with `pypdf`
3. Clean and normalize extracted text
4. Validate extraction quality
5. Send only plain text to the LLM
6. Execute LangGraph orchestration
7. Persist generated business data to PostgreSQL

## LangGraph Workflows

### Interview generation graph

The main `StateGraph` includes:

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

### Practice graphs

- Question regeneration graph
- Answer feedback graph

These keep generation and evaluation workflows explicit, inspectable, and maintainable.

## What I Want An Interviewer To Notice

1. I know how to decompose an LLM feature into explicit workflow stages with typed intermediate state.
2. I understand that agent systems need validation, repair, and fallback behavior, not just "call the model once".
3. I treat persistence, orchestration, and UI as separate layers with clear responsibilities.
4. I can turn agent workflows into a product that supports review, regeneration, and critique rather than one-shot output.

## Tech Stack

### Backend

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

### Frontend

- Next.js App Router
- TypeScript
- Tailwind CSS
- TanStack Query
- axios

### Infrastructure

- Docker
- docker compose

## Project Structure

```text
ai-interview-studio/
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

## Quick Start

### 1. Configure environment files

Copy:

- `backend/.env.example` -> `backend/.env`
- `frontend/.env.example` -> `frontend/.env`

Backend example:

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

Frontend example:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

### 2. Start with Docker

```bash
docker compose up --build
```

### 3. Access the app

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/api`
- FastAPI docs: `http://localhost:8000/docs`

## Selected API Endpoints

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

## Testing

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm install
npm test
```

## Security Notes

- Real secrets must stay in local `backend/.env` and `frontend/.env`
- `.env.example` files use placeholders only
- Generated business data is stored in PostgreSQL
- LangGraph is used for orchestration, not for business persistence

## License

This project is released under the [MIT License](./LICENSE).

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

An end-to-end AI interview practice platform that turns a PDF resume into a reviewable, persistent, programmer-focused mock interview experience.

This project is designed as a portfolio-quality full-stack application. It demonstrates local PDF text extraction, LangGraph-based orchestration, production-style FastAPI and PostgreSQL backend design, Next.js frontend implementation, Dockerized local development, persistent study workflows, and structured LLM feedback loops for practice.

## Preview

![AI Mock Interview Platform homepage](docs/images/github-homepage.png)

## Why This Project Is Strong for a Portfolio

- It is a full product, not a one-off script
- It combines backend engineering, frontend product UX, database design, LLM orchestration, and deployment workflow
- It uses LangGraph as a real orchestration layer instead of a plain function chain
- It stores business data persistently for history, favorites, user answers, and AI feedback
- It solves a realistic product problem: turning resumes into tailored practice material

## Product Overview

Users upload a PDF resume, the backend extracts text locally, validates text quality, and sends only cleaned plain text into a LangGraph workflow. The system analyzes the resume, plans an interview strategy, generates 20 programmer-focused interview questions across easy, medium, and hard difficulty levels, and writes reference answers in first-person candidate voice. Everything is persisted for later review and practice.

## Core Features

- JWT-based authentication
- Resume upload with text-first PDF extraction
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

## Quick Start

### 1. Configure environment files

Copy:

- `backend/.env.example` -> `backend/.env`
- `frontend/.env.example` -> `frontend/.env`

Backend example:

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

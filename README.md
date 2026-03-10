# AI Mock Interview Platform

A production-style MVP for interview practice with a programmer-focused workflow.

Users upload a PDF resume, the backend extracts resume text locally, LangGraph orchestrates resume analysis and interview generation, and the platform stores the generated interview sets for later review, favorites, answer writing, AI feedback, and regeneration.

## What This Project Does

- Registers and authenticates users with JWT
- Accepts PDF resumes and processes them with a text-first pipeline
- Generates 20 programmer-focused interview Q&A items in Simplified Chinese
- Stores interview history, favorites, user-written answers, and AI feedback in PostgreSQL
- Supports full interview set regeneration and single-question regeneration
- Provides a practice-oriented frontend with hidden reference answers

## Core Product Features

- User accounts
  - Register
  - Login
  - Current user profile
  - Per-user data isolation
- Resume upload and AI generation
  - PDF upload
  - Local text extraction with `pypdf`
  - Resume text cleaning and quality validation
  - Resume analysis and interview strategy planning
  - 20 generated questions with reference answers
- Practice workflow
  - Hide / reveal reference answers
  - Save your own answer for each question
  - Request structured AI feedback on your answer
  - Favorite meaningful questions
- Review and persistence
  - Interview set history
  - Full detail page for every generated set
  - Favorites page
  - Persistent question, answer, and feedback records
- Regeneration
  - Regenerate a whole interview set
  - Regenerate one question while preserving difficulty and position as much as possible

## Text-First Resume Processing

This project is explicitly text-first, not vision-first.

The system does **not** send PDF page images or screenshots to the LLM.

Default processing flow:

1. Upload PDF resume
2. Extract text locally with `pypdf`
3. Clean and normalize extracted text
4. Validate extraction quality
5. Send only plain text to the LLM
6. Run LangGraph generation workflow

This keeps the pipeline simpler, cheaper, more controllable, and easier to debug.

## LangGraph Workflows

### Main interview generation graph

The main `StateGraph` includes these nodes:

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
  - `prepare_regeneration_context`
  - `generate_replacement_question`
  - `finalize_replacement_question`
- Answer feedback graph
  - `prepare_feedback_context`
  - `evaluate_answer_feedback`
  - `finalize_answer_feedback`

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

## Architecture Overview

```text
ai-mock-interview-platform/
├─ backend/
│  ├─ app/
│  │  ├─ core/
│  │  ├─ graph/
│  │  ├─ models/
│  │  ├─ prompts/
│  │  ├─ routers/
│  │  ├─ schemas/
│  │  ├─ services/
│  │  ├─ utils/
│  │  ├─ config.py
│  │  ├─ db.py
│  │  └─ main.py
│  ├─ alembic/
│  ├─ tests/
│  ├─ Dockerfile
│  ├─ requirements.txt
│  └─ .env.example
├─ frontend/
│  ├─ app/
│  ├─ components/
│  ├─ lib/
│  ├─ types/
│  ├─ __tests__/
│  ├─ Dockerfile
│  ├─ package.json
│  └─ .env.example
├─ docker-compose.yml
└─ README.md
```

## Database Model Summary

Main business tables:

- `users`
- `resume_sessions`
- `question_sets`
- `questions`
- `favorites`
- `user_answers`
- `answer_feedback`

Important notes:

- `favorites` has a uniqueness constraint on `(user_id, question_id)`
- Generated business data is stored in PostgreSQL
- LangGraph is used for orchestration, not as the primary business persistence layer

## Environment Variables

### Backend

Copy `backend/.env.example` to `backend/.env` and fill in your own values.

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

### Frontend

Copy `frontend/.env.example` to `frontend/.env`.

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

## Run with Docker

From the project root:

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/api`
- FastAPI docs: `http://localhost:8000/docs`

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Database Migrations

Docker startup already runs:

```bash
alembic upgrade head
```

Manual migration:

```bash
cd backend
alembic upgrade head
```

## Main API Endpoints

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Health

- `GET /api/health`

### Interview sets

- `POST /api/interviews/generate`
- `GET /api/interviews`
- `GET /api/interviews/{id}`
- `POST /api/interviews/{id}/regenerate`

### Questions and practice

- `GET /api/questions/{id}`
- `POST /api/questions/{id}/favorite`
- `DELETE /api/questions/{id}/favorite`
- `GET /api/questions/{id}/my-answer`
- `POST /api/questions/{id}/my-answer`
- `PUT /api/questions/{id}/my-answer`
- `POST /api/questions/{id}/feedback`
- `POST /api/questions/{id}/regenerate`

### Favorites

- `GET /api/favorites`

## Example Requests

### Register

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"user@example.com\",\"password\":\"strongpass123\"}"
```

### Generate an interview set

```bash
curl -X POST http://localhost:8000/api/interviews/generate \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@./resume.pdf" \
  -F "target_role=backend engineer" \
  -F "interview_style=project-deep-dive"
```

### Save a user answer

```bash
curl -X POST http://localhost:8000/api/questions/31/my-answer \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d "{\"answer_text\":\"I would first clarify the target, then explain the interface boundary, failure handling, and observability plan.\"}"
```

### Request AI feedback

```bash
curl -X POST http://localhost:8000/api/questions/31/feedback \
  -H "Authorization: Bearer <TOKEN>"
```

### Regenerate one question

```bash
curl -X POST http://localhost:8000/api/questions/31/regenerate \
  -H "Authorization: Bearer <TOKEN>"
```

## Example Response Shape

Interview set detail responses include:

```json
{
  "id": 12,
  "title": "backend engineer mock interview set",
  "created_at": "2026-03-10T10:00:00Z",
  "meta": {
    "difficulty_breakdown": {
      "easy": 6,
      "medium": 8,
      "hard": 6
    },
    "total_questions": 20,
    "target_role": "backend engineer",
    "interview_style": "project-deep-dive"
  },
  "resume_summary": {
    "summary": "..."
  },
  "questions": [
    {
      "id": 101,
      "difficulty": "medium",
      "category": "backend development",
      "question": "...",
      "answer": "...",
      "intent": "...",
      "reference_from_resume": "...",
      "is_favorited": false,
      "my_answer": null,
      "feedback": null
    }
  ]
}
```

## Testing

### Backend

```bash
cd backend
pytest
```

Current backend coverage includes:

- Health endpoint
- Register / login
- Interview generation with mocked LLM
- Favorites
- User answer CRUD
- Feedback
- Regeneration
- Resume text extraction / cleaning / validation

### Frontend

```bash
cd frontend
npm install
npm test
```

## Developer Notes

- All final generated interview content is intended for Simplified Chinese output
- Reference answers stay in first-person candidate voice
- The frontend is designed for interview practice, not just content browsing
- PDF files are not stored long term, but generated interview data is persisted
- If generation is slow with your chosen provider, increase `OPENAI_TIMEOUT_SECONDS` or switch to a faster compatible model

## Security Notes

- Do not commit real values in `backend/.env` or `frontend/.env`
- Keep API keys only in local runtime env files
- `backend/.env.example` should always use placeholders, never live secrets

## License

Add your preferred license before publishing publicly.

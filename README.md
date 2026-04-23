# koreanVocab

A full-stack application to help improve Korean language vocabulary through
written and listening practice tests. Tests scale by experience level
(beginner / intermediate / advanced) and include multiple question types.

## Stack

- **Backend:** FastAPI (Python 3.12), SQLite, python-dotenv, OpenAI SDK (TTS)
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
- **Middleware:** FastAPI CORS middleware (plus a Vite dev proxy) bridges the
  React frontend (port `3005`) to the FastAPI backend (port `8000`).

## Features

- **Written module** — translate between English and Korean with multiple
  question types:
  - Korean → English multiple choice
  - English → Korean multiple choice
  - Korean → English free text
  - English → Korean free text (Hangul or romanization accepted)
- **Listening module** — plays audio of Korean words generated via the
  OpenAI TTS API; answer by typing the English meaning or by multiple choice.
- **Experience levels** — beginner, intermediate, advanced. Each level draws
  from its own curated vocabulary list.
- **Test generation** — configurable question count (5 / 10 / 20) and mix of
  question types.
- **Session history** — every test is saved to SQLite with per-question
  results so you can review progress later.

## Local setup

### Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/) (or `pip` — a `requirements.txt` is
  provided as a fallback)
- Node.js 20+ and `npm`

### 1. Configure the OpenAI API key

The backend loads the API key from `backend/.env`. Copy the example file and
fill in your key:

```bash
cp backend/.env.example backend/.env
# then edit backend/.env and set OPENAI_API_KEY=sk-...
```

`backend/.env` is gitignored. The listening module falls back to a
silent / disabled state if the key is missing, so written practice still
works without it.

### 2. Install and run the backend

```bash
cd backend
poetry install
poetry run fastapi dev app/main.py
```

The API will be available at <http://localhost:8000> (docs at
<http://localhost:8000/docs>).

### 3. Install and run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:3005>.

## Project layout

```
backend/
  app/
    main.py            # FastAPI routes
    models.py          # Pydantic request/response schemas
    database.py        # SQLite connection + schema
    vocab_data.py      # Seed vocabulary (by level + category)
    test_generator.py  # Builds tests from the vocab pool
    openai_client.py   # OpenAI TTS wrapper
  pyproject.toml
  .env.example
frontend/
  src/
    App.tsx            # Top-level view-state router
    api.ts             # Typed client for the FastAPI backend
    types.ts           # Shared TypeScript types
    components/        # Home, TestSetup, WrittenTest, ListeningTest, Results
  package.json
  vite.config.ts
```

## API overview

| Method | Path                          | Description                           |
|--------|-------------------------------|---------------------------------------|
| GET    | `/healthz`                    | Health check                          |
| GET    | `/vocab/levels`               | List experience levels + counts       |
| POST   | `/tests`                      | Create a new test                     |
| GET    | `/tests`                      | List past tests                       |
| GET    | `/tests/{id}`                 | Fetch a test with questions           |
| POST   | `/tests/{id}/submit`          | Submit answers, get graded results    |
| DELETE | `/tests/{id}`                 | Delete a test from history            |
| GET    | `/tts?text=...&voice=...`     | Proxy OpenAI TTS (MP3 stream)         |

All endpoints return JSON except `/tts` which streams `audio/mpeg`.

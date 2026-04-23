# koreanVocab backend

FastAPI + SQLite backend for the Korean vocabulary practice app.

See the top-level [README](../README.md) for full setup instructions.

Quick start:

```bash
cp .env.example .env  # set OPENAI_API_KEY
poetry install
poetry run fastapi dev app/main.py
```

API runs on <http://localhost:8000>, OpenAPI docs at `/docs`.

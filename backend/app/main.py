"""FastAPI application for the Korean vocabulary practice app.

Routes:
    GET    /healthz                      Health check.
    GET    /vocab/levels                 Summary of available levels.
    POST   /tests                        Create a new test.
    GET    /tests                        List past tests.
    GET    /tests/{test_id}              Fetch a test with questions.
    POST   /tests/{test_id}/submit       Grade answers and save results.
    DELETE /tests/{test_id}              Delete a test from history.
    GET    /tts                          OpenAI TTS proxy (MP3 stream).

CORS middleware is wired up so the Vite dev server (http://localhost:3005)
can talk to the backend during local development.
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from openai import OpenAIError

from app.database import get_db, init_db
from app.models import (
    AnswerSubmit,
    LevelSummary,
    Question,
    TestCreate,
    TestResponse,
    TestSubmit,
    TestSummary,
)
from app.openai_client import generate_tts_audio, is_configured as openai_is_configured
from app.test_generator import (
    GeneratedQuestion,
    generate_questions,
    grade_answer,
    normalize_answer,
)
from app.vocab_data import LEVELS

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="Korean Vocab API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------- health & meta


@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    return {"status": "ok", "openai_configured": openai_is_configured()}


@app.get("/vocab/levels", response_model=list[LevelSummary])
async def list_levels() -> list[LevelSummary]:
    """Return per-level word counts and the set of categories available."""
    with get_db() as conn:
        summaries: list[LevelSummary] = []
        for level in LEVELS:
            rows = conn.execute(
                "SELECT category FROM vocab WHERE level = ?", (level,)
            ).fetchall()
            categories = sorted({row["category"] for row in rows})
            summaries.append(
                LevelSummary(level=level, word_count=len(rows), categories=categories)
            )
        return summaries


# ------------------------------------------------------------------------ tests


@app.post("/tests", response_model=TestResponse)
async def create_test(payload: TestCreate) -> TestResponse:
    if payload.mode == "listening" and not openai_is_configured():
        raise HTTPException(
            status_code=503,
            detail=(
                "Listening mode requires the OPENAI_API_KEY to be set in "
                "backend/.env. Written mode works without it."
            ),
        )

    with get_db() as conn:
        try:
            questions = generate_questions(
                conn,
                level=payload.level,
                mode=payload.mode,
                num_questions=payload.num_questions,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        cursor = conn.execute(
            "INSERT INTO tests (level, mode, num_questions, total) VALUES (?, ?, ?, ?)",
            (payload.level, payload.mode, payload.num_questions, payload.num_questions),
        )
        test_id = cursor.lastrowid

        for position, q in enumerate(questions, start=1):
            conn.execute(
                """
                INSERT INTO questions
                    (test_id, position, question_type, vocab_id,
                     prompt, correct_answer, options_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    test_id,
                    position,
                    q.question_type,
                    q.vocab_id,
                    q.prompt,
                    q.correct_answer,
                    q.options_json(),
                ),
            )

        return _load_test(conn, test_id, reveal_answers=False)


@app.get("/tests", response_model=list[TestSummary])
async def list_tests() -> list[TestSummary]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, created_at, completed_at, level, mode, num_questions, "
            "score, total FROM tests ORDER BY id DESC"
        ).fetchall()
        return [
            TestSummary(
                id=row["id"],
                created_at=row["created_at"],
                completed_at=row["completed_at"],
                level=row["level"],
                mode=row["mode"],
                num_questions=row["num_questions"],
                score=row["score"],
                total=row["total"],
            )
            for row in rows
        ]


@app.get("/tests/{test_id}", response_model=TestResponse)
async def get_test(test_id: int) -> TestResponse:
    with get_db() as conn:
        test_row = conn.execute(
            "SELECT completed_at FROM tests WHERE id = ?", (test_id,)
        ).fetchone()
        if test_row is None:
            raise HTTPException(status_code=404, detail="Test not found")
        reveal = test_row["completed_at"] is not None
        return _load_test(conn, test_id, reveal_answers=reveal)


@app.post("/tests/{test_id}/submit", response_model=TestResponse)
async def submit_test(test_id: int, payload: TestSubmit) -> TestResponse:
    with get_db() as conn:
        test_row = conn.execute(
            "SELECT id, completed_at FROM tests WHERE id = ?", (test_id,)
        ).fetchone()
        if test_row is None:
            raise HTTPException(status_code=404, detail="Test not found")
        if test_row["completed_at"] is not None:
            raise HTTPException(
                status_code=400, detail="Test has already been submitted"
            )

        answers_by_qid: dict[int, str] = {a.question_id: a.answer for a in payload.answers}

        question_rows = conn.execute(
            """
            SELECT q.id, q.question_type, q.correct_answer, q.vocab_id,
                   v.english, v.korean, v.romanization
            FROM questions q
            JOIN vocab v ON q.vocab_id = v.id
            WHERE q.test_id = ?
            """,
            (test_id,),
        ).fetchall()

        score = 0
        for q in question_rows:
            user_answer = answers_by_qid.get(q["id"], "")
            is_correct = grade_answer(
                q["question_type"], user_answer, q["correct_answer"], q
            )
            conn.execute(
                "UPDATE questions SET user_answer = ?, is_correct = ? WHERE id = ?",
                (user_answer, 1 if is_correct else 0, q["id"]),
            )
            if is_correct:
                score += 1

        conn.execute(
            "UPDATE tests SET score = ?, completed_at = datetime('now') WHERE id = ?",
            (score, test_id),
        )

        return _load_test(conn, test_id, reveal_answers=True)


@app.delete("/tests/{test_id}")
async def delete_test(test_id: int) -> dict[str, Any]:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM tests WHERE id = ?", (test_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Test not found")
        return {"deleted": test_id}


# -------------------------------------------------------------------------- tts


@app.get("/tts")
async def tts(
    text: str = Query(..., min_length=1, max_length=200),
    voice: str | None = Query(None),
) -> Response:
    """Synthesize Korean text to MP3 audio via OpenAI."""
    if not openai_is_configured():
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key is not configured (set OPENAI_API_KEY in backend/.env).",
        )
    try:
        audio = await asyncio.to_thread(generate_tts_audio, text, voice)
    except OpenAIError as exc:
        logger.warning("OpenAI TTS failed: %s", exc)
        raise HTTPException(status_code=502, detail="OpenAI TTS request failed") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return Response(content=audio, media_type="audio/mpeg")


# ------------------------------------------------------------------------ utils


def _load_test(conn: Any, test_id: int, *, reveal_answers: bool) -> TestResponse:
    test_row = conn.execute(
        "SELECT id, created_at, completed_at, level, mode, num_questions, score, total "
        "FROM tests WHERE id = ?",
        (test_id,),
    ).fetchone()
    if test_row is None:
        raise HTTPException(status_code=404, detail="Test not found")

    q_rows = conn.execute(
        """
        SELECT q.id, q.position, q.question_type, q.prompt, q.options_json,
               q.correct_answer, q.user_answer, q.is_correct,
               v.korean AS audio_text
        FROM questions q
        JOIN vocab v ON q.vocab_id = v.id
        WHERE q.test_id = ?
        ORDER BY q.position
        """,
        (test_id,),
    ).fetchall()

    questions: list[Question] = []
    for row in q_rows:
        options = json.loads(row["options_json"]) if row["options_json"] else None
        is_listening = row["question_type"].startswith("listening_")
        questions.append(
            Question(
                id=row["id"],
                position=row["position"],
                question_type=row["question_type"],
                prompt=row["prompt"],
                options=options,
                audio_text=row["audio_text"] if is_listening else None,
                correct_answer=row["correct_answer"] if reveal_answers else None,
                user_answer=row["user_answer"] if reveal_answers else None,
                is_correct=(
                    bool(row["is_correct"])
                    if reveal_answers and row["is_correct"] is not None
                    else None
                ),
            )
        )

    return TestResponse(
        id=test_row["id"],
        created_at=test_row["created_at"],
        completed_at=test_row["completed_at"],
        level=test_row["level"],
        mode=test_row["mode"],
        num_questions=test_row["num_questions"],
        score=test_row["score"],
        total=test_row["total"],
        questions=questions,
    )


# Expose helpers for tests / future callers.
__all__ = [
    "app",
    "normalize_answer",
    "GeneratedQuestion",
    "AnswerSubmit",
]

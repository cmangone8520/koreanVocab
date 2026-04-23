"""Pydantic request / response schemas for the Korean vocab API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Level = Literal["beginner", "intermediate", "advanced"]
Mode = Literal["written", "listening", "mixed"]
# Where the target vocabulary came from for a given test.
VocabSource = Literal["openai", "static", "static_fallback"]
QuestionType = Literal[
    "kr_to_en_multiple_choice",
    "en_to_kr_multiple_choice",
    "kr_to_en_free_text",
    "en_to_kr_free_text",
    "listening_multiple_choice",
    "listening_free_text",
]


class LevelSummary(BaseModel):
    level: Level
    word_count: int
    categories: list[str]


class VocabItem(BaseModel):
    id: int
    korean: str
    romanization: str
    english: str
    level: Level
    category: str


class TestCreate(BaseModel):
    level: Level
    mode: Mode = "written"
    num_questions: int = Field(default=10, ge=1, le=50)
    # When true (default) and OPENAI_API_KEY is configured, ask OpenAI for
    # fresh vocabulary. Falls back to the static seed pool on any error.
    use_openai_vocab: bool = True


class Question(BaseModel):
    id: int
    position: int
    question_type: QuestionType
    prompt: str
    options: list[str] | None = None
    # Included with the prompt so the frontend can trigger audio for
    # listening questions without a second round-trip.
    audio_text: str | None = None
    # Graded fields, populated only after submission.
    correct_answer: str | None = None
    user_answer: str | None = None
    is_correct: bool | None = None


class TestResponse(BaseModel):
    id: int
    created_at: str
    completed_at: str | None = None
    level: Level
    mode: Mode
    num_questions: int
    score: int | None = None
    total: int | None = None
    questions: list[Question]
    # Where the vocabulary for this test came from.
    vocab_source: VocabSource = "static"
    # Populated when OpenAI generation was requested but failed; the test
    # fell back to the static pool and the frontend should surface this.
    vocab_source_error: str | None = None


class TestSummary(BaseModel):
    id: int
    created_at: str
    completed_at: str | None = None
    level: Level
    mode: Mode
    num_questions: int
    score: int | None = None
    total: int | None = None
    vocab_source: VocabSource = "static"


class AnswerSubmit(BaseModel):
    question_id: int
    answer: str


class TestSubmit(BaseModel):
    answers: list[AnswerSubmit]

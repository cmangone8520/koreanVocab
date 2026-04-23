"""Build practice tests from the SQLite vocab pool.

A test is a list of questions; each question has a ``question_type`` that
determines how the prompt, options, and correct answer are rendered.
"""

from __future__ import annotations

import json
import random
import sqlite3
from dataclasses import dataclass
from typing import Literal

QuestionType = Literal[
    "kr_to_en_multiple_choice",
    "en_to_kr_multiple_choice",
    "kr_to_en_free_text",
    "en_to_kr_free_text",
    "listening_multiple_choice",
    "listening_free_text",
]


@dataclass
class GeneratedQuestion:
    """A question ready to insert into the ``questions`` table."""

    question_type: QuestionType
    vocab_id: int
    prompt: str
    correct_answer: str
    options: list[str] | None
    audio_text: str | None  # Korean word to synthesize for listening questions

    def options_json(self) -> str | None:
        return json.dumps(self.options, ensure_ascii=False) if self.options else None


# Question-type pools per mode.
_WRITTEN_TYPES: tuple[QuestionType, ...] = (
    "kr_to_en_multiple_choice",
    "en_to_kr_multiple_choice",
    "kr_to_en_free_text",
    "en_to_kr_free_text",
)
_LISTENING_TYPES: tuple[QuestionType, ...] = (
    "listening_multiple_choice",
    "listening_free_text",
)


def _types_for_mode(mode: str) -> tuple[QuestionType, ...]:
    if mode == "written":
        return _WRITTEN_TYPES
    if mode == "listening":
        return _LISTENING_TYPES
    return _WRITTEN_TYPES + _LISTENING_TYPES


def _canonical_english(english: str) -> str:
    """Return the first, canonical English meaning (before the first comma)."""
    return english.split(",", 1)[0].strip()


def _pick_distractors(
    rows: list[sqlite3.Row],
    answer_field: str,
    correct_row: sqlite3.Row,
    n: int = 3,
) -> list[str]:
    """Pick ``n`` distinct distractor values from ``rows`` avoiding the answer."""
    correct_value = (
        _canonical_english(correct_row[answer_field])
        if answer_field == "english"
        else correct_row[answer_field]
    )
    pool: list[str] = []
    seen: set[str] = {correct_value}
    shuffled = list(rows)
    random.shuffle(shuffled)
    for row in shuffled:
        if row["id"] == correct_row["id"]:
            continue
        value = (
            _canonical_english(row[answer_field])
            if answer_field == "english"
            else row[answer_field]
        )
        if value in seen:
            continue
        seen.add(value)
        pool.append(value)
        if len(pool) >= n:
            break
    return pool


def _build_question(
    q_type: QuestionType,
    row: sqlite3.Row,
    level_rows: list[sqlite3.Row],
) -> GeneratedQuestion:
    korean: str = row["korean"]
    english_canonical = _canonical_english(row["english"])

    if q_type == "kr_to_en_multiple_choice":
        options = _pick_distractors(level_rows, "english", row) + [english_canonical]
        random.shuffle(options)
        return GeneratedQuestion(
            question_type=q_type,
            vocab_id=row["id"],
            prompt=f"What does “{korean}” mean in English?",
            correct_answer=english_canonical,
            options=options,
            audio_text=None,
        )

    if q_type == "en_to_kr_multiple_choice":
        options = _pick_distractors(level_rows, "korean", row) + [korean]
        random.shuffle(options)
        return GeneratedQuestion(
            question_type=q_type,
            vocab_id=row["id"],
            prompt=f'Which Korean word means "{english_canonical}"?',
            correct_answer=korean,
            options=options,
            audio_text=None,
        )

    if q_type == "kr_to_en_free_text":
        return GeneratedQuestion(
            question_type=q_type,
            vocab_id=row["id"],
            prompt=f"Translate to English: {korean}",
            correct_answer=english_canonical,
            options=None,
            audio_text=None,
        )

    if q_type == "en_to_kr_free_text":
        return GeneratedQuestion(
            question_type=q_type,
            vocab_id=row["id"],
            prompt=f'Translate to Korean (Hangul or romanization): "{english_canonical}"',
            correct_answer=korean,
            options=None,
            audio_text=None,
        )

    if q_type == "listening_multiple_choice":
        options = _pick_distractors(level_rows, "english", row) + [english_canonical]
        random.shuffle(options)
        return GeneratedQuestion(
            question_type=q_type,
            vocab_id=row["id"],
            prompt="Listen and choose the correct English meaning.",
            correct_answer=english_canonical,
            options=options,
            audio_text=korean,
        )

    if q_type == "listening_free_text":
        return GeneratedQuestion(
            question_type=q_type,
            vocab_id=row["id"],
            prompt="Listen and type the English meaning.",
            correct_answer=english_canonical,
            options=None,
            audio_text=korean,
        )

    # Should be unreachable.
    raise ValueError(f"Unknown question type: {q_type}")


def build_questions_from_rows(
    target_rows: list[sqlite3.Row],
    distractor_pool: list[sqlite3.Row],
    mode: str,
    num_questions: int,
) -> list[GeneratedQuestion]:
    """Build ``num_questions`` questions drawing targets from ``target_rows``.

    Distractors for multiple-choice questions are picked from
    ``distractor_pool``, which should include ``target_rows`` plus any
    additional same-level vocab so wrong options look plausible.
    """
    if not target_rows:
        raise ValueError("No vocabulary rows available to build a test")

    # Sample without replacement; if the user asks for more questions than
    # there are words, allow repeats but shuffle between rounds.
    words: list[sqlite3.Row] = []
    pool = target_rows[:]
    while len(words) < num_questions:
        random.shuffle(pool)
        take = min(num_questions - len(words), len(pool))
        words.extend(pool[:take])

    types = _types_for_mode(mode)
    questions: list[GeneratedQuestion] = []
    for row in words:
        q_type = random.choice(types)
        questions.append(_build_question(q_type, row, distractor_pool))
    return questions


def generate_questions(
    conn: sqlite3.Connection,
    level: str,
    mode: str,
    num_questions: int,
) -> list[GeneratedQuestion]:
    """Generate ``num_questions`` questions from the static level pool."""
    rows: list[sqlite3.Row] = list(
        conn.execute(
            "SELECT id, korean, romanization, english, level, category "
            "FROM vocab WHERE level = ?",
            (level,),
        )
    )
    if not rows:
        raise ValueError(f"No vocabulary found for level '{level}'")
    return build_questions_from_rows(rows, rows, mode, num_questions)


def normalize_answer(s: str) -> str:
    """Case-fold, collapse whitespace, strip punctuation for comparison."""
    import re as _re

    s = s.strip().lower()
    s = _re.sub(r"[\s\u200b]+", " ", s)
    s = _re.sub(r"[.,!?;:'\"()\[\]{}]", "", s)
    return s


def grade_answer(
    q_type: QuestionType,
    user_answer: str,
    correct_answer: str,
    vocab_row: sqlite3.Row,
) -> bool:
    """Grade a single answer.

    - For English targets, any of the comma-separated meanings are accepted.
    - For Korean targets (free text), either the Hangul or the romanization
      is accepted.
    - Multiple-choice comparisons are exact (after normalization).
    """
    user_norm = normalize_answer(user_answer)
    if not user_norm:
        return False

    if q_type in ("kr_to_en_multiple_choice", "en_to_kr_multiple_choice", "listening_multiple_choice"):
        return user_norm == normalize_answer(correct_answer)

    if q_type in ("kr_to_en_free_text", "listening_free_text"):
        accepted = {
            normalize_answer(meaning)
            for meaning in vocab_row["english"].split(",")
        }
        return user_norm in accepted

    if q_type == "en_to_kr_free_text":
        accepted = {
            normalize_answer(vocab_row["korean"]),
            normalize_answer(vocab_row["romanization"]),
        }
        return user_norm in accepted

    return False

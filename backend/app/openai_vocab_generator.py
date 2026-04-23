"""OpenAI-backed generator of random Korean vocabulary for practice tests.

Given a level and a count, asks a chat model to return a JSON list of
distinct Korean words with romanization, English meaning(s), and a
short category tag. The caller is responsible for inserting the rows
into the ``vocab`` table and falling back to the static pool on error.
"""

from __future__ import annotations

import json
import logging
import os
from typing import TypedDict

from openai import OpenAIError

from app.openai_client import _get_client

logger = logging.getLogger(__name__)


class VocabItem(TypedDict):
    korean: str
    romanization: str
    english: str
    category: str


class OpenAIVocabError(RuntimeError):
    """Raised when the OpenAI vocab generator cannot return a valid payload."""


_LEVEL_GUIDANCE = {
    "beginner": (
        "Essential everyday Korean: greetings, numbers, family, common foods, "
        "basic verbs (to eat, to go, to see), basic adjectives, pronouns, and "
        "common household objects. Avoid rare or idiomatic words."
    ),
    "intermediate": (
        "Workplace, school, weather, travel, directions, feelings, time "
        "expressions, and common verbs/adjectives beyond the absolute basics. "
        "Avoid very specialized or technical vocabulary."
    ),
    "advanced": (
        "Nuanced and abstract Korean: business, society, technology, culture, "
        "politics, psychology, and less common verbs/adjectives. Include "
        "idiomatic or formal vocabulary where appropriate."
    ),
}


def _model() -> str:
    return os.getenv("OPENAI_VOCAB_MODEL", "gpt-4o-mini")


def _build_prompt(level: str, count: int) -> str:
    guidance = _LEVEL_GUIDANCE.get(level, _LEVEL_GUIDANCE["beginner"])
    return (
        f"You are generating a Korean vocabulary practice set for a "
        f"{level}-level learner.\n\n"
        f"Level guidance: {guidance}\n\n"
        f"Return EXACTLY {count} DISTINCT Korean vocabulary words. No duplicates, "
        f"no repetition of the same lemma in different forms. Every word must be "
        f"appropriate for the {level} level.\n\n"
        "Respond with a single JSON object with this schema and no prose:\n"
        "{\n"
        '  "words": [\n'
        "    {\n"
        '      "korean": "Hangul form of the word",\n'
        '      "romanization": "Revised Romanization (lowercase, no tone marks), '
        'e.g. \'annyeonghaseyo\'",\n'
        '      "english": "one or more English meanings, comma-separated if more '
        'than one, most common meaning first",\n'
        '      "category": "short lowercase tag like \'verbs\', \'numbers\', '
        "'food', 'family', 'work', 'weather'\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )


def _clean_item(raw: object) -> VocabItem | None:
    if not isinstance(raw, dict):
        return None
    korean = str(raw.get("korean", "")).strip()
    romanization = str(raw.get("romanization", "")).strip().lower()
    english = str(raw.get("english", "")).strip()
    category = str(raw.get("category", "")).strip().lower() or "general"
    if not korean or not romanization or not english:
        return None
    return VocabItem(
        korean=korean,
        romanization=romanization,
        english=english,
        category=category,
    )


def generate_vocab_items(level: str, count: int) -> list[VocabItem]:
    """Ask OpenAI for ``count`` distinct vocab items at ``level``.

    Raises:
        OpenAIVocabError: if the key is not configured, the call fails, or
            the response cannot be parsed into at least one valid item.
    """
    if level not in _LEVEL_GUIDANCE:
        raise OpenAIVocabError(f"Unknown level: {level}")
    if count < 1:
        raise OpenAIVocabError("count must be >= 1")

    client = _get_client()
    if client is None:
        raise OpenAIVocabError("OPENAI_API_KEY is not configured")

    prompt = _build_prompt(level, count)

    try:
        response = client.chat.completions.create(
            model=_model(),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Korean language tutor. Produce accurate "
                        "Korean vocabulary with Revised Romanization and natural "
                        "English translations. Always reply with valid JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
    except OpenAIError as exc:
        logger.warning("OpenAI vocab generation failed: %s", exc)
        raise OpenAIVocabError(str(exc)) from exc

    content = response.choices[0].message.content if response.choices else None
    if not content:
        raise OpenAIVocabError("empty response from OpenAI")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise OpenAIVocabError(f"invalid JSON from OpenAI: {exc}") from exc

    raw_words = parsed.get("words") if isinstance(parsed, dict) else None
    if not isinstance(raw_words, list):
        raise OpenAIVocabError("response missing 'words' array")

    items: list[VocabItem] = []
    seen_korean: set[str] = set()
    for raw in raw_words:
        item = _clean_item(raw)
        if item is None:
            continue
        if item["korean"] in seen_korean:
            continue
        seen_korean.add(item["korean"])
        items.append(item)

    if not items:
        raise OpenAIVocabError("no valid vocabulary items returned")

    return items

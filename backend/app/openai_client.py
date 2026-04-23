"""OpenAI integration for the listening module (Text-to-Speech).

The API key is loaded from ``backend/.env`` via :mod:`python-dotenv`.
If the key is missing the TTS endpoint returns a 503 so the frontend can
gracefully disable the listening module.
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)

# Load backend/.env regardless of the CWD.
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

_client: OpenAI | None = None

# OpenAI TTS supports these voices as of 2024+ (see docs).
_VALID_VOICES = {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}


def _default_voice() -> str:
    voice = os.getenv("OPENAI_TTS_VOICE", "nova").strip().lower()
    return voice if voice in _VALID_VOICES else "nova"


def _get_client() -> OpenAI | None:
    """Return a cached OpenAI client, or None if the key is not configured."""
    global _client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    if _client is None:
        _client = OpenAI(api_key=api_key)
    return _client


def is_configured() -> bool:
    """True if an OpenAI API key has been provided in the environment."""
    return bool(os.getenv("OPENAI_API_KEY"))


def generate_tts_audio(text: str, voice: str | None = None) -> bytes:
    """Synthesize ``text`` as MP3 audio bytes using OpenAI TTS.

    Raises:
        RuntimeError: if the API key is not configured.
        OpenAIError: if the OpenAI API call fails.
    """
    client = _get_client()
    if client is None:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured. Set it in backend/.env."
        )

    selected_voice = (voice or _default_voice()).strip().lower()
    if selected_voice not in _VALID_VOICES:
        selected_voice = _default_voice()

    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=selected_voice,
            input=text,
            response_format="mp3",
        )
    except OpenAIError:
        logger.exception("OpenAI TTS request failed")
        raise

    # Prefer the streaming iterator if available; fall back to .content.
    if hasattr(response, "iter_bytes"):
        return b"".join(response.iter_bytes())
    return response.read() if hasattr(response, "read") else response.content  # type: ignore[no-any-return]

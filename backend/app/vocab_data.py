"""Seed Korean vocabulary dataset.

Each entry has:
  - ``korean``: Hangul spelling of the word
  - ``romanization``: Revised Romanization spelling (accepted as an
    alternative answer for Korean free-text questions)
  - ``english``: English meaning(s); the first form is the canonical answer,
    additional comma-separated forms are all accepted when grading.
  - ``level``: ``"beginner"``, ``"intermediate"``, or ``"advanced"``
  - ``category``: free-form label (numbers, greetings, food, verbs, ...)

The dataset is intentionally hand-curated and small enough to load into
memory. The database is seeded from this list on startup (see
:func:`app.database.seed_vocab`) so test generation can run purely against
SQLite.
"""

from __future__ import annotations

from typing import TypedDict


class VocabEntry(TypedDict):
    korean: str
    romanization: str
    english: str
    level: str
    category: str


VOCAB: list[VocabEntry] = [
    # ---------------------------------------------------------------- beginner
    {"korean": "안녕하세요", "romanization": "annyeonghaseyo", "english": "hello", "level": "beginner", "category": "greetings"},
    {"korean": "안녕히 가세요", "romanization": "annyeonghi gaseyo", "english": "goodbye (to someone leaving)", "level": "beginner", "category": "greetings"},
    {"korean": "감사합니다", "romanization": "gamsahamnida", "english": "thank you", "level": "beginner", "category": "greetings"},
    {"korean": "죄송합니다", "romanization": "joesonghamnida", "english": "sorry, excuse me", "level": "beginner", "category": "greetings"},
    {"korean": "네", "romanization": "ne", "english": "yes", "level": "beginner", "category": "basics"},
    {"korean": "아니요", "romanization": "aniyo", "english": "no", "level": "beginner", "category": "basics"},
    {"korean": "물", "romanization": "mul", "english": "water", "level": "beginner", "category": "food"},
    {"korean": "밥", "romanization": "bap", "english": "rice, meal", "level": "beginner", "category": "food"},
    {"korean": "김치", "romanization": "gimchi", "english": "kimchi", "level": "beginner", "category": "food"},
    {"korean": "사과", "romanization": "sagwa", "english": "apple", "level": "beginner", "category": "food"},
    {"korean": "집", "romanization": "jip", "english": "house, home", "level": "beginner", "category": "places"},
    {"korean": "학교", "romanization": "hakgyo", "english": "school", "level": "beginner", "category": "places"},
    {"korean": "책", "romanization": "chaek", "english": "book", "level": "beginner", "category": "objects"},
    {"korean": "친구", "romanization": "chingu", "english": "friend", "level": "beginner", "category": "people"},
    {"korean": "가족", "romanization": "gajok", "english": "family", "level": "beginner", "category": "people"},
    {"korean": "엄마", "romanization": "eomma", "english": "mom, mother", "level": "beginner", "category": "people"},
    {"korean": "아빠", "romanization": "appa", "english": "dad, father", "level": "beginner", "category": "people"},
    {"korean": "하나", "romanization": "hana", "english": "one", "level": "beginner", "category": "numbers"},
    {"korean": "둘", "romanization": "dul", "english": "two", "level": "beginner", "category": "numbers"},
    {"korean": "셋", "romanization": "set", "english": "three", "level": "beginner", "category": "numbers"},
    {"korean": "넷", "romanization": "net", "english": "four", "level": "beginner", "category": "numbers"},
    {"korean": "다섯", "romanization": "daseot", "english": "five", "level": "beginner", "category": "numbers"},
    {"korean": "오늘", "romanization": "oneul", "english": "today", "level": "beginner", "category": "time"},
    {"korean": "내일", "romanization": "naeil", "english": "tomorrow", "level": "beginner", "category": "time"},
    {"korean": "어제", "romanization": "eoje", "english": "yesterday", "level": "beginner", "category": "time"},
    {"korean": "지금", "romanization": "jigeum", "english": "now", "level": "beginner", "category": "time"},
    {"korean": "좋아요", "romanization": "joayo", "english": "good, I like it", "level": "beginner", "category": "adjectives"},
    {"korean": "나쁘다", "romanization": "nappeuda", "english": "bad", "level": "beginner", "category": "adjectives"},
    {"korean": "크다", "romanization": "keuda", "english": "big, to be big", "level": "beginner", "category": "adjectives"},
    {"korean": "작다", "romanization": "jakda", "english": "small, to be small", "level": "beginner", "category": "adjectives"},
    {"korean": "가다", "romanization": "gada", "english": "to go", "level": "beginner", "category": "verbs"},
    {"korean": "오다", "romanization": "oda", "english": "to come", "level": "beginner", "category": "verbs"},
    {"korean": "먹다", "romanization": "meokda", "english": "to eat", "level": "beginner", "category": "verbs"},
    {"korean": "마시다", "romanization": "masida", "english": "to drink", "level": "beginner", "category": "verbs"},
    {"korean": "보다", "romanization": "boda", "english": "to see, to watch", "level": "beginner", "category": "verbs"},
    # ------------------------------------------------------------ intermediate
    {"korean": "회사", "romanization": "hoesa", "english": "company", "level": "intermediate", "category": "work"},
    {"korean": "직장", "romanization": "jikjang", "english": "workplace, job", "level": "intermediate", "category": "work"},
    {"korean": "회의", "romanization": "hoeui", "english": "meeting", "level": "intermediate", "category": "work"},
    {"korean": "여행", "romanization": "yeohaeng", "english": "travel, trip", "level": "intermediate", "category": "travel"},
    {"korean": "공항", "romanization": "gonghang", "english": "airport", "level": "intermediate", "category": "travel"},
    {"korean": "기차", "romanization": "gicha", "english": "train", "level": "intermediate", "category": "travel"},
    {"korean": "지하철", "romanization": "jihacheol", "english": "subway", "level": "intermediate", "category": "travel"},
    {"korean": "시장", "romanization": "sijang", "english": "market", "level": "intermediate", "category": "places"},
    {"korean": "식당", "romanization": "sikdang", "english": "restaurant", "level": "intermediate", "category": "places"},
    {"korean": "병원", "romanization": "byeongwon", "english": "hospital", "level": "intermediate", "category": "places"},
    {"korean": "약국", "romanization": "yakguk", "english": "pharmacy", "level": "intermediate", "category": "places"},
    {"korean": "생각하다", "romanization": "saenggakhada", "english": "to think", "level": "intermediate", "category": "verbs"},
    {"korean": "말하다", "romanization": "malhada", "english": "to speak, to say", "level": "intermediate", "category": "verbs"},
    {"korean": "듣다", "romanization": "deutda", "english": "to listen, to hear", "level": "intermediate", "category": "verbs"},
    {"korean": "읽다", "romanization": "ilkda", "english": "to read", "level": "intermediate", "category": "verbs"},
    {"korean": "쓰다", "romanization": "sseuda", "english": "to write, to use", "level": "intermediate", "category": "verbs"},
    {"korean": "배우다", "romanization": "baeuda", "english": "to learn", "level": "intermediate", "category": "verbs"},
    {"korean": "가르치다", "romanization": "gareuchida", "english": "to teach", "level": "intermediate", "category": "verbs"},
    {"korean": "일하다", "romanization": "ilhada", "english": "to work", "level": "intermediate", "category": "verbs"},
    {"korean": "쉬다", "romanization": "swida", "english": "to rest", "level": "intermediate", "category": "verbs"},
    {"korean": "기다리다", "romanization": "gidarida", "english": "to wait", "level": "intermediate", "category": "verbs"},
    {"korean": "바쁘다", "romanization": "bappeuda", "english": "busy, to be busy", "level": "intermediate", "category": "adjectives"},
    {"korean": "피곤하다", "romanization": "pigonhada", "english": "tired, to be tired", "level": "intermediate", "category": "adjectives"},
    {"korean": "재미있다", "romanization": "jaemiitda", "english": "fun, interesting", "level": "intermediate", "category": "adjectives"},
    {"korean": "어렵다", "romanization": "eoryeopda", "english": "difficult", "level": "intermediate", "category": "adjectives"},
    {"korean": "쉽다", "romanization": "swipda", "english": "easy", "level": "intermediate", "category": "adjectives"},
    {"korean": "날씨", "romanization": "nalssi", "english": "weather", "level": "intermediate", "category": "weather"},
    {"korean": "비", "romanization": "bi", "english": "rain", "level": "intermediate", "category": "weather"},
    {"korean": "눈", "romanization": "nun", "english": "snow, eye", "level": "intermediate", "category": "weather"},
    {"korean": "바람", "romanization": "baram", "english": "wind", "level": "intermediate", "category": "weather"},
    {"korean": "음악", "romanization": "eumak", "english": "music", "level": "intermediate", "category": "culture"},
    {"korean": "영화", "romanization": "yeonghwa", "english": "movie, film", "level": "intermediate", "category": "culture"},
    {"korean": "운동", "romanization": "undong", "english": "exercise, sports", "level": "intermediate", "category": "activities"},
    {"korean": "요리", "romanization": "yori", "english": "cooking, cuisine", "level": "intermediate", "category": "activities"},
    {"korean": "여권", "romanization": "yeogwon", "english": "passport", "level": "intermediate", "category": "travel"},
    # ---------------------------------------------------------------- advanced
    {"korean": "경제", "romanization": "gyeongje", "english": "economy", "level": "advanced", "category": "business"},
    {"korean": "정치", "romanization": "jeongchi", "english": "politics", "level": "advanced", "category": "society"},
    {"korean": "사회", "romanization": "sahoe", "english": "society", "level": "advanced", "category": "society"},
    {"korean": "환경", "romanization": "hwangyeong", "english": "environment", "level": "advanced", "category": "society"},
    {"korean": "기술", "romanization": "gisul", "english": "technology, skill", "level": "advanced", "category": "technology"},
    {"korean": "인공지능", "romanization": "ingongjineung", "english": "artificial intelligence", "level": "advanced", "category": "technology"},
    {"korean": "개발하다", "romanization": "gaebalhada", "english": "to develop", "level": "advanced", "category": "verbs"},
    {"korean": "연구하다", "romanization": "yeonguhada", "english": "to research", "level": "advanced", "category": "verbs"},
    {"korean": "분석하다", "romanization": "bunseokhada", "english": "to analyze", "level": "advanced", "category": "verbs"},
    {"korean": "설명하다", "romanization": "seolmyeonghada", "english": "to explain", "level": "advanced", "category": "verbs"},
    {"korean": "설득하다", "romanization": "seoldeukhada", "english": "to persuade", "level": "advanced", "category": "verbs"},
    {"korean": "결정하다", "romanization": "gyeoljeonghada", "english": "to decide", "level": "advanced", "category": "verbs"},
    {"korean": "계약", "romanization": "gyeyak", "english": "contract", "level": "advanced", "category": "business"},
    {"korean": "협상", "romanization": "hyeopsang", "english": "negotiation", "level": "advanced", "category": "business"},
    {"korean": "투자", "romanization": "tuja", "english": "investment", "level": "advanced", "category": "business"},
    {"korean": "예산", "romanization": "yesan", "english": "budget", "level": "advanced", "category": "business"},
    {"korean": "철학", "romanization": "cheolhak", "english": "philosophy", "level": "advanced", "category": "academia"},
    {"korean": "문학", "romanization": "munhak", "english": "literature", "level": "advanced", "category": "academia"},
    {"korean": "역사", "romanization": "yeoksa", "english": "history", "level": "advanced", "category": "academia"},
    {"korean": "감동적이다", "romanization": "gamdongjeogida", "english": "moving, touching", "level": "advanced", "category": "adjectives"},
    {"korean": "효율적이다", "romanization": "hyoyuljeogida", "english": "efficient", "level": "advanced", "category": "adjectives"},
    {"korean": "복잡하다", "romanization": "bokjaphada", "english": "complicated, complex", "level": "advanced", "category": "adjectives"},
    {"korean": "구체적이다", "romanization": "guchejeogida", "english": "concrete, specific", "level": "advanced", "category": "adjectives"},
    {"korean": "추상적이다", "romanization": "chusangjeogida", "english": "abstract", "level": "advanced", "category": "adjectives"},
    {"korean": "가능성", "romanization": "ganeungseong", "english": "possibility", "level": "advanced", "category": "nouns"},
    {"korean": "필요성", "romanization": "piryoseong", "english": "necessity", "level": "advanced", "category": "nouns"},
    {"korean": "책임", "romanization": "chaegim", "english": "responsibility", "level": "advanced", "category": "nouns"},
    {"korean": "기회", "romanization": "gihoe", "english": "opportunity, chance", "level": "advanced", "category": "nouns"},
    {"korean": "경험", "romanization": "gyeongheom", "english": "experience", "level": "advanced", "category": "nouns"},
]


LEVELS: tuple[str, ...] = ("beginner", "intermediate", "advanced")


def vocab_for_level(level: str) -> list[VocabEntry]:
    """Return all vocab entries matching the given level."""
    return [v for v in VOCAB if v["level"] == level]

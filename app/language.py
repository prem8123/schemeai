from __future__ import annotations

from langdetect import DetectorFactory, LangDetectException, detect

DetectorFactory.seed = 0

LANG_MAP = {"en": "en", "hi": "hi", "kn": "kn"}


def detect_supported_language(text: str, fallback: str = "en") -> str:
    if not text.strip():
        return fallback
    try:
        detected = detect(text)
    except LangDetectException:
        return fallback
    return LANG_MAP.get(detected, fallback)

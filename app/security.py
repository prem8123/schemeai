from __future__ import annotations

import re


_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")


def clean_user_text(value: str, max_length: int = 2000) -> str:
    """Remove control characters and cap user-controlled text before processing/logging."""
    cleaned = _CONTROL_CHARS.sub(" ", value).strip()
    return cleaned[:max_length]

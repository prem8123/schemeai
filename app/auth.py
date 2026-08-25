from __future__ import annotations

import hmac
import os

from fastapi import Header, HTTPException, status


async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Require an API key when SCHEMEAI_API_KEY is configured.

    Local development remains keyless unless the environment explicitly sets a key.
    """
    expected = os.getenv("SCHEMEAI_API_KEY", "").strip()
    if not expected:
        return
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Valid X-API-Key required")

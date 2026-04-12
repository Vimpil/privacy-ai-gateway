from __future__ import annotations

import hashlib


def safe_preview(text: str, prefix_len: int = 12) -> str:
    """Return a non-reversible preview safe for logs/audit metadata."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"sha256:{digest[:prefix_len]}"


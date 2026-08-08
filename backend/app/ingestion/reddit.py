"""Reddit ingestion via the public, unauthenticated .json search endpoint.

No OAuth is used (no client id/secret needed), which keeps this free and
key-less, but it also means Reddit can rate-limit or block requests from
some cloud IP ranges without warning. Every call is defensive: failures are
logged and surfaced to the caller as an empty list plus a status flag,
never silently faked.
"""
import logging
import time
from typing import TypedDict

import httpx

from app.config import REDDIT_SUBREDDITS, REDDIT_USER_AGENT

log = logging.getLogger("ingestion.reddit")

SEARCH_URL = f"https://www.reddit.com/r/{REDDIT_SUBREDDITS}/search.json"


class RedditItem(TypedDict):
    external_id: str
    title: str
    url: str
    created_utc: int
    score: float


def fetch_reddit(query: str, limit: int = 50, timeframe: str = "month") -> tuple[list[RedditItem], bool]:
    """Returns (items, ok). ok=False means the fetch failed/was blocked."""
    params = {
        "q": query,
        "restrict_sr": "1",
        "sort": "new",
        "limit": str(limit),
        "t": timeframe,
    }
    headers = {"User-Agent": REDDIT_USER_AGENT}
    try:
        resp = httpx.get(SEARCH_URL, params=params, headers=headers, timeout=15.0, follow_redirects=True)
        if resp.status_code != 200:
            log.warning("reddit fetch non-200 status=%s query=%r", resp.status_code, query)
            return [], False
        payload = resp.json()
    except Exception as exc:
        log.warning("reddit fetch failed query=%r err=%s", query, exc)
        return [], False

    items: list[RedditItem] = []
    for child in payload.get("data", {}).get("children", []):
        d = child.get("data", {})
        if not d.get("id") or not d.get("title"):
            continue
        items.append(
            RedditItem(
                external_id=d["id"],
                title=d["title"],
                url=f"https://reddit.com{d.get('permalink', '')}",
                created_utc=int(d.get("created_utc", time.time())),
                score=float(d.get("score", 0)),
            )
        )
    return items, True

"""Google News RSS ingestion. No API key required."""
import logging
import time
from email.utils import parsedate_to_datetime
from typing import TypedDict
from urllib.parse import quote

import feedparser

log = logging.getLogger("ingestion.news")

RSS_URL = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"


class NewsItem(TypedDict):
    external_id: str
    title: str
    url: str
    created_utc: int


def fetch_news(query: str, limit: int = 50) -> tuple[list[NewsItem], bool]:
    url = RSS_URL.format(query=quote(query))
    try:
        feed = feedparser.parse(url)
        if feed.bozo and not feed.entries:
            log.warning("news fetch bozo, no entries query=%r err=%s", query, feed.bozo_exception)
            return [], False
    except Exception as exc:
        log.warning("news fetch failed query=%r err=%s", query, exc)
        return [], False

    items: list[NewsItem] = []
    for entry in feed.entries[:limit]:
        link = entry.get("link", "")
        guid = entry.get("id") or link
        if not guid or not entry.get("title"):
            continue
        created = time.time()
        if entry.get("published"):
            try:
                created = parsedate_to_datetime(entry["published"]).timestamp()
            except Exception:
                pass
        items.append(
            NewsItem(
                external_id=str(hash(guid)),
                title=entry["title"],
                url=link,
                created_utc=int(created),
            )
        )
    return items, True

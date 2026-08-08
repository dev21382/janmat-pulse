from fastapi import APIRouter, HTTPException

from app.db.database import cursor
from app.ingestion.topics import TOPICS

router = APIRouter()


@router.get("/feed/{topic_id}")
def get_feed(topic_id: str, limit: int = 30):
    if topic_id not in TOPICS:
        raise HTTPException(404, "unknown topic")

    with cursor() as cur:
        cur.execute(
            """SELECT source, title, url, created_utc, score, sentiment
               FROM opinion_items WHERE topic_id=? ORDER BY created_utc DESC LIMIT ?""",
            (topic_id, limit),
        )
        rows = [dict(r) for r in cur.fetchall()]

    return {"topic_id": topic_id, "items": rows}


@router.get("/status")
def ingestion_status():
    with cursor() as cur:
        cur.execute(
            """SELECT topic_id, source, COUNT(*) as n, MAX(fetched_utc) as last_fetch
               FROM opinion_items GROUP BY topic_id, source"""
        )
        rows = [dict(r) for r in cur.fetchall()]
    return {"counts": rows}

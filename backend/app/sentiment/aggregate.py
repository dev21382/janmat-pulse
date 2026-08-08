from datetime import datetime, timezone

from app.db.database import cursor


def day_str(unix_ts: int) -> str:
    return datetime.fromtimestamp(unix_ts, tz=timezone.utc).strftime("%Y-%m-%d")


def recompute_daily_sentiment(topic_id: str) -> None:
    """Rebuilds the daily_sentiment rollup for a topic from opinion_items."""
    with cursor() as cur:
        cur.execute(
            "SELECT created_utc, sentiment FROM opinion_items WHERE topic_id=? AND sentiment IS NOT NULL",
            (topic_id,),
        )
        rows = cur.fetchall()

    buckets: dict[str, list[float]] = {}
    for row in rows:
        day = day_str(row["created_utc"])
        buckets.setdefault(day, []).append(row["sentiment"])

    with cursor() as cur:
        for day, scores in buckets.items():
            mean = sum(scores) / len(scores)
            cur.execute(
                """INSERT INTO daily_sentiment (topic_id, day, mean_sentiment, item_count)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(topic_id, day) DO UPDATE SET
                     mean_sentiment=excluded.mean_sentiment,
                     item_count=excluded.item_count""",
                (topic_id, day, mean, len(scores)),
            )


def get_daily_series(topic_id: str) -> list[dict]:
    with cursor() as cur:
        cur.execute(
            "SELECT day, mean_sentiment, item_count FROM daily_sentiment WHERE topic_id=? ORDER BY day ASC",
            (topic_id,),
        )
        return [dict(r) for r in cur.fetchall()]

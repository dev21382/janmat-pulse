from fastapi import APIRouter

from app.ingestion.topics import TOPICS

router = APIRouter()


@router.get("/topics")
def list_topics():
    return [{"id": tid, **meta} for tid, meta in TOPICS.items()]

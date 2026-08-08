from fastapi import APIRouter, HTTPException

from app.forecast.service import forecast_topic
from app.ingestion.topics import TOPICS

router = APIRouter()


@router.get("/forecast/{topic_id}")
def get_forecast(topic_id: str):
    if topic_id not in TOPICS:
        raise HTTPException(404, "unknown topic")
    return forecast_topic(topic_id)

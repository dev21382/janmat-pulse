import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import INGESTION_INTERVAL_MINUTES
from app.forecast.service import forecast_topic
from app.ingestion.pipeline import ingest_all
from app.ingestion.topics import TOPICS

log = logging.getLogger("scheduler")

_scheduler = BackgroundScheduler()


def _run_ingestion_job():
    try:
        ingest_all()
    except Exception as exc:
        log.exception("ingestion job failed: %s", exc)
        return
    _run_forecast_job()


def _run_forecast_job():
    for topic_id in TOPICS:
        try:
            forecast_topic(topic_id)
        except Exception as exc:
            log.exception("forecast job failed topic=%s: %s", topic_id, exc)


def start_scheduler():
    now = datetime.now()
    _scheduler.add_job(
        _run_ingestion_job, "interval", minutes=INGESTION_INTERVAL_MINUTES, id="ingestion", next_run_time=now
    )
    _scheduler.start()
    log.info(
        "scheduler started: ingestion+forecast every %sm", INGESTION_INTERVAL_MINUTES
    )


def shutdown_scheduler():
    _scheduler.shutdown(wait=False)

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import routes_feed, routes_forecast, routes_rag, routes_topics
from app.db.database import init_db
from app.rag.pipeline import build_index
from app.scheduler import shutdown_scheduler, start_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("main")

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        result = build_index()
        log.info("manifesto index status: %s", result)
    except Exception as exc:
        log.exception("manifesto index build failed at startup: %s", exc)
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(title="Public Opinion Aggregator", lifespan=lifespan)

app.include_router(routes_topics.router, prefix="/api")
app.include_router(routes_feed.router, prefix="/api")
app.include_router(routes_forecast.router, prefix="/api")
app.include_router(routes_rag.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}


if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        candidate = FRONTEND_DIST / full_path
        if full_path and candidate.exists() and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")

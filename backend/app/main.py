import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, close_db
from app.api.health import router as health_router
from app.api.news import router as news_router
from app.api.dashboard import router as dashboard_router
from app.api.admin import router as admin_router

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Israel News Developmental Analysis Engine")
    logger.info(f"Mode: {'DEMO' if settings.demo_mode else 'PRODUCTION'}")
    logger.info(f"Timezone: {settings.timezone}")

    await init_db()
    logger.info("Database initialized")

    if settings.demo_mode:
        from app.database import async_session
        async with async_session() as db:
            from app.services.demo_data import load_demo_articles
            count = await load_demo_articles(db)
            logger.info(f"Loaded {count} demo articles")

            from app.services.analysis_service import analyze_unprocessed_articles
            result = await analyze_unprocessed_articles(db)
            logger.info(f"Analyzed articles: {result}")

    from app.services.scheduler import start_scheduler
    start_scheduler()

    yield

    from app.services.scheduler import stop_scheduler
    stop_scheduler()
    await close_db()
    logger.info("Shutdown complete")


app = FastAPI(
    title="Israel News Developmental Analysis Engine",
    description="מנוע ניתוח חדשות התפתחותי — Partzuf Yomi",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(news_router)
app.include_router(dashboard_router)
app.include_router(admin_router)

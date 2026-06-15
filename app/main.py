"""
FastAPI application entry point.
Runs the admin panel and payment webhook server.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.middleware.security_headers import SecurityHeadersMiddleware
from app.config import settings
from app.db.base import engine
from app.models.models import Base
from app.routers.webhooks import router as webhook_router
from app.routers.admin import router as admin_router
from app.seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all DB tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_data()
    yield


app = FastAPI(title="Telegram Crypto Bot API", lifespan=lifespan)

# Middleware — order matters: outermost runs first
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="strict",
    https_only=settings.secure_cookies,
    max_age=60 * 60 * 8,  # 8 hours
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(webhook_router)
app.include_router(admin_router)


@app.get("/health")
async def health():
    return {"ok": True}

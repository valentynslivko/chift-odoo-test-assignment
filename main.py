import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.logger import init_logging
from src.core.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Used to manage startup and shutdown events.
    """
    init_logging()
    yield


app = FastAPI(title="Chift Odoo Test Task API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Pong"}


if __name__ == "__main__":
    uvicorn.run("main:app", log_config=None, host="0.0.0.0", reload=True, port=8000)

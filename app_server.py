from __future__ import annotations
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import logging
from clipnotes.api.notes import router as notes_router
from clipnotes.mcp_server.server import mcp_app
from clipnotes.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(title="ClipNotes", version="0.1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - {process_time:.3f}s"
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"{request.method} {request.url.path} - "
            f"ERROR - {process_time:.3f}s - {str(e)}",
            exc_info=True
        )
        raise

app.include_router(notes_router)
app.mount("/mcp", mcp_app)

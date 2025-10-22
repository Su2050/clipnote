from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from clipnotes.api.notes import router as notes_router
from clipnotes.mcp_server.server import mcp_app

app = FastAPI(title="ClipNotes", version="0.1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)

app.include_router(notes_router)
app.mount("/mcp", mcp_app)

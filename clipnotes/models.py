from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional, Literal, Any
from datetime import datetime

class SourceRef(BaseModel):
    thread_title: Optional[str] = None
    msg_id: Optional[str] = None
    url: Optional[str] = None

class ContextMsg(BaseModel):
    role: Literal["user", "assistant", "system"]
    text: str

class NoteIn(BaseModel):
    content: str
    tags: Optional[List[str]] = []
    topic: Optional[str] = None
    source: Optional[SourceRef] = None
    context_before: Optional[List[ContextMsg]] = None
    receipt_style: Optional[Literal["check", "simple"]] = "check"

class Note(BaseModel):
    id: str
    title: str
    content: str
    tags: List[str] = []
    topic: Optional[str] = None
    saved_at: datetime
    source: Optional[SourceRef] = None
    dedup_key: str
    summary: Optional[str] = None
    embedding: Optional[Any] = None
    context_before: Optional[List[ContextMsg]] = None
    tenant: Optional[str] = None

class NoteList(BaseModel):
    items: List[Note]

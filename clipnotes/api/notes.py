from __future__ import annotations
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from datetime import datetime, timezone
from typing import Optional
from ..models import NoteIn, Note, NoteList
from ..config import settings
from ..storage import LocalStorage, AliyunOSSStorage

router = APIRouter()

def get_tenant(x_user_id: Optional[str] = Header(None)) -> str:
    return x_user_id or settings.default_tenant

def auth(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token not in settings.api_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    return True

def get_store(tenant: str):
    if settings.storage_provider == 'local':
        return LocalStorage(settings.data_dir, tenant)
    elif settings.storage_provider == 'aliyun_oss':
        return AliyunOSSStorage(
            settings.aliyun_oss_endpoint, settings.aliyun_oss_ak, settings.aliyun_oss_sk,
            settings.aliyun_oss_bucket, settings.aliyun_oss_prefix, tenant
        )
    else:
        raise HTTPException(status_code=500, detail=f"unknown storage provider: {settings.storage_provider}")

@router.get("/healthz")
def healthz():
    return {"ok": True, "provider": settings.storage_provider}

@router.post("/notes", response_model=Note)
def create_note(note: NoteIn, _=Depends(auth), tenant: str = Depends(get_tenant)):
    store = get_store(tenant)
    now = datetime.now(timezone.utc)
    saved = store.save(note, now)
    return saved

@router.get("/notes", response_model=NoteList)
def list_recent(limit: int = Query(5, ge=1, le=50), _=Depends(auth), tenant: str = Depends(get_tenant)):
    store = get_store(tenant)
    items = store.list_recent(limit)
    return NoteList(items=items)

@router.get("/notes/search", response_model=NoteList)
def search(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=100), _=Depends(auth), tenant: str = Depends(get_tenant)):
    store = get_store(tenant)
    items = store.search(q, limit)
    return NoteList(items=items)

@router.delete("/notes/{note_id}")
def delete_note(note_id: str, _=Depends(auth), tenant: str = Depends(get_tenant)):
    store = get_store(tenant)
    ok = store.delete(note_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True, "id": note_id}

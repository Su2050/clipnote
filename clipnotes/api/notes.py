from __future__ import annotations
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status, Request
from datetime import datetime, timezone
from typing import Optional
import time
import logging
from ..models import NoteIn, Note, NoteList
from ..config import settings
from ..storage import LocalStorage, AliyunOSSStorage
from ..utils import sanitize_tenant

logger = logging.getLogger(__name__)

router = APIRouter()

def get_tenant(x_user_id: Optional[str] = Header(None)) -> str:
    """获取并清理租户ID"""
    tenant = x_user_id or settings.default_tenant
    return sanitize_tenant(tenant)

def auth(authorization: Optional[str] = Header(None)):
    """认证中间件，带日志记录"""
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("认证失败: 缺少 Bearer token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token not in settings.api_tokens:
        logger.warning(f"认证失败: 无效的 token (前10字符: {token[:10]}...)")
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
    """创建笔记，带错误处理和日志"""
    try:
        store = get_store(tenant)
        now = datetime.now(timezone.utc)
        saved = store.save(note, now)
        logger.info(f"创建笔记成功: {saved.id}, 租户: {tenant}")
        return saved
    except Exception as e:
        logger.error(f"创建笔记失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建笔记失败: {str(e)}")

@router.get("/notes", response_model=NoteList)
def list_recent(limit: int = Query(5, ge=1, le=50), _=Depends(auth), tenant: str = Depends(get_tenant)):
    """列出最近笔记，带错误处理"""
    try:
        store = get_store(tenant)
        items = store.list_recent(limit)
        logger.debug(f"列出笔记: 租户={tenant}, limit={limit}, 返回={len(items)}条")
        return NoteList(items=items)
    except Exception as e:
        logger.error(f"列出笔记失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"列出笔记失败: {str(e)}")

@router.get("/notes/search", response_model=NoteList)
def search(q: str = Query(..., min_length=1, max_length=200), limit: int = Query(10, ge=1, le=100), _=Depends(auth), tenant: str = Depends(get_tenant)):
    """搜索笔记，带错误处理"""
    try:
        store = get_store(tenant)
        items = store.search(q, limit)
        logger.debug(f"搜索笔记: 租户={tenant}, 查询='{q}', limit={limit}, 返回={len(items)}条")
        return NoteList(items=items)
    except Exception as e:
        logger.error(f"搜索笔记失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"搜索笔记失败: {str(e)}")

@router.delete("/notes/{note_id}")
def delete_note(note_id: str, _=Depends(auth), tenant: str = Depends(get_tenant)):
    """删除笔记，带错误处理"""
    try:
        store = get_store(tenant)
        ok = store.delete(note_id)
        if not ok:
            logger.warning(f"删除笔记失败: 未找到, note_id={note_id}, 租户={tenant}")
            raise HTTPException(status_code=404, detail="not found")
        logger.info(f"删除笔记成功: note_id={note_id}, 租户={tenant}")
        return {"deleted": True, "id": note_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除笔记失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除笔记失败: {str(e)}")

from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
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
    content: str = Field(..., min_length=1, max_length=100000, description="笔记内容")
    tags: Optional[List[str]] = Field(default=[], max_items=20, description="标签列表")
    topic: Optional[str] = Field(None, max_length=200, description="主题/分类")
    source: Optional[SourceRef] = None
    context_before: Optional[List[ContextMsg]] = Field(None, max_items=10, description="上下文消息（最多10条）")
    receipt_style: Optional[Literal["check", "simple"]] = "check"
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """验证内容不为空且长度合理"""
        if not v or not v.strip():
            raise ValueError("内容不能为空")
        return v.strip()
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> List[str]:
        """验证并清理标签"""
        if not v:
            return []
        # 清理标签：去空格、限制长度、去重
        cleaned = []
        for tag in v:
            tag = tag.strip()[:50]  # 每个标签最多50字符
            if tag and tag not in cleaned:
                cleaned.append(tag)
        return cleaned[:20]  # 最多20个标签
    
    @field_validator('topic')
    @classmethod
    def validate_topic(cls, v: Optional[str]) -> Optional[str]:
        """验证主题"""
        if v:
            return v.strip()[:200]
        return v

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

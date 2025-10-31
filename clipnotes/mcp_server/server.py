from __future__ import annotations
from typing import Optional, Literal, List
from pydantic import BaseModel
import httpx
import os
from mcp.server.fastmcp import FastMCP, Context
from ..models import NoteIn, ContextMsg, SourceRef
from ..config import settings

API_URL = settings.notes_api_url
API_TOKEN = settings.notes_api_token

mcp = FastMCP(name=settings.mcp_server_name, stateless_http=settings.mcp_stateless_http)

class AddNoteArgs(BaseModel):
    mode: Literal["explicit", "last_assistant"] = "explicit"
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    topic: Optional[str] = None
    source: Optional[SourceRef] = None
    context_before: Optional[List[ContextMsg]] = None
    receipt_style: Literal["check", "simple"] = "check"

class ListArgs(BaseModel):
    limit: int = 5

@mcp.tool(
    name="add_note",
    description=(
        "保存片段到 ClipNotes - 保存聊天中的一段内容到用户的笔记系统（本地/OSS）。"
        "当用户输入'摘：上一条/记录/总结知识点并保存'时，请把上一条助理输出作为 content；"
        "当用户输入以'记：'开头时，取后面的显式文本作为 content；"
        "同时请把最近的最多 3 条上下文（context_before）一并传入。"
        "返回一行回执：✅ 已记：<短标题>。"
    ),
)
async def add_note(args: AddNoteArgs, ctx: Context) -> str:
    payload = NoteIn(
        content=(args.content or "").strip(),
        tags=args.tags or [],
        topic=args.topic,
        source=args.source,
        context_before=args.context_before or [],
        receipt_style=args.receipt_style,
    )
    if not payload.content and args.mode == "last_assistant":
        await ctx.warning("缺少 content（应由模型填入上一条助理输出）")
        raise ValueError("missing content")

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "X-User-Id": os.getenv("DEFAULT_TENANT", settings.default_tenant),
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(f"{API_URL}/notes", headers=headers, json=payload.model_dump())
        r.raise_for_status()
        data = r.json()
    title = (data.get("title") or "").strip()[:60]
    return f"✅ 已记：{title}" if args.receipt_style == "check" else f"已记：{title}"

@mcp.tool(
    name="list_notes",
    description="列出最近的笔记 - 列出最近 N 条笔记（默认 5 条），仅显示标题与时间。"
)
async def list_notes(args: ListArgs) -> str:
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "X-User-Id": os.getenv("DEFAULT_TENANT", settings.default_tenant),
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{API_URL}/notes", headers=headers, params={"limit": args.limit})
        r.raise_for_status()
        data = r.json()
    lines = []
    for it in data.get("items", []):
        t = (it.get("saved_at","")[:19]).replace("T"," ")
        lines.append(f"- [{t}] {it.get('title','')}")
    return "\n".join(lines) or "(暂无)"

# 创建 Starlette 应用用于 MCP SSE 端点
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from mcp.server.sse import SseServerTransport
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream

async def handle_sse(request):
    """处理 SSE 连接"""
    from sse_starlette import EventSourceResponse
    
    async def event_generator():
        # 这里需要实现 MCP SSE 协议
        # 暂时返回简单响应
        yield {
            "event": "message",
            "data": "MCP endpoint - under construction"
        }
    
    return EventSourceResponse(event_generator())

async def handle_messages(request):
    """处理 MCP 消息"""
    return JSONResponse({"error": "MCP endpoint under construction"})

mcp_app = Starlette(
    routes=[
        Route("/sse", handle_sse),
        Route("/messages", handle_messages, methods=["POST"]),
    ]
)

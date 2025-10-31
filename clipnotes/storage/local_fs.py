from __future__ import annotations
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import json
import logging
from ..models import Note, NoteIn
from ..utils import short_title, dedup_key, extract_keywords, generate_ai_title, sanitize_filename, sanitize_tenant

logger = logging.getLogger(__name__)

class LocalStorage:
    def __init__(self, base_dir: str, tenant: str):
        self.base_dir = Path(base_dir).resolve()
        self.tenant = sanitize_tenant(tenant)
        try:
            (self.base_dir / self.tenant).mkdir(parents=True, exist_ok=True)
            (self.base_dir / self.tenant / 'index').mkdir(parents=True, exist_ok=True)
            logger.info(f"初始化本地存储: {self.base_dir}/{self.tenant}")
        except Exception as e:
            logger.error(f"创建存储目录失败: {e}", exc_info=True)
            raise

    def _path_for(self, note_id: str, ts: datetime):
        sub = ts.strftime('%Y/%m/%d')
        p = self.base_dir / self.tenant / sub
        p.mkdir(parents=True, exist_ok=True)
        return p / f"{note_id}.json"

    def _path_for_md(self, note_id: str, ts: datetime):
        sub = ts.strftime('%Y/%m/%d')
        p = self.base_dir / self.tenant / sub
        p.mkdir(parents=True, exist_ok=True)
        return p / f"{note_id}.md"

    def save(self, note_in: NoteIn, now: datetime, suggested_id: Optional[str] = None) -> Note:
        try:
            # 尝试使用 AI 生成标题，如果未启用则使用默认策略
            ai_title = generate_ai_title(note_in.content)
            title = ai_title if ai_title else short_title(note_in.content)
            tags = list(note_in.tags or []) or extract_keywords(note_in.content, topk=5)
            dd = dedup_key(note_in.content, now)
            note_id = sanitize_filename(suggested_id or dd.replace('@','-'))

            note = Note(
                id=note_id, title=title, content=note_in.content, tags=tags, topic=note_in.topic,
                saved_at=now, source=note_in.source, dedup_key=dd, summary=None, embedding=None,
                context_before=note_in.context_before, tenant=self.tenant
            )

            # 幂等：dedup_index.json
            idx_file = self.base_dir / self.tenant / 'index' / 'dedup_index.json'
            try:
                existing: Dict[str, str] = json.loads(idx_file.read_text(encoding='utf-8'))
            except FileNotFoundError:
                existing = {}
                logger.debug(f"索引文件不存在，创建新索引: {idx_file}")
            except json.JSONDecodeError as e:
                logger.warning(f"索引文件损坏，重置索引: {idx_file}, 错误: {e}")
                existing = {}
            except Exception as e:
                logger.error(f"读取索引文件失败: {idx_file}, 错误: {e}", exc_info=True)
                raise
            
            if note.dedup_key in existing:
                logger.info(f"检测到重复内容，返回已存在的笔记: {existing[note.dedup_key]}")
                return note.model_copy(update={"id": existing[note.dedup_key]})

            # 写 JSON
            p_json = self._path_for(note.id, now)
            try:
                p_json.write_text(note.model_dump_json(ensure_ascii=False, indent=2), encoding='utf-8')
                logger.debug(f"保存 JSON 文件: {p_json}")
            except Exception as e:
                logger.error(f"保存 JSON 文件失败: {p_json}, 错误: {e}", exc_info=True)
                raise

            # 写 Markdown（带前三轮上下文）
            p_md = self._path_for_md(note.id, now)
            ctx_md = ''
            if note.context_before:
                ctx_lines = [f"- **{m['role'] if isinstance(m, dict) else m.role}**：{(m['text'] if isinstance(m, dict) else m.text)}" for m in note.context_before]
                ctx_md = "\n\n### 上下文（前 3 轮）\n" + "\n".join(ctx_lines)
            md = f"# {note.title}\n- 时间：{now.isoformat()}\n- 标签：{', '.join(note.tags) if note.tags else '-'}\n- 主题：{note.topic or '-'}\n- 来源：{(note.source and (note.source.thread_title or '')) or '-'}\n\n## 原文\n{note.content}{ctx_md}\n"
            try:
                p_md.write_text(md, encoding='utf-8')
                logger.debug(f"保存 Markdown 文件: {p_md}")
            except Exception as e:
                logger.error(f"保存 Markdown 文件失败: {p_md}, 错误: {e}", exc_info=True)
                raise

            # 更新索引
            existing[note.dedup_key] = note.id
            try:
                idx_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding='utf-8')
                logger.debug(f"更新索引文件: {idx_file}")
            except Exception as e:
                logger.error(f"更新索引文件失败: {idx_file}, 错误: {e}", exc_info=True)
                raise
            
            logger.info(f"笔记保存成功: {note.id}, 标题: {note.title[:50]}")
            return note
        except Exception as e:
            logger.error(f"保存笔记失败: {e}", exc_info=True)
            raise

    def list_recent(self, limit: int = 5) -> List[Note]:
        items: List[Note] = []
        try:
            tenant_dir = self.base_dir / self.tenant
            for y in sorted([p for p in tenant_dir.glob('*') if p.is_dir() and p.name.isdigit()], reverse=True):
                for m in sorted([p for p in y.glob('*') if p.is_dir()], reverse=True):
                    for d in sorted([p for p in m.glob('*') if p.is_dir()], reverse=True):
                        # 按文件修改时间排序，而不是文件名
                        for f in sorted([p for p in d.glob('*.json')], key=lambda x: x.stat().st_mtime, reverse=True):
                            try:
                                data = json.loads(f.read_text(encoding='utf-8'))
                                items.append(Note.model_validate(data))
                                if len(items) >= limit:
                                    return items
                            except json.JSONDecodeError as e:
                                logger.warning(f"JSON 解析失败: {f}, 错误: {e}")
                                continue
                            except Exception as e:
                                logger.warning(f"读取笔记失败: {f}, 错误: {e}")
                                continue
            logger.debug(f"列出最近笔记: {len(items)} 条")
            return items
        except Exception as e:
            logger.error(f"列出笔记失败: {e}", exc_info=True)
            raise

    def search(self, q: str, limit: int = 10) -> List[Note]:
        items: List[Note] = []
        try:
            search_dir = self.base_dir / self.tenant
            for f in search_dir.glob('**/*.json'):
                try:
                    data = json.loads(f.read_text(encoding='utf-8'))
                    hay = (data.get('title','') + ' ' + data.get('content','')).lower()
                    for m in (data.get('context_before') or []):
                        hay += ' ' + (m.get('text','') if isinstance(m, dict) else '')
                    if q.lower() in hay:
                        items.append(Note.model_validate(data))
                        if len(items) >= limit:
                            return items
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON 解析失败: {f}, 错误: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"搜索笔记失败: {f}, 错误: {e}")
                    continue
            logger.debug(f"搜索完成: 查询 '{q}', 找到 {len(items)} 条")
            return items
        except Exception as e:
            logger.error(f"搜索失败: {e}", exc_info=True)
            raise

    def delete(self, note_id: str) -> bool:
        """删除笔记，带安全检查"""
        note_id = sanitize_filename(note_id)
        found = False
        try:
            search_dir = self.base_dir / self.tenant
            for f in search_dir.glob('**/*.json'):
                if f.stem == note_id:
                    found = True
                    md = f.with_suffix('.md')
                    try:
                        f.unlink()
                        logger.debug(f"删除 JSON 文件: {f}")
                    except FileNotFoundError:
                        logger.warning(f"JSON 文件不存在: {f}")
                    except Exception as e:
                        logger.error(f"删除 JSON 文件失败: {f}, 错误: {e}", exc_info=True)
                    
                    try:
                        md.unlink()
                        logger.debug(f"删除 Markdown 文件: {md}")
                    except FileNotFoundError:
                        logger.warning(f"Markdown 文件不存在: {md}")
                    except Exception as e:
                        logger.error(f"删除 Markdown 文件失败: {md}, 错误: {e}", exc_info=True)
            
            if found:
                logger.info(f"笔记删除成功: {note_id}")
            else:
                logger.warning(f"笔记未找到: {note_id}")
            return found
        except Exception as e:
            logger.error(f"删除笔记失败: {note_id}, 错误: {e}", exc_info=True)
            raise

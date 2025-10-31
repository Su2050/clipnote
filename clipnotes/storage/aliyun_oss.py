from __future__ import annotations
from typing import List, Optional
from datetime import datetime
import json
import logging
import oss2
from ..models import Note, NoteIn
from ..utils import short_title, dedup_key, extract_keywords, generate_ai_title, sanitize_filename, sanitize_tenant

logger = logging.getLogger(__name__)

class AliyunOSSStorage:
    def __init__(self, endpoint: str, ak: str, sk: str, bucket_name: str, prefix: str, tenant: str):
        try:
            self.bucket = oss2.Bucket(oss2.Auth(ak, sk), endpoint, bucket_name)
            self.prefix = prefix.rstrip('/') + '/'
            self.tenant = sanitize_tenant(tenant)
            logger.info(f"初始化阿里云 OSS 存储: bucket={bucket_name}, tenant={self.tenant}")
        except Exception as e:
            logger.error(f"初始化 OSS 存储失败: {e}", exc_info=True)
            raise

    def _key(self, note_id: str, ts: datetime, ext: str):
        sub = ts.strftime('%Y/%m/%d')
        return f"{self.prefix}{self.tenant}/{sub}/{note_id}.{ext}"

    def save(self, note_in: NoteIn, now: datetime, suggested_id: Optional[str] = None) -> Note:
        try:
            # 尝试使用 AI 生成标题，如果未启用则使用默认策略
            ai_title = generate_ai_title(note_in.content)
            title = ai_title if ai_title else short_title(note_in.content)
            tags = list(note_in.tags or []) or extract_keywords(note_in.content, topk=5)
            dd = dedup_key(note_in.content, now)
            note_id = sanitize_filename(suggested_id or dd.replace('@','-'))

            note = Note(id=note_id, title=title, content=note_in.content, tags=tags, topic=note_in.topic,
                        saved_at=now, source=note_in.source, dedup_key=dd, summary=None, embedding=None,
                        context_before=note_in.context_before, tenant=self.tenant)

            # 幂等索引
            idx_key = f"{self.prefix}{self.tenant}/index/dedup_index.json"
            try:
                existing = json.loads(self.bucket.get_object(idx_key).read().decode('utf-8'))
            except oss2.exceptions.NoSuchKey:
                existing = {}
                logger.debug(f"索引文件不存在，创建新索引: {idx_key}")
            except json.JSONDecodeError as e:
                logger.warning(f"索引文件损坏，重置索引: {idx_key}, 错误: {e}")
                existing = {}
            except Exception as e:
                logger.error(f"读取索引文件失败: {idx_key}, 错误: {e}", exc_info=True)
                raise
            
            if note.dedup_key in existing:
                logger.info(f"检测到重复内容，返回已存在的笔记: {existing[note.dedup_key]}")
                return note.model_copy(update={"id": existing[note.dedup_key]})

            # 写 JSON
            try:
                self.bucket.put_object(self._key(note.id, now, "json"), note.model_dump_json(ensure_ascii=False, indent=2).encode('utf-8'))
                logger.debug(f"保存 JSON 文件到 OSS: {self._key(note.id, now, 'json')}")
            except Exception as e:
                logger.error(f"保存 JSON 文件到 OSS 失败: {e}", exc_info=True)
                raise

            # 写 Markdown
            ctx_md = ''
            if note.context_before:
                ctx_lines = [f"- **{m['role'] if isinstance(m, dict) else m.role}**：{(m['text'] if isinstance(m, dict) else m.text)}" for m in note.context_before]
                ctx_md = "\n\n### 上下文（前 3 轮）\n" + "\n".join(ctx_lines)
            md = f"# {note.title}\n- 时间：{now.isoformat()}\n- 标签：{', '.join(note.tags) if note.tags else '-'}\n- 主题：{note.topic or '-'}\n- 来源：{(note.source and (note.source.thread_title or '')) or '-'}\n\n## 原文\n{note.content}{ctx_md}\n"
            try:
                self.bucket.put_object(self._key(note.id, now, "md"), md.encode('utf-8'))
                logger.debug(f"保存 Markdown 文件到 OSS: {self._key(note.id, now, 'md')}")
            except Exception as e:
                logger.error(f"保存 Markdown 文件到 OSS 失败: {e}", exc_info=True)
                raise

            existing[note.dedup_key] = note.id
            try:
                self.bucket.put_object(idx_key, json.dumps(existing, ensure_ascii=False, indent=2).encode('utf-8'))
                logger.debug(f"更新索引文件: {idx_key}")
            except Exception as e:
                logger.error(f"更新索引文件失败: {idx_key}, 错误: {e}", exc_info=True)
                raise
            
            logger.info(f"笔记保存成功: {note.id}, 标题: {note.title[:50]}")
            return note
        except Exception as e:
            logger.error(f"保存笔记失败: {e}", exc_info=True)
            raise

    def list_recent(self, limit: int = 5) -> List[Note]:
        items: List[Note] = []
        try:
            prefix = f"{self.prefix}{self.tenant}/"
            for obj in self.bucket.list_objects(prefix=prefix).object_list[::-1]:
                if obj.key.endswith('.json'):
                    try:
                        data = self.bucket.get_object(obj.key).read().decode('utf-8')
                        items.append(Note.model_validate_json(data))
                        if len(items) >= limit:
                            break
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON 解析失败: {obj.key}, 错误: {e}")
                        continue
                    except Exception as e:
                        logger.warning(f"读取笔记失败: {obj.key}, 错误: {e}")
                        continue
            logger.debug(f"列出最近笔记: {len(items)} 条")
            return items
        except Exception as e:
            logger.error(f"列出笔记失败: {e}", exc_info=True)
            raise

    def search(self, q: str, limit: int = 10) -> List[Note]:
        items: List[Note] = []
        try:
            prefix = f"{self.prefix}{self.tenant}/"
            for obj in self.bucket.list_objects(prefix=prefix).object_list:
                if not obj.key.endswith('.json'): 
                    continue
                try:
                    data = json.loads(self.bucket.get_object(obj.key).read().decode('utf-8'))
                    hay = (data.get('title','') + ' ' + data.get('content','')).lower()
                    for m in (data.get('context_before') or []):
                        hay += ' ' + (m.get('text','') if isinstance(m, dict) else '')
                    if q.lower() in hay:
                        items.append(Note.model_validate(data))
                        if len(items) >= limit:
                            return items
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON 解析失败: {obj.key}, 错误: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"搜索笔记失败: {obj.key}, 错误: {e}")
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
            prefix = f"{self.prefix}{self.tenant}/"
            for obj in self.bucket.list_objects(prefix=prefix).object_list:
                base = obj.key.rsplit('/', 1)[-1]
                if base.split('.')[0] == note_id:
                    try:
                        self.bucket.delete_object(obj.key)
                        logger.debug(f"删除文件: {obj.key}")
                        found = True
                    except Exception as e:
                        logger.error(f"删除文件失败: {obj.key}, 错误: {e}", exc_info=True)
            
            if found:
                logger.info(f"笔记删除成功: {note_id}")
            else:
                logger.warning(f"笔记未找到: {note_id}")
            return found
        except Exception as e:
            logger.error(f"删除笔记失败: {note_id}, 错误: {e}", exc_info=True)
            raise

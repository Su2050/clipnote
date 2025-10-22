from __future__ import annotations
from typing import List, Optional
from datetime import datetime
import json
import oss2
from ..models import Note, NoteIn
from ..utils import short_title, dedup_key, extract_keywords

class AliyunOSSStorage:
    def __init__(self, endpoint: str, ak: str, sk: str, bucket_name: str, prefix: str, tenant: str):
        self.bucket = oss2.Bucket(oss2.Auth(ak, sk), endpoint, bucket_name)
        self.prefix = prefix.rstrip('/') + '/'
        self.tenant = tenant or "default"

    def _key(self, note_id: str, ts: datetime, ext: str):
        sub = ts.strftime('%Y/%m/%d')
        return f"{self.prefix}{self.tenant}/{sub}/{note_id}.{ext}"

    def save(self, note_in: NoteIn, now: datetime, suggested_id: Optional[str] = None) -> Note:
        title = short_title(note_in.content)
        tags = list(note_in.tags or []) or extract_keywords(note_in.content, topk=5)
        dd = dedup_key(note_in.content, now)
        note_id = suggested_id or dd.replace('@','-')

        note = Note(id=note_id, title=title, content=note_in.content, tags=tags, topic=note_in.topic,
                    saved_at=now, source=note_in.source, dedup_key=dd, summary=None, embedding=None,
                    context_before=note_in.context_before, tenant=self.tenant)

        # 幂等索引
        idx_key = f"{self.prefix}{self.tenant}/index/dedup_index.json"
        try:
            existing = json.loads(self.bucket.get_object(idx_key).read().decode('utf-8'))
        except Exception:
            existing = {}
        if note.dedup_key in existing:
            return note.model_copy(update={"id": existing[note.dedup_key]})

        # 写 JSON
        self.bucket.put_object(self._key(note.id, now, "json"), note.model_dump_json(ensure_ascii=False, indent=2).encode('utf-8'))

        # 写 Markdown
        ctx_md = ''
        if note.context_before:
            ctx_lines = [f"- **{m['role'] if isinstance(m, dict) else m.role}**：{(m['text'] if isinstance(m, dict) else m.text)}" for m in note.context_before]
            ctx_md = "\n\n### 上下文（前 3 轮）\n" + "\n".join(ctx_lines)
        md = f"# {note.title}\n- 时间：{now.isoformat()}\n- 标签：{', '.join(note.tags) if note.tags else '-'}\n- 主题：{note.topic or '-'}\n- 来源：{(note.source and (note.source.thread_title or '')) or '-'}\n\n## 原文\n{note.content}{ctx_md}\n"
        self.bucket.put_object(self._key(note.id, now, "md"), md.encode('utf-8'))

        existing[note.dedup_key] = note.id
        self.bucket.put_object(idx_key, json.dumps(existing, ensure_ascii=False, indent=2).encode('utf-8'))
        return note

    def list_recent(self, limit: int = 5) -> List[Note]:
        items: List[Note] = []
        prefix = f"{self.prefix}{self.tenant}/"
        for obj in self.bucket.list_objects(prefix=prefix).object_list[::-1]:
            if obj.key.endswith('.json'):
                try:
                    data = self.bucket.get_object(obj.key).read().decode('utf-8')
                    items.append(Note.model_validate_json(data))
                    if len(items) >= limit:
                        break
                except Exception:
                    continue
        return items

    def search(self, q: str, limit: int = 10) -> List[Note]:
        items: List[Note] = []
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
            except Exception:
                continue
        return items

    def delete(self, note_id: str) -> bool:
        prefix = f"{self.prefix}{self.tenant}/"
        found = False
        for obj in self.bucket.list_objects(prefix=prefix).object_list:
            base = obj.key.rsplit('/', 1)[-1]
            if base.split('.')[0] == note_id:
                self.bucket.delete_object(obj.key)
                found = True
        return found

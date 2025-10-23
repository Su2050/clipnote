from __future__ import annotations
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import json
from ..models import Note, NoteIn
from ..utils import short_title, dedup_key, extract_keywords

class LocalStorage:
    def __init__(self, base_dir: str, tenant: str):
        self.base_dir = Path(base_dir).resolve()
        self.tenant = tenant or "default"
        (self.base_dir / self.tenant).mkdir(parents=True, exist_ok=True)
        (self.base_dir / self.tenant / 'index').mkdir(parents=True, exist_ok=True)

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
        title = short_title(note_in.content)
        tags = list(note_in.tags or []) or extract_keywords(note_in.content, topk=5)
        dd = dedup_key(note_in.content, now)
        note_id = suggested_id or dd.replace('@','-')

        note = Note(
            id=note_id, title=title, content=note_in.content, tags=tags, topic=note_in.topic,
            saved_at=now, source=note_in.source, dedup_key=dd, summary=None, embedding=None,
            context_before=note_in.context_before, tenant=self.tenant
        )

        # 幂等：dedup_index.json
        idx_file = self.base_dir / self.tenant / 'index' / 'dedup_index.json'
        try:
            existing: Dict[str, str] = json.loads(idx_file.read_text(encoding='utf-8'))
        except Exception:
            existing = {}
        if note.dedup_key in existing:
            return note.model_copy(update={"id": existing[note.dedup_key]})

        # 写 JSON
        p_json = self._path_for(note.id, now)
        p_json.write_text(note.model_dump_json(ensure_ascii=False, indent=2), encoding='utf-8')

        # 写 Markdown（带前三轮上下文）
        p_md = self._path_for_md(note.id, now)
        ctx_md = ''
        if note.context_before:
            ctx_lines = [f"- **{m['role'] if isinstance(m, dict) else m.role}**：{(m['text'] if isinstance(m, dict) else m.text)}" for m in note.context_before]
            ctx_md = "\n\n### 上下文（前 3 轮）\n" + "\n".join(ctx_lines)
        md = f"# {note.title}\n- 时间：{now.isoformat()}\n- 标签：{', '.join(note.tags) if note.tags else '-'}\n- 主题：{note.topic or '-'}\n- 来源：{(note.source and (note.source.thread_title or '')) or '-'}\n\n## 原文\n{note.content}{ctx_md}\n"
        p_md.write_text(md, encoding='utf-8')

        # 更新索引
        existing[note.dedup_key] = note.id
        idx_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding='utf-8')
        return note

    def list_recent(self, limit: int = 5) -> List[Note]:
        items: List[Note] = []
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
                        except Exception:
                            continue
        return items

    def search(self, q: str, limit: int = 10) -> List[Note]:
        items: List[Note] = []
        for f in (self.base_dir / self.tenant).glob('**/*.json'):
            try:
                data = json.loads(f.read_text(encoding='utf-8'))
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
        found = False
        for f in (self.base_dir / self.tenant).glob('**/*.json'):
            if f.stem == note_id:
                found = True
                md = f.with_suffix('.md')
                try: f.unlink()
                except FileNotFoundError: pass
                try: md.unlink()
                except FileNotFoundError: pass
        return found

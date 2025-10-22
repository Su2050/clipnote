import re, hashlib, base64
from datetime import datetime
import jieba.analyse as ja

def slugify(text: str, maxlen: int = 60) -> str:
    t = re.sub(r'\s+', ' ', text.strip())
    t = re.sub(r'[^\u4e00-\u9fffA-Za-z0-9 _\-.,，。！？!?：:；;（）()\[\]]+', '', t)
    return (t[:maxlen].rstrip() or "untitled")

def short_title(content: str) -> str:
    return slugify(content, 60)

def dedup_key(content: str, ts: datetime) -> str:
    h = hashlib.sha256(content.encode('utf-8')).digest()
    b22 = base64.urlsafe_b64encode(h).decode('ascii').rstrip('=')[:22]
    minute = ts.strftime('%Y%m%d%H%M')
    return f"{b22}@{minute}"

def extract_keywords(text: str, topk: int = 5):
    try:
        kws = ja.extract_tags(text, topK=topk, withWeight=False, allowPOS=())
        return [k for k in kws if len(k.strip()) > 1]
    except Exception:
        return []

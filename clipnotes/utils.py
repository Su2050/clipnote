import re, hashlib, base64
from datetime import datetime
import jieba.analyse as ja
import logging

logger = logging.getLogger(__name__)

def sanitize_filename(name: str, max_length: int = 100) -> str:
    """
    清理文件名/ID，防止路径注入攻击
    
    Args:
        name: 原始文件名/ID
        max_length: 最大长度限制
    
    Returns:
        清理后的安全文件名
    """
    if not name:
        return "untitled"
    
    # 移除路径分隔符和危险字符
    name = re.sub(r'[<>:"|?*\x00-\x1f]', '', name)
    # 移除目录遍历尝试
    name = name.replace('..', '').replace('/', '').replace('\\', '')
    # 移除首尾空格和点
    name = name.strip(' .')
    # 限制长度
    name = name[:max_length]
    
    # 如果清理后为空，返回默认值
    return name or "untitled"

def sanitize_tenant(tenant: str, max_length: int = 50) -> str:
    """
    清理租户ID，防止路径注入
    
    Args:
        tenant: 原始租户ID
        max_length: 最大长度限制
    
    Returns:
        清理后的安全租户ID
    """
    if not tenant:
        return "default"
    
    # 只允许字母、数字、下划线、连字符
    tenant = re.sub(r'[^a-zA-Z0-9_-]', '', tenant)
    tenant = tenant[:max_length]
    
    return tenant or "default"

def slugify(text: str, maxlen: int = 120) -> str:
    """清理文本，保留有效字符"""
    t = re.sub(r'\s+', ' ', text.strip())
    t = re.sub(r'[^\u4e00-\u9fffA-Za-z0-9 _\-.,，。！？!?：:；;（）()\[\]]+', '', t)
    return (t[:maxlen].rstrip() or "untitled")

def short_title(content: str, maxlen: int = 120) -> str:
    """
    从内容中提取标题
    
    策略：
    1. 尝试提取第一句话作为标题
    2. 避免截断单词
    3. TODO: 未来可以集成 AI (如 GPT) 自动生成摘要标题
    
    Args:
        content: 笔记内容
        maxlen: 标题最大长度
    
    Returns:
        清理后的标题文本
    """
    # 先清理 Markdown 标记和空白
    text = re.sub(r'^#+\s*', '', content)  # 去除开头的 # 标题符号
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # 去除粗体标记
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # 去除链接，保留文字
    text = re.sub(r'`([^`]+)`', r'\1', text)  # 去除代码标记
    text = re.sub(r'\s+', ' ', text.strip())  # 统一空白
    
    # 策略1: 尝试按句号、问号、感叹号分割，取第一句
    sentences = re.split(r'[。！？\n]', text)
    if sentences and len(sentences[0].strip()) >= 10:
        first_sentence = sentences[0].strip()
        if len(first_sentence) <= maxlen:
            return slugify(first_sentence, maxlen)
    
    # 策略2: 如果第一句太长或太短，智能截断
    if len(text) <= maxlen:
        return slugify(text, maxlen)
    
    # 截取到最大长度
    truncated = text[:maxlen]
    
    # 找最后一个词语边界（空格、逗号等）
    last_break = max(
        truncated.rfind(' '),
        truncated.rfind('，'),
        truncated.rfind('、'),
        truncated.rfind('；'),
        truncated.rfind('：'),
    )
    
    # 如果找到合理的断点（不要太靠前），在那里截断
    if last_break > maxlen * 0.7:  # 断点至少在 70% 位置之后
        truncated = truncated[:last_break]
    
    return slugify(truncated, maxlen)

def dedup_key(content: str, ts: datetime) -> str:
    h = hashlib.sha256(content.encode('utf-8')).digest()
    b22 = base64.urlsafe_b64encode(h).decode('ascii').rstrip('=')[:22]
    minute = ts.strftime('%Y%m%d%H%M')
    return f"{b22}@{minute}"

def extract_keywords(text: str, topk: int = 5):
    """提取关键词，带错误处理和日志"""
    try:
        kws = ja.extract_tags(text, topK=topk, withWeight=False, allowPOS=())
        return [k for k in kws if len(k.strip()) > 1]
    except Exception as e:
        logger.warning(f"关键词提取失败: {e}", exc_info=True)
        return []

def generate_ai_title(content: str) -> str:
    """
    使用 AI 生成笔记标题（未来功能）
    
    TODO: 集成 AI 服务生成标题
    
    可选方案：
    1. 使用 OpenAI API (GPT-4/3.5)
    2. 使用本地模型 (如 Ollama)
    3. 使用其他 LLM API
    
    实现示例：
    ```python
    # 方案1: OpenAI
    import openai
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user", 
            "content": f"请为以下笔记生成一个简洁的标题（10-20字）：\n\n{content[:500]}"
        }],
        max_tokens=50
    )
    return response.choices[0].message.content.strip()
    
    # 方案2: 本地模型
    # from ollama import Client
    # client = Client()
    # response = client.generate(
    #     model='llama2',
    #     prompt=f'生成标题：{content[:500]}'
    # )
    # return response['response']
    ```
    
    Args:
        content: 笔记内容
    
    Returns:
        AI 生成的标题，如果失败则返回 None
    """
    # 暂未实现，返回 None 表示使用默认策略
    return None

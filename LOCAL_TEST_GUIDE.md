# ClipNotes 本地测试指南

本指南将带你一步步在本地环境中运行和测试 ClipNotes 项目。

## 📋 前置要求

- **Python 3.9+**（推荐 3.11）
- **pip** 或 **uv**（Python 包管理工具）
- （可选）**Docker & Docker Compose**（如果使用容器化部署）
- （可选）**VSCode + REST Client 插件**（用于测试 HTTP 请求）

---

## 🚀 方式一：直接运行（推荐用于开发）

### 1️⃣ 创建虚拟环境

```bash
cd /Users/suliangliang/Documents/clipnotes

# 使用 Python venv
python3 -m venv .venv

# 或使用 uv（更快）
uv venv

# 激活虚拟环境
source .venv/bin/activate
```

### 2️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 3️⃣ 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env（本地测试使用默认值即可）
# 对于本地测试，默认配置已经足够，无需修改
```

### 4️⃣ 启动服务

```bash
# 开发模式（自动重载）
uvicorn app_server:app --reload --port 8000

# 或指定 host（允许局域网访问）
uvicorn app_server:app --reload --host 0.0.0.0 --port 8000
```

**看到以下输出说明启动成功：**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 5️⃣ 测试 API

#### 方法1：使用 curl

```bash
# 健康检查
curl http://localhost:8000/healthz

# 创建笔记
curl -X POST http://localhost:8000/notes \
  -H "Authorization: Bearer dev-token-please-change" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: localdev" \
  -d '{
    "content": "这是我的第一条测试笔记！今天学习了 FastAPI 和 MCP 集成。",
    "tags": ["FastAPI", "MCP", "Python"],
    "topic": "学习笔记"
  }'

# 列出最近的笔记
curl -H "Authorization: Bearer dev-token-please-change" \
     -H "X-User-Id: localdev" \
     http://localhost:8000/notes?limit=5

# 搜索笔记
curl -H "Authorization: Bearer dev-token-please-change" \
     -H "X-User-Id: localdev" \
     "http://localhost:8000/notes/search?q=FastAPI&limit=10"
```

#### 方法2：使用 VSCode REST Client

1. 安装 VSCode 扩展：[REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)
2. 打开 `examples/test.http`
3. 点击请求上方的 **"Send Request"** 按钮

#### 方法3：使用 Python 脚本

创建测试脚本 `test_api.py`：

```python
import httpx

BASE_URL = "http://localhost:8000"
TOKEN = "dev-token-please-change"
TENANT = "localdev"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-User-Id": TENANT,
    "Content-Type": "application/json"
}

# 测试健康检查
r = httpx.get(f"{BASE_URL}/healthz")
print("✅ 健康检查:", r.json())

# 创建笔记
note_data = {
    "content": "Python 异步编程要点：使用 async/await 关键字...",
    "tags": ["Python", "异步编程"],
    "topic": "编程技巧",
    "context_before": [
        {"role": "user", "text": "什么是异步编程？"},
        {"role": "assistant", "text": "异步编程是一种并发编程模式..."}
    ]
}
r = httpx.post(f"{BASE_URL}/notes", headers=headers, json=note_data)
print("✅ 创建笔记:", r.json())

# 列出笔记
r = httpx.get(f"{BASE_URL}/notes?limit=5", headers=headers)
print("✅ 最近笔记:", r.json())

# 搜索笔记
r = httpx.get(f"{BASE_URL}/notes/search?q=Python&limit=10", headers=headers)
print("✅ 搜索结果:", r.json())
```

运行测试：
```bash
python test_api.py
```

### 6️⃣ 查看保存的文件

```bash
# 查看数据目录结构
tree data/

# 示例输出：
# data/
# └── localdev/
#     ├── 2025/
#     │   └── 10/
#     │       └── 22/
#     │           ├── xxx.json
#     │           └── xxx.md
#     └── index/
#         └── dedup_index.json

# 查看 JSON 文件
cat data/localdev/2025/10/22/*.json | jq .

# 查看 Markdown 文件
cat data/localdev/2025/10/22/*.md
```

---

## 🐳 方式二：使用 Docker Compose

### 1️⃣ 启动容器

```bash
cd /Users/suliangliang/Documents/clipnotes

# 启动服务（后台运行）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 2️⃣ 测试

使用上面的 curl 或其他方法测试 API（端口仍然是 8000）。

---

## 🤖 测试 MCP Server

### 方法1：使用 MCP Inspector（推荐）

```bash
# 安装 MCP Inspector
pip install mcp

# 启动服务（在另一个终端）
uvicorn app_server:app --port 8000

# 使用 MCP Inspector 连接
mcp dev http://localhost:8000/mcp
```

### 方法2：使用 httpx 直接调用

创建 `test_mcp.py`：

```python
import httpx
import json

MCP_URL = "http://localhost:8000/mcp"

# 1. 列出可用工具
response = httpx.post(
    MCP_URL,
    json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
)
print("📝 可用工具:", json.dumps(response.json(), indent=2, ensure_ascii=False))

# 2. 调用 add_note 工具
response = httpx.post(
    MCP_URL,
    json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "add_note",
            "arguments": {
                "mode": "explicit",
                "content": "今天学习了 MCP 协议，它让 AI 模型可以调用外部工具！",
                "tags": ["MCP", "AI"],
                "topic": "技术学习",
                "receipt_style": "check"
            }
        }
    }
)
print("✅ 添加笔记结果:", response.json())

# 3. 调用 list_notes 工具
response = httpx.post(
    MCP_URL,
    json={
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "list_notes",
            "arguments": {
                "limit": 5
            }
        }
    }
)
print("📋 笔记列表:", response.json())
```

运行：
```bash
python test_mcp.py
```

---

## 🧪 完整测试流程示例

创建一个完整的测试脚本 `full_test.py`：

```python
#!/usr/bin/env python3
"""ClipNotes 完整功能测试"""

import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TOKEN = "dev-token-please-change"
TENANT = "test-user-" + datetime.now().strftime("%Y%m%d%H%M%S")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-User-Id": TENANT,
}

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    r = httpx.get(f"{BASE_URL}/healthz")
    assert r.status_code == 200
    print(f"✅ 健康检查通过: {r.json()}\n")

def test_create_note():
    """测试创建笔记"""
    print("📝 测试创建笔记...")
    note = {
        "content": "FastAPI 是一个现代、高性能的 Python Web 框架，支持异步、自动文档生成。",
        "tags": ["Python", "FastAPI", "Web"],
        "topic": "技术学习",
        "source": {
            "thread_title": "测试会话",
            "msg_id": "msg-001"
        },
        "context_before": [
            {"role": "user", "text": "什么是 FastAPI？"},
            {"role": "assistant", "text": "FastAPI 是一个现代、高性能的 Python Web 框架..."}
        ]
    }
    r = httpx.post(f"{BASE_URL}/notes", headers=headers, json=note)
    assert r.status_code == 200
    data = r.json()
    print(f"✅ 创建成功: ID={data['id']}, Title={data['title']}\n")
    return data['id']

def test_list_notes():
    """测试列出笔记"""
    print("📋 测试列出笔记...")
    r = httpx.get(f"{BASE_URL}/notes?limit=5", headers=headers)
    assert r.status_code == 200
    data = r.json()
    print(f"✅ 查询成功: 共 {len(data['items'])} 条笔记")
    for item in data['items']:
        print(f"   - [{item['saved_at'][:19]}] {item['title']}")
    print()

def test_search_notes():
    """测试搜索笔记"""
    print("🔎 测试搜索笔记...")
    r = httpx.get(f"{BASE_URL}/notes/search?q=FastAPI&limit=10", headers=headers)
    assert r.status_code == 200
    data = r.json()
    print(f"✅ 搜索成功: 找到 {len(data['items'])} 条结果\n")

def test_duplicate_prevention():
    """测试去重机制"""
    print("🔄 测试去重机制...")
    note = {
        "content": "相同的内容不应该被重复保存",
        "tags": ["测试"],
    }
    # 第一次创建
    r1 = httpx.post(f"{BASE_URL}/notes", headers=headers, json=note)
    id1 = r1.json()['id']
    
    # 第二次创建（应该返回相同ID）
    r2 = httpx.post(f"{BASE_URL}/notes", headers=headers, json=note)
    id2 = r2.json()['id']
    
    assert id1 == id2, "去重失败：生成了不同的ID"
    print(f"✅ 去重成功: 两次创建返回相同ID {id1}\n")

def test_delete_note(note_id):
    """测试删除笔记"""
    print(f"🗑️  测试删除笔记 {note_id}...")
    r = httpx.delete(f"{BASE_URL}/notes/{note_id}", headers=headers)
    assert r.status_code == 200
    print(f"✅ 删除成功\n")

def test_mcp_tools():
    """测试 MCP 工具"""
    print("🤖 测试 MCP 工具...")
    
    # 列出工具
    r = httpx.post(
        f"{BASE_URL}/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
    )
    tools = r.json()['result']['tools']
    print(f"✅ MCP 工具列表: {[t['name'] for t in tools]}\n")

if __name__ == "__main__":
    print(f"🚀 开始测试 ClipNotes (租户: {TENANT})\n")
    print("=" * 60)
    
    try:
        test_health()
        note_id = test_create_note()
        test_list_notes()
        test_search_notes()
        test_duplicate_prevention()
        test_mcp_tools()
        test_delete_note(note_id)
        
        print("=" * 60)
        print("🎉 所有测试通过！\n")
        
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
    except Exception as e:
        print(f"❌ 错误: {e}")
```

运行完整测试：
```bash
python full_test.py
```

---

## 🐛 常见问题排查

### 问题1：端口被占用
```bash
# 错误: Address already in use
# 解决: 更换端口或杀死占用进程
lsof -ti:8000 | xargs kill -9
# 或使用其他端口
uvicorn app_server:app --port 8001
```

### 问题2：依赖安装失败
```bash
# 升级 pip
pip install --upgrade pip

# 如果是 M1/M2 Mac，某些包可能需要特殊处理
# 使用 conda 或指定架构
```

### 问题3：权限错误
```bash
# 确保 data 目录有写权限
chmod -R 755 data/
```

### 问题4：401 Unauthorized
- 检查 Authorization header 是否正确
- 确认 token 与 .env 中的 API_TOKENS 匹配
- 检查 Bearer 前缀（注意大小写和空格）

### 问题5：找不到模块
```bash
# 确保在项目根目录
cd /Users/suliangliang/Documents/clipnotes

# 确保虚拟环境已激活
source .venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
```

---

## 📊 测试检查清单

- [ ] ✅ 健康检查接口正常
- [ ] ✅ 创建笔记成功，返回完整 Note 对象
- [ ] ✅ 列出笔记功能正常
- [ ] ✅ 搜索笔记功能正常
- [ ] ✅ 删除笔记功能正常
- [ ] ✅ 去重机制工作正常（相同内容返回相同ID）
- [ ] ✅ JSON 文件正确保存到 data 目录
- [ ] ✅ Markdown 文件正确生成
- [ ] ✅ 自动提取标签功能正常（使用 jieba）
- [ ] ✅ 上下文对话正确保存在 MD 文件中
- [ ] ✅ MCP 工具可以正常列出和调用
- [ ] ✅ 多租户隔离正常（不同 X-User-Id 数据分离）

---

## 🎯 下一步

测试通过后，你可以：

1. **连接 ChatGPT**：参考主 README 的 "连接 ChatGPT" 部分
2. **切换到 OSS 存储**：修改 .env 中的存储配置
3. **部署到服务器**：使用 nginx 反向代理 + HTTPS
4. **扩展功能**：添加向量搜索、AI 摘要等

祝测试顺利！🚀


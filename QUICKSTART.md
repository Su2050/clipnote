# ClipNotes 快速开始指南 ⚡

## 📦 一键启动（本地测试）

```bash
# 1. 创建虚拟环境并安装依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. 配置环境变量（本地测试使用默认值即可）
cp .env.example .env

# 3. 启动服务
./start_server.sh
# 或手动启动：uvicorn app_server:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/healthz

## 🧪 快速测试

```bash
# 创建笔记
curl -X POST http://localhost:8000/notes \
  -H "Authorization: Bearer dev-token-please-change" \
  -H "Content-Type: application/json" \
  -d '{"content": "我的第一条笔记！"}'

# 列出笔记
curl -H "Authorization: Bearer dev-token-please-change" \
     'http://localhost:8000/notes?limit=5'

# 搜索笔记
curl -H "Authorization: Bearer dev-token-please-change" \
     'http://localhost:8000/notes/search?q=笔记'
```

## 📁 数据存储位置

```
./data/
└── localdev/              # 租户目录
    ├── 2025/10/22/        # 按日期分层
    │   ├── xxx.json       # 结构化数据
    │   └── xxx.md         # 可读版本（含上下文）
    └── index/
        └── dedup_index.json
```

查看笔记：
```bash
# 查看所有 Markdown 笔记
find data -name "*.md" -exec echo "=== {} ===" \; -exec cat {} \; -exec echo "" \;

# 或使用你喜欢的 Markdown 查看器
open data/localdev/2025/10/22/*.md
```

## 🛑 停止服务

```bash
./stop_server.sh
# 或手动：Ctrl+C（如果在前台运行）
```

## 🎯 核心功能演示

### 1. 创建笔记（自动提取标签）
```python
import httpx

headers = {
    "Authorization": "Bearer dev-token-please-change",
    "Content-Type": "application/json"
}

# 不指定标签，系统会自动提取关键词
note = {
    "content": "今天学习了 Docker 容器化技术，通过 docker-compose 可以快速部署应用。"
}

r = httpx.post("http://localhost:8000/notes", headers=headers, json=note)
print(r.json()['tags'])  # 自动提取: ['Docker', 'docker', 'compose', ...]
```

### 2. 保存对话上下文
```python
note = {
    "content": "FastAPI 的主要优势是性能高、开发快、自动生成文档。",
    "topic": "技术问答",
    "source": {
        "thread_title": "FastAPI 学习笔记",
        "msg_id": "msg-123"
    },
    "context_before": [
        {"role": "user", "text": "FastAPI 有什么优势？"},
        {"role": "assistant", "text": "FastAPI 的主要优势..."}
    ]
}

r = httpx.post("http://localhost:8000/notes", headers=headers, json=note)
```

生成的 Markdown 会包含完整上下文：
```markdown
# FastAPI 的主要优势是性能高、开发快、自动生成文档。
- 时间：2025-10-22T...
- 标签：FastAPI, 性能, 文档
- 主题：技术问答

## 原文
FastAPI 的主要优势是性能高、开发快、自动生成文档。

### 上下文（前 3 轮）
- **user**：FastAPI 有什么优势？
- **assistant**：FastAPI 的主要优势...
```

### 3. 去重机制
```python
# 相同内容在同一分钟内只会保存一次
note = {"content": "重复内容测试"}

r1 = httpx.post("http://localhost:8000/notes", headers=headers, json=note)
r2 = httpx.post("http://localhost:8000/notes", headers=headers, json=note)

print(r1.json()['id'] == r2.json()['id'])  # True
```

## 🌐 连接 ChatGPT（Apps SDK）

1. **公网暴露**（本地开发）
   ```bash
   # 使用 ngrok
   ngrok http 8000
   # 获得公网 URL: https://xxx.ngrok.io
   ```

2. **ChatGPT 配置**
   - 进入 Settings → Apps & Connectors
   - 开启 Developer Mode
   - Create Connector:
     - Name: ClipNotes
     - URL: `https://xxx.ngrok.io/mcp`（注意：目前 MCP 功能需要进一步完善）
   
3. **使用召唤词**
   - `记：今天学到的重要知识点`
   - `摘：上一条`
   - `列：最近5条`

**注意**：当前版本的 MCP 集成是基础版本，完整的 ChatGPT 集成功能正在开发中。REST API 已完全可用。

## 🔧 配置说明

编辑 `.env` 文件：

```bash
# 存储方式
STORAGE_PROVIDER=local        # 本地文件系统
# STORAGE_PROVIDER=aliyun_oss  # 切换到阿里云 OSS

# 本地存储配置
DATA_DIR=./data

# 阿里云 OSS 配置（如果使用）
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ALIYUN_OSS_ACCESS_KEY_ID=your_ak
ALIYUN_OSS_ACCESS_KEY_SECRET=your_sk
ALIYUN_OSS_BUCKET=your_bucket
ALIYUN_OSS_PREFIX=clipnotes/

# 鉴权（⚠️ 生产环境必须修改）
API_TOKENS=your-secure-token-here

# 多租户
DEFAULT_TENANT=localdev
```

## 📚 更多资源

- **完整文档**: [LOCAL_TEST_GUIDE.md](LOCAL_TEST_GUIDE.md)
- **API 文档**: http://localhost:8000/docs（启动服务后访问）
- **OpenAPI 规范**: [openapi/notes-openapi.yaml](openapi/notes-openapi.yaml)
- **召唤词示例**: [examples/summon_phrases.md](examples/summon_phrases.md)
- **HTTP 测试用例**: [examples/test.http](examples/test.http)（VSCode REST Client）

## 🐛 常见问题

### 端口被占用
```bash
# 查看占用进程
lsof -i :8000
# 杀死进程
./stop_server.sh
```

### 依赖冲突
```bash
# 重新创建虚拟环境
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 权限错误
```bash
chmod -R 755 data/
chmod +x start_server.sh stop_server.sh
```

### 找不到模块
```bash
# 确保在项目根目录并激活了虚拟环境
cd /Users/suliangliang/Documents/clipnotes
source .venv/bin/activate
```

## 💡 开发技巧

### 实时查看日志
```bash
# 服务日志会在终端实时显示
# 或使用 --log-level debug 查看详细日志
uvicorn app_server:app --reload --log-level debug
```

### 清空测试数据
```bash
rm -rf data/localdev/*
# 或删除特定日期
rm -rf data/localdev/2025/10/22/
```

### 使用 VSCode REST Client 测试
1. 安装扩展：REST Client
2. 打开 `examples/test.http`
3. 点击 "Send Request"

### Python 交互式测试
```python
import httpx

# 创建会话
client = httpx.Client(
    base_url="http://localhost:8000",
    headers={"Authorization": "Bearer dev-token-please-change"}
)

# 测试 API
r = client.get("/healthz")
print(r.json())

# 创建笔记
r = client.post("/notes", json={"content": "交互式测试笔记"})
print(r.json()['id'])
```

## 🚀 生产部署提示

1. **使用强密码**: 修改 `.env` 中的 `API_TOKENS`
2. **HTTPS**: 使用 nginx 反向代理 + Let's Encrypt
3. **云存储**: 切换到 `aliyun_oss` 存储
4. **进程管理**: 使用 systemd 或 supervisord
5. **监控**: 添加健康检查和日志监控
6. **备份**: 定期备份 data 目录或 OSS bucket

---

**祝你使用愉快！** 🎉

有问题查看完整文档或提交 Issue。


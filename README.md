# ClipNotes 📝

<div align="center">

**轻量级聊天内容提取系统 · ChatGPT 最佳伴侣**

在 ChatGPT 对话中，一键保存精彩内容到本地 / OSS

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[快速开始](#快速开始) • [ChatGPT 集成](#chatgpt-集成) • [文档](#文档)

</div>

---

## ✨ 特性

- 🚀 **一键保存** - 对话中直接使用召唤词 `记：内容`、`摘：上一条` 秒存笔记
- 📁 **双格式存储** - 同时生成 JSON（结构化）+ Markdown（可读性）
- 🏷️ **智能标签** - 自动提取关键词，支持中文分词（jieba）
- 🔄 **上下文保存** - 完整保存对话上下文，还原聊天场景
- 🎯 **自动去重** - 基于内容哈希，同一分钟内相同内容只保存一次
- 💾 **灵活存储** - 支持本地文件系统 / 阿里云 OSS，一键切换
- 🔐 **多租户** - 通过 `X-User-Id` 实现用户隔离
- 🌐 **ChatGPT 集成** - 通过 Custom GPT + Actions 无缝对接
- 🐳 **开箱即用** - 提供 Docker Compose 一键部署

## 🎯 使用场景

- 💡 **知识管理** - 随手记录学习要点和灵感
- 📚 **会话归档** - 保存重要的 AI 对话记录
- 🔖 **内容收藏** - 快速收集有价值的信息片段
- 📖 **笔记整理** - 自动分类、标签化管理笔记

## 🚀 快速开始

### 前置要求

- Python 3.13+
- pip / uv

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/clipnotes.git
cd clipnotes

# 2. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 修改必要配置（如 API_TOKENS）

# 5. 启动服务
./start_server.sh
# 或手动：uvicorn app_server:app --host 0.0.0.0 --port 8000
```

### 验证安装

访问 http://localhost:8000/docs 查看 API 文档

```bash
# 健康检查
curl http://localhost:8000/healthz

# 创建测试笔记
curl -X POST http://localhost:8000/notes \
  -H "Authorization: Bearer dev-token-please-change" \
  -H "Content-Type: application/json" \
  -d '{"content": "我的第一条笔记！"}'

# 查看笔记
ls -la data/localdev/$(date +%Y/%m/%d)/
```

📖 **详细教程**: 查看 [QUICKSTART.md](QUICKSTART.md) 和 [LOCAL_TEST_GUIDE.md](LOCAL_TEST_GUIDE.md)

## 🤖 ChatGPT 集成

### 方式一：Custom GPT + Actions（推荐）

#### 1. 公网暴露（本地开发）

```bash
# 安装 ngrok
brew install ngrok  # macOS
# 或访问 https://ngrok.com 下载

# 注册并配置 authtoken
ngrok config add-authtoken YOUR_TOKEN

# 启动服务和 ngrok
./start_with_ngrok.sh
# 记下 ngrok URL（如 https://xxx.ngrok-free.dev）
```

#### 2. 创建 Custom GPT

1. 访问 https://chat.openai.com/gpts/editor
2. 配置 GPT：
   - **名称**: ClipNotes 笔记助手
   - **描述**: 快速保存聊天内容到笔记系统
   - **Instructions**: 使用 `优化的Instructions.txt` 中的内容（见 [CHATGPT_快速配置.md](CHATGPT_快速配置.md)）

#### 3. 配置 Actions

1. 点击 "Create new action"
2. 导入 Schema：复制 `chatgpt_final.yaml` 内容
3. 配置 Authentication：
   - Type: **API Key**
   - Auth Type: **Bearer**
   - API Key: 你的 `API_TOKENS` 值
4. 设置 Privacy Policy：https://su2050.github.io/gpt_privacy/privacy.html
5. 点击 **Update** 保存

#### 4. 开始使用

在 ChatGPT 对话中：
- `记：FastAPI 的性能优势在于异步处理和类型检查`
- `摘：上一条`（保存上一条 AI 回复）
- `列：最近5条`（查看最近的笔记）

📖 **完整配置**: 查看 [CHATGPT_快速配置.md](CHATGPT_快速配置.md)

### 方式二：MCP Server（实验性）

```bash
# MCP 端点在同一进程
# 访问：http://localhost:8000/mcp/sse
```

⚠️ **注意**: MCP 集成目前处于实验阶段，推荐使用 Custom GPT + Actions。

## 📦 技术栈

- **框架**: [FastAPI](https://fastapi.tiangolo.com) - 高性能异步 Web 框架
- **数据验证**: [Pydantic](https://docs.pydantic.dev) - 类型安全的数据模型
- **中文分词**: [jieba](https://github.com/fxsjy/jieba) - 关键词提取
- **云存储**: [oss2](https://github.com/aliyun/aliyun-oss-python-sdk) - 阿里云 OSS SDK
- **MCP**: [fastmcp](https://github.com/jlowin/fastmcp) - Model Context Protocol

## 📂 项目结构

```
clipnotes/
├── app_server.py          # FastAPI 应用入口
├── clipnotes/             # 核心模块
│   ├── api/
│   │   └── notes.py       # REST API 路由
│   ├── mcp_server/
│   │   └── server.py      # MCP 工具集成
│   ├── storage/
│   │   ├── local_fs.py    # 本地文件存储
│   │   └── aliyun_oss.py  # 阿里云 OSS 存储
│   ├── config.py          # 配置管理
│   ├── models.py          # 数据模型
│   └── utils.py           # 工具函数
├── data/                  # 本地数据目录
│   └── {tenant}/
│       └── YYYY/MM/DD/
│           ├── *.json     # 结构化数据
│           └── *.md       # 可读版本
├── openapi/
│   └── notes-openapi.yaml # OpenAPI 规范
├── examples/
│   ├── test.http          # API 测试用例
│   └── summon_phrases.md  # 召唤词示例
├── privacy/
│   └── privacy.html       # 隐私政策（用于 GPT）
├── chatgpt_final.yaml     # ChatGPT Actions Schema
├── docker-compose.yml     # Docker 部署配置
└── requirements.txt       # Python 依赖
```

## 🔧 配置说明

编辑 `.env` 文件：

```bash
# === 存储配置 ===
STORAGE_PROVIDER=local           # local 或 aliyun_oss
DATA_DIR=./data                  # 本地存储目录

# === 阿里云 OSS（可选）===
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ALIYUN_OSS_ACCESS_KEY_ID=your_ak
ALIYUN_OSS_ACCESS_KEY_SECRET=your_sk
ALIYUN_OSS_BUCKET=your_bucket
ALIYUN_OSS_PREFIX=clipnotes/

# === 鉴权 ===
API_TOKENS=your-secure-token-here   # ⚠️ 生产环境必须修改

# === 多租户 ===
DEFAULT_TENANT=localdev             # 默认租户ID
```

## 📡 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/healthz` | 健康检查 |
| `POST` | `/notes` | 创建笔记 |
| `GET` | `/notes` | 列出笔记（分页、过滤） |
| `GET` | `/notes/search` | 搜索笔记 |
| `DELETE` | `/notes/{note_id}` | 删除笔记 |

详细的 API 文档：http://localhost:8000/docs（启动服务后访问）

## 📚 文档

| 文档 | 说明 |
|------|------|
| [QUICKSTART.md](QUICKSTART.md) | 快速开始指南 |
| [LOCAL_TEST_GUIDE.md](LOCAL_TEST_GUIDE.md) | 本地测试详细教程 |
| [CHATGPT_快速配置.md](CHATGPT_快速配置.md) | ChatGPT 集成配置 |
| [openapi/notes-openapi.yaml](openapi/notes-openapi.yaml) | OpenAPI 规范 |
| [examples/test.http](examples/test.http) | HTTP 测试用例 |

## 🐳 Docker 部署

```bash
# 编辑 .env 配置文件
cp .env.example .env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 🔐 安全建议

1. **修改默认 Token**: 编辑 `.env` 中的 `API_TOKENS`，使用强密码
2. **启用 HTTPS**: 生产环境使用 nginx + Let's Encrypt
3. **限制访问**: 配置防火墙规则，仅开放必要端口
4. **定期备份**: 备份 `data/` 目录或 OSS bucket
5. **更新依赖**: 定期运行 `pip install --upgrade -r requirements.txt`

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com) - 优雅的 Web 框架
- [jieba](https://github.com/fxsjy/jieba) - 强大的中文分词工具
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP 协议实现

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star！**

Made with ❤️ by [Your Name]

</div>

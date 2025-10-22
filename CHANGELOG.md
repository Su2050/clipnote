# 更新日志

本文档记录 ClipNotes 项目的重要变更。

## [1.0.0] - 2025-10-22

### ✨ 新增
- 完整的 REST API（创建、列表、搜索、删除笔记）
- 双格式存储（JSON + Markdown）
- 智能标签自动提取（jieba 中文分词）
- 对话上下文保存
- 内容自动去重（基于哈希）
- 本地文件系统存储
- 阿里云 OSS 存储支持
- MCP Server 集成（实验性）
- ChatGPT Custom GPT + Actions 集成
- Bearer Token 认证
- 多租户支持（X-User-Id）
- Docker Compose 部署配置
- OpenAPI 3.1.0 规范

### 📚 文档
- README.md - 完整的项目介绍
- QUICKSTART.md - 快速开始指南
- LOCAL_TEST_GUIDE.md - 本地测试详细教程
- CHATGPT_快速配置.md - ChatGPT 集成配置指南
- LICENSE - MIT 许可证

### 🔧 配置
- `.env.example` - 环境变量模板
- `docker-compose.yml` - Docker 部署
- `nginx.example.conf` - Nginx 反向代理示例
- `chatgpt_final.yaml` - ChatGPT Actions Schema

### 🚀 脚本
- `start_server.sh` - 启动 API 服务
- `start_with_ngrok.sh` - 启动服务 + ngrok 公网暴露
- `stop_all.sh` - 停止所有服务

### 🗂️ 项目优化
- 删除临时测试文件和重复 schema
- 统一文档风格和格式
- 优化项目结构
- 增强 .gitignore 规则

### 🔐 安全
- Bearer Token 认证
- 环境变量配置管理
- 支持自定义 API Token

### 🐛 修复
- 修复 Pydantic 版本冲突（升级到 2.10.1+）
- 修复 MCP Server 集成问题
- 修复 ChatGPT Actions Schema 验证问题

---

## 版本说明

版本号遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)

- **主版本号（Major）**：不兼容的 API 修改
- **次版本号（Minor）**：向下兼容的功能性新增
- **修订号（Patch）**：向下兼容的问题修正

## 反馈

如有问题或建议，请在 [GitHub Issues](https://github.com/yourusername/clipnotes/issues) 提出。


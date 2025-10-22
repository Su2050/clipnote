# ChatGPT 实战配置 - 10分钟搞定 🚀

## ✅ 准备工作（你现在做的）

1. **注册 ngrok**: https://dashboard.ngrok.com/signup
2. **复制 authtoken**（登录后在 Dashboard 首页）
3. **配置 token**：
   ```bash
   ngrok config add-authtoken 你的token
   ```

## 🚀 启动服务（配置好 token 后）

```bash
cd /Users/suliangliang/Documents/clipnotes

# 一键启动（包含 ClipNotes + ngrok）
./start_with_ngrok.sh
```

**会看到类似输出：**
```
📍 公网地址: https://abc123.ngrok-free.app
```

**复制这个 URL！** 📋

---

## 🤖 在 ChatGPT 中配置

### 第 1 步：创建 GPT

访问：https://chatgpt.com/gpts/editor

### 第 2 步：基本信息

- **Name**: ClipNotes 笔记助手
- **Description**: 快速保存对话内容到笔记
- **Instructions**（复制粘贴）:

```
你是专业的笔记助手。核心规则：

1. 识别召唤词：
   - "记：<内容>" → 保存指定内容
   - "摘：上一条" / "记录" / "保存" → 保存你刚才的完整回答
   - "列：最近N条" → 列出笔记

2. 保存规则（⚠️ 重要）：
   - 必须保存【完整内容】，不要总结、不要省略、不要改写
   - 保持原始格式（代码块、列表、标题等）
   - 包含所有细节和示例
   - 对话内容原文记录

3. 调用方式：
   - 使用 createNote Action
   - content 字段填入【完整原文】
   - 返回：✅ 已记：<标题>

示例：
用户："摘：上一条"
→ 将你上一条回复的【完整内容】传给 content 字段
→ 回复："✅ 已记：<从内容提取的标题>"
```

### 第 3 步：配置 Action

点击 **Actions** → **Create new action**

**Schema**（复制 `chatgpt_final.yaml` 的内容，记得改 URL）：

1. 打开项目中的 `chatgpt_final.yaml` 文件
2. 将 `servers` 部分的 URL 改为你的 ngrok 地址
3. 完整复制粘贴到 ChatGPT 的 Schema 输入框

或者直接复制以下内容（记得改 URL）：

```yaml
openapi: 3.1.0
info:
  title: ClipNotes API
  description: 轻量级笔记管理系统
  version: 1.0.0
servers:
  - url: https://你的ngrok地址.ngrok-free.dev
    description: ClipNotes 服务器
paths:
  /notes:
    post:
      operationId: createNote
      summary: 创建笔记
      description: 保存一条新笔记
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - content
              properties:
                content:
                  type: string
                  description: 笔记的完整内容
                tags:
                  type: array
                  items:
                    type: string
                  description: 标签列表（可选，不填会自动提取）
                topic:
                  type: string
                  description: 主题（可选）
                source:
                  type: object
                  properties:
                    thread_title:
                      type: string
                    msg_id:
                      type: string
                context_before:
                  type: array
                  items:
                    type: object
                    properties:
                      role:
                        type: string
                      text:
                        type: string
      responses:
        '200':
          description: 笔记创建成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                    description: 笔记ID
                  title:
                    type: string
                    description: 笔记标题
                  tags:
                    type: array
                    items:
                      type: string
                    description: 提取的标签
                  saved_at:
                    type: string
                    description: 保存时间
    get:
      operationId: listNotes
      summary: 列出笔记
      description: 获取笔记列表
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 10
          description: 返回笔记数量
        - name: topic
          in: query
          schema:
            type: string
          description: 按主题过滤
      responses:
        '200':
          description: 笔记列表
          content:
            application/json:
              schema:
                type: object
                properties:
                  items:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                        title:
                          type: string
                        content:
                          type: string
                        tags:
                          type: array
                          items:
                            type: string
                        saved_at:
                          type: string
                  total:
                    type: integer
```

**⚠️ 注意**：
- 不要在 Schema 中包含 `components` 或 `security` 部分
- 认证信息在下一步单独配置

### 第 4 步：配置认证

- **Authentication**: API Key
- **Auth Type**: Bearer
- **Token**: `dev-token-please-change`

### 第 5 步：测试

点击 **Test** → 选择 `createNote` → 输入：
```json
{
  "content": "测试笔记：集成成功！"
}
```

如果返回成功，点击 **Save**！

---

## 🎉 开始使用！

在你的 GPT 对话中：

```
👤 你：什么是 Docker？

🤖 GPT：Docker 是一个开源的容器化平台...（详细解释）

👤 你：记：上一条

🤖 GPT：✅ 已记：Docker 是一个开源的容器化平台

👤 你：列：最近3条

🤖 GPT：📋 你的笔记：
       1. [2025-10-22 16:30] Docker 是一个开源的容器化平台
       2. [2025-10-22 15:20] Python 异步编程
       3. [2025-10-22 14:10] Git 分支管理
```

---

## 💡 使用技巧

### 1. 随时保存
```
👤：记：今天学到的重点：Kubernetes 用于容器编排
```

### 2. 保存对话
```
👤：摘：上一条
👤：记录              ← 也可以
👤：保存上一条         ← 也可以
```

### 3. 查看笔记
```
👤：列：最近5条
👤：列：最近10条
```

### 4. 自动提取标签
不用手动写标签，系统会自动从内容中提取关键词！

---

## 📁 查看保存的笔记

所有笔记保存在本地：

```bash
# 查看最新笔记
ls -lht data/localdev/**/*.md | head -5

# 查看某个笔记
cat data/localdev/2025/10/22/最新的笔记.md

# 搜索特定主题
grep -r "Docker" data/localdev/ --include="*.md"
```

每条笔记都包含：
- ✅ 完整内容
- ✅ 自动标签
- ✅ 时间戳
- ✅ 对话上下文（前3轮）

---

## 🛑 停止服务

```bash
./stop_all.sh
```

---

## 🐛 常见问题

### Q1: Action 调用失败？
**检查：**
- ngrok 是否在运行？运行 `curl https://你的ngrok地址.ngrok-free.app/healthz`
- Bearer Token 是否是 `dev-token-please-change`？

### Q2: ngrok URL 变了？
免费版 ngrok 每次启动 URL 会变，需要更新 GPT 的 Action Schema。

**解决方案**：
- 付费版 ngrok（固定域名）
- 或部署到自己的服务器

### Q3: 笔记保存到哪里？
```bash
/Users/suliangliang/Documents/clipnotes/data/localdev/
```

---

## 🚀 下一步

1. **多租户**: 修改 `.env` 中的 `DEFAULT_TENANT`，让不同人的笔记分开存储
2. **云端存储**: 配置阿里云 OSS，笔记自动同步到云端
3. **固定域名**: 部署到服务器或使用付费 ngrok

---

**完成配置后，就可以在任何 ChatGPT 对话中随时保存笔记了！** 🎉


# 部署指南

## ✅ 已完成
- [x] 初始化 Git 仓库
- [x] 创建 privacy.html 和 README.md
- [x] 提交到本地仓库

## 🚀 待完成

### 1. 创建 GitHub 仓库

访问：https://github.com/new

- Repository name: `clipnotes-privacy`
- Description: `Privacy policy for ClipNotes GPT`
- **Public** ✅
- 不要勾选 "Add a README file" ❌

### 2. 推送代码

替换 `YOUR_USERNAME` 为你的 GitHub 用户名：

```bash
git remote add origin https://github.com/YOUR_USERNAME/clipnotes-privacy.git
git branch -M main
git push -u origin main
```

### 3. 启用 GitHub Pages

1. 进入仓库页面
2. 点击 **Settings** 标签
3. 左侧菜单找到 **Pages**
4. Source 选择：**Deploy from a branch**
5. Branch 选择：**main** → **/ (root)**
6. 点击 **Save**
7. 等待 1-2 分钟部署完成

### 4. 获取 URL

你的隐私政策 URL 将是：

```
https://YOUR_USERNAME.github.io/clipnotes-privacy/privacy.html
```

### 5. 填入 ChatGPT GPT

1. 打开 GPT 编辑页面：https://chatgpt.com/gpts/editor
2. 滚动到底部的"隐私政策"框
3. 粘贴上面的 URL
4. 点击"更新"
5. 现在可以选择"知道该链接的任何人"分享了！

---

## 🔧 当前目录

你现在在：`/Users/suliangliang/Documents/clipnotes/privacy/`

运行命令时确保在这个目录下：
```bash
cd /Users/suliangliang/Documents/clipnotes/privacy
```

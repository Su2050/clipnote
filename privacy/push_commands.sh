#!/bin/bash
# 推送到 GitHub 的命令
# 请先把 YOUR_USERNAME 替换为你的 GitHub 用户名

# 确保在正确的目录
cd /Users/suliangliang/Documents/clipnotes/privacy

# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/clipnotes-privacy.git

# 重命名分支为 main
git branch -M main

# 推送到 GitHub
git push -u origin main

echo ""
echo "✅ 推送完成！"
echo ""
echo "📍 下一步："
echo "1. 访问你的仓库：https://github.com/YOUR_USERNAME/clipnotes-privacy"
echo "2. 点击 Settings → Pages"
echo "3. 启用 GitHub Pages"
echo ""

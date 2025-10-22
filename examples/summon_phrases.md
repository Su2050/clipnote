# 召唤词建议
- `摘：上一条` → 模式 last_assistant；把上一条助理输出放入 content，并附上 **前 3 轮对话**到 context_before。
- `记：<文本>` → 模式 explicit；解析 `#tag` 到 tags[]。
- `列：最近5条` → list_notes(limit=5)。
- `总结知识点并保存` / `记录` → 语义等同于 `摘：上一条`。
**回执**：统一 `✅ 已记：<短标题>`。

---
name: tech-summary
description: 当需要对采集的技术内容进行深度分析总结时使用此技能
allowed-tools:
  - Read
  - Grep
  - Glob
  - WebFetch
---

## 使用场景

当 `knowledge/raw/` 目录下存在新采集的技术内容文件（如 github-trending 输出的 JSON），需要对每个条目进行深度分析、打分并提炼整体趋势时使用此技能。

## 执行步骤

**Step 1 — 读取最新采集文件**

使用 Glob 扫描 `knowledge/raw/` 目录，按文件名中的日期降序找到最新的采集文件并用 Read 读取其全部内容。若同日存在多个来源文件，逐一读取并合并 `items` 列表后统一处理。

**Step 2 — 逐条深度分析**

对 `items` 中的每个条目依次执行以下分析，必要时用 WebFetch 补充读取项目主页或 README：

- **摘要**：在原有 `summary` 基础上精炼，限 50 字以内，去除套话，直指核心价值
- **技术亮点**：列举 2–3 个具体亮点，必须用事实说话（如架构设计、性能数据、创新机制），不写泛泛描述
- **评分**：按下方评分标准给出 1–10 整数分，并附一句理由（说明评分依据，不超过 20 字）
- **标签建议**：从项目内容归纳 2–4 个英文小写标签，用于后续分类检索（如 `rag`、`inference`、`agent-framework`）

**Step 3 — 趋势发现**

在所有条目分析完成后，从整体视角提炼：

- **共同主题**：本批次项目中反复出现的技术方向或关键词（≥3 个项目共同涉及才算）
- **新概念**：首次出现或近期突然升温的术语、架构模式或工具类别，简述其含义

**Step 4 — 输出分析结果 JSON**

将分析结果写入 `knowledge/analyzed/tech-summary-YYYY-MM-DD.json`，日期取当天执行日期。

## 评分标准

| 分数 | 含义 |
|------|------|
| 9–10 | 改变格局：引入新范式、解决行业痛点或有望成为基础设施 |
| 7–8  | 直接有帮助：可立即应用于实际项目，节省大量时间或提升效果 |
| 5–6  | 值得了解：有一定创新但适用场景受限，或尚不成熟 |
| 1–4  | 可略过：重复造轮子、质量低、或与主题关联度不足 |

## 注意事项

- **评分约束**：每批 15 个项目中，9–10 分的条目不超过 2 个；标准从严，避免分数通胀
- 技术亮点必须来自可验证的事实（代码结构、Benchmark、论文引用等），不得凭印象描述
- 摘要不得复制原始 `summary` 字段，须重新提炼
- 趋势分析基于当批数据，不与历史文件对比（历史对比由其他技能负责）
- 若某条目信息不足以支撑分析，标注 `"insufficient_info": true` 并跳过技术亮点字段

## 输出格式

输出文件路径：`knowledge/analyzed/tech-summary-YYYY-MM-DD.json`

```json
{
  "source": "tech-summary",
  "skill": "tech-summary",
  "analyzed_at": "YYYY-MM-DDTHH:mm:ssZ",
  "raw_file": "knowledge/raw/github-trending-YYYY-MM-DD.json",
  "trends": {
    "common_themes": ["主题1", "主题2"],
    "new_concepts": [
      { "term": "概念名称", "explanation": "简短说明" }
    ]
  },
  "items": [
    {
      "name": "owner/repo",
      "url": "https://github.com/owner/repo",
      "summary": "精炼后的中文摘要，不超过50字",
      "highlights": [
        "亮点1：具体事实描述",
        "亮点2：具体事实描述"
      ],
      "score": 8,
      "score_reason": "评分理由，不超过20字",
      "tags": ["tag1", "tag2", "tag3"]
    }
  ]
}
```

`items` 数组按 `score` 降序排列，分数相同时保持原始顺序。

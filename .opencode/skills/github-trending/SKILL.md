---
name: github-trending
description: 当需要采集 GitHub 热门开源项目时使用此技能
allowed-tools:
  - Read
  - Grep
  - Glob
  - WebFetch
---

## 使用场景

当需要采集 GitHub 上近期热门开源项目，尤其是 AI、LLM、Agent 相关方向的仓库，并生成结构化摘要时使用此技能。

## 执行步骤

**Step 1 — 搜索热门仓库（GitHub API）**

通过 WebFetch 访问 GitHub Trending 页面或 GitHub Search API，按星标数、最近更新时间等维度抓取当日/当周热门仓库列表。

```
https://github.com/trending
https://api.github.com/search/repositories?q=topic:llm&sort=stars&order=desc
```

**Step 2 — 提取仓库信息**

从返回结果中提取每个仓库的以下字段：
- 仓库名称（owner/repo）
- 仓库 URL
- 星标总数（stars）
- 编程语言（language）
- Topics 标签列表
- 仓库描述（description）
- README 摘要（可选，用于撰写中文摘要）

**Step 3 — 过滤**

按以下规则筛选仓库：

- **纳入**：包含关键词 `AI`、`LLM`、`Agent`、`RAG`、`MCP`、`Embedding`、`Fine-tune`、`Inference` 的仓库（名称、描述或 topics 中任意匹配）
- **排除**：名称或描述中含 `awesome`、`awesome-list`、`collection`、`resources` 等聚合列表类仓库

**Step 4 — 去重**

以仓库完整路径（`owner/repo`）为唯一键进行去重，保留星标数最高的条目。若与 `knowledge/raw/` 目录下已有文件中的仓库重复，亦予以排除。

**Step 5 — 撰写中文摘要**

按以下公式为每个仓库生成一句话中文摘要：

> **项目名** + **做什么**（核心功能） + **为什么值得关注**（技术亮点或社区热度）

示例：`LangChain 是一个用于构建 LLM 应用的开发框架，因其丰富的集成生态和活跃的社区而备受关注。`

**Step 6 — 排序并取 Top 15**

按星标数降序排列所有通过过滤的仓库，取前 15 个作为最终输出。

**Step 7 — 输出 JSON 文件**

将结果写入 `knowledge/raw/github-trending-YYYY-MM-DD.json`，日期取当天执行日期。

## 注意事项

- WebFetch 访问 GitHub API 时注意频率限制，未认证请求限 60 次/小时
- README 内容较长时只读取前 3000 字符用于摘要提炼
- 中文摘要应客观准确，避免夸大；不明确的项目宁可跳过，也不要生成误导性描述
- 若某日热门列表与前一日高度重叠（>80%），在输出 JSON 中添加 `"note": "与前日高度重叠"` 字段提示

## 输出格式

输出文件路径：`knowledge/raw/github-trending-YYYY-MM-DD.json`

```json
{
  "source": "github-trending",
  "skill": "github-trending",
  "collected_at": "YYYY-MM-DDTHH:mm:ssZ",
  "items": [
    {
      "name": "owner/repo",
      "url": "https://github.com/owner/repo",
      "summary": "一句话中文摘要：项目名 + 做什么 + 为什么值得关注",
      "stars": 12345,
      "language": "Python",
      "topics": ["llm", "agent", "rag"]
    }
  ]
}
```

`items` 数组按 `stars` 降序排列，最多包含 15 条记录。

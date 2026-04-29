# AGENTS.md — AI 知识库助手

## 项目概述

本项目是一个全自动 AI 技术情报系统：定时从 GitHub Trending 和 Hacker News 采集 AI/LLM/Agent 领域的最新动态，通过国产大模型对原始内容进行结构化分析与摘要，将结果持久化为 JSON 知识条目，并经由 Telegram 和飞书多渠道推送给订阅者。

---

## 技术栈

| 层次 | 技术 |
|------|------|
| 运行时 | Python 3.12 |
| Agent 框架 | LangGraph |
| 编排工具 | OpenCode + 国产大模型（通义 / DeepSeek / 文心） |
| 爬取工具 | OpenClaw |
| 分发渠道 | Telegram Bot API、飞书 Webhook |
| 数据格式 | JSON（知识条目）、Markdown（文章正文） |

---

## 编码规范

- **风格**：严格遵循 PEP 8；所有标识符使用 `snake_case`
- **文档**：函数与类必须写 Google 风格 docstring（`Args:` / `Returns:` / `Raises:` 三段式）
- **日志**：禁止裸 `print()`；统一使用标准库 `logging`，级别不低于 `INFO`
- **类型**：所有公开函数必须标注类型注解（`from __future__ import annotations`）
- **异常**：不捕获裸 `Exception`；捕获具体异常并在 `except` 块内记录日志后重新抛出或处理
- **导入顺序**：标准库 → 第三方库 → 本项目内部模块，组间空一行

---

## 项目结构

```
ai-knowledge-base/
├── AGENTS.md                  # 本文件
├── .opencode/
│   ├── agents/                # Agent 定义文件（YAML / JSON）
│   └── skills/                # 可复用 Skill 定义
├── knowledge/
│   ├── raw/                   # 采集 Agent 输出的原始数据（未经分析）
│   └── articles/              # 分析 Agent 输出的结构化知识条目（JSON）
├── src/
│   ├── collectors/            # 各数据源采集器
│   ├── analyzers/             # AI 分析与摘要模块
│   ├── publishers/            # 分发渠道适配器
│   └── graph/                 # LangGraph 工作流定义
├── tests/                     # 单元 & 集成测试
└── pyproject.toml
```

---

## 知识条目 JSON 格式

每条知识条目存储于 `knowledge/articles/<YYYY-MM-DD>/<id>.json`，字段定义如下：

```jsonc
{
  "id": "gh-2024042701",          // 唯一标识：来源前缀 + 日期 + 序号
  "title": "文章或仓库标题",
  "source": "github_trending",    // 枚举: github_trending | hacker_news
  "source_url": "https://...",    // 原始链接，必填
  "collected_at": "2024-04-27T08:00:00Z",   // ISO 8601 UTC
  "published_at": "2024-04-26T00:00:00Z",   // 原文发布时间，可为 null
  "summary": "AI 生成的中文摘要，100-300 字",
  "key_points": [                 // 3-5 条核心要点
    "要点一",
    "要点二"
  ],
  "tags": ["LLM", "Agent", "RAG"], // 技术标签，小写复数
  "language": "zh",               // 摘要语言
  "status": "published",          // 枚举: raw | analyzed | published | archived
  "distribution": {
    "telegram": true,             // 是否已推送
    "feishu": false
  },
  "raw_file": "knowledge/raw/gh-2024042701.json"  // 指向原始数据
}
```

**字段约束**

- `id`：全局唯一，生成后不可更改
- `source_url`：必须通过 URL 格式校验，不可为空
- `status` 流转顺序：`raw` → `analyzed` → `published` → `archived`，不可逆跳步
- `tags`：每条至少 1 个，至多 10 个；值取自受控词表（见 `src/analyzers/tag_vocab.py`）

---

## Agent 角色概览

| 角色 | 名称 | 职责 | 输入 | 输出 |
|------|------|------|------|------|
| 采集 Agent | `collector` | 定时访问 GitHub Trending 和 Hacker News，过滤 AI/LLM/Agent 相关条目，将原始数据落盘 | 调度触发信号 | `knowledge/raw/*.json` |
| 分析 Agent | `analyzer` | 读取原始数据，调用大模型生成中文摘要、提取关键点和标签，更新 status | `raw` 状态的 JSON 文件 | `knowledge/articles/**/*.json`（status: analyzed） |
| 整理 Agent | `publisher` | 将 `analyzed` 条目按渠道格式化后推送至 Telegram / 飞书，推送成功后更新 distribution 和 status | `analyzed` 状态的 JSON 文件 | 推送结果日志；条目 status 更新为 `published` |

Agent 之间通过 LangGraph 状态机编排，`collector` 完成后触发 `analyzer`，`analyzer` 完成后触发 `publisher`，任意节点失败时整条链路进入 `error` 状态并告警。

---

## 红线（绝对禁止）

以下操作在任何情况下都不允许执行，无论需求如何描述：

1. **禁止修改已发布条目**：`status` 为 `published` 或 `archived` 的 JSON 文件只读，不得覆盖或删除
2. **禁止绕过去重检查**：向分发渠道推送前必须校验 `distribution` 字段，已推送渠道不得重复推送
3. **禁止明文存储凭据**：API Key、Bot Token、Webhook URL 等敏感信息只能通过环境变量或 Secret Manager 注入，不得硬编码在代码或配置文件中并提交 Git
4. **禁止无限重试**：任何网络请求或 API 调用必须设置最大重试次数（≤ 3）和退避策略，不得无限循环
5. **禁止跨越 status 流转顺序**：不得将条目从 `raw` 直接置为 `published`，必须经过 `analyzed` 阶段
6. **禁止采集非 AI 领域内容**：采集器输出的每条原始数据必须包含至少一个 AI/LLM/Agent 相关关键词，否则丢弃

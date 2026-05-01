from __future__ import annotations

TAG_VOCAB: set[str] = {
    # 基础 AI 领域
    "ai",
    "machine learning",
    "deep learning",
    "llm",
    "agent",
    "rag",
    "aigc",
    "multimodal",
    # 模型与框架
    "claude",
    "gpt",
    "deepseek",
    "qwen",
    "gemini",
    "ollama",
    "langchain",
    "langgraph",
    "transformers",
    "diffusers",
    # 应用方向
    "code analysis",
    "code generation",
    "video generation",
    "image generation",
    "voice",
    "finance",
    "trading",
    "search",
    "recommendation",
    # 基础设施与工具
    "mcp",
    "prompt engineering",
    "fine tuning",
    "rlhf",
    "quantization",
    "inference",
    "training",
    "vector database",
    "embedding",
    # 开源与生态
    "open source",
    "developer tools",
    "cli",
    "api",
    "middleware",
    "proxy",
}

TAG_ALIASES: dict[str, str] = {
    "ml": "machine learning",
    "dl": "deep learning",
    "large language model": "llm",
    "large language models": "llm",
    "ai agent": "agent",
    "ai agents": "agent",
    "multi-agent": "agent",
    "multi agent": "agent",
    "gpt-4": "gpt",
    "gpt-4o": "gpt",
    "generative ai": "aigc",
    "finetune": "fine tuning",
    "finetuning": "fine tuning",
    "vector db": "vector database",
    "devtools": "developer tools",
    "codex": "code generation",
    "copilot": "code generation",
    "text to video": "video generation",
    "text-to-video": "video generation",
    "tts": "voice",
    "speech": "voice",
    "video gen": "video generation",
}


def normalize_tag(raw: str) -> str | None:
    tag = raw.strip().lower()
    if tag in TAG_VOCAB:
        return tag
    if tag in TAG_ALIASES:
        return TAG_ALIASES[tag]
    return None


def validate_tags(tags: list[str]) -> list[str]:
    normalized: list[str] = []
    for t in tags:
        n = normalize_tag(t)
        if n is not None and n not in normalized:
            normalized.append(n)
    return normalized

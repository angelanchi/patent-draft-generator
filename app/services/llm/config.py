"""
LLM 提供商配置

包含所有支持的 LLM 提供商的元數據和推薦配置
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class ModelInfo(BaseModel):
    """模型信息"""
    name: str
    display_name: str
    description: str
    context_window: int
    is_default: bool = False


class ProviderInfo(BaseModel):
    """提供商信息"""
    name: str
    display_name: str
    api_key_url: str
    api_key_prefix: str
    models: List[ModelInfo]


# 提供商配置
PROVIDER_CONFIGS: Dict[str, ProviderInfo] = {
    "openai": ProviderInfo(
        name="openai",
        display_name="OpenAI",
        api_key_url="https://platform.openai.com/api-keys",
        api_key_prefix="sk-",
        models=[
            ModelInfo(
                name="gpt-4-turbo",
                display_name="GPT-4 Turbo",
                description="最新的 GPT-4 模型，性能強大，適合複雜章節",
                context_window=128000,
                is_default=True
            ),
            ModelInfo(
                name="gpt-4",
                display_name="GPT-4",
                description="GPT-4 標準版，性能優異",
                context_window=8192
            ),
            ModelInfo(
                name="gpt-3.5-turbo",
                display_name="GPT-3.5 Turbo",
                description="經濟實惠的選擇，適合簡單章節",
                context_window=16385
            )
        ]
    ),

    "claude": ProviderInfo(
        name="claude",
        display_name="Anthropic Claude",
        api_key_url="https://console.anthropic.com/settings/keys",
        api_key_prefix="sk-ant-",
        models=[
            ModelInfo(
                name="claude-3-5-sonnet-20241022",
                display_name="Claude 3.5 Sonnet",
                description="最新的 Claude 3.5，性價比極高，推薦使用",
                context_window=200000,
                is_default=True
            ),
            ModelInfo(
                name="claude-opus-4.5-20251101",
                display_name="Claude Opus 4.5",
                description="最先進的 Claude 模型，適合最複雜的任務",
                context_window=200000
            ),
            ModelInfo(
                name="claude-3-opus-20240229",
                display_name="Claude 3 Opus",
                description="Claude 3 最強版本，適合複雜推理",
                context_window=200000
            ),
            ModelInfo(
                name="claude-3-haiku-20240307",
                display_name="Claude 3 Haiku",
                description="最快速且經濟的 Claude 模型",
                context_window=200000
            )
        ]
    ),

    "gemini": ProviderInfo(
        name="gemini",
        display_name="Google Gemini",
        api_key_url="https://aistudio.google.com/app/apikey",
        api_key_prefix="AIza",
        models=[
            ModelInfo(
                name="gemini-1.5-pro",
                display_name="Gemini 1.5 Pro",
                description="功能強大的 Gemini 模型，適合複雜任務",
                context_window=2000000,
                is_default=True
            ),
            ModelInfo(
                name="gemini-1.5-flash",
                display_name="Gemini 1.5 Flash",
                description="快速且經濟，性價比最高",
                context_window=1000000
            ),
            ModelInfo(
                name="gemini-2.0-flash-exp",
                display_name="Gemini 2.0 Flash (實驗版)",
                description="最新實驗版本，目前免費",
                context_window=1000000
            )
        ]
    ),

    "qwen": ProviderInfo(
        name="qwen",
        display_name="阿里通義千問",
        api_key_url="https://dashscope.console.aliyun.com/apiKey",
        api_key_prefix="sk-",
        models=[
            ModelInfo(
                name="qwen-max",
                display_name="通義千問 Max",
                description="最強大的通義千問模型，適合複雜任務",
                context_window=8000,
                is_default=True
            ),
            ModelInfo(
                name="qwen-plus",
                display_name="通義千問 Plus",
                description="平衡性能和成本，適合大多數場景",
                context_window=32000
            ),
            ModelInfo(
                name="qwen-turbo",
                display_name="通義千問 Turbo",
                description="快速且經濟，適合簡單任務",
                context_window=8000
            )
        ]
    )
}


# 章節複雜度定義
class SectionComplexity(BaseModel):
    """章節複雜度"""
    section_name: str
    complexity: str  # "simple" 或 "complex"
    description: str


SECTION_COMPLEXITY: Dict[str, SectionComplexity] = {
    "technical_field": SectionComplexity(
        section_name="technical_field",
        complexity="simple",
        description="技術領域章節，內容簡短直接"
    ),
    "background": SectionComplexity(
        section_name="background",
        complexity="complex",
        description="背景技術章節，需要詳細分析"
    ),
    "invention_content": SectionComplexity(
        section_name="invention_content",
        complexity="complex",
        description="發明內容章節，核心部分，需要高質量輸出"
    ),
    "figure_description": SectionComplexity(
        section_name="figure_description",
        complexity="simple",
        description="附圖說明章節，格式化描述"
    ),
    "implementation": SectionComplexity(
        section_name="implementation",
        complexity="complex",
        description="具體實施方式章節，需要詳細技術描述"
    )
}


# 推薦模型配置
RECOMMENDED_MODELS: Dict[str, Dict[str, str]] = {
    "openai": {
        "simple": "gpt-3.5-turbo",
        "complex": "gpt-4-turbo"
    },
    "claude": {
        "simple": "claude-3-haiku-20240307",
        "complex": "claude-3-5-sonnet-20241022"
    },
    "gemini": {
        "simple": "gemini-1.5-flash",
        "complex": "gemini-1.5-pro"
    },
    "qwen": {
        "simple": "qwen-turbo",
        "complex": "qwen-max"
    }
}


def get_provider_info(provider: str) -> Optional[ProviderInfo]:
    """
    獲取提供商信息

    Args:
        provider: 提供商名稱

    Returns:
        Optional[ProviderInfo]: 提供商信息，如果不存在則返回 None
    """
    return PROVIDER_CONFIGS.get(provider.lower())


def get_default_model(provider: str) -> Optional[str]:
    """
    獲取提供商的默認模型

    Args:
        provider: 提供商名稱

    Returns:
        Optional[str]: 默認模型名稱，如果不存在則返回 None
    """
    provider_info = get_provider_info(provider)
    if not provider_info:
        return None

    for model in provider_info.models:
        if model.is_default:
            return model.name

    # 如果沒有標記為默認的，返回第一個
    return provider_info.models[0].name if provider_info.models else None


def get_recommended_model(provider: str, section_name: str) -> str:
    """
    根據章節獲取推薦模型

    Args:
        provider: 提供商名稱
        section_name: 章節名稱

    Returns:
        str: 推薦的模型名稱
    """
    provider = provider.lower()

    # 獲取章節複雜度
    section_info = SECTION_COMPLEXITY.get(section_name)
    complexity = section_info.complexity if section_info else "complex"

    # 獲取推薦模型
    if provider in RECOMMENDED_MODELS:
        return RECOMMENDED_MODELS[provider].get(complexity)

    # 如果沒有推薦配置，返回默認模型
    return get_default_model(provider)


def get_all_providers() -> List[Dict[str, str]]:
    """
    獲取所有提供商的基本信息

    Returns:
        List[Dict[str, str]]: 提供商列表
    """
    return [
        {
            "name": config.name,
            "display_name": config.display_name,
            "api_key_url": config.api_key_url
        }
        for config in PROVIDER_CONFIGS.values()
    ]


def get_provider_models(provider: str) -> List[Dict[str, any]]:
    """
    獲取提供商的所有模型

    Args:
        provider: 提供商名稱

    Returns:
        List[Dict]: 模型列表
    """
    provider_info = get_provider_info(provider)
    if not provider_info:
        return []

    return [
        {
            "name": model.name,
            "display_name": model.display_name,
            "description": model.description,
            "context_window": model.context_window,
            "is_default": model.is_default
        }
        for model in provider_info.models
    ]

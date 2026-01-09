"""
LLM 適配器模塊

支持多個 LLM 提供商的統一接口
"""

from .base_adapter import BaseLLMAdapter, LLMConfig, LLMResponse
from .llm_factory import LLMFactory
from .openai_adapter import OpenAIAdapter
from .claude_adapter import ClaudeAdapter
from .gemini_adapter import GeminiAdapter
from .qwen_adapter import QwenAdapter
from .config import (
    get_provider_info,
    get_default_model,
    get_recommended_model,
    get_all_providers,
    get_provider_models
)

__all__ = [
    'BaseLLMAdapter',
    'LLMConfig',
    'LLMResponse',
    'LLMFactory',
    'OpenAIAdapter',
    'ClaudeAdapter',
    'GeminiAdapter',
    'QwenAdapter',
    'get_provider_info',
    'get_default_model',
    'get_recommended_model',
    'get_all_providers',
    'get_provider_models'
]

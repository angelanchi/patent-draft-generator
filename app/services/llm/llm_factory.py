"""
LLM 服務工廠類

根據配置動態創建對應的 LLM 適配器
"""

from typing import Dict, Type
from loguru import logger

from .base_adapter import BaseLLMAdapter, LLMConfig


class LLMFactory:
    """LLM 服務工廠類"""

    _PROVIDERS: Dict[str, Type[BaseLLMAdapter]] = {}

    @classmethod
    def register_provider(cls, provider_name: str, adapter_class: Type[BaseLLMAdapter]):
        """
        註冊 LLM 提供商

        Args:
            provider_name: 提供商名稱
            adapter_class: 適配器類
        """
        cls._PROVIDERS[provider_name.lower()] = adapter_class
        logger.debug(f"已註冊LLM提供商: {provider_name}")

    @classmethod
    def create_adapter(cls, config: LLMConfig) -> BaseLLMAdapter:
        """
        創建 LLM 適配器

        Args:
            config: LLM 配置

        Returns:
            BaseLLMAdapter: 對應的適配器實例

        Raises:
            ValueError: 不支持的提供商時
        """
        provider = config.provider.lower()

        if provider not in cls._PROVIDERS:
            raise ValueError(
                f"不支持的LLM提供商: {config.provider}。"
                f"支持的提供商: {', '.join(cls._PROVIDERS.keys())}"
            )

        adapter_class = cls._PROVIDERS[provider]

        logger.info(f"創建LLM適配器: {provider} ({config.model})")

        return adapter_class(config)

    @classmethod
    def get_supported_providers(cls) -> list:
        """獲取支持的提供商列表"""
        return list(cls._PROVIDERS.keys())

    @classmethod
    def get_provider_models(cls, provider: str) -> list:
        """
        獲取指定提供商支持的模型列表

        Args:
            provider: 提供商名稱

        Returns:
            list: 支持的模型列表
        """
        provider = provider.lower()

        if provider not in cls._PROVIDERS:
            return []

        adapter_class = cls._PROVIDERS[provider]
        return adapter_class.get_supported_models()

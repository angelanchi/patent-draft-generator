"""
LLM 適配器抽象基類

定義所有 LLM 提供商必須實現的統一接口
"""

from abc import ABC, abstractmethod
from typing import Tuple
from pydantic import BaseModel, Field
from loguru import logger


class LLMConfig(BaseModel):
    """LLM 配置模型"""
    provider: str = Field(..., description="提供商名稱")
    model: str = Field(..., description="模型名稱")
    api_key: str = Field(..., description="API 密鑰")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, gt=0)
    timeout: int = Field(default=60, gt=0)

    class Config:
        json_encoders = {
            str: lambda v: "***" if len(v) > 20 else v
        }


class LLMResponse(BaseModel):
    """統一的 LLM 響應格式"""
    content: str = Field(..., description="生成的內容")
    model: str = Field(..., description="使用的模型")
    prompt_tokens: int = Field(default=0, description="提示 token 數")
    completion_tokens: int = Field(default=0, description="完成 token 數")
    total_tokens: int = Field(default=0, description="總 token 數")
    cost: float = Field(default=0.0, description="成本（美元）")


class BaseLLMAdapter(ABC):
    """LLM 適配器抽象基類"""

    PROVIDER_NAME: str = ""
    SUPPORTED_MODELS: list = []

    def __init__(self, config: LLMConfig):
        """
        初始化適配器

        Args:
            config: LLM 配置
        """
        self.config = config
        self._validate_config()
        self._initialize_client()

        logger.info(
            f"LLM適配器已初始化 "
            f"(提供商: {self.PROVIDER_NAME}, 模型: {config.model})"
        )

    @abstractmethod
    def _validate_config(self) -> None:
        """
        驗證配置（API 密鑰格式、模型是否支持等）

        Raises:
            ValueError: 配置無效時
        """
        pass

    @abstractmethod
    def _initialize_client(self) -> None:
        """初始化提供商的 API 客戶端"""
        pass

    @abstractmethod
    def generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs
    ) -> LLMResponse:
        """
        生成內容（核心方法）

        Args:
            system_prompt: 系統提示
            user_prompt: 用戶提示
            **kwargs: 其他參數

        Returns:
            LLMResponse: 統一格式的響應

        Raises:
            Exception: API 調用失敗時
        """
        pass

    @abstractmethod
    def estimate_cost(self, prompt: str, system_prompt: str = "") -> float:
        """
        估算成本

        Args:
            prompt: 用戶提示
            system_prompt: 系統提示

        Returns:
            float: 估算成本（美元）
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        計算 token 數量

        Args:
            text: 文本

        Returns:
            int: token 數量
        """
        pass

    def validate_content(
        self,
        content: str,
        min_length: int = 50
    ) -> Tuple[bool, str]:
        """
        驗證生成的內容

        Args:
            content: 生成的內容
            min_length: 最小長度要求

        Returns:
            Tuple[bool, str]: (是否有效, 錯誤信息)
        """
        if not content or len(content.strip()) < min_length:
            return False, f"內容過短（長度: {len(content)}）"

        error_keywords = ['error', 'sorry', '抱歉', '無法', '錯誤']
        content_lower = content.lower()
        if any(keyword in content_lower for keyword in error_keywords):
            return False, "內容可能包含錯誤訊息"

        return True, ""

    @classmethod
    def get_supported_models(cls) -> list:
        """獲取支持的模型列表"""
        return cls.SUPPORTED_MODELS

    @classmethod
    def is_model_supported(cls, model: str) -> bool:
        """檢查模型是否支持"""
        return model in cls.SUPPORTED_MODELS

"""
Google Gemini 適配器

實現 Google Gemini API 的統一接口
使用新的 google-genai SDK（1.57.0+）
"""

from typing import Optional
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from .base_adapter import BaseLLMAdapter, LLMConfig, LLMResponse


class GeminiAdapter(BaseLLMAdapter):
    """Google Gemini API 適配器"""

    PROVIDER_NAME = "gemini"
    SUPPORTED_MODELS = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b"
    ]

    # 定價信息（每 1000 tokens，美元）
    # 參考：https://ai.google.dev/pricing
    PRICING = {
        "gemini-2.0-flash-exp": {"input": 0.0, "output": 0.0},  # 實驗版本免費
        "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
        "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
        "gemini-1.5-flash-8b": {"input": 0.0000375, "output": 0.00015}
    }

    # 模型的最大上下文窗口
    CONTEXT_WINDOWS = {
        "gemini-2.0-flash-exp": 1000000,
        "gemini-1.5-pro": 2000000,
        "gemini-1.5-flash": 1000000,
        "gemini-1.5-flash-8b": 1000000
    }

    def __init__(self, config: LLMConfig):
        """
        初始化 Gemini 適配器

        Args:
            config: LLM 配置
        """
        self.client: Optional[genai.Client] = None
        super().__init__(config)

    def _validate_config(self) -> None:
        """
        驗證 Gemini 配置

        Raises:
            ValueError: 配置無效時
        """
        # 驗證 API 密鑰
        if not self.config.api_key:
            raise ValueError("Gemini API 密鑰不能為空")

        # Gemini API 密鑰格式：AIza 開頭
        if not self.config.api_key.startswith("AIza"):
            logger.warning(
                "Gemini API 密鑰通常以 'AIza' 開頭，"
                "請確認密鑰是否正確"
            )

        # 驗證模型是否支持
        if self.config.model not in self.SUPPORTED_MODELS:
            logger.warning(
                f"模型 '{self.config.model}' 不在已知的支持列表中，"
                f"但仍會嘗試使用。支持的模型: {', '.join(self.SUPPORTED_MODELS)}"
            )

    def _initialize_client(self) -> None:
        """初始化 Gemini 客戶端"""
        try:
            self.client = genai.Client(api_key=self.config.api_key)
            logger.debug("Gemini 客戶端已初始化")
        except Exception as e:
            logger.error(f"Gemini 客戶端初始化失敗: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs
    ) -> LLMResponse:
        """
        生成內容

        Args:
            system_prompt: 系統提示
            user_prompt: 用戶提示
            **kwargs: 其他參數（可選：temperature, max_tokens）

        Returns:
            LLMResponse: 統一格式的響應

        Raises:
            Exception: API 調用失敗時
        """
        try:
            # 使用傳入的參數或配置默認值
            temperature = kwargs.get('temperature', self.config.temperature)
            max_tokens = kwargs.get('max_tokens', self.config.max_tokens)

            logger.info(
                f"調用 Gemini API - "
                f"模型: {self.config.model}, "
                f"溫度: {temperature}"
            )

            # 構建完整的提示（Gemini 將系統提示合併到用戶消息中）
            full_prompt = f"{system_prompt}\n\n{user_prompt}"

            # 調用 Gemini API
            response = self.client.models.generate_content(
                model=self.config.model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    top_p=0.95,
                    top_k=40
                )
            )

            # 提取內容
            content = response.text.strip()

            # 提取使用統計
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count
                total_tokens = response.usage_metadata.total_token_count
            else:
                # 如果 API 沒有返回使用統計，使用估算值
                input_tokens = self.count_tokens(full_prompt)
                output_tokens = self.count_tokens(content)
                total_tokens = input_tokens + output_tokens
                logger.warning("API 未返回使用統計，使用估算值")

            # 計算成本
            cost = self._calculate_cost(input_tokens, output_tokens)

            logger.info(
                f"API 調用成功 - "
                f"tokens: {total_tokens} "
                f"(輸入: {input_tokens}, "
                f"輸出: {output_tokens}), "
                f"成本: ${cost:.4f}"
            )

            return LLMResponse(
                content=content,
                model=self.config.model,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                total_tokens=total_tokens,
                cost=cost
            )

        except Exception as e:
            logger.error(f"Gemini API 調用失敗: {e}")
            raise

    def estimate_cost(self, prompt: str, system_prompt: str = "") -> float:
        """
        估算 API 調用成本

        Args:
            prompt: 用戶提示
            system_prompt: 系統提示

        Returns:
            float: 估算成本（美元）
        """
        try:
            # 計算輸入 token（系統提示和用戶提示合併）
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            input_tokens = self.count_tokens(full_prompt)

            # 估算輸出 token（通常是輸入的 2-3 倍）
            estimated_output_tokens = min(
                input_tokens * 2.5,
                self.config.max_tokens
            )

            # 計算成本
            cost = self._calculate_cost(
                int(input_tokens),
                int(estimated_output_tokens)
            )

            logger.debug(
                f"成本估算 - "
                f"輸入 tokens: {input_tokens}, "
                f"預估輸出 tokens: {estimated_output_tokens:.0f}, "
                f"預估成本: ${cost:.4f}"
            )

            return cost

        except Exception as e:
            logger.warning(f"成本估算失敗: {e}")
            return 0.0

    def count_tokens(self, text: str) -> int:
        """
        計算文本的 token 數量

        Args:
            text: 文本內容

        Returns:
            int: token 數量
        """
        try:
            # 使用 Gemini API 的 count_tokens 方法
            response = self.client.models.count_tokens(
                model=self.config.model,
                contents=text
            )
            return response.total_tokens
        except Exception as e:
            logger.warning(f"Token 計數失敗: {e}，使用近似值")
            # 使用近似值：平均約 2.5 字符/token（考慮中英文混合）
            return len(text) // 2

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        計算實際成本

        Args:
            input_tokens: 輸入 token 數
            output_tokens: 輸出 token 數

        Returns:
            float: 成本（美元）
        """
        # 獲取定價（如果模型不在定價表中，使用 1.5-pro 的價格作為保守估計）
        pricing = self.PRICING.get(
            self.config.model,
            {"input": 0.00125, "output": 0.005}
        )

        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]

        return input_cost + output_cost


# 註冊 Gemini 適配器到工廠
from .llm_factory import LLMFactory
LLMFactory.register_provider("gemini", GeminiAdapter)

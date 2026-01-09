"""
Claude (Anthropic) 適配器

實現 Anthropic Claude API 的統一接口
"""

from typing import Optional
from anthropic import Anthropic, APIError
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from .base_adapter import BaseLLMAdapter, LLMConfig, LLMResponse


class ClaudeAdapter(BaseLLMAdapter):
    """Anthropic Claude API 適配器"""

    PROVIDER_NAME = "claude"
    SUPPORTED_MODELS = [
        "claude-opus-4.5-20251101",
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]

    # 定價信息（每 1000 tokens，美元）
    PRICING = {
        "claude-opus-4.5-20251101": {"input": 0.015, "output": 0.075},
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125}
    }

    # 模型的最大上下文窗口
    CONTEXT_WINDOWS = {
        "claude-opus-4.5-20251101": 200000,
        "claude-3-5-sonnet-20241022": 200000,
        "claude-3-opus-20240229": 200000,
        "claude-3-sonnet-20240229": 200000,
        "claude-3-haiku-20240307": 200000
    }

    def __init__(self, config: LLMConfig):
        """
        初始化 Claude 適配器

        Args:
            config: LLM 配置
        """
        self.client: Optional[Anthropic] = None
        super().__init__(config)

    def _validate_config(self) -> None:
        """
        驗證 Claude 配置

        Raises:
            ValueError: 配置無效時
        """
        # 驗證 API 密鑰格式
        if not self.config.api_key:
            raise ValueError("Claude API 密鑰不能為空")

        if not self.config.api_key.startswith("sk-ant-"):
            raise ValueError(
                "Claude API 密鑰格式無效，應以 'sk-ant-' 開頭"
            )

        # 驗證模型是否支持
        if self.config.model not in self.SUPPORTED_MODELS:
            logger.warning(
                f"模型 '{self.config.model}' 不在已知的支持列表中，"
                f"但仍會嘗試使用。支持的模型: {', '.join(self.SUPPORTED_MODELS)}"
            )

    def _initialize_client(self) -> None:
        """初始化 Claude 客戶端"""
        try:
            self.client = Anthropic(
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
            logger.debug("Claude 客戶端已初始化")
        except Exception as e:
            logger.error(f"Claude 客戶端初始化失敗: {e}")
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
                f"調用 Claude API - "
                f"模型: {self.config.model}, "
                f"溫度: {temperature}"
            )

            # 調用 Claude API
            response = self.client.messages.create(
                model=self.config.model,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            # 提取內容
            content = response.content[0].text.strip()

            # 提取使用統計
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens

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

        except APIError as e:
            logger.error(f"Claude API 調用失敗: {e}")
            raise
        except Exception as e:
            logger.error(f"Claude API 調用失敗: {e}")
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
            # 計算輸入 token
            input_tokens = self.count_tokens(prompt)
            if system_prompt:
                input_tokens += self.count_tokens(system_prompt)

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

        Note:
            Anthropic 的 API 會自動計算 token，這裡使用近似方法。
            Claude 的 tokenization 與 OpenAI 類似，約為：
            - 中文：約 1.5-2 字符/token
            - 英文：約 4 字符/token

        Args:
            text: 文本內容

        Returns:
            int: token 數量（近似值）
        """
        try:
            # 使用 Anthropic 的推薦方法計算 token
            # 參考：https://docs.anthropic.com/claude/docs/counting-tokens
            response = self.client.messages.count_tokens(
                model=self.config.model,
                messages=[{"role": "user", "content": text}]
            )
            return response.input_tokens
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
        # 獲取定價（如果模型不在定價表中，使用 Opus 的價格作為保守估計）
        pricing = self.PRICING.get(
            self.config.model,
            {"input": 0.015, "output": 0.075}
        )

        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]

        return input_cost + output_cost


# 註冊 Claude 適配器到工廠
from .llm_factory import LLMFactory
LLMFactory.register_provider("claude", ClaudeAdapter)

"""
OpenAI 適配器

實現 OpenAI API 的統一接口
"""

from typing import Optional
from openai import OpenAI
from openai.types.chat import ChatCompletion
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger
import tiktoken

from .base_adapter import BaseLLMAdapter, LLMConfig, LLMResponse


class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI API 適配器"""

    PROVIDER_NAME = "openai"
    SUPPORTED_MODELS = [
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-4-0125-preview",
        "gpt-4-1106-preview",
        "gpt-4",
        "gpt-4-0613",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-1106"
    ]

    # 定價信息（每 1000 tokens，美元）
    PRICING = {
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "gpt-4-0125-preview": {"input": 0.01, "output": 0.03},
        "gpt-4-1106-preview": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-0613": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-3.5-turbo-0125": {"input": 0.0005, "output": 0.0015},
        "gpt-3.5-turbo-1106": {"input": 0.001, "output": 0.002}
    }

    def __init__(self, config: LLMConfig):
        """
        初始化 OpenAI 適配器

        Args:
            config: LLM 配置
        """
        self.client: Optional[OpenAI] = None
        super().__init__(config)

    def _validate_config(self) -> None:
        """
        驗證 OpenAI 配置

        Raises:
            ValueError: 配置無效時
        """
        # 驗證 API 密鑰格式
        if not self.config.api_key:
            raise ValueError("OpenAI API 密鑰不能為空")

        if not self.config.api_key.startswith("sk-"):
            raise ValueError(
                "OpenAI API 密鑰格式無效，應以 'sk-' 開頭"
            )

        # 驗證模型是否支持
        if self.config.model not in self.SUPPORTED_MODELS:
            logger.warning(
                f"模型 '{self.config.model}' 不在已知的支持列表中，"
                f"但仍會嘗試使用。支持的模型: {', '.join(self.SUPPORTED_MODELS)}"
            )

    def _initialize_client(self) -> None:
        """初始化 OpenAI 客戶端"""
        try:
            self.client = OpenAI(
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
            logger.debug("OpenAI 客戶端已初始化")
        except Exception as e:
            logger.error(f"OpenAI 客戶端初始化失敗: {e}")
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
                f"調用 OpenAI API - "
                f"模型: {self.config.model}, "
                f"溫度: {temperature}"
            )

            # 調用 OpenAI API
            response: ChatCompletion = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )

            # 提取內容和使用統計
            content = response.choices[0].message.content.strip()
            usage = response.usage

            # 計算成本
            cost = self._calculate_cost(
                usage.prompt_tokens,
                usage.completion_tokens
            )

            logger.info(
                f"API 調用成功 - "
                f"tokens: {usage.total_tokens} "
                f"(提示: {usage.prompt_tokens}, "
                f"完成: {usage.completion_tokens}), "
                f"成本: ${cost:.4f}"
            )

            return LLMResponse(
                content=content,
                model=self.config.model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                cost=cost
            )

        except Exception as e:
            logger.error(f"OpenAI API 調用失敗: {e}")
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

        Args:
            text: 文本內容

        Returns:
            int: token 數量
        """
        try:
            encoding = tiktoken.encoding_for_model(self.config.model)
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Token 計數失敗: {e}，使用近似值")
            # 使用近似值：中文約 1.5 字符/token，英文約 4 字符/token
            # 這裡使用保守估計 2 字符/token
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
        # 獲取定價（如果模型不在定價表中，使用 GPT-4 的價格作為保守估計）
        pricing = self.PRICING.get(
            self.config.model,
            {"input": 0.01, "output": 0.03}
        )

        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]

        return input_cost + output_cost


# 註冊 OpenAI 適配器到工廠
from .llm_factory import LLMFactory
LLMFactory.register_provider("openai", OpenAIAdapter)

"""
阿里通義千問 (Qwen) 適配器

實現阿里雲通義千問 API 的統一接口
"""

from typing import Optional
import dashscope
from dashscope import Generation
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from .base_adapter import BaseLLMAdapter, LLMConfig, LLMResponse


class QwenAdapter(BaseLLMAdapter):
    """阿里通義千問 API 適配器"""

    PROVIDER_NAME = "qwen"
    SUPPORTED_MODELS = [
        "qwen-max",
        "qwen-max-0428",
        "qwen-max-0403",
        "qwen-max-0107",
        "qwen-plus",
        "qwen-turbo",
        "qwen-long"
    ]

    # 定價信息（每 1000 tokens，人民幣）
    # 參考：https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-thousand-questions-metering-and-billing
    PRICING_CNY = {
        "qwen-max": {"input": 0.04, "output": 0.12},
        "qwen-max-0428": {"input": 0.04, "output": 0.12},
        "qwen-max-0403": {"input": 0.04, "output": 0.12},
        "qwen-max-0107": {"input": 0.04, "output": 0.12},
        "qwen-plus": {"input": 0.008, "output": 0.024},
        "qwen-turbo": {"input": 0.003, "output": 0.006},
        "qwen-long": {"input": 0.0005, "output": 0.002}
    }

    # 人民幣轉美元匯率（近似值）
    CNY_TO_USD = 0.14  # 1 CNY ≈ 0.14 USD

    # 模型的最大上下文窗口
    CONTEXT_WINDOWS = {
        "qwen-max": 8000,
        "qwen-max-0428": 8000,
        "qwen-max-0403": 8000,
        "qwen-max-0107": 8000,
        "qwen-plus": 32000,
        "qwen-turbo": 8000,
        "qwen-long": 10000000
    }

    def __init__(self, config: LLMConfig):
        """
        初始化 Qwen 適配器

        Args:
            config: LLM 配置
        """
        super().__init__(config)

    def _validate_config(self) -> None:
        """
        驗證 Qwen 配置

        Raises:
            ValueError: 配置無效時
        """
        # 驗證 API 密鑰
        if not self.config.api_key:
            raise ValueError("Qwen API 密鑰不能為空")

        # Qwen API 密鑰格式：sk- 開頭
        if not self.config.api_key.startswith("sk-"):
            logger.warning(
                "Qwen API 密鑰通常以 'sk-' 開頭，"
                "請確認密鑰是否正確"
            )

        # 驗證模型是否支持
        if self.config.model not in self.SUPPORTED_MODELS:
            logger.warning(
                f"模型 '{self.config.model}' 不在已知的支持列表中，"
                f"但仍會嘗試使用。支持的模型: {', '.join(self.SUPPORTED_MODELS)}"
            )

    def _initialize_client(self) -> None:
        """初始化 Qwen 客戶端"""
        try:
            # DashScope 使用全局 API key 配置
            dashscope.api_key = self.config.api_key
            logger.debug("Qwen 客戶端已初始化")
        except Exception as e:
            logger.error(f"Qwen 客戶端初始化失敗: {e}")
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
                f"調用 Qwen API - "
                f"模型: {self.config.model}, "
                f"溫度: {temperature}"
            )

            # 調用通義千問 API
            response = Generation.call(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                result_format='message'
            )

            # 檢查響應狀態
            if response.status_code != 200:
                error_msg = f"API 調用失敗，狀態碼: {response.status_code}"
                if hasattr(response, 'message'):
                    error_msg += f"，錯誤信息: {response.message}"
                raise Exception(error_msg)

            # 提取內容
            content = response.output.choices[0].message.content.strip()

            # 提取使用統計
            usage = response.usage
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
            total_tokens = usage.total_tokens

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
            logger.error(f"Qwen API 調用失敗: {e}")
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
            DashScope API 沒有提供專門的 token 計數接口，
            這裡使用近似方法。通義千問的 tokenization 約為：
            - 中文：約 1.5-2 字符/token
            - 英文：約 4 字符/token

        Args:
            text: 文本內容

        Returns:
            int: token 數量（近似值）
        """
        # 使用近似值：平均約 2.5 字符/token（考慮中英文混合）
        # 這個估算適用於中文為主的場景
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
        # 獲取定價（人民幣）
        pricing_cny = self.PRICING_CNY.get(
            self.config.model,
            {"input": 0.04, "output": 0.12}  # 使用 qwen-max 價格作為保守估計
        )

        # 計算人民幣成本
        input_cost_cny = (input_tokens / 1000) * pricing_cny["input"]
        output_cost_cny = (output_tokens / 1000) * pricing_cny["output"]
        total_cost_cny = input_cost_cny + output_cost_cny

        # 轉換為美元
        cost_usd = total_cost_cny * self.CNY_TO_USD

        return cost_usd


# 註冊 Qwen 適配器到工廠
from .llm_factory import LLMFactory
LLMFactory.register_provider("qwen", QwenAdapter)

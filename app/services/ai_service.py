"""
AI服務模塊
處理與多個 LLM 提供商的交互，生成專利文件內容
"""
from loguru import logger
from typing import Optional, Dict

from app.config import get_settings
from app.utils.prompts import (
    SYSTEM_PROMPT,
    get_prompt_template,
    get_section_display_name
)
from app.services.llm import (
    LLMFactory,
    LLMConfig,
    LLMResponse,
    get_default_model,
    get_recommended_model as get_llm_recommended_model
)


class AIService:
    """AI服務類，處理多個 LLM 提供商的 API 調用"""

    def __init__(
        self,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        api_key: Optional[str] = None,
        use_server_config: bool = True
    ):
        """
        初始化 AI 服務

        Args:
            llm_provider: LLM 提供商名稱（默認 None，使用 OpenAI）
            llm_model: LLM 模型名稱（默認 None，使用提供商的默認模型）
            api_key: 用戶提供的 API 密鑰（默認 None，使用服務器配置）
            use_server_config: 是否使用服務器配置的密鑰（默認 True）
        """
        self.settings = get_settings()

        # 確定提供商
        self.provider = (llm_provider or "openai").lower()

        # 確定 API 密鑰
        if use_server_config and not api_key:
            # 使用服務器配置的密鑰（僅 OpenAI 支持）
            if self.provider == "openai":
                api_key = self.settings.OPENAI_API_KEY
                if not api_key:
                    raise ValueError(
                        "服務器未配置 OpenAI API 密鑰。"
                        "請在生成時輸入您自己的 API 密鑰。"
                    )
            else:
                raise ValueError(
                    f"提供商 '{self.provider}' 需要提供 API 密鑰。"
                    "請在生成時輸入您的 API 密鑰。"
                )

        if not api_key:
            raise ValueError(
                "API 密鑰不能為空。請輸入您的 API 密鑰或選擇使用服務器配置。"
            )

        # 確定模型
        self.model = llm_model or get_default_model(self.provider)
        if not self.model:
            raise ValueError(f"無法確定提供商 '{self.provider}' 的默認模型")

        # 創建 LLM 配置
        self.llm_config = LLMConfig(
            provider=self.provider,
            model=self.model,
            api_key=api_key,
            temperature=self.settings.OPENAI_TEMPERATURE,
            max_tokens=self.settings.OPENAI_MAX_TOKENS,
            timeout=60
        )

        # 使用工廠創建適配器
        try:
            self.adapter = LLMFactory.create_adapter(self.llm_config)
            logger.info(
                f"AI 服務已初始化 - "
                f"提供商: {self.provider}, "
                f"模型: {self.model}"
            )
        except Exception as e:
            logger.error(f"AI 服務初始化失敗: {e}")
            raise

    def generate_content(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """
        生成內容的核心方法

        Args:
            prompt: 提示詞
            model: 模型名稱（可選，默認使用配置中的模型）
            temperature: 溫度參數（可選）
            max_tokens: 最大token數（可選）

        Returns:
            LLMResponse: LLM 響應（包含內容、token 統計和成本）

        Raises:
            Exception: API調用失敗時拋出異常
        """
        try:
            # 如果指定了不同的模型，需要創建新的適配器
            if model and model != self.model:
                logger.info(f"切換模型: {self.model} → {model}")
                temp_config = LLMConfig(
                    provider=self.provider,
                    model=model,
                    api_key=self.llm_config.api_key,
                    temperature=temperature or self.llm_config.temperature,
                    max_tokens=max_tokens or self.llm_config.max_tokens,
                    timeout=self.llm_config.timeout
                )
                temp_adapter = LLMFactory.create_adapter(temp_config)
                response = temp_adapter.generate_content(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=prompt
                )
            else:
                # 使用當前適配器
                response = self.adapter.generate_content(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

            return response

        except Exception as e:
            logger.error(f"LLM API 調用失敗: {e}")
            raise

    def generate_section_content(
        self,
        section_name: str,
        input_data: Dict[str, str],
        use_recommended_model: bool = True
    ) -> str:
        """
        生成指定章節的內容

        Args:
            section_name: 章節名稱 (technical_field, background等)
            input_data: 輸入數據字典
            use_recommended_model: 是否使用推薦的模型（默認True）

        Returns:
            str: 生成的章節內容

        Raises:
            ValueError: 如果章節名稱無效
            Exception: API調用失敗時拋出異常
        """
        # 獲取章節顯示名稱
        display_name = get_section_display_name(section_name)

        logger.info(f"開始生成章節: {display_name} ({section_name})")

        # 獲取提示模板
        prompt_template = get_prompt_template(section_name)
        if not prompt_template:
            raise ValueError(f"未找到章節 '{section_name}' 的提示模板")

        # 準備提示數據
        prompt_data = self._prepare_prompt_data(input_data)

        # 格式化提示
        try:
            formatted_prompt = prompt_template.format(**prompt_data)
        except KeyError as e:
            logger.error(f"提示模板格式化失敗，缺少鍵: {e}")
            raise ValueError(f"輸入數據缺少必要字段: {e}")

        # 決定使用的模型
        model = None
        if use_recommended_model:
            model = get_llm_recommended_model(self.provider, section_name)
            logger.info(f"使用推薦模型: {model}")

        # 生成內容
        response = self.generate_content(
            prompt=formatted_prompt,
            model=model
        )

        logger.info(
            f"章節 '{display_name}' 生成完成 - "
            f"字數: {len(response.content)}, "
            f"tokens: {response.total_tokens}, "
            f"成本: ${response.cost:.4f}"
        )

        return response.content

    def _prepare_prompt_data(self, input_data: Dict[str, str]) -> Dict[str, str]:
        """
        準備提示數據，確保所有必要字段都有值

        Args:
            input_data: 原始輸入數據

        Returns:
            Dict[str, str]: 處理後的數據
        """
        # 定義默認值
        defaults = {
            'patent_name': '',
            'keywords': '',
            'technical_description': '',
            'inventors': '',
            'classification': '待補充',
            'contact_person': '待補充',
            'contact_info': '待補充',
            'submission_date': '待補充',
            'product_info': '（根據技術描述）',
            'working_principle': '（根據技術描述）',
            'innovation_points': '（根據技術描述）',
            'background_references': '（現有技術通用描述）',
            'problems_to_solve': '（基於技術描述推斷）',
            'has_diagrams': 'false',
            'diagram_description': '無附圖描述',
            'special_requirements': '無特殊要求'
        }

        # 合併數據
        prompt_data = {**defaults, **input_data}

        # 確保布爾值轉換為字符串
        if 'has_diagrams' in prompt_data:
            prompt_data['has_diagrams'] = str(prompt_data.get('has_diagrams', False)).lower()

        return prompt_data

    def estimate_cost(self, prompt: str, model: Optional[str] = None) -> float:
        """
        估算 API 調用成本

        Args:
            prompt: 提示詞
            model: 模型名稱（可選）

        Returns:
            float: 估算成本（美元）
        """
        try:
            # 如果指定了不同的模型，需要使用對應的適配器
            if model and model != self.model:
                temp_config = LLMConfig(
                    provider=self.provider,
                    model=model,
                    api_key=self.llm_config.api_key,
                    temperature=self.llm_config.temperature,
                    max_tokens=self.llm_config.max_tokens,
                    timeout=self.llm_config.timeout
                )
                temp_adapter = LLMFactory.create_adapter(temp_config)
                cost = temp_adapter.estimate_cost(prompt, SYSTEM_PROMPT)
            else:
                cost = self.adapter.estimate_cost(prompt, SYSTEM_PROMPT)

            return cost

        except Exception as e:
            logger.warning(f"成本估算失敗: {e}")
            return 0.0

    def validate_content(self, content: str, min_length: int = 50) -> bool:
        """
        驗證生成的內容是否有效

        Args:
            content: 生成的內容
            min_length: 最小長度要求

        Returns:
            bool: 內容是否有效
        """
        is_valid, error_msg = self.adapter.validate_content(content, min_length)
        if not is_valid:
            logger.warning(f"內容驗證失敗: {error_msg}")
        return is_valid


# 創建全局AI服務實例
_ai_service_instance = None


def get_ai_service() -> AIService:
    """
    獲取AI服務的全局實例（單例模式）

    Returns:
        AIService: AI服務實例
    """
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance

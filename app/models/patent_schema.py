"""
專利數據模型
使用Pydantic定義專利文件的數據結構
"""
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
import re


class PatentInput(BaseModel):
    """用戶輸入的專利信息"""

    # 基本信息
    patent_name: str = Field(..., min_length=5, max_length=200, description="專利名稱")
    inventors: str = Field(..., min_length=2, max_length=500, description="發明人（多個用逗號分隔）")
    classification: Optional[str] = Field(None, max_length=50, description="分類號")
    contact_person: Optional[str] = Field(None, max_length=100, description="聯絡人")
    contact_number: Optional[str] = Field(None, max_length=50, description="手機長號")
    contact_email: Optional[str] = Field(None, max_length=100, description="電子郵件")
    submission_date: Optional[str] = Field(None, description="提案日期")

    # 技術信息
    keywords: str = Field(..., min_length=5, max_length=500, description="技術關鍵字（用逗號分隔）")
    technical_description: str = Field(..., min_length=50, max_length=5000, description="基本技術描述")
    product_info: Optional[str] = Field(None, max_length=2000, description="產品/元件資訊")
    working_principle: Optional[str] = Field(None, max_length=2000, description="工作原理")
    innovation_points: Optional[str] = Field(None, max_length=2000, description="創新點")

    # 背景資訊
    background_references: Optional[str] = Field(None, max_length=2000, description="背景技術參考")
    problems_to_solve: Optional[str] = Field(None, max_length=2000, description="要解決的問題")

    # 附圖信息
    has_diagrams: bool = Field(default=False, description="是否包含附圖")
    diagram_description: Optional[str] = Field(None, max_length=1000, description="附圖描述")

    # 特殊要求
    special_requirements: Optional[str] = Field(None, max_length=1000, description="特殊要求或備註")

    # LLM 配置
    llm_provider: Optional[str] = Field(default="openai", description="LLM 提供商")
    llm_model: Optional[str] = Field(None, description="LLM 模型名稱")
    api_key: Optional[str] = Field(None, description="用戶提供的 API 密鑰")
    use_server_key: bool = Field(default=False, description="是否使用服務器配置的密鑰")

    @validator('keywords')
    def validate_keywords(cls, v):
        """驗證關鍵字格式"""
        if not v or len(v.strip()) == 0:
            raise ValueError('關鍵字不能為空')
        return v.strip()

    @validator('patent_name', 'inventors', 'technical_description')
    def validate_required_fields(cls, v):
        """驗證必填字段"""
        if not v or len(v.strip()) == 0:
            raise ValueError('此字段不能為空')
        return v.strip()

    @validator('llm_provider')
    def validate_llm_provider(cls, v):
        """驗證 LLM 提供商"""
        if not v:
            return "openai"  # 默認值

        v = v.lower().strip()
        supported_providers = ["openai", "claude", "gemini", "qwen"]

        if v not in supported_providers:
            raise ValueError(
                f"不支持的 LLM 提供商: {v}。"
                f"支持的提供商: {', '.join(supported_providers)}"
            )

        return v

    @validator('api_key')
    def validate_api_key(cls, v, values):
        """驗證 API 密鑰格式並防止注入攻擊"""
        if not v:
            return v  # 允許空值（使用服務器密鑰時）

        # 移除前後空白
        v = v.strip()

        # 檢查長度（API 密鑰通常在 20-200 字符之間）
        if len(v) < 20 or len(v) > 200:
            raise ValueError("API 密鑰長度無效")

        # 防止注入攻擊：檢查危險字符
        dangerous_chars = ['<', '>', '&', '"', "'", ';', '\n', '\r', '\t']
        if any(char in v for char in dangerous_chars):
            raise ValueError("API 密鑰包含無效字符")

        # 根據提供商驗證密鑰格式
        provider = values.get('llm_provider', 'openai')
        if provider == 'openai' and not v.startswith('sk-'):
            raise ValueError("OpenAI API 密鑰應以 'sk-' 開頭")
        elif provider == 'claude' and not v.startswith('sk-ant-'):
            raise ValueError("Claude API 密鑰應以 'sk-ant-' 開頭")
        elif provider == 'gemini' and not v.startswith('AIza'):
            raise ValueError("Gemini API 密鑰應以 'AIza' 開頭")
        elif provider == 'qwen' and not v.startswith('sk-'):
            raise ValueError("Qwen API 密鑰應以 'sk-' 開頭")

        return v

    @validator('use_server_key')
    def validate_use_server_key(cls, v, values):
        """驗證服務器密鑰配置"""
        api_key = values.get('api_key')

        # 如果既沒有用戶密鑰又不使用服務器密鑰，則報錯
        if not api_key and not v:
            # 只有 OpenAI 支持服務器密鑰（向後兼容）
            provider = values.get('llm_provider', 'openai')
            if provider == 'openai':
                return True  # 默認使用服務器密鑰
            else:
                raise ValueError(
                    f"提供商 '{provider}' 需要提供 API 密鑰"
                )

        return v


class PatentSection(BaseModel):
    """專利文件的單個章節"""

    section_name: str = Field(..., description="章節名稱")
    content: str = Field(..., description="章節內容")
    word_count: int = Field(default=0, description="字數")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成時間")

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }


class PatentDocument(BaseModel):
    """完整的專利文件"""

    # 元數據
    patent_id: Optional[str] = Field(None, description="專利文件ID")
    patent_name: str = Field(..., description="專利名稱")
    inventors: str = Field(..., description="發明人")
    classification: Optional[str] = Field(None, description="分類號")
    submission_date: Optional[str] = Field(None, description="提案日期")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成時間")

    # 6個主要章節
    technical_field: Optional[PatentSection] = Field(None, description="技術領域")
    background: Optional[PatentSection] = Field(None, description="背景技術")
    invention_content: Optional[PatentSection] = Field(None, description="發明內容")
    figure_description: Optional[PatentSection] = Field(None, description="附圖說明")
    implementation: Optional[PatentSection] = Field(None, description="具體實施方式")
    attachments: Optional[PatentSection] = Field(None, description="其它發明附件")

    # 額外信息
    keywords: Optional[List[str]] = Field(default_factory=list, description="關鍵字列表")
    total_word_count: int = Field(default=0, description="總字數")
    status: str = Field(default="draft", description="狀態 (draft, completed, error)")
    error_message: Optional[str] = Field(None, description="錯誤信息")

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }

    def calculate_total_words(self) -> int:
        """計算總字數"""
        total = 0
        sections = [
            self.technical_field,
            self.background,
            self.invention_content,
            self.figure_description,
            self.implementation,
            self.attachments
        ]
        for section in sections:
            if section:
                total += section.word_count
        self.total_word_count = total
        return total

    def is_complete(self) -> bool:
        """檢查文件是否完整（所有必需章節都存在）"""
        required_sections = [
            self.technical_field,
            self.background,
            self.invention_content,
            self.implementation
        ]
        return all(section is not None for section in required_sections)


class GenerationProgress(BaseModel):
    """生成進度追蹤"""

    patent_id: str = Field(..., description="專利文件ID")
    current_section: str = Field(default="", description="當前正在生成的章節")
    completed_sections: List[str] = Field(default_factory=list, description="已完成的章節")
    progress_percentage: int = Field(default=0, ge=0, le=100, description="進度百分比 (0-100)")
    status: str = Field(default="pending", description="狀態 (pending, generating, completed, error)")
    error_message: Optional[str] = Field(None, description="錯誤信息")
    started_at: datetime = Field(default_factory=datetime.now, description="開始時間")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新時間")

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }


class GenerationResult(BaseModel):
    """生成結果"""

    success: bool = Field(..., description="是否成功")
    patent_document: Optional[PatentDocument] = Field(None, description="生成的專利文件")
    file_path: Optional[str] = Field(None, description="生成的Word文件路徑")
    error_message: Optional[str] = Field(None, description="錯誤信息")
    generation_time: Optional[float] = Field(None, description="生成耗時（秒）")

    # LLM 使用統計
    llm_provider: Optional[str] = Field(None, description="使用的 LLM 提供商")
    llm_model: Optional[str] = Field(None, description="使用的 LLM 模型")
    total_tokens: Optional[int] = Field(None, description="總 token 使用量")
    total_cost: Optional[float] = Field(None, description="總成本（美元）")

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }

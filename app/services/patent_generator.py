"""
專利生成器模塊
協調整個專利文件生成流程
"""
import time
from typing import Dict, Optional, Callable
from datetime import datetime
from loguru import logger

from app.models.patent_schema import (
    PatentInput,
    PatentDocument,
    PatentSection,
    GenerationProgress,
    GenerationResult
)
from app.services.ai_service import AIService
from app.services.document_service import get_document_service
from app.services.validation_service import get_validation_service
from app.utils.prompts import get_section_display_name
from app.utils.helpers import generate_unique_id


class PatentGenerator:
    """專利生成器類 - 協調整個生成流程"""

    # 章節生成順序
    SECTION_ORDER = [
        'technical_field',
        'background',
        'invention_content',
        'figure_description',
        'implementation',
        'attachments'
    ]

    def __init__(self):
        """初始化專利生成器"""
        self.ai_service = None  # 將在 generate_patent 時根據配置創建
        self.document_service = get_document_service()
        self.validation_service = get_validation_service()

        logger.info("專利生成器已初始化")

    def generate_patent(
        self,
        patent_input: PatentInput,
        progress_callback: Optional[Callable[[GenerationProgress], None]] = None
    ) -> GenerationResult:
        """
        生成完整的專利文件

        Args:
            patent_input: 專利輸入數據
            progress_callback: 進度回調函數（可選）

        Returns:
            GenerationResult: 生成結果
        """
        start_time = time.time()
        patent_id = generate_unique_id()
        total_tokens = 0
        total_cost = 0.0

        logger.info(f"開始生成專利文件 (ID: {patent_id}): {patent_input.patent_name}")

        try:
            # 步驟0: 創建 AI 服務（根據 LLM 配置）
            logger.info(
                f"步驟0: 初始化 AI 服務 - "
                f"提供商: {patent_input.llm_provider}, "
                f"模型: {patent_input.llm_model or '默認'}"
            )

            self.ai_service = AIService(
                llm_provider=patent_input.llm_provider,
                llm_model=patent_input.llm_model,
                api_key=patent_input.api_key,
                use_server_config=patent_input.use_server_key
            )

            # 步驟1: 驗證輸入
            logger.info("步驟1: 驗證輸入數據")
            is_valid, errors = self.validation_service.validate_patent_input(
                patent_input.dict()
            )

            if not is_valid:
                error_msg = f"輸入驗證失敗: {', '.join(errors)}"
                logger.error(error_msg)
                return GenerationResult(
                    success=False,
                    error_message=error_msg
                )

            # 步驟2: 創建專利文件對象
            logger.info("步驟2: 初始化專利文件對象")
            patent_doc = PatentDocument(
                patent_id=patent_id,
                patent_name=patent_input.patent_name,
                inventors=patent_input.inventors,
                classification=patent_input.classification,
                submission_date=patent_input.submission_date,
                keywords=patent_input.keywords.split(',') if patent_input.keywords else []
            )

            # 步驟3: 逐個生成章節
            logger.info("步驟3: 開始生成章節")
            total_sections = len(self.SECTION_ORDER)

            for idx, section_name in enumerate(self.SECTION_ORDER):
                section_display_name = get_section_display_name(section_name)

                # 更新進度
                progress = GenerationProgress(
                    patent_id=patent_id,
                    current_section=section_display_name,
                    completed_sections=[
                        get_section_display_name(s)
                        for s in self.SECTION_ORDER[:idx]
                    ],
                    progress_percentage=int((idx / total_sections) * 100),
                    status='generating'
                )

                if progress_callback:
                    progress_callback(progress)

                logger.info(f"生成章節 {idx + 1}/{total_sections}: {section_display_name}")

                # 生成章節內容
                section, section_stats = self._generate_section(section_name, patent_input)

                # 累計統計
                total_tokens += section_stats.get('tokens', 0)
                total_cost += section_stats.get('cost', 0.0)

                # 設置章節到文檔
                setattr(patent_doc, section_name, section)

            # 步驟4: 驗證生成的文件
            logger.info("步驟4: 驗證生成的專利文件")
            is_valid, issues = self.validation_service.validate_patent_document(patent_doc)

            if not is_valid:
                logger.warning(f"專利文件驗證有問題: {', '.join(issues)}")
                # 不阻止生成，只記錄警告

            # 計算總字數
            patent_doc.calculate_total_words()
            patent_doc.status = 'completed'

            # 步驟5: 創建Word文檔
            logger.info("步驟5: 創建Word文檔")
            file_path = self.document_service.create_patent_document(patent_doc)

            # 計算耗時
            generation_time = time.time() - start_time

            # 最終進度更新
            final_progress = GenerationProgress(
                patent_id=patent_id,
                current_section='已完成',
                completed_sections=[
                    get_section_display_name(s)
                    for s in self.SECTION_ORDER
                ],
                progress_percentage=100,
                status='completed'
            )

            if progress_callback:
                progress_callback(final_progress)

            logger.info(
                f"專利文件生成完成 (ID: {patent_id}, 耗時: {generation_time:.2f}秒, "
                f"總字數: {patent_doc.total_word_count}, "
                f"總成本: ${total_cost:.4f}"
            )

            return GenerationResult(
                success=True,
                patent_document=patent_doc,
                file_path=file_path,
                generation_time=generation_time,
                llm_provider=self.ai_service.provider,
                llm_model=self.ai_service.model,
                total_tokens=total_tokens,
                total_cost=total_cost
            )

        except Exception as e:
            error_msg = f"生成專利文件時發生錯誤: {str(e)}"
            logger.error(error_msg, exc_info=True)

            # 錯誤進度更新
            if progress_callback:
                error_progress = GenerationProgress(
                    patent_id=patent_id,
                    status='error',
                    error_message=str(e)
                )
                progress_callback(error_progress)

            return GenerationResult(
                success=False,
                error_message=error_msg,
                generation_time=time.time() - start_time
            )

        finally:
            # 安全清理：清除 API 密鑰
            if self.ai_service and self.ai_service.llm_config:
                self.ai_service.llm_config.api_key = None
                logger.debug("已清理 API 密鑰")

    def _generate_section(
        self,
        section_name: str,
        patent_input: PatentInput
    ) -> tuple:
        """
        生成單個章節

        Args:
            section_name: 章節名稱
            patent_input: 專利輸入數據

        Returns:
            tuple: (PatentSection, Dict[str, any]) - 章節對象和統計信息
        """
        section_display_name = get_section_display_name(section_name)
        stats = {'tokens': 0, 'cost': 0.0}

        try:
            # 準備輸入數據
            input_data = self._prepare_section_input(patent_input)

            # 調用 AI 服務生成內容（返回 LLMResponse）
            response = self.ai_service.generate_content(
                prompt=self._format_section_prompt(section_name, input_data),
                model=None  # 使用推薦模型
            )

            content = response.content
            stats['tokens'] = response.total_tokens
            stats['cost'] = response.cost

            # 驗證生成的內容
            is_valid, warnings = self.validation_service.validate_section_content(
                section_name=section_name,
                content=content
            )

            if not is_valid:
                logger.warning(f"章節 '{section_display_name}' 驗證有警告: {', '.join(warnings)}")

            # 創建章節對象
            section = PatentSection(
                section_name=section_display_name,
                content=content,
                word_count=len(content),
                generated_at=datetime.now()
            )

            return section, stats

        except Exception as e:
            logger.error(f"生成章節 '{section_display_name}' 失敗: {e}")

            # 返回一個錯誤佔位章節
            section = PatentSection(
                section_name=section_display_name,
                content=f"[生成失敗: {str(e)}]",
                word_count=0,
                generated_at=datetime.now()
            )
            return section, stats

    def _format_section_prompt(self, section_name: str, input_data: Dict[str, str]) -> str:
        """
        格式化章節提示

        Args:
            section_name: 章節名稱
            input_data: 輸入數據

        Returns:
            str: 格式化的提示
        """
        from app.utils.prompts import get_prompt_template

        prompt_template = get_prompt_template(section_name)
        if not prompt_template:
            raise ValueError(f"未找到章節 '{section_name}' 的提示模板")

        try:
            return prompt_template.format(**input_data)
        except KeyError as e:
            logger.error(f"提示模板格式化失敗，缺少鍵: {e}")
            raise ValueError(f"輸入數據缺少必要字段: {e}")

    def _prepare_section_input(self, patent_input: PatentInput) -> Dict[str, str]:
        """
        準備章節輸入數據

        Args:
            patent_input: 專利輸入對象

        Returns:
            Dict[str, str]: 輸入數據字典
        """
        # 組合聯絡資訊
        contact_info = ""
        if patent_input.contact_person:
            contact_info += f"{patent_input.contact_person}"
        if patent_input.contact_number:
            contact_info += f", {patent_input.contact_number}"
        if patent_input.contact_email:
            contact_info += f", {patent_input.contact_email}"

        return {
            'patent_name': patent_input.patent_name or '',
            'keywords': patent_input.keywords or '',
            'technical_description': patent_input.technical_description or '',
            'inventors': patent_input.inventors or '',
            'classification': patent_input.classification or '待補充',
            'contact_person': patent_input.contact_person or '待補充',
            'contact_info': contact_info or '待補充',
            'submission_date': patent_input.submission_date or datetime.now().strftime('%Y-%m-%d'),
            'product_info': patent_input.product_info or '',
            'working_principle': patent_input.working_principle or '',
            'innovation_points': patent_input.innovation_points or '',
            'background_references': patent_input.background_references or '',
            'problems_to_solve': patent_input.problems_to_solve or '',
            'has_diagrams': str(patent_input.has_diagrams).lower(),
            'diagram_description': patent_input.diagram_description or '無附圖',
            'special_requirements': patent_input.special_requirements or ''
        }

    def regenerate_section(
        self,
        section_name: str,
        patent_input: PatentInput
    ) -> PatentSection:
        """
        重新生成指定章節

        Args:
            section_name: 章節名稱
            patent_input: 專利輸入數據

        Returns:
            PatentSection: 重新生成的章節
        """
        logger.info(f"重新生成章節: {get_section_display_name(section_name)}")

        section, _ = self._generate_section(section_name, patent_input)
        return section

    def estimate_generation_cost(self, patent_input: PatentInput) -> Dict[str, float]:
        """
        估算生成成本

        Args:
            patent_input: 專利輸入數據

        Returns:
            Dict[str, float]: 成本估算
        """
        logger.info("估算專利生成成本")

        input_data = self._prepare_section_input(patent_input)

        total_cost = 0.0
        section_costs = {}

        for section_name in self.SECTION_ORDER:
            # 這裡簡化估算，實際成本會根據生成內容長度變化
            estimated_cost = 0.02  # 平均每章節約$0.02
            section_costs[section_name] = estimated_cost
            total_cost += estimated_cost

        return {
            'total_cost': total_cost,
            'section_costs': section_costs,
            'currency': 'USD'
        }

    def get_generation_statistics(self, patent_doc: PatentDocument) -> Dict:
        """
        獲取生成統計信息

        Args:
            patent_doc: 專利文件對象

        Returns:
            Dict: 統計信息
        """
        sections_info = []

        for section_name in self.SECTION_ORDER:
            section = getattr(patent_doc, section_name, None)
            if section:
                sections_info.append({
                    'name': section.section_name,
                    'word_count': section.word_count,
                    'generated_at': section.generated_at.strftime('%Y-%m-%d %H:%M:%S')
                })

        return {
            'patent_id': patent_doc.patent_id,
            'patent_name': patent_doc.patent_name,
            'total_word_count': patent_doc.total_word_count,
            'section_count': len(sections_info),
            'sections': sections_info,
            'status': patent_doc.status,
            'generated_at': patent_doc.generated_at.strftime('%Y-%m-%d %H:%M:%S')
        }


# 創建全局專利生成器實例
_patent_generator_instance = None


def get_patent_generator() -> PatentGenerator:
    """
    獲取專利生成器的全局實例

    Returns:
        PatentGenerator: 專利生成器實例
    """
    global _patent_generator_instance
    if _patent_generator_instance is None:
        _patent_generator_instance = PatentGenerator()
    return _patent_generator_instance

"""
驗證服務模塊
驗證用戶輸入和生成內容的質量
"""
from typing import Dict, List, Tuple
from loguru import logger

from app.models.patent_schema import PatentInput, PatentDocument
from app.utils.helpers import count_chinese_characters, validate_chinese_name


class ValidationService:
    """驗證服務類"""

    # 章節字數要求
    SECTION_WORD_LIMITS = {
        "technical_field": (80, 150),
        "background": (300, 600),
        "invention_content": (500, 1000),
        "figure_description": (100, 300),
        "implementation": (600, 1200),
        "attachments": (100, 300)
    }

    def __init__(self):
        """初始化驗證服務"""
        logger.info("驗證服務已初始化")

    def validate_patent_input(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        驗證專利輸入數據

        Args:
            data: 輸入數據字典

        Returns:
            Tuple[bool, List[str]]: (是否有效, 錯誤訊息列表)
        """
        errors = []

        # 驗證必填字段
        required_fields = ['patent_name', 'inventors', 'keywords', 'technical_description']
        for field in required_fields:
            if not data.get(field) or len(str(data.get(field)).strip()) == 0:
                errors.append(f"'{field}' 是必填字段")

        # 驗證專利名稱
        patent_name = data.get('patent_name', '')
        if patent_name:
            if len(patent_name) < 5:
                errors.append("專利名稱過短，至少需要5個字符")
            elif len(patent_name) > 200:
                errors.append("專利名稱過長，最多200個字符")

            # 檢查是否包含中文
            if not validate_chinese_name(patent_name):
                logger.warning("專利名稱不包含中文字符")

        # 驗證發明人
        inventors = data.get('inventors', '')
        if inventors and len(inventors) < 2:
            errors.append("發明人信息過短")

        # 驗證技術描述
        tech_desc = data.get('technical_description', '')
        if tech_desc and len(tech_desc) < 50:
            errors.append("技術描述過短，至少需要50個字符以便AI理解")
        elif tech_desc and len(tech_desc) > 5000:
            errors.append("技術描述過長，最多5000個字符")

        # 驗證關鍵字
        keywords = data.get('keywords', '')
        if keywords and len(keywords) < 5:
            errors.append("請提供更詳細的技術關鍵字")

        is_valid = len(errors) == 0

        if is_valid:
            logger.info("輸入數據驗證通過")
        else:
            logger.warning(f"輸入數據驗證失敗: {', '.join(errors)}")

        return is_valid, errors

    def validate_section_content(
        self,
        section_name: str,
        content: str
    ) -> Tuple[bool, List[str]]:
        """
        驗證章節內容

        Args:
            section_name: 章節名稱
            content: 章節內容

        Returns:
            Tuple[bool, List[str]]: (是否有效, 警告訊息列表)
        """
        warnings = []

        # 檢查內容是否為空
        if not content or len(content.strip()) == 0:
            warnings.append(f"章節 '{section_name}' 內容為空")
            return False, warnings

        # 獲取字數限制
        word_limits = self.SECTION_WORD_LIMITS.get(section_name)
        if not word_limits:
            logger.warning(f"未找到章節 '{section_name}' 的字數限制")
            return True, warnings

        min_words, max_words = word_limits
        word_count = len(content)

        # 檢查字數
        if word_count < min_words:
            warnings.append(
                f"章節 '{section_name}' 字數過少 ({word_count}/{min_words})"
            )
        elif word_count > max_words * 1.5:  # 允許超出50%
            warnings.append(
                f"章節 '{section_name}' 字數過多 ({word_count}/{max_words})"
            )

        # 檢查是否包含中文
        chinese_count = count_chinese_characters(content)
        if chinese_count < 10:
            warnings.append(f"章節 '{section_name}' 中文內容過少")

        # 檢查是否包含錯誤關鍵字
        error_keywords = ['error', 'sorry', '抱歉', '無法生成', '錯誤']
        content_lower = content.lower()
        for keyword in error_keywords:
            if keyword in content_lower:
                warnings.append(f"章節內容可能包含錯誤訊息: '{keyword}'")

        is_valid = len(warnings) == 0

        if is_valid:
            logger.info(f"章節 '{section_name}' 內容驗證通過 (字數: {word_count})")
        else:
            logger.warning(f"章節 '{section_name}' 內容驗證有警告: {', '.join(warnings)}")

        return is_valid, warnings

    def validate_patent_document(
        self,
        patent_doc: PatentDocument
    ) -> Tuple[bool, List[str]]:
        """
        驗證完整的專利文件

        Args:
            patent_doc: 專利文件對象

        Returns:
            Tuple[bool, List[str]]: (是否有效, 問題列表)
        """
        issues = []

        # 檢查必要章節是否存在
        required_sections = [
            ('technical_field', '技術領域'),
            ('background', '背景技術'),
            ('invention_content', '發明內容'),
            ('implementation', '具體實施方式')
        ]

        for section_key, section_name in required_sections:
            section = getattr(patent_doc, section_key, None)
            if not section:
                issues.append(f"缺少必要章節: {section_name}")
            elif not section.content or len(section.content.strip()) == 0:
                issues.append(f"章節 '{section_name}' 內容為空")

        # 檢查總字數
        total_words = patent_doc.calculate_total_words()
        if total_words < 1000:
            issues.append(f"文件總字數過少 ({total_words}/1000)")

        logger.info(f"專利文件總字數: {total_words}")

        # 檢查元數據
        if not patent_doc.patent_name or len(patent_doc.patent_name.strip()) == 0:
            issues.append("專利名稱為空")

        if not patent_doc.inventors or len(patent_doc.inventors.strip()) == 0:
            issues.append("發明人信息為空")

        is_valid = len(issues) == 0

        if is_valid:
            logger.info(f"專利文件驗證通過 (總字數: {total_words})")
        else:
            logger.warning(f"專利文件驗證失敗: {', '.join(issues)}")

        return is_valid, issues

    def check_content_quality(self, content: str) -> Dict[str, any]:
        """
        檢查內容質量

        Args:
            content: 內容文本

        Returns:
            Dict: 質量報告
        """
        report = {
            'total_chars': len(content),
            'chinese_chars': count_chinese_characters(content),
            'has_punctuation': any(p in content for p in '。，、；：？！'),
            'paragraph_count': len(content.split('\n\n')),
            'quality_score': 0.0
        }

        # 計算質量分數（0-100）
        score = 0.0

        # 字數合理性 (30分)
        if 100 <= report['total_chars'] <= 2000:
            score += 30
        elif report['total_chars'] > 50:
            score += 15

        # 中文內容比例 (30分)
        if report['total_chars'] > 0:
            chinese_ratio = report['chinese_chars'] / report['total_chars']
            if chinese_ratio > 0.5:
                score += 30
            elif chinese_ratio > 0.3:
                score += 15

        # 標點符號 (20分)
        if report['has_punctuation']:
            score += 20

        # 段落結構 (20分)
        if report['paragraph_count'] >= 2:
            score += 20
        elif report['paragraph_count'] >= 1:
            score += 10

        report['quality_score'] = score

        return report

    def get_validation_summary(
        self,
        input_valid: bool,
        input_errors: List[str],
        section_results: Dict[str, Tuple[bool, List[str]]]
    ) -> Dict:
        """
        獲取驗證摘要

        Args:
            input_valid: 輸入是否有效
            input_errors: 輸入錯誤列表
            section_results: 章節驗證結果

        Returns:
            Dict: 驗證摘要
        """
        total_sections = len(section_results)
        valid_sections = sum(1 for valid, _ in section_results.values() if valid)

        all_warnings = []
        for section_name, (_, warnings) in section_results.items():
            all_warnings.extend(warnings)

        summary = {
            'input_valid': input_valid,
            'input_errors': input_errors,
            'total_sections': total_sections,
            'valid_sections': valid_sections,
            'section_pass_rate': valid_sections / total_sections if total_sections > 0 else 0,
            'total_warnings': len(all_warnings),
            'all_warnings': all_warnings,
            'overall_valid': input_valid and (valid_sections == total_sections)
        }

        return summary


# 創建全局驗證服務實例
_validation_service_instance = None


def get_validation_service() -> ValidationService:
    """
    獲取驗證服務的全局實例

    Returns:
        ValidationService: 驗證服務實例
    """
    global _validation_service_instance
    if _validation_service_instance is None:
        _validation_service_instance = ValidationService()
    return _validation_service_instance

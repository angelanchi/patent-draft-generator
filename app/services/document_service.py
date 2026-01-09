"""
文檔服務模塊
負責創建和格式化Word文檔
"""
from pathlib import Path
from datetime import datetime
from typing import Optional
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from loguru import logger

from app.models.patent_schema import PatentDocument, PatentSection
from app.config import get_settings
from app.utils.helpers import generate_filename, ensure_directory


class DocumentService:
    """文檔生成服務類"""

    def __init__(self):
        """初始化文檔服務"""
        self.settings = get_settings()
        self.output_dir = Path(self.settings.OUTPUT_DIR)
        ensure_directory(self.output_dir)
        logger.info("文檔服務已初始化")

    def create_patent_document(
        self,
        patent_data: PatentDocument,
        filename: Optional[str] = None
    ) -> str:
        """
        創建專利Word文檔

        Args:
            patent_data: 專利文件數據
            filename: 文件名（可選，默認自動生成）

        Returns:
            str: 生成的文件路徑
        """
        try:
            logger.info(f"開始創建專利文檔: {patent_data.patent_name}")

            # 創建新文檔
            doc = Document()

            # 設置文檔屬性
            self._set_document_properties(doc, patent_data)

            # 設置文檔樣式
            self._setup_styles(doc)

            # 添加標題頁
            self._add_title_page(doc, patent_data)

            # 添加目錄（佔位符）
            self._add_table_of_contents(doc)

            # 添加主要章節
            self._add_sections(doc, patent_data)

            # 添加頁腳
            self._add_footer(doc, patent_data)

            # 生成文件名
            if not filename:
                filename = generate_filename(patent_data.patent_name)

            # 保存文檔
            file_path = self.output_dir / filename
            doc.save(str(file_path))

            logger.info(f"專利文檔已創建: {file_path}")

            return str(file_path)

        except Exception as e:
            logger.error(f"創建專利文檔失敗: {e}")
            raise

    def _set_document_properties(self, doc: Document, patent_data: PatentDocument):
        """設置文檔屬性"""
        core_properties = doc.core_properties
        core_properties.title = patent_data.patent_name
        core_properties.author = patent_data.inventors
        core_properties.subject = "專利申請文件"
        core_properties.keywords = ', '.join(patent_data.keywords) if patent_data.keywords else ""
        core_properties.created = datetime.now()

    def _setup_styles(self, doc: Document):
        """設置文檔樣式"""
        # 設置默認字體為宋體或微軟雅黑
        style = doc.styles['Normal']
        style.font.name = '宋體'
        style._element.rPr.rFonts.set(qn('w:eastAsia'), '宋體')
        style.font.size = Pt(12)

        # 設置標題1樣式
        heading1 = doc.styles['Heading 1']
        heading1.font.name = '黑體'
        heading1._element.rPr.rFonts.set(qn('w:eastAsia'), '黑體')
        heading1.font.size = Pt(16)
        heading1.font.bold = True
        heading1.font.color.rgb = RGBColor(0, 0, 0)

        # 設置標題2樣式
        heading2 = doc.styles['Heading 2']
        heading2.font.name = '黑體'
        heading2._element.rPr.rFonts.set(qn('w:eastAsia'), '黑體')
        heading2.font.size = Pt(14)
        heading2.font.bold = True

    def _add_title_page(self, doc: Document, patent_data: PatentDocument):
        """添加標題頁"""
        # 專利名稱（居中、大字體）
        title = doc.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title.add_run(patent_data.patent_name)
        title_run.font.size = Pt(22)
        title_run.font.bold = True
        title_run.font.name = '黑體'
        title_run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑體')

        doc.add_paragraph()  # 空行

        # 基本信息表格
        table = doc.add_table(rows=5, cols=2)
        table.style = 'Light Grid Accent 1'

        # 填充表格
        cells = table.rows[0].cells
        cells[0].text = '專利名稱'
        cells[1].text = patent_data.patent_name

        cells = table.rows[1].cells
        cells[0].text = '發明人'
        cells[1].text = patent_data.inventors

        cells = table.rows[2].cells
        cells[0].text = '分類號'
        cells[1].text = patent_data.classification or '待補充'

        cells = table.rows[3].cells
        cells[0].text = '提案日期'
        cells[1].text = patent_data.submission_date or datetime.now().strftime('%Y年%m月%d日')

        cells = table.rows[4].cells
        cells[0].text = '生成日期'
        cells[1].text = patent_data.generated_at.strftime('%Y年%m月%d日 %H:%M:%S')

        # 分頁
        doc.add_page_break()

    def _add_table_of_contents(self, doc: Document):
        """添加目錄（佔位符）"""
        heading = doc.add_heading('目錄', level=1)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph('（在Microsoft Word中，請使用"引用" -> "更新目錄"來生成完整目錄）')

        doc.add_page_break()

    def _add_sections(self, doc: Document, patent_data: PatentDocument):
        """添加所有章節"""
        sections = [
            ('1. 技術領域', patent_data.technical_field),
            ('2. 背景技術', patent_data.background),
            ('3. 發明內容', patent_data.invention_content),
            ('4. 附圖說明', patent_data.figure_description),
            ('5. 具體實施方式', patent_data.implementation),
            ('6. 其它發明附件', patent_data.attachments)
        ]

        for section_title, section_data in sections:
            if section_data:
                self._add_section(doc, section_title, section_data)

    def _add_section(self, doc: Document, title: str, section: PatentSection):
        """
        添加單個章節

        Args:
            doc: Document對象
            title: 章節標題
            section: 章節數據
        """
        # 添加標題
        heading = doc.add_heading(title, level=1)

        # 添加內容
        content = section.content.strip()

        # 分段處理（按雙換行符分段）
        paragraphs = content.split('\n\n')

        for para_text in paragraphs:
            para_text = para_text.strip()
            if para_text:
                para = doc.add_paragraph(para_text)
                para.paragraph_format.line_spacing = 1.5
                para.paragraph_format.space_after = Pt(6)

                # 設置段落字體
                for run in para.runs:
                    run.font.name = '宋體'
                    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋體')
                    run.font.size = Pt(12)

        # 添加章節之間的間距
        doc.add_paragraph()

    def _add_footer(self, doc: Document, patent_data: PatentDocument):
        """添加頁腳"""
        section = doc.sections[0]
        footer = section.footer

        # 添加頁碼和生成信息
        footer_para = footer.paragraphs[0]
        footer_para.text = f"第 頁 | {patent_data.patent_name} | 生成於 {patent_data.generated_at.strftime('%Y-%m-%d')}"
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 設置頁腳字體
        for run in footer_para.runs:
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(128, 128, 128)

    def add_image_to_document(
        self,
        doc: Document,
        image_path: str,
        caption: Optional[str] = None,
        width: Optional[float] = None
    ):
        """
        向文檔添加圖片

        Args:
            doc: Document對象
            image_path: 圖片路徑
            caption: 圖片說明（可選）
            width: 圖片寬度（英寸，可選）
        """
        try:
            if not Path(image_path).exists():
                logger.warning(f"圖片不存在: {image_path}")
                return

            # 添加圖片
            if width:
                doc.add_picture(image_path, width=Inches(width))
            else:
                doc.add_picture(image_path, width=Inches(5))

            # 添加圖片說明
            if caption:
                caption_para = doc.add_paragraph(caption)
                caption_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in caption_para.runs:
                    run.font.size = Pt(10)
                    run.font.italic = True

            logger.info(f"已添加圖片: {image_path}")

        except Exception as e:
            logger.error(f"添加圖片失敗: {e}")

    def get_document_info(self, file_path: str) -> dict:
        """
        獲取文檔信息

        Args:
            file_path: 文件路徑

        Returns:
            dict: 文檔信息
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {}

            doc = Document(str(path))

            return {
                'filename': path.name,
                'size_bytes': path.stat().st_size,
                'size_mb': path.stat().st_size / (1024 * 1024),
                'created': path.stat().st_ctime,
                'modified': path.stat().st_mtime,
                'paragraph_count': len(doc.paragraphs),
                'section_count': len(doc.sections)
            }

        except Exception as e:
            logger.error(f"獲取文檔信息失敗: {e}")
            return {}


# 創建全局文檔服務實例
_document_service_instance = None


def get_document_service() -> DocumentService:
    """
    獲取文檔服務的全局實例

    Returns:
        DocumentService: 文檔服務實例
    """
    global _document_service_instance
    if _document_service_instance is None:
        _document_service_instance = DocumentService()
    return _document_service_instance

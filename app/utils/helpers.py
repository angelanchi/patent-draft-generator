"""
輔助工具函數
提供通用的輔助功能
"""
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


def generate_unique_id() -> str:
    """
    生成唯一ID

    Returns:
        str: UUID字符串
    """
    return str(uuid.uuid4())


def generate_filename(patent_name: str, extension: str = 'docx') -> str:
    """
    根據專利名稱生成文件名

    Args:
        patent_name: 專利名稱
        extension: 文件擴展名

    Returns:
        str: 文件名
    """
    # 移除非法文件名字符
    safe_name = re.sub(r'[<>:"/\\|?*]', '', patent_name)
    safe_name = safe_name.strip()

    # 限制長度
    if len(safe_name) > 50:
        safe_name = safe_name[:50]

    # 添加時間戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 組合文件名
    filename = f"{safe_name}_{timestamp}.{extension}"

    return filename


def count_chinese_characters(text: str) -> int:
    """
    計算中文字符數

    Args:
        text: 文本內容

    Returns:
        int: 中文字符數量
    """
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    chinese_chars = chinese_pattern.findall(text)
    return len(chinese_chars)


def clean_text(text: str) -> str:
    """
    清理文本，移除多餘的空白和特殊字符

    Args:
        text: 原始文本

    Returns:
        str: 清理後的文本
    """
    # 移除多餘的空白
    text = re.sub(r'\s+', ' ', text)

    # 移除首尾空白
    text = text.strip()

    return text


def format_date(date_str: Optional[str] = None, format: str = '%Y年%m月%d日') -> str:
    """
    格式化日期

    Args:
        date_str: 日期字符串（可選，默認當前日期）
        format: 輸出格式

    Returns:
        str: 格式化的日期字符串
    """
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            date_obj = datetime.now()
    else:
        date_obj = datetime.now()

    return date_obj.strftime(format)


def ensure_directory(directory: str) -> Path:
    """
    確保目錄存在，如果不存在則創建

    Args:
        directory: 目錄路徑

    Returns:
        Path: 目錄的Path對象
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_file_size_mb(file_path: str) -> float:
    """
    獲取文件大小（MB）

    Args:
        file_path: 文件路徑

    Returns:
        float: 文件大小（MB）
    """
    path = Path(file_path)
    if path.exists():
        size_bytes = path.stat().st_size
        return size_bytes / (1024 * 1024)
    return 0.0


def validate_chinese_name(name: str) -> bool:
    """
    驗證是否包含中文字符

    Args:
        name: 名稱

    Returns:
        bool: 是否包含中文
    """
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(chinese_pattern.search(name))


def split_keywords(keywords: str) -> list:
    """
    分割關鍵字字符串為列表

    Args:
        keywords: 關鍵字字符串（逗號或頓號分隔）

    Returns:
        list: 關鍵字列表
    """
    # 支持多種分隔符
    keywords = re.sub(r'[,，、;；]', ',', keywords)
    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
    return keyword_list


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    截斷文本到指定長度

    Args:
        text: 原始文本
        max_length: 最大長度
        suffix: 截斷後綴

    Returns:
        str: 截斷後的文本
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def format_number(number: int or float, decimal_places: int = 2) -> str:
    """
    格式化數字為字符串

    Args:
        number: 數字
        decimal_places: 小數位數

    Returns:
        str: 格式化的數字字符串
    """
    if isinstance(number, int):
        return f"{number:,}"
    else:
        return f"{number:,.{decimal_places}f}"


def seconds_to_time_string(seconds: float) -> str:
    """
    將秒數轉換為可讀的時間字符串

    Args:
        seconds: 秒數

    Returns:
        str: 時間字符串（如"2分30秒"）
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}分{secs}秒"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}小時{minutes}分鐘"

"""
配置管理模塊
管理應用程序的所有配置設置
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """應用程序設置"""

    # OpenAI配置（可選，用戶可以輸入自己的 API 密鑰）
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7

    # Flask配置
    FLASK_APP: str = "run.py"
    FLASK_ENV: str = "development"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    SESSION_TYPE: str = "filesystem"

    # 文件存儲配置
    OUTPUT_DIR: str = "output"
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB

    # 應用設置
    DEFAULT_LANGUAGE: str = "zh-CN"
    MAX_GENERATION_TIME: int = 300  # 5分鐘
    ENABLE_CACHING: bool = True

    # 日誌配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 創建全局配置實例
def get_settings() -> Settings:
    """
    獲取配置實例

    Returns:
        Settings: 配置對象
    """
    return Settings()


# Flask配置類
class FlaskConfig:
    """Flask應用配置"""

    def __init__(self, settings: Settings = None):
        if settings is None:
            settings = get_settings()

        # 基礎配置
        self.SECRET_KEY = settings.SECRET_KEY
        self.SESSION_TYPE = settings.SESSION_TYPE

        # 文件上傳配置
        self.MAX_CONTENT_LENGTH = settings.MAX_UPLOAD_SIZE
        self.UPLOAD_FOLDER = settings.UPLOAD_DIR

        # 輸出目錄
        self.OUTPUT_FOLDER = settings.OUTPUT_DIR

        # 確保目錄存在
        self._ensure_directories()

    def _ensure_directories(self):
        """確保必要的目錄存在"""
        directories = [
            self.UPLOAD_FOLDER,
            self.OUTPUT_FOLDER,
            "logs"
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(FlaskConfig):
    """開發環境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(FlaskConfig):
    """生產環境配置"""
    DEBUG = False
    TESTING = False


class TestingConfig(FlaskConfig):
    """測試環境配置"""
    DEBUG = True
    TESTING = True


# 配置映射
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}


def get_flask_config(env: str = None):
    """
    獲取Flask配置

    Args:
        env: 環境名稱 ('development', 'production', 'testing')

    Returns:
        FlaskConfig: Flask配置對象
    """
    if env is None:
        settings = get_settings()
        env = settings.FLASK_ENV

    config_class = config_dict.get(env, DevelopmentConfig)
    return config_class()

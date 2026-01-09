"""
Flask應用工廠
創建和配置Flask應用程序實例
"""
from flask import Flask
from flask_session import Session
from loguru import logger
import sys
from pathlib import Path

from app.config import get_flask_config, get_settings


def create_app(config_name=None):
    """
    創建Flask應用程序實例

    Args:
        config_name: 配置環境名稱 ('development', 'production', 'testing')

    Returns:
        Flask: 配置好的Flask應用程序實例
    """
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # 載入配置
    flask_config = get_flask_config(config_name)
    app.config.from_object(flask_config)

    # 配置日誌
    configure_logging(app)

    # 初始化擴展
    Session(app)

    # 註冊藍圖
    register_blueprints(app)

    # 註冊錯誤處理器
    register_error_handlers(app)

    # 配置Jinja2模板環境
    configure_template_filters(app)

    logger.info(f"Flask應用程序已創建 (環境: {config_name or 'development'})")

    return app


def configure_logging(app):
    """
    配置日誌系統

    Args:
        app: Flask應用程序實例
    """
    settings = get_settings()

    # 移除默認處理器
    logger.remove()

    # 添加控制台輸出
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )

    # 添加文件輸出
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        settings.LOG_FILE,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days",
        encoding="utf-8"
    )


def register_blueprints(app):
    """
    註冊Flask藍圖

    Args:
        app: Flask應用程序實例
    """
    from app.routes import main, api, download

    app.register_blueprint(main.bp)
    app.register_blueprint(api.bp, url_prefix='/api')
    app.register_blueprint(download.bp, url_prefix='/download')

    logger.info("已註冊所有藍圖")


def register_error_handlers(app):
    """
    註冊錯誤處理器

    Args:
        app: Flask應用程序實例
    """

    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404錯誤: {error}")
        return {"error": "頁面未找到"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500錯誤: {error}")
        return {"error": "內部服務器錯誤"}, 500

    @app.errorhandler(413)
    def request_entity_too_large(error):
        logger.warning(f"文件過大: {error}")
        return {"error": "上傳文件過大，請確保文件小於10MB"}, 413


def configure_template_filters(app):
    """
    配置Jinja2模板過濾器

    Args:
        app: Flask應用程序實例
    """

    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
        """格式化日期時間"""
        if value is None:
            return ""
        return value.strftime(format)

    @app.template_filter('truncate_chars')
    def truncate_chars(value, length=100):
        """截斷字符串"""
        if len(value) <= length:
            return value
        return value[:length] + '...'

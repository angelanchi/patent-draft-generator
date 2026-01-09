"""
應用程序入口點
啟動Flask應用程序
"""
import os
from dotenv import load_dotenv
from app import create_app
from loguru import logger

# 載入環境變量
load_dotenv()

# 創建Flask應用
app = create_app()

if __name__ == '__main__':
    # 從環境變量獲取配置
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'

    logger.info(f"啟動Flask應用程序於 http://{host}:{port}")
    logger.info(f"調試模式: {debug}")

    # 運行應用
    app.run(
        host=host,
        port=port,
        debug=debug
    )

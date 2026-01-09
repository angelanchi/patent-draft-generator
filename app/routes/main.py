"""
主要Web路由
處理Web界面相關的請求
"""
from flask import Blueprint, render_template, request, jsonify, session
from loguru import logger

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """
    首頁 - 專利生成表單

    Returns:
        HTML: 渲染的首頁模板
    """
    logger.info("訪問首頁")
    return render_template('index.html')


@bp.route('/about')
def about():
    """
    關於頁面

    Returns:
        HTML: 關於頁面模板
    """
    return render_template('about.html')


@bp.route('/form')
def form():
    """
    專利生成表單頁面

    Returns:
        HTML: 多步驟表單模板
    """
    logger.info("訪問表單頁面")
    return render_template('form.html')


@bp.route('/generating')
def generating():
    """
    專利生成進度頁面

    Returns:
        HTML: 生成進度模板
    """
    logger.info("訪問生成進度頁面")
    return render_template('generating.html')


@bp.route('/preview')
def preview():
    """
    專利預覽頁面

    Returns:
        HTML: 預覽模板
    """
    logger.info("訪問預覽頁面")
    return render_template('preview.html')


@bp.route('/files')
def list_files():
    """
    文件列表頁面

    Returns:
        HTML: 文件列表模板
    """
    logger.info("訪問文件列表頁面")
    return render_template('files.html')


@bp.route('/health')
def health():
    """
    健康檢查端點

    Returns:
        JSON: 健康狀態
    """
    return jsonify({
        'status': 'healthy',
        'service': 'IP Generator',
        'version': '1.0.0'
    })

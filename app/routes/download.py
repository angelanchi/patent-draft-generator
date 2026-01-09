"""
下載路由
處理文件下載相關的請求
"""
from flask import Blueprint, send_file, abort, jsonify
from loguru import logger
from pathlib import Path

from app.config import get_settings

bp = Blueprint('download', __name__)


@bp.route('/patent/<filename>', methods=['GET'])
def download_patent(filename):
    """
    下載生成的專利文件

    Args:
        filename: 文件名

    Returns:
        File: Word文檔文件
    """
    try:
        settings = get_settings()
        file_path = Path(settings.OUTPUT_DIR) / filename

        # 檢查文件是否存在
        if not file_path.exists():
            logger.warning(f"文件不存在: {filename}")
            abort(404)

        # 檢查文件是否為docx格式
        if not filename.endswith('.docx'):
            logger.warning(f"非法文件格式: {filename}")
            abort(400)

        logger.info(f"下載文件: {filename}")

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        logger.error(f"文件下載失敗: {e}")
        return jsonify({'error': '文件下載失敗'}), 500


@bp.route('/list', methods=['GET'])
def list_files():
    """
    列出所有可下載的文件

    Returns:
        JSON: 文件列表
    """
    try:
        settings = get_settings()
        output_dir = Path(settings.OUTPUT_DIR)

        if not output_dir.exists():
            return jsonify({'files': []})

        # 獲取所有docx文件
        files = []
        for file_path in output_dir.glob('*.docx'):
            files.append({
                'filename': file_path.name,
                'size': file_path.stat().st_size,
                'modified': file_path.stat().st_mtime
            })

        # 按修改時間降序排序
        files.sort(key=lambda x: x['modified'], reverse=True)

        return jsonify({'files': files})

    except Exception as e:
        logger.error(f"獲取文件列表失敗: {e}")
        return jsonify({'error': '獲取文件列表失敗'}), 500

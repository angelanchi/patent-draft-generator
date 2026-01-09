"""
API路由
處理RESTful API請求
"""
from flask import Blueprint, request, jsonify
from loguru import logger
from pydantic import ValidationError

from app.models.patent_schema import PatentInput
from app.services.ai_service import AIService
from app.services.patent_generator import get_patent_generator
from app.services.llm import get_all_providers, get_provider_models

bp = Blueprint('api', __name__)


@bp.route('/test', methods=['GET'])
def test():
    """
    API測試端點

    Returns:
        JSON: 測試響應
    """
    return jsonify({
        'message': 'API is working',
        'status': 'success'
    })


@bp.route('/generate/section', methods=['POST'])
def generate_section():
    """
    生成單個章節的API端點（用於測試）

    Request Body:
        {
            "section_name": "technical_field",
            "patent_data": {...}
        }

    Returns:
        JSON: 生成的章節內容
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '請提供有效的JSON數據'}), 400

        section_name = data.get('section_name')
        patent_data = data.get('patent_data', {})

        if not section_name:
            return jsonify({'error': '請指定要生成的章節名稱'}), 400

        logger.info(f"API請求: 生成章節 '{section_name}'")

        # 獲取AI服務
        ai_service = get_ai_service()

        # 生成章節內容
        content = ai_service.generate_section_content(
            section_name=section_name,
            input_data=patent_data
        )

        return jsonify({
            'success': True,
            'section_name': section_name,
            'content': content,
            'word_count': len(content)
        })

    except ValidationError as e:
        logger.error(f"數據驗證失敗: {e}")
        return jsonify({'error': '輸入數據驗證失敗', 'details': str(e)}), 400

    except Exception as e:
        logger.error(f"生成章節失敗: {e}")
        return jsonify({'error': '生成失敗', 'message': str(e)}), 500


@bp.route('/validate/input', methods=['POST'])
def validate_input():
    """
    驗證用戶輸入

    Request Body:
        PatentInput模型的JSON數據

    Returns:
        JSON: 驗證結果
    """
    try:
        data = request.get_json()

        # 使用Pydantic模型驗證
        patent_input = PatentInput(**data)

        return jsonify({
            'success': True,
            'message': '輸入數據驗證通過',
            'data': patent_input.dict()
        })

    except ValidationError as e:
        logger.warning(f"輸入驗證失敗: {e}")
        return jsonify({
            'success': False,
            'errors': e.errors()
        }), 400

    except Exception as e:
        logger.error(f"驗證過程出錯: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/generate/patent', methods=['POST'])
def generate_patent():
    """
    生成完整專利文件的API端點

    Request Body:
        PatentInput模型的JSON數據

    Returns:
        JSON: 生成結果，包含文件路徑和專利文件信息
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '請提供有效的JSON數據'}), 400

        logger.info("API請求: 生成完整專利文件")

        # 驗證並創建PatentInput對象
        patent_input = PatentInput(**data)

        # 獲取專利生成器
        generator = get_patent_generator()

        # 生成專利文件
        result = generator.generate_patent(patent_input)

        if result.success:
            return jsonify({
                'success': True,
                'message': '專利文件生成成功',
                'file_path': result.file_path,
                'generation_time': result.generation_time,
                'patent_info': {
                    'patent_id': result.patent_document.patent_id,
                    'patent_name': result.patent_document.patent_name,
                    'total_word_count': result.patent_document.total_word_count,
                    'generated_at': result.patent_document.generated_at.strftime('%Y-%m-%d %H:%M:%S')
                },
                'llm_stats': {
                    'provider': result.llm_provider,
                    'model': result.llm_model,
                    'total_tokens': result.total_tokens,
                    'total_cost': result.total_cost
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result.error_message
            }), 500

    except ValidationError as e:
        logger.error(f"輸入驗證失敗: {e}")
        return jsonify({
            'success': False,
            'error': '輸入數據驗證失敗',
            'details': e.errors()
        }), 400

    except Exception as e:
        logger.error(f"生成專利文件失敗: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '生成失敗',
            'message': str(e)
        }), 500


@bp.route('/estimate/cost', methods=['POST'])
def estimate_cost():
    """
    估算生成成本的API端點

    Request Body:
        PatentInput模型的JSON數據

    Returns:
        JSON: 成本估算信息
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '請提供有效的JSON數據'}), 400

        # 驗證並創建PatentInput對象
        patent_input = PatentInput(**data)

        # 獲取專利生成器
        generator = get_patent_generator()

        # 估算成本
        cost_estimate = generator.estimate_generation_cost(patent_input)

        return jsonify({
            'success': True,
            'cost_estimate': cost_estimate
        })

    except ValidationError as e:
        logger.error(f"輸入驗證失敗: {e}")
        return jsonify({
            'success': False,
            'error': '輸入數據驗證失敗',
            'details': e.errors()
        }), 400

    except Exception as e:
        logger.error(f"成本估算失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/llm/providers', methods=['GET'])
def get_llm_providers():
    """
    獲取所有支持的 LLM 提供商列表

    Returns:
        JSON: 提供商列表
    """
    try:
        providers = get_all_providers()

        return jsonify({
            'success': True,
            'providers': providers
        })

    except Exception as e:
        logger.error(f"獲取提供商列表失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/llm/models/<provider>', methods=['GET'])
def get_llm_models(provider: str):
    """
    獲取指定提供商的模型列表

    Args:
        provider: 提供商名稱

    Returns:
        JSON: 模型列表
    """
    try:
        models = get_provider_models(provider)

        if not models:
            return jsonify({
                'success': False,
                'error': f'提供商 "{provider}" 不存在或沒有支持的模型'
            }), 404

        return jsonify({
            'success': True,
            'provider': provider,
            'models': models
        })

    except Exception as e:
        logger.error(f"獲取模型列表失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

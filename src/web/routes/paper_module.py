from flask import Blueprint, render_template, request, jsonify, current_app, g
from flask_login import login_required
from src.models.paper_generator import PaperGenerator
from src.models.api_manager import APIManager
from src.utils.logger import setup_logger
from src.config.prompt_templates import EDUCATION_LEVELS, SUBJECT_AREAS
from src.utils.validators import validate_input, sanitize_html
from src.utils.exceptions import ValidationError, GenerationError
import asyncio
import json
import os
import time
import traceback
import bleach
from functools import wraps

logger = setup_logger(__name__)

# 创建蓝图
paper_module_bp = Blueprint('paper_module', __name__, url_prefix='/paper_module')

# 存储生成任务的进度信息
body_generation_tasks = {}

# 初始化API管理器和论文生成器
api_manager = APIManager()
paper_generator = PaperGenerator(api_manager)

# 全局变量存储生成状态
generation_status = {
    "in_progress": False,
    "progress": 0.0,
    "current_section": "",
    "content": ""
}

# 定义请求超时时间（秒）
REQUEST_TIMEOUT = 60

# 输入验证装饰器
def validate_json_input(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if not request.is_json:
                    return jsonify({"success": False, "message": "请求必须是JSON格式"}), 400
                
                data = request.json
                validate_input(data, schema)
                return f(*args, **kwargs)
            except ValidationError as e:
                logger.warning(f"输入验证失败: {str(e)}")
                return jsonify({"success": False, "message": str(e)}), 400
            except Exception as e:
                logger.error(f"处理请求时出错: {str(e)}")
                return jsonify({"success": False, "message": "服务器内部错误"}), 500
        return decorated_function
    return decorator

@paper_module_bp.route('/', methods=['GET'])
def index():
    """论文模块化生成页面"""
    return render_template(
        'paper_module/index.html', 
        education_levels=EDUCATION_LEVELS,
        subject_areas=SUBJECT_AREAS
    )

@paper_module_bp.route('/generate_abstract_cn', methods=['POST'])
@validate_json_input({
    "title": {"type": "string", "required": True, "min_length": 1, "max_length": 200},
    "outline": {"type": "string", "required": True, "min_length": 1},
    "subject": {"type": "string", "required": False},
    "education_level": {"type": "string", "required": False},
    "custom_prompt": {"type": "string", "required": False}
})
def generate_abstract_cn():
    """生成中文摘要"""
    try:
        data = request.json
        title = bleach.clean(data.get('title', ''))
        outline = bleach.clean(data.get('outline', ''))
        subject = bleach.clean(data.get('subject', '通用'))
        education_level = bleach.clean(data.get('education_level', '本科'))
        custom_prompt = bleach.clean(data.get('custom_prompt', ''))
        
        # 验证学科和教育水平
        if subject not in SUBJECT_AREAS:
            subject = "通用"
        
        if education_level not in EDUCATION_LEVELS:
            education_level = "本科"
        
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 执行异步生成，设置超时
            abstract = loop.run_until_complete(
                asyncio.wait_for(
                    paper_generator.generate_abstract_cn(
                        title=title, 
                        outline=outline,
                        subject=subject,
                        education_level=education_level,
                        custom_prompt=custom_prompt
                    ),
                    timeout=REQUEST_TIMEOUT
                )
            )
            return jsonify({"success": True, "abstract_cn": abstract})
        except asyncio.TimeoutError:
            logger.error(f"生成中文摘要超时")
            return jsonify({"success": False, "message": "生成超时，请稍后重试或减少内容长度"})
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"生成中文摘要出错: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"生成失败: {str(e)}"})

@paper_module_bp.route('/generate_keywords_cn', methods=['POST'])
@validate_json_input({
    "title": {"type": "string", "required": True, "min_length": 1, "max_length": 200},
    "abstract_cn": {"type": "string", "required": True, "min_length": 1},
    "subject": {"type": "string", "required": False},
    "education_level": {"type": "string", "required": False},
    "custom_prompt": {"type": "string", "required": False}
})
def generate_keywords_cn():
    """生成中文关键词"""
    try:
        data = request.json
        title = bleach.clean(data.get('title', ''))
        abstract = bleach.clean(data.get('abstract_cn', ''))
        subject = bleach.clean(data.get('subject', '通用'))
        education_level = bleach.clean(data.get('education_level', '本科'))
        custom_prompt = bleach.clean(data.get('custom_prompt', ''))
        
        # 验证学科和教育水平
        if subject not in SUBJECT_AREAS:
            subject = "通用"
        
        if education_level not in EDUCATION_LEVELS:
            education_level = "本科"
        
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 执行异步生成，设置超时
            keywords = loop.run_until_complete(
                asyncio.wait_for(
                    paper_generator.generate_keywords_cn(
                        title=title, 
                        abstract=abstract,
                        subject=subject,
                        education_level=education_level,
                        custom_prompt=custom_prompt
                    ),
                    timeout=REQUEST_TIMEOUT
                )
            )
            return jsonify({"success": True, "keywords_cn": keywords})
        except asyncio.TimeoutError:
            logger.error(f"生成中文关键词超时")
            return jsonify({"success": False, "message": "生成超时，请稍后重试"})
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"生成中文关键词出错: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"生成失败: {str(e)}"})

@paper_module_bp.route('/generate_abstract_en', methods=['POST'])
@validate_json_input({
    "title": {"type": "string", "required": True, "min_length": 1, "max_length": 200},
    "abstract_cn": {"type": "string", "required": True, "min_length": 1},
    "subject": {"type": "string", "required": False},
    "education_level": {"type": "string", "required": False},
    "custom_prompt": {"type": "string", "required": False}
})
def generate_abstract_en():
    """生成英文摘要"""
    try:
        data = request.json
        title = bleach.clean(data.get('title', ''))
        abstract_cn = bleach.clean(data.get('abstract_cn', ''))
        subject = bleach.clean(data.get('subject', '通用'))
        education_level = bleach.clean(data.get('education_level', '本科'))
        custom_prompt = bleach.clean(data.get('custom_prompt', ''))
        
        # 验证学科和教育水平
        if subject not in SUBJECT_AREAS:
            subject = "通用"
        
        if education_level not in EDUCATION_LEVELS:
            education_level = "本科"
        
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 执行异步生成，设置超时
            abstract = loop.run_until_complete(
                asyncio.wait_for(
                    paper_generator.generate_abstract_en(
                        title=title, 
                        abstract_cn=abstract_cn,
                        subject=subject,
                        education_level=education_level,
                        custom_prompt=custom_prompt
                    ),
                    timeout=REQUEST_TIMEOUT
                )
            )
            return jsonify({"success": True, "abstract_en": abstract})
        except asyncio.TimeoutError:
            logger.error(f"生成英文摘要超时")
            return jsonify({"success": False, "message": "生成超时，请稍后重试或减少内容长度"})
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"生成英文摘要出错: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"生成失败: {str(e)}"})

@paper_module_bp.route('/generate_keywords_en', methods=['POST'])
@validate_json_input({
    "title": {"type": "string", "required": True, "min_length": 1, "max_length": 200},
    "keywords_cn": {"type": "string", "required": True, "min_length": 1},
    "subject": {"type": "string", "required": False},
    "education_level": {"type": "string", "required": False},
    "custom_prompt": {"type": "string", "required": False}
})
def generate_keywords_en():
    """生成英文关键词"""
    try:
        data = request.json
        title = bleach.clean(data.get('title', ''))
        keywords_cn = bleach.clean(data.get('keywords_cn', ''))
        subject = bleach.clean(data.get('subject', '通用'))
        education_level = bleach.clean(data.get('education_level', '本科'))
        custom_prompt = bleach.clean(data.get('custom_prompt', ''))
        
        # 验证学科和教育水平
        if subject not in SUBJECT_AREAS:
            subject = "通用"
        
        if education_level not in EDUCATION_LEVELS:
            education_level = "本科"
        
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 执行异步生成，设置超时
            keywords = loop.run_until_complete(
                asyncio.wait_for(
                    paper_generator.generate_keywords_en(
                        title=title, 
                        keywords_cn=keywords_cn,
                        subject=subject,
                        education_level=education_level,
                        custom_prompt=custom_prompt
                    ),
                    timeout=REQUEST_TIMEOUT
                )
            )
            return jsonify({"success": True, "keywords_en": keywords})
        except asyncio.TimeoutError:
            logger.error(f"生成英文关键词超时")
            return jsonify({"success": False, "message": "生成超时，请稍后重试"})
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"生成英文关键词出错: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"生成失败: {str(e)}"})

@paper_module_bp.route('/generate_paper_body', methods=['POST'])
@validate_json_input({
    "title": {"type": "string", "required": True, "min_length": 1, "max_length": 200},
    "outline": {"type": "string", "required": True, "min_length": 1},
    "word_count": {"type": "integer", "required": True, "min": 1000, "max": 20000},
    "subject": {"type": "string", "required": False},
    "education_level": {"type": "string", "required": False},
    "custom_prompt": {"type": "string", "required": False}
})
def generate_paper_body():
    """生成论文正文"""
    try:
        data = request.json
        title = bleach.clean(data.get('title', ''))
        outline = bleach.clean(data.get('outline', ''))
        word_count = int(data.get('word_count', 3000))
        subject = bleach.clean(data.get('subject', '通用'))
        education_level = bleach.clean(data.get('education_level', '本科'))
        custom_prompt = bleach.clean(data.get('custom_prompt', ''))
        
        # 验证学科和教育水平
        if subject not in SUBJECT_AREAS:
            subject = "通用"
        
        if education_level not in EDUCATION_LEVELS:
            education_level = "本科"
        
        # 限制字数范围
        if word_count < 1000:
            word_count = 1000
        elif word_count > 20000:
            word_count = 20000
        
        # 重置生成状态
        global generation_status
        generation_status = {
            "in_progress": True,
            "progress": 0.0,
            "current_section": "准备中...",
            "content": ""
        }
        
        # 创建回调函数
        def progress_callback(section, progress, content):
            global generation_status
            generation_status["progress"] = progress
            generation_status["current_section"] = section
            generation_status["content"] = sanitize_html(content)
        
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 执行异步生成
            content = loop.run_until_complete(
                asyncio.wait_for(
                    paper_generator.generate_paper_body(
                        title=title, 
                        outline_text=outline,
                        total_word_count=word_count,
                        subject=subject,
                        education_level=education_level,
                        custom_prompt=custom_prompt,
                        progress_callback=progress_callback
                    ),
                    timeout=REQUEST_TIMEOUT * 3  # 正文生成需要更长时间
                )
            )
            
            # 更新状态
            generation_status["in_progress"] = False
            generation_status["progress"] = 1.0
            generation_status["current_section"] = "完成"
            generation_status["content"] = sanitize_html(content)
            
            return jsonify({"success": True, "body": content})
        except asyncio.TimeoutError:
            logger.error(f"生成论文正文超时")
            
            # 更新状态
            generation_status["in_progress"] = False
            generation_status["current_section"] = "生成超时，请减少字数或分段生成"
            
            return jsonify({"success": False, "message": "生成超时，请减少字数或分段生成"})
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"生成论文正文出错: {str(e)}")
        traceback.print_exc()
        
        # 更新状态
        generation_status["in_progress"] = False
        generation_status["current_section"] = f"生成失败: {str(e)}"
        
        return jsonify({"success": False, "message": f"生成失败: {str(e)}"})

@paper_module_bp.route('/generate_references', methods=['POST'])
@validate_json_input({
    "title": {"type": "string", "required": True, "min_length": 1, "max_length": 200},
    "subject": {"type": "string", "required": False},
    "education_level": {"type": "string", "required": False},
    "custom_prompt": {"type": "string", "required": False}
})
def generate_references():
    """生成参考文献"""
    try:
        data = request.json
        title = bleach.clean(data.get('title', ''))
        subject = bleach.clean(data.get('subject', '通用'))
        education_level = bleach.clean(data.get('education_level', '本科'))
        custom_prompt = bleach.clean(data.get('custom_prompt', ''))
        
        # 验证学科和教育水平
        if subject not in SUBJECT_AREAS:
            subject = "通用"
        
        if education_level not in EDUCATION_LEVELS:
            education_level = "本科"
        
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 执行异步生成，设置超时
            references = loop.run_until_complete(
                asyncio.wait_for(
                    paper_generator.generate_references(
                        title=title,
                        subject=subject,
                        education_level=education_level,
                        custom_prompt=custom_prompt
                    ),
                    timeout=REQUEST_TIMEOUT
                )
            )
            return jsonify({"success": True, "references": references})
        except asyncio.TimeoutError:
            logger.error(f"生成参考文献超时")
            return jsonify({"success": False, "message": "生成超时，请稍后重试"})
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"生成参考文献出错: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"生成失败: {str(e)}"})

@paper_module_bp.route('/generate_acknowledgement', methods=['POST'])
@validate_json_input({
    "title": {"type": "string", "required": True, "min_length": 1, "max_length": 200},
    "subject": {"type": "string", "required": False},
    "education_level": {"type": "string", "required": False},
    "custom_prompt": {"type": "string", "required": False}
})
def generate_acknowledgement():
    """生成致谢"""
    try:
        data = request.json
        title = bleach.clean(data.get('title', ''))
        subject = bleach.clean(data.get('subject', '通用'))
        education_level = bleach.clean(data.get('education_level', '本科'))
        custom_prompt = bleach.clean(data.get('custom_prompt', ''))
        
        # 验证学科和教育水平
        if subject not in SUBJECT_AREAS:
            subject = "通用"
        
        if education_level not in EDUCATION_LEVELS:
            education_level = "本科"
        
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 执行异步生成，设置超时
            acknowledgement = loop.run_until_complete(
                asyncio.wait_for(
                    paper_generator.generate_acknowledgement(
                        title=title,
                        subject=subject,
                        education_level=education_level,
                        custom_prompt=custom_prompt
                    ),
                    timeout=REQUEST_TIMEOUT
                )
            )
            return jsonify({"success": True, "acknowledgement": acknowledgement})
        except asyncio.TimeoutError:
            logger.error(f"生成致谢超时")
            return jsonify({"success": False, "message": "生成超时，请稍后重试"})
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"生成致谢出错: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"生成失败: {str(e)}"})

@paper_module_bp.route('/parse_outline', methods=['POST'])
@validate_json_input({
    "outline_text": {"type": "string", "required": True, "min_length": 1}
})
def parse_outline():
    """解析大纲结构"""
    try:
        data = request.json
        outline_text = bleach.clean(data.get('outline_text', ''))
        
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 解析大纲结构
            outline_structure = loop.run_until_complete(
                paper_generator._parse_outline_text(outline_text)
            )
            
            # 找出最小级别标题单元
            min_level_sections = loop.run_until_complete(
                paper_generator._extract_min_level_sections(outline_structure)
            )
            
            return jsonify({
                'success': True,
                'outline_structure': outline_structure,
                'min_level_sections': min_level_sections,
                'section_count': len(min_level_sections)
            })
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"解析大纲失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500 

@paper_module_bp.route('/status', methods=['GET'])
def get_status():
    """获取生成状态"""
    return jsonify(generation_status)

@paper_module_bp.route('/stop', methods=['POST'])
def stop_generation():
    """停止生成过程"""
    paper_generator.stop_generation()
    
    global generation_status
    generation_status["in_progress"] = False
    generation_status["current_section"] = "已停止"
    
    return jsonify({"success": True, "message": "已停止生成"}) 
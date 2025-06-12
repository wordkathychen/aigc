"""
API模块
提供给客户端程序的接口
"""

from flask import Blueprint, request, jsonify, current_app, g
from werkzeug.security import check_password_hash
from functools import wraps
import datetime
import jwt
import json
import os
import socket
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect, generate_csrf
import functools
import uuid
import time
import bleach
import re

from . import db
from .models import Member, APIKey, PromptTemplate, SchoolTemplate, UsageRecord, MemberQuota, SensitiveWord, User, ModelConfig, Quota, Transaction
from src.utils.exceptions import ValidationError, AuthenticationError, format_exception
from src.utils.logger import setup_logger

api_bp = Blueprint('api', __name__, url_prefix='/api')
csrf = CSRFProtect()

# 初始化CSRF保护
def init_csrf(app):
    csrf.init_app(app)
    # 为API请求排除CSRF保护，但API使用JWT认证
    csrf.exempt(api_bp)

# 安全头部中间件
@api_bp.after_request
def add_security_headers(response):
    """添加安全相关的HTTP响应头"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

# 输入验证装饰器
def validate_json_input(schema):
    """验证JSON输入是否符合指定模式"""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                # 获取请求的JSON数据
                json_data = request.get_json(force=True, silent=True)
                if not json_data:
                    raise ValidationError("无效的JSON数据")
                    
                # 验证JSON数据
                errors = schema.validate(json_data)
                if errors:
                    raise ValidationError("数据验证失败", details=errors)
                
                # 将验证后的数据添加到请求中
                g.validated_data = json_data
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify(format_exception(e)), 400
        return wrapper
    return decorator

# 速率限制中间件
def rate_limit(limit_per_minute=60):
    """API请求速率限制"""
    def decorator(f):
        # 使用简单的内存缓存记录请求
        cache = {}
        
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # 获取客户端IP
            client_ip = request.remote_addr
            current_time = time.time()
            
            # 清理过期记录
            for ip in list(cache.keys()):
                if current_time - cache[ip]['timestamp'] > 60:
                    del cache[ip]
            
            # 检查限制
            if client_ip in cache:
                cache_data = cache[client_ip]
                if current_time - cache_data['timestamp'] < 60 and cache_data['count'] >= limit_per_minute:
                    return jsonify({
                        'code': 429,
                        'message': '请求频率过高，请稍后再试'
                    }), 429
                
                if current_time - cache_data['timestamp'] < 60:
                    cache_data['count'] += 1
                else:
                    cache_data['timestamp'] = current_time
                    cache_data['count'] = 1
            else:
                cache[client_ip] = {
                    'timestamp': current_time,
                    'count': 1
                }
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

# 请求日志中间件
@api_bp.before_request
def log_request():
    """记录API请求日志"""
    g.start_time = time.time()
    
    # 生成请求ID
    request_id = str(uuid.uuid4())
    g.request_id = request_id
    
    # 记录请求信息
    logger.info(f"API请求开始 [{request_id}] {request.method} {request.path} 来自 {request.remote_addr}")

@api_bp.after_request
def log_response(response):
    """记录API响应日志"""
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        request_id = getattr(g, 'request_id', 'unknown')
        logger.info(f"API请求完成 [{request_id}] {request.method} {request.path} - 状态码: {response.status_code} - 耗时: {duration:.3f}s")
    return response

# 安全性工具函数
def sanitize_input(text):
    """清理用户输入，防止XSS攻击"""
    if text is None:
        return None
    # 使用bleach库清理HTML标签
    return bleach.clean(text, strip=True)

def validate_filename(filename):
    """验证文件名是否安全"""
    secure_name = secure_filename(filename)
    # 仅允许特定文件扩展名
    allowed_extensions = ['pdf', 'docx', 'txt', 'jpg', 'png']
    if '.' in secure_name and secure_name.rsplit('.', 1)[1].lower() in allowed_extensions:
        return secure_name
    return None

# 检查Docker环境
def check_docker():
    """检查是否在Docker环境中运行"""
    # Docker环境检测方法1: /.dockerenv文件存在
    if os.path.exists('/.dockerenv'):
        return True
    
    # Docker环境检测方法2: cgroup文件包含docker字样
    try:
        with open('/proc/self/cgroup', 'r') as f:
            return any('docker' in line for line in f)
    except:
        pass
    
    # Docker环境检测方法3: 主机名通常是一个短哈希
    try:
        hostname = socket.gethostname()
        if len(hostname) == 12 and all(c in '0123456789abcdef' for c in hostname):
            return True
    except:
        pass
    
    return False

# 验证客户端JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从请求头获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token不存在', 'code': 401}), 401
        
        try:
            # 验证token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Member.query.filter_by(id=data['user_id']).first()
            
            if not current_user:
                return jsonify({'error': '用户不存在', 'code': 401}), 401
                
            if not current_user.is_active:
                return jsonify({'error': '账号已禁用', 'code': 403}), 403
        
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token已过期', 'code': 401}), 401
        except Exception as e:
            return jsonify({'error': f'Token无效: {str(e)}', 'code': 401}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@api_bp.route('/auth/login', methods=['POST'])
@rate_limit(limit_per_minute=5)
def auth_login():
    """会员登录API
    
    客户端用户认证接口
    
    Returns:
        JSON: 登录结果，包含令牌和用户信息
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({
            'success': False,
            'message': '请提供用户名和密码'
        }), 400
    
    # 查找用户
    member = Member.query.filter_by(username=data.get('username')).first()
    
    if not member:
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 401
    
    # 验证密码
    if member.verify_password(data.get('password')):
        if not member.is_active:
            return jsonify({
                'success': False,
                'message': '账号已禁用'
            }), 403
        
        # 生成JWT令牌
        token = jwt.encode({
            'user_id': member.id,
            'username': member.username,
            'exp': datetime.datetime.now() + datetime.timedelta(days=7)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        # 更新最后登录时间
        member.last_login = datetime.datetime.now()
        db.session.commit()
        
        # 获取用户额度
        quota = member.quota
        quota_info = None
        if quota:
            quota_info = {
                'total_credits': quota.total_credits,
                'remaining_credits': quota.remaining_credits,
                'total_tokens': quota.total_tokens,
                'remaining_tokens': quota.remaining_tokens,
                'expires_at': quota.expires_at.strftime('%Y-%m-%d %H:%M:%S') if quota.expires_at else None
            }
        
        # 返回令牌和用户信息
        return jsonify({
            'success': True,
            'message': '登录成功',
            'token': token,
            'user_info': {
                'id': member.id,
                'username': member.username,
                'email': member.email,
                'is_active': member.is_active,
                'last_login': member.last_login.strftime('%Y-%m-%d %H:%M:%S') if member.last_login else None,
                'quota': quota_info
            }
        })
    
    return jsonify({
        'success': False,
        'message': '密码错误'
    }), 401

@api_bp.route('/check_environment', methods=['GET'])
@rate_limit(limit_per_minute=10)
def check_environment():
    """检查环境状态的API端点
    
    用于客户端测试连接是否正常
    
    Returns:
        JSON: 环境状态信息
    """
    try:
        is_docker = check_docker()
        
        # 检查数据库连接
        db_connected = False
        try:
            db.session.execute('SELECT 1')
            db_connected = True
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            
        # 检查网络连接
        network_connected = False
        try:
            socket.create_connection(("www.baidu.com", 80), timeout=3)
            network_connected = True
        except:
            try:
                socket.create_connection(("www.google.com", 80), timeout=3)
                network_connected = True
            except Exception as e:
                logger.error(f"网络连接检查失败: {str(e)}")
        
        return jsonify({
            'code': 200,
            'message': '环境检查成功',
            'is_docker': is_docker,
            'db_connected': db_connected,
            'network_connected': network_connected,
            'server_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': current_app.config.get('APP_VERSION', '1.0.0')
        })
    except Exception as e:
        logger.error(f"环境检查失败: {str(e)}")
        return jsonify(format_exception(e)), 500

@api_bp.route('/user_info', methods=['GET'])
@token_required
def get_user_info(current_user):
    """获取用户信息"""
    # 获取用户额度
    quota = current_user.quota
    
    if not quota:
        return jsonify({
            'error': '用户额度不存在',
            'code': 404
        }), 404
    
    return jsonify({
        'code': 200,
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'phone': current_user.phone,
            'created_at': current_user.created_at.strftime('%Y-%m-%d %H:%M:%S') if current_user.created_at else None,
            'last_login': current_user.last_login.strftime('%Y-%m-%d %H:%M:%S') if current_user.last_login else None,
            'quota': {
                'total_credits': quota.total_credits,
                'remaining_credits': quota.remaining_credits,
                'total_tokens': quota.total_tokens,
                'remaining_tokens': quota.remaining_tokens,
                'expires_at': quota.expires_at.strftime('%Y-%m-%d %H:%M:%S') if quota.expires_at else None
            }
        }
    })

@api_bp.route('/prompt_templates', methods=['GET'])
@token_required
def get_prompt_templates(current_user):
    """获取提示词模板列表"""
    template_type = request.args.get('type')
    
    if template_type:
        templates = PromptTemplate.query.filter_by(template_type=template_type, is_active=True).all()
    else:
        templates = PromptTemplate.query.filter_by(is_active=True).all()
    
    template_list = []
    for template in templates:
        template_list.append({
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'template_type': template.template_type,
            'content': template.content,
            'variables': json.loads(template.variables) if template.variables else {}
        })
    
    return jsonify({
        'code': 200,
        'templates': template_list
    })

@api_bp.route('/prompt_template/<int:id>', methods=['GET'])
@token_required
def get_prompt_template(current_user, id):
    """获取单个提示词模板"""
    template = PromptTemplate.query.filter_by(id=id, is_active=True).first()
    
    if not template:
        return jsonify({
            'code': 404,
            'error': '模板不存在或已禁用'
        }), 404
    
    return jsonify({
        'code': 200,
        'template': {
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'template_type': template.template_type,
            'content': template.content,
            'variables': json.loads(template.variables) if template.variables else {}
        }
    })

@api_bp.route('/prompt_template/by_name/<string:name>', methods=['GET'])
@token_required
def get_prompt_template_by_name(current_user, name):
    """根据名称获取提示词模板"""
    template = PromptTemplate.query.filter_by(name=name, is_active=True).first()
    
    if not template:
        return jsonify({
            'code': 404,
            'error': '模板不存在或已禁用'
        }), 404
    
    return jsonify({
        'code': 200,
        'template': {
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'template_type': template.template_type,
            'content': template.content,
            'variables': json.loads(template.variables) if template.variables else {}
        }
    })

@api_bp.route('/school_templates', methods=['GET'])
@token_required
def get_school_templates(current_user):
    """获取学校模板列表"""
    # 获取所有已启用的学校模板
    templates = SchoolTemplate.query.filter_by(is_active=True).all()
    
    result = []
    for template in templates:
        result.append({
            'id': template.id,
            'school_name': template.school_name,
            'template_name': template.template_name,
            'created_at': template.created_at.strftime('%Y-%m-%d %H:%M:%S') if template.created_at else None
        })
    
    return jsonify({
        'code': 200,
        'templates': result
    })

@api_bp.route('/api_keys', methods=['GET'])
@token_required
def get_api_keys(current_user):
    """获取API密钥"""
    # 获取所有已启用的API密钥
    api_keys = APIKey.query.filter_by(is_active=True).all()
    
    # 按类型分组
    keys_by_type = {}
    for key in api_keys:
        if key.api_type not in keys_by_type:
            keys_by_type[key.api_type] = []
        
        keys_by_type[key.api_type].append({
            'id': key.id,
            'key_name': key.key_name,
            'api_key': key.api_key,
            'api_endpoint': key.api_endpoint,
            'model_name': key.model_name
        })
    
    return jsonify({
        'code': 200,
        'api_keys': keys_by_type
    })

@api_bp.route('/sensitive_words', methods=['GET'])
@token_required
def get_sensitive_words(current_user):
    """获取敏感词列表"""
    # 获取所有已启用的敏感词
    words = SensitiveWord.query.filter_by(is_active=True).all()
    word_list = [word.word for word in words]
    
    return jsonify({
        'code': 200,
        'sensitive_words': word_list
    })

@api_bp.route('/consume_credits', methods=['POST'])
@token_required
def consume_credits(current_user):
    """消费额度"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '无效的请求数据', 'code': 400}), 400
    
    credits = data.get('credits', 1)
    tokens = data.get('tokens', 0)
    record_type = data.get('record_type', 'generation')
    request_data = data.get('request_data', {})
    
    # 获取用户额度
    quota = current_user.quota
    
    if not quota:
        return jsonify({'error': '用户额度不存在', 'code': 404}), 404
    
    # 检查额度是否足够
    if not quota.has_sufficient_credits(credits):
        return jsonify({'error': '额度不足', 'code': 403}), 403
    
    if tokens > 0 and not quota.has_sufficient_tokens(tokens):
        return jsonify({'error': '字数额度不足', 'code': 403}), 403
    
    # 消费额度
    quota.remaining_credits -= credits
    
    if tokens > 0:
        quota.remaining_tokens -= tokens
    
    # 记录使用情况
    record = UsageRecord(
        member_id=current_user.id,
        record_type=record_type,
        credits_used=credits,
        tokens_used=tokens,
        request_data=json.dumps(request_data) if request_data else None,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '额度消费成功',
        'remaining_credits': quota.remaining_credits,
        'remaining_tokens': quota.remaining_tokens
    })

@api_bp.route('/auth/verify_token', methods=['GET'])
@token_required
def verify_token(current_user):
    """验证令牌有效性
    
    用于客户端验证令牌是否有效
    
    Returns:
        JSON: 验证结果
    """
    return jsonify({
        "success": True,
        "message": "令牌有效",
        "user_info": {
            "id": current_user.id,
            "username": current_user.username,
            "is_active": current_user.is_active
        }
    })

@api_bp.route('/model_configs', methods=['GET'])
@token_required
def get_model_configs(current_user):
    """获取模型配置列表"""
    try:
        task_type = request.args.get('task_type')
        education_level = request.args.get('education_level')
        
        # 构建查询
        query = ModelConfig.query.filter_by(is_active=True)
        
        if task_type:
            query = query.filter_by(task_type=task_type)
            
        if education_level:
            query = query.filter_by(education_level=education_level)
            
        configs = query.all()
        
        # 格式化结果
        result = []
        for config in configs:
            result.append({
                'id': config.id,
                'task_type': config.task_type,
                'education_level': config.education_level,
                'api_type': config.api_type,
                'model_name': config.model_name,
                'temperature': config.temperature,
                'max_tokens': config.max_tokens,
                'top_p': config.top_p,
                'frequency_penalty': config.frequency_penalty,
                'presence_penalty': config.presence_penalty
            })
            
        return jsonify({
            'code': 200,
            'message': '获取模型配置成功',
            'configs': result
        })
    except Exception as e:
        return jsonify(format_exception(e)), 500 
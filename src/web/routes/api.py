"""
API模块
提供给客户端程序的接口
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
from functools import wraps
import datetime
import jwt
import json
import os
import socket

from . import db
from .models import Member, APIKey, PromptTemplate, SchoolTemplate, UsageRecord, MemberQuota, SensitiveWord

api_bp = Blueprint('api', __name__, url_prefix='/api')

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

@api_bp.route('/check_environment', methods=['GET'])
def check_environment():
    """检查环境状态的API端点
    
    用于客户端测试连接是否正常
    
    Returns:
        JSON: 环境状态信息
    """
    try:
        return jsonify({
            "success": True,
            "message": "环境正常",
            "version": "1.0.0",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        current_app.logger.error(f"检查环境失败: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"检查环境失败: {str(e)}"
        }), 500

@api_bp.route('/auth/login', methods=['POST'])
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
                'remaining_tokens': quota.remaining_tokens
            }
        }
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

@api_bp.route('/prompt_template/by_name/<name>', methods=['GET'])
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
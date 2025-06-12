"""
Flask应用程序入口
用于启动Web后台管理系统
"""

from flask import Flask, render_template, redirect, url_for, flash, jsonify, request, session
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix
from src.utils.logger import setup_logger
from src.utils.exceptions import BaseError, format_exception
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta
import socket

from . import db
from .models import User, APIKey, ModelConfig
from .api import api_bp, init_csrf
from .views import main_bp
from .admin import admin_bp
from .annotation import annotation_bp
from .routes.paper_module import paper_module_bp
from .routes.auth import auth_bp
from .routes.prompt_templates import prompt_templates_bp
from src.config.settings import SECRET_KEY, SQLALCHEMY_DATABASE_URI, SESSION_LIFETIME

logger = setup_logger(__name__)

# 创建CSRF保护
csrf = CSRFProtect()

def create_app(config=None):
    """创建Flask应用实例"""
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates',
                instance_relative_config=True)
    
    # 加载默认配置
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=SESSION_LIFETIME),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE='Lax',
        WTF_CSRF_ENABLED=True,
        WTF_CSRF_TIME_LIMIT=3600,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 限制上传文件大小为16MB
        APP_VERSION='2.0.0',
        UPLOAD_FOLDER=os.path.join(os.path.dirname(__file__), 'uploads'),
        ALLOWED_EXTENSIONS={'pdf', 'docx', 'txt', 'jpg', 'png'},
        LOG_LEVEL=os.environ.get('LOG_LEVEL', 'INFO'),
        DEBUG=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true',
        TEMPLATES_AUTO_RELOAD=True,
        SERVER_NAME=os.environ.get('SERVER_NAME'),
        PREFERRED_URL_SCHEME=os.environ.get('PREFERRED_URL_SCHEME', 'http')
    )
    
    # 加载环境变量配置
    if 'FLASK_CONFIG' in os.environ:
        app.config.from_envvar('FLASK_CONFIG')
    
    # 加载传入的配置
    if config:
        app.config.from_mapping(config)
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 初始化数据库
    db.init_app(app)
    Migrate(app, db)
    
    # 初始化JWT
    jwt = JWTManager(app)
    
    # 初始化CSRF保护
    init_csrf(app)
    
    # 配置安全头信息
    csp = {
        'default-src': '\'self\'',
        'script-src': ['\'self\'', '\'unsafe-inline\'', 'https://cdn.jsdelivr.net'],
        'style-src': ['\'self\'', '\'unsafe-inline\'', 'https://cdn.jsdelivr.net', 'https://fonts.googleapis.com'],
        'font-src': ['\'self\'', 'https://cdn.jsdelivr.net', 'https://fonts.gstatic.com'],
        'img-src': ['\'self\'', 'data:', 'https:'],
        'connect-src': ['\'self\'', 'https:']
    }
    
    # 在生产环境中启用Talisman
    if not app.debug and not app.testing:
        Talisman(app,
                content_security_policy=csp,
                content_security_policy_nonce_in=['script-src'],
                feature_policy={
                    'geolocation': '\'none\'',
                    'microphone': '\'none\'',
                    'camera': '\'none\''
                },
                force_https=True,
                force_https_permanent=True,
                session_cookie_secure=True,
                session_cookie_http_only=True,
                strict_transport_security=True,
                strict_transport_security_preload=True,
                strict_transport_security_max_age=31536000,
                referrer_policy='same-origin'
                )
    
    # 配置代理修复
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
    
    # 初始化登录管理器
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录以访问此页面'
    login_manager.login_message_category = 'warning'
    login_manager.session_protection = 'strong'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 注册蓝图
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(annotation_bp, url_prefix='/annotation')
    app.register_blueprint(paper_module_bp, url_prefix='/paper_module')
    app.register_blueprint(auth_bp)
    app.register_blueprint(prompt_templates_bp)
    
    # 配置日志
    setup_logging(app)
    
    # 全局错误处理
    register_error_handlers(app)
    
    # 环境检测
    with app.app_context():
        check_environment(app)
    
    return app

def setup_logging(app):
    """配置应用日志"""
    log_level = getattr(logging, app.config['LOG_LEVEL'])
    
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 文件处理器 - 按大小轮转
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'web.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(name)s] [%(process)d:%(thread)d] - %(message)s'
    ))
    
    # 为应用添加处理器
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
    
    # 设置Werkzeug日志
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.addHandler(file_handler)
    
    # 开发环境下启用控制台日志
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(name)s] - %(message)s'
        ))
        app.logger.addHandler(console_handler)
        werkzeug_logger.addHandler(console_handler)
    
    # 禁用默认处理器
    app.logger.propagate = False
    werkzeug_logger.propagate = False

def register_error_handlers(app):
    """注册全局错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(format_exception(e)), 400
    
    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify(format_exception(e)), 401
    
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify(format_exception(e)), 403
    
    @app.errorhandler(404)
    def page_not_found(e):
        if request.path.startswith('/api/'):
            return jsonify(format_exception(e)), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"服务器错误: {str(e)}")
        if request.path.startswith('/api/'):
            return jsonify(format_exception(e)), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(BaseError)
    def handle_base_error(e):
        if request.path.startswith('/api/'):
            return jsonify(e.to_dict()), e.code
        flash(e.message, 'error')
        return redirect(url_for('main.index'))

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template('errors/413.html'), 413

    # 请求前钩子 - 记录请求信息
    @app.before_request
    def log_request_info():
        if not app.debug:
            logger.debug(f"请求: {request.method} {request.path} - IP: {request.remote_addr}")
    
    # 请求后钩子 - 添加安全头
    @app.after_request
    def add_security_headers(response):
        # 添加安全头信息
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # 添加缓存控制
        if request.path.startswith('/static'):
            # 静态资源可以缓存一周
            response.headers['Cache-Control'] = 'public, max-age=604800'
        else:
            # 其他页面不缓存
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
    
    # 上下文处理器 - 添加全局变量
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'AI Text Generator',
            'app_version': '1.0.0',
            'current_year': '2023'
        }
    
    # 检查网络连接
    @app.route('/check_network')
    def check_network():
        try:
            # 尝试连接百度，超时设置为2秒
            socket.create_connection(("www.baidu.com", 80), timeout=2)
            return "网络连接正常"
        except OSError:
            return "网络连接失败"

def check_environment(app):
    """检查运行环境"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        app.logger.info("数据库连接正常")
        
        # 检查是否在Docker中运行
        in_docker = False
        if os.path.exists('/.dockerenv'):
            in_docker = True
        elif os.path.isfile('/proc/self/cgroup'):
            with open('/proc/self/cgroup', 'rt') as f:
                in_docker = 'docker' in f.read()
        
        app.logger.info(f"Docker环境: {in_docker}")
        
        # 检查网络连接
        try:
            socket.create_connection(("www.baidu.com", 80), timeout=2)
            app.logger.info("网络连接正常")
        except:
            app.logger.warning("网络连接不可用，部分功能可能受限")
            
        # 检查上传目录
        if not os.access(app.config['UPLOAD_FOLDER'], os.W_OK):
            app.logger.warning(f"上传目录 {app.config['UPLOAD_FOLDER']} 不可写，文件上传功能可能不可用")
            
        # 检查JWT密钥
        if app.config['JWT_SECRET_KEY'] == 'jwt-secret-key-change-in-production' and not app.debug:
            app.logger.warning("生产环境使用了默认JWT密钥，建议通过环境变量设置JWT_SECRET_KEY")
            
    except Exception as e:
        app.logger.error(f"环境检查失败: {str(e)}")

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000) 
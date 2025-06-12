"""
Web后台管理系统
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 创建扩展实例
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=None):
    """创建Flask应用实例"""
    # 创建Flask应用
    app = Flask(__name__, template_folder='templates')
    
    # 加载配置
    if config_class:
        app.config.from_object(config_class)
    else:
        from .config import Config
        app.config.from_object(Config)
    
    # 确保上传目录存在
    import os
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder:
        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(os.path.join(upload_folder, 'annotations'), exist_ok=True)
        os.makedirs(os.path.join(upload_folder, 'outputs'), exist_ok=True)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    
    # 注册蓝图
    from .auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from .admin import admin_bp
    app.register_blueprint(admin_bp)
    
    # 注册API蓝图
    from .api import api_bp
    app.register_blueprint(api_bp)
    
    # 注册批注处理蓝图
    from .routes.annotation import annotation_bp
    app.register_blueprint(annotation_bp)
    
    # 注册提示词模板蓝图
    from .routes.prompt_templates import prompt_bp
    app.register_blueprint(prompt_bp)
    
    # 注册错误处理
    from .errors import register_error_handlers
    register_error_handlers(app)
    
    # 创建数据库
    with app.app_context():
        db.create_all()
        from .auth import create_default_admin
        create_default_admin()
        
        # 初始化默认提示词模板
        from .models.prompt_template import init_default_templates
        init_default_templates()
    
    return app 
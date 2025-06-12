"""
Web后台配置文件
"""

import os
import sys
import secrets
from datetime import timedelta

# 获取基础路径
def get_base_path():
    """获取应用基础路径"""
    # 如果在打包环境中
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # 如果在开发环境中
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Config:
    """基本配置类"""
    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(get_base_path(), "data", "backend.db")}'
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    
    # 模板配置
    TEMPLATES_FOLDER = os.path.join(get_base_path(), "templates")
    
    # 上传配置
    UPLOAD_FOLDER = os.path.join(get_base_path(), "data", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Docker检测配置
    DOCKER_CHECK_ENABLED = True
    
    # 默认管理员账号
    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "admin123"  # 实际部署时应更改为强密码

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    DOCKER_CHECK_ENABLED = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 安全设置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # 日志配置
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    DOCKER_CHECK_ENABLED = False

# 根据环境变量选择配置
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# 获取当前配置
def get_config():
    """获取当前环境配置"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_map.get(env, config_map['default']) 
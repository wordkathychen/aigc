"""
客户端配置文件
用于配置客户端连接到远程服务器
"""

import os
import json

# Web API服务器地址
# 默认为远程服务器地址，可通过环境变量或配置文件覆盖
WEB_API_URL = os.environ.get("AI_TEXT_API_URL", "http://your-server-address:5000/api")

# 是否启用Web后台功能
WEB_ENABLED = True

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".ai_text_generator", "config.json")

# 加载用户配置
def load_user_config():
    """加载用户配置"""
    global WEB_API_URL, WEB_ENABLED
    
    # 确保配置目录存在
    config_dir = os.path.dirname(CONFIG_FILE)
    os.makedirs(config_dir, exist_ok=True)
    
    # 如果配置文件存在，则加载配置
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                
                if "web_api_url" in config:
                    WEB_API_URL = config["web_api_url"]
                
                if "web_enabled" in config:
                    WEB_ENABLED = config["web_enabled"]
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")

# 保存用户配置
def save_user_config(web_api_url=None, web_enabled=None):
    """保存用户配置"""
    global WEB_API_URL, WEB_ENABLED
    
    # 更新配置
    if web_api_url is not None:
        WEB_API_URL = web_api_url
    
    if web_enabled is not None:
        WEB_ENABLED = web_enabled
    
    # 确保配置目录存在
    config_dir = os.path.dirname(CONFIG_FILE)
    os.makedirs(config_dir, exist_ok=True)
    
    # 保存配置
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "web_api_url": WEB_API_URL,
                "web_enabled": WEB_ENABLED
            }, f, indent=4)
        return True
    except Exception as e:
        print(f"保存配置文件失败: {str(e)}")
        return False

# 初始化时加载配置
load_user_config() 
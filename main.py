"""
AI文本生成器客户端入口
"""

import sys
import os
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def setup_environment():
    """设置环境变量和路径"""
    # 获取应用根目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        app_dir = Path(sys.executable).parent
    else:
        # 如果是开发环境
        app_dir = Path(__file__).parent
    
    # 创建必要的目录
    data_dir = app_dir / 'data'
    cache_dir = data_dir / 'cache'
    logs_dir = app_dir / 'logs'
    
    for directory in [data_dir, cache_dir, logs_dir]:
        directory.mkdir(exist_ok=True)
    
    # 设置工作目录
    os.chdir(app_dir)
    
    # 返回应用根目录
    return app_dir

def check_web_backend():
    """检查Web后台是否可用"""
    try:
        from src.models.client_init import ClientInitializer
        client_init = ClientInitializer()
        return client_init.check_connection()
    except Exception as e:
        logger.error(f"检查Web后台连接失败: {str(e)}")
        return False

def start_gui():
    """启动图形界面"""
    try:
        # 这里导入GUI模块并启动
        from src.gui.main_window import start_application
        start_application()
    except ImportError:
        logger.error("GUI模块不可用")
        print("错误: GUI模块不可用，请确保安装了所有依赖")
        sys.exit(1)
    except Exception as e:
        logger.error(f"启动GUI失败: {str(e)}")
        print(f"错误: 启动界面失败 - {str(e)}")
        sys.exit(1)

def main():
    """程序入口点"""
    try:
        # 设置环境
        app_dir = setup_environment()
        logger.info(f"应用目录: {app_dir}")
        
        # 检查Web后台连接
        web_available = check_web_backend()
        if web_available:
            logger.info("Web后台连接成功")
        else:
            logger.warning("Web后台连接失败，将使用本地模式")
        
        # 启动图形界面
        start_gui()
        
    except Exception as e:
        logger.critical(f"程序启动失败: {str(e)}", exc_info=True)
        print(f"严重错误: 程序无法启动 - {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
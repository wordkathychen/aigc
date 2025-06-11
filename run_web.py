"""
Web后台启动脚本
"""

import os
import sys
from src.web.app import app

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('FLASK_HOST', '0.0.0.0')
os.environ.setdefault('FLASK_PORT', '5000')

if __name__ == '__main__':
    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == 'prod' or sys.argv[1] == 'production':
            os.environ['FLASK_ENV'] = 'production'
            print("Running in production mode")
        elif sys.argv[1] == 'dev' or sys.argv[1] == 'development':
            os.environ['FLASK_ENV'] = 'development'
            print("Running in development mode")
    
    # 获取主机和端口
    host = os.environ.get('FLASK_HOST')
    port = int(os.environ.get('FLASK_PORT'))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # 启动服务
    print(f"Starting AI Text Generator Web Backend on {host}:{port}")
    app.run(host=host, port=port, debug=debug) 
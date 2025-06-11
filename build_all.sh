#!/bin/bash

echo "==================================================="
echo "AI文本生成器 - 一键打包脚本"
echo "==================================================="
echo "此脚本将执行两个任务:"
echo "1. 构建Web后台Docker镜像（可部署到服务器）"
echo "2. 将客户端程序打包为可执行文件"
echo "==================================================="
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "[错误] 未找到Docker，请先安装Docker"
    exit 1
fi

# 检查PyInstaller是否安装
if ! pip show pyinstaller &> /dev/null; then
    echo "[信息] 正在安装PyInstaller..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "[错误] 安装PyInstaller失败"
        exit 1
    fi
fi

echo "[步骤1] 构建Web后台Docker镜像..."
docker-compose build
if [ $? -ne 0 ]; then
    echo "[错误] Docker镜像构建失败"
    exit 1
fi

echo "[信息] Docker镜像构建成功，您可以将镜像推送到服务器或注册表"
echo "       使用以下命令推送镜像:"
echo "       docker tag ai-text-generator-web:latest your-registry/ai-text-generator-web:latest"
echo "       docker push your-registry/ai-text-generator-web:latest"

# 获取服务器地址
read -p "请输入服务器地址(例如 http://your-server-ip:5000/api): " SERVER_URL
if [ -z "$SERVER_URL" ]; then
    SERVER_URL="http://localhost:5000/api"
fi

echo "[步骤3] 创建客户端打包目录..."
mkdir -p build dist

echo "[步骤4] 准备客户端文件..."
# 创建临时目录
mkdir -p temp_client

# 复制所需文件到临时目录，排除web相关文件
rsync -av --exclude-from='exclude_web.txt' src/ temp_client/src/

echo "[步骤5] 生成客户端配置文件..."
cat > temp_client/src/config/client_config.py << EOL
"""
客户端配置文件
用于配置客户端连接到远程服务器
"""

import os
import json

# Web API服务器地址
# 默认为远程服务器地址，可通过环境变量或配置文件覆盖
WEB_API_URL = os.environ.get("AI_TEXT_API_URL", "${SERVER_URL}")

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
EOL

echo "[步骤6] 使用PyInstaller打包客户端..."
pyinstaller --noconfirm --onefile --windowed \
    --add-data "temp_client/src:src" \
    --icon=resources/icon.ico \
    --name "AI文本生成器" \
    --hidden-import=src \
    --hidden-import=src.models \
    --hidden-import=src.utils \
    --hidden-import=src.config \
    main.py

echo "[步骤7] 清理临时文件..."
rm -rf temp_client

echo ""
echo "==================================================="
echo "打包完成!"
echo ""
echo "Web后台Docker镜像已构建完成，可以部署到服务器:"
echo "  1. 将镜像推送到Docker注册表"
echo "  2. 在服务器上拉取镜像并运行"
echo "  3. 确保服务器防火墙开放5000端口"
echo ""
echo "客户端可执行文件位于: dist/AI文本生成器"
echo "客户端默认连接到: ${SERVER_URL}"
echo "用户可以在设置中修改服务器地址"
echo "===================================================" 
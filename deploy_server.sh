#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # 无颜色

# 打印带颜色的文本
print_color() {
    echo -e "${1}${2}${NC}"
}

print_color "$CYAN" "====================================================="
print_color "$CYAN" "       AI Text Generator 服务器部署脚本              "
print_color "$CYAN" "====================================================="
echo ""

# 检查是否以root用户运行
if [ "$EUID" -eq 0 ]; then
    print_color "$YELLOW" "[提示] 您正在以root用户运行此脚本。建议使用非root用户运行。"
    read -p "是否继续? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_color "$RED" "部署已取消。"
        exit 1
    fi
fi

# 检查Docker是否安装
print_color "$YELLOW" "[1/12] 检查Docker环境..."
if ! command -v docker &> /dev/null; then
    print_color "$RED" "错误: Docker未安装。请先安装Docker。"
    print_color "$YELLOW" "您可以使用以下命令安装Docker:"
    echo "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_color "$RED" "错误: Docker Compose未安装。请先安装Docker Compose。"
    print_color "$YELLOW" "您可以使用以下命令安装Docker Compose:"
    echo "pip install docker-compose"
    exit 1
fi

print_color "$GREEN" "Docker环境检查通过。"
docker --version
docker-compose --version

# 检查必要的端口是否被占用
print_color "$YELLOW" "[2/12] 检查端口占用情况..."
WEB_PORT=5000
API_PORT=8000

check_port() {
    if command -v netstat &> /dev/null; then
        netstat -tuln | grep ":$1 " &> /dev/null
    elif command -v ss &> /dev/null; then
        ss -tuln | grep ":$1 " &> /dev/null
    else
        # 如果netstat和ss都不可用，尝试使用lsof
        if command -v lsof &> /dev/null; then
            lsof -i:$1 &> /dev/null
        else
            # 如果以上命令都不可用，假设端口未被占用
            return 1
        fi
    fi
    return $?
}

if check_port $WEB_PORT; then
    print_color "$RED" "警告: 端口 $WEB_PORT 已被占用。Web服务可能无法启动。"
    read -p "是否继续? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_color "$RED" "部署已取消。"
        exit 1
    fi
else
    print_color "$GREEN" "端口 $WEB_PORT 未被占用。"
fi

if check_port $API_PORT; then
    print_color "$RED" "警告: 端口 $API_PORT 已被占用。API服务可能无法启动。"
    read -p "是否继续? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_color "$RED" "部署已取消。"
        exit 1
    fi
else
    print_color "$GREEN" "端口 $API_PORT 未被占用。"
fi

# 检查磁盘空间
print_color "$YELLOW" "[3/12] 检查磁盘空间..."
FREE_SPACE=$(df -h . | awk 'NR==2 {print $4}')
print_color "$BLUE" "当前目录可用空间: $FREE_SPACE"

# 检查内存
print_color "$YELLOW" "[4/12] 检查系统内存..."
if command -v free &> /dev/null; then
    TOTAL_MEM=$(free -m | awk 'NR==2 {print $2}')
    FREE_MEM=$(free -m | awk 'NR==2 {print $7}')
    print_color "$BLUE" "总内存: ${TOTAL_MEM}MB, 可用内存: ${FREE_MEM}MB"
    
    if [ "$FREE_MEM" -lt 1024 ]; then
        print_color "$RED" "警告: 可用内存不足1GB，应用可能无法正常运行。"
        read -p "是否继续? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_color "$RED" "部署已取消。"
            exit 1
        fi
    fi
else
    print_color "$YELLOW" "无法检查内存信息，跳过内存检查。"
fi

# 检查防火墙
print_color "$YELLOW" "[5/12] 检查防火墙配置..."
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        print_color "$YELLOW" "检测到UFW防火墙已启用。请确保以下端口已开放:"
        echo "- $WEB_PORT (Web服务)"
        echo "- $API_PORT (API服务)"
        print_color "$YELLOW" "您可以使用以下命令开放端口:"
        echo "sudo ufw allow $WEB_PORT/tcp"
        echo "sudo ufw allow $API_PORT/tcp"
    else
        print_color "$GREEN" "UFW防火墙未启用，无需配置。"
    fi
elif command -v firewall-cmd &> /dev/null; then
    if firewall-cmd --state | grep -q "running"; then
        print_color "$YELLOW" "检测到firewalld防火墙已启用。请确保以下端口已开放:"
        echo "- $WEB_PORT (Web服务)"
        echo "- $API_PORT (API服务)"
        print_color "$YELLOW" "您可以使用以下命令开放端口:"
        echo "sudo firewall-cmd --permanent --add-port=$WEB_PORT/tcp"
        echo "sudo firewall-cmd --permanent --add-port=$API_PORT/tcp"
        echo "sudo firewall-cmd --reload"
    else
        print_color "$GREEN" "firewalld防火墙未启用，无需配置。"
    fi
else
    print_color "$YELLOW" "未检测到常见防火墙服务，跳过防火墙检查。"
fi

# 创建必要的目录
print_color "$YELLOW" "[6/12] 创建必要的目录..."
mkdir -p data/uploads/annotations
mkdir -p data/uploads/outputs
mkdir -p data/uploads/templates
mkdir -p logs
chmod 755 data logs
print_color "$GREEN" "目录创建完成。"

# 检查配置文件
print_color "$YELLOW" "[7/12] 检查配置文件..."
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        print_color "$GREEN" "已从env.example创建.env文件。"
        print_color "$YELLOW" "请检查并编辑.env文件中的配置。"
    else
        print_color "$RED" "警告: 未找到env.example文件，将创建默认.env文件。"
        cat > .env << EOF
# 基本配置
DEBUG=false
SECRET_KEY=$(openssl rand -hex 24)
FLASK_ENV=production
ALLOWED_HOSTS=*

# 数据库配置
DATABASE_URI=sqlite:///data/app.db

# 安全配置
JWT_SECRET_KEY=$(openssl rand -hex 24)
SESSION_LIFETIME=24
CSRF_ENABLED=true
HTTPS_ENABLED=false

# API配置
API_CHECK_TIMEOUT=10
REQUEST_TIMEOUT=60
EOF
        print_color "$GREEN" "已创建默认.env文件。"
    fi
    
    # 提示用户编辑配置文件
    print_color "$YELLOW" "请检查并编辑.env文件中的配置。"
    read -p "是否现在编辑.env文件? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v nano &> /dev/null; then
            nano .env
        elif command -v vim &> /dev/null; then
            vim .env
        else
            print_color "$RED" "未找到可用的文本编辑器(nano/vim)，请稍后手动编辑.env文件。"
        fi
    fi
else
    print_color "$GREEN" ".env文件已存在。"
fi

# 安全检查
print_color "$YELLOW" "[8/12] 执行安全检查..."

# 检查.env文件中的密钥长度
if [ -f ".env" ]; then
    SECRET_KEY=$(grep "SECRET_KEY" .env | cut -d '=' -f2)
    JWT_SECRET_KEY=$(grep "JWT_SECRET_KEY" .env | cut -d '=' -f2)
    
    if [ ${#SECRET_KEY} -lt 16 ]; then
        print_color "$RED" "警告: SECRET_KEY长度不足，建议使用更长的密钥。"
        read -p "是否自动生成新的SECRET_KEY? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            NEW_SECRET_KEY=$(openssl rand -hex 24)
            sed -i "s/SECRET_KEY=.*/SECRET_KEY=$NEW_SECRET_KEY/" .env
            print_color "$GREEN" "已生成新的SECRET_KEY。"
        fi
    fi
    
    if [ ${#JWT_SECRET_KEY} -lt 16 ]; then
        print_color "$RED" "警告: JWT_SECRET_KEY长度不足，建议使用更长的密钥。"
        read -p "是否自动生成新的JWT_SECRET_KEY? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            NEW_JWT_SECRET_KEY=$(openssl rand -hex 24)
            sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$NEW_JWT_SECRET_KEY/" .env
            print_color "$GREEN" "已生成新的JWT_SECRET_KEY。"
        fi
    fi
fi

# 检查docker-compose.yml文件
print_color "$YELLOW" "[9/12] 检查Docker Compose配置..."
if [ ! -f "docker-compose.yml" ]; then
    print_color "$RED" "错误: 未找到docker-compose.yml文件。"
    exit 1
fi

# 检查docker-compose.yml文件中的安全配置
if grep -q "privileged: true" docker-compose.yml; then
    print_color "$RED" "警告: 检测到容器使用了privileged模式，这可能存在安全风险。"
fi

if ! grep -q "restart:" docker-compose.yml; then
    print_color "$YELLOW" "提示: 未检测到restart策略，建议添加restart: unless-stopped以提高可靠性。"
fi

# 检查Docker镜像安全性
print_color "$YELLOW" "[10/12] 构建和检查Docker镜像..."
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    # 构建Docker镜像
    docker-compose build
    
    if [ $? -ne 0 ]; then
        print_color "$RED" "错误: Docker镜像构建失败。"
        exit 1
    fi
    
    print_color "$GREEN" "Docker镜像构建成功。"
    
    # 检查Docker镜像漏洞，但使其变为可选
    if command -v trivy &> /dev/null; then
        print_color "$YELLOW" "使用Trivy检查Docker镜像漏洞..."
        
        # 获取镜像名称的方式更加灵活
        IMAGE_NAME=$(grep -o "image:.*" docker-compose.yml | head -n 1 | sed 's/image://' | tr -d ' "')
        
        if [ -n "$IMAGE_NAME" ]; then
            print_color "$YELLOW" "检测到镜像: $IMAGE_NAME"
            read -p "是否运行安全扫描? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                trivy image --severity HIGH,CRITICAL "$IMAGE_NAME" || true
                print_color "$GREEN" "Docker镜像安全检查完成。"
            else
                print_color "$YELLOW" "跳过安全扫描。"
            fi
        else
            print_color "$YELLOW" "无法确定Docker镜像名称，跳过漏洞扫描。"
        fi
    else
        print_color "$YELLOW" "未安装Trivy，跳过Docker镜像漏洞检查。"
        print_color "$YELLOW" "建议安装Trivy进行Docker镜像安全检查:"
        echo "curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin"
    fi
else
    print_color "$RED" "错误: Docker或Docker Compose未安装。"
    exit 1
fi

# 启动服务
print_color "$YELLOW" "[11/12] 启动服务..."
docker-compose down
docker-compose up -d

if [ $? -ne 0 ]; then
    print_color "$RED" "错误: 服务启动失败。"
    exit 1
fi

print_color "$GREEN" "服务已成功启动。"

# 检查服务状态
print_color "$YELLOW" "[12/12] 检查服务状态..."
sleep 5
docker-compose ps

# 检查服务是否正常运行
WEB_CONTAINER=$(docker-compose ps -q web)
API_CONTAINER=$(docker-compose ps -q api)

if [ -z "$WEB_CONTAINER" ] || [ -z "$API_CONTAINER" ]; then
    print_color "$RED" "警告: 无法确定容器ID，跳过服务健康检查。"
else
    # 检查Web服务
    WEB_STATUS=$(docker inspect --format='{{.State.Status}}' $WEB_CONTAINER)
    if [ "$WEB_STATUS" != "running" ]; then
        print_color "$RED" "警告: Web服务未正常运行，状态: $WEB_STATUS"
        print_color "$YELLOW" "查看Web服务日志:"
        echo "docker-compose logs web"
    else
        print_color "$GREEN" "Web服务运行正常。"
    fi
    
    # 检查API服务
    API_STATUS=$(docker inspect --format='{{.State.Status}}' $API_CONTAINER)
    if [ "$API_STATUS" != "running" ]; then
        print_color "$RED" "警告: API服务未正常运行，状态: $API_STATUS"
        print_color "$YELLOW" "查看API服务日志:"
        echo "docker-compose logs api"
    else
        print_color "$GREEN" "API服务运行正常。"
    fi
fi

# 完成
print_color "$CYAN" "====================================================="
print_color "$GREEN" "部署完成! 服务已启动。"
print_color "$CYAN" "====================================================="
print_color "$YELLOW" "Web服务访问地址: http://localhost:$WEB_PORT"
print_color "$YELLOW" "API服务访问地址: http://localhost:$API_PORT"
print_color "$CYAN" "====================================================="
print_color "$YELLOW" "常用命令:"
echo "- 查看服务状态: docker-compose ps"
echo "- 查看服务日志: docker-compose logs"
echo "- 重启服务: docker-compose restart"
echo "- 停止服务: docker-compose down"
echo "- 更新服务: git pull && docker-compose build && docker-compose up -d"
print_color "$CYAN" "====================================================="

# 提示设置开机自启动
print_color "$YELLOW" "是否设置Docker服务开机自启动? (y/n): "
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v systemctl &> /dev/null; then
        sudo systemctl enable docker
        print_color "$GREEN" "Docker服务已设置为开机自启动。"
    else
        print_color "$RED" "无法设置开机自启动，请手动配置。"
    fi
fi

exit 0 
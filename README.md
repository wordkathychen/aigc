# AI文本生成器

## 项目概述

AI文本生成器是一个功能全面的基于人工智能的文本生成工具，支持多种文本生成功能，包括论文模块化生成、文本摘要、内容扩写等。系统采用前后端分离架构，包含Web界面(5000端口)和API接口(8000端口)，可以独立部署或作为服务调用。同时提供桌面客户端应用，满足不同用户的使用需求。

## 目录

- [功能特性](#功能特性)
- [系统架构](#系统架构)
- [安装与部署](#安装与部署)
  - [本地开发环境](#本地开发环境)
  - [Docker部署](#docker部署)
  - [服务器部署](#服务器部署)
- [GitHub上传与管理](#github上传与管理)
- [打包为可执行文件](#打包为可执行文件)
- [使用指南](#使用指南)
- [安全性与性能](#安全性与性能)
- [维护与故障排除](#维护与故障排除)
- [常见问题解答](#常见问题解答)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 功能特性

### 核心功能

1. **论文模块化生成**
   - 支持按学历等级（大专、本科、硕士、博士）生成
   - 支持不同专业领域（计算机科学、经济学、医学等）
   - 分模块生成（摘要、关键词、引言、文献综述、方法、结果、讨论、结论、参考文献）
   - 支持中英文双语生成

2. **文本摘要生成**
   - 长文本自动提取关键信息
   - 支持多种摘要长度控制
   - 保留原文重点内容

3. **内容扩写与润色**
   - 短文本扩展为详细内容
   - 文章润色与改写
   - 风格调整与语言优化

4. **多语言支持**
   - 中文、英文内容生成与翻译
   - 支持多语言切换界面

### 特色功能

1. **自定义提示词模板**
   - 用户可创建和保存个人提示词
   - 系统预设多种专业领域模板
   - 模板参数化配置

2. **批量处理**
   - 支持多文件批量生成
   - 自动保存处理结果
   - 任务队列管理

3. **导出与分享**
   - 多格式导出(PDF, Word, Markdown, TXT)
   - 生成结果分享功能
   - 历史记录管理

4. **API接口**
   - RESTful API设计
   - 支持第三方应用集成
   - 完整的API文档

## 系统架构

### 技术栈

- **后端**: Python, Flask, SQLAlchemy
- **前端**: HTML, CSS, JavaScript, Bootstrap
- **数据库**: SQLite (开发), MySQL/PostgreSQL (生产)
- **容器化**: Docker, Docker Compose
- **桌面应用**: PyInstaller打包

### 组件结构

- **Web服务**: 提供Web界面和REST API
- **生成引擎**: 核心文本生成逻辑
- **数据存储**: 用户数据和生成历史
- **桌面客户端**: 独立运行的GUI应用

## 安装与部署

### 本地开发环境

1. **克隆代码仓库**

```bash
git clone https://github.com/yourusername/ai-text-generator.git
cd ai-text-generator
```

2. **创建并激活虚拟环境**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置环境变量**

```bash
# 复制示例配置
cp env.example .env

# 编辑.env文件设置必要的配置项
```

5. **初始化数据库**

```bash
flask db init
flask db migrate
flask db upgrade
```

6. **运行开发服务器**

```bash
# 启动Web界面服务
python run_web.py

# 启动API服务
python run_api.py
```

现在可以通过以下地址访问服务：
- Web界面: http://localhost:5000
- API接口: http://localhost:8000/api

### Docker部署

使用Docker是最简单的服务器部署方式，确保您的系统已安装Docker和Docker Compose。

#### 完整Docker部署步骤

1. **准备环境**

确保服务器已安装Docker和Docker Compose：

```bash
# 检查Docker版本
docker --version

# 检查Docker Compose版本
docker-compose --version

# 如果未安装，请参考官方文档安装
# Docker: https://docs.docker.com/engine/install/
# Docker Compose: https://docs.docker.com/compose/install/
```

2. **配置环境变量**

```bash
# 复制示例配置文件
cp env.example .env

# 编辑.env文件，设置必要的配置
# 特别注意设置正确的API密钥和数据库连接信息
```

3. **指定服务器IP地址**

在部署前，您必须指定服务器的IP地址，确保Web界面和API接口都能正确映射。有三种方法：

- **方法1: 使用部署脚本**（推荐）
  
  **Windows系统**:
  编辑`deploy_server.bat`文件，将其中的IP地址`154.201.65.63`替换为您的服务器IP：
  
  ```batch
  echo version: '3.8' > docker-compose.override.yml
  echo. >> docker-compose.override.yml
  echo services: >> docker-compose.override.yml
  echo   web: >> docker-compose.override.yml
  echo     ports: >> docker-compose.override.yml
  echo       - "您的服务器IP:5000:5000" >> docker-compose.override.yml
  echo       - "您的服务器IP:8000:8000" >> docker-compose.override.yml
  ```
  
  **Linux/Mac系统**:
  创建`docker-compose.override.yml`文件，指定端口映射：
  
  ```yaml
  version: '3.8'
  services:
    web:
      ports:
        - "您的服务器IP:5000:5000"
        - "您的服务器IP:8000:8000"
  ```

- **方法2: 直接修改docker-compose.yml**
  
  编辑`docker-compose.yml`文件，将端口映射部分修改为：
  
  ```yaml
  ports:
    - "您的服务器IP:5000:5000"
    - "您的服务器IP:8000:8000"
  ```

- **方法3: 使用环境变量**

  在`.env`文件中添加以下配置：
  
  ```
  SERVER_IP=您的服务器IP
  WEB_PORT=5000
  API_PORT=8000
  ```
  
  然后修改`docker-compose.yml`文件，使用环境变量：
  
  ```yaml
  ports:
    - "${SERVER_IP}:${WEB_PORT}:5000"
    - "${SERVER_IP}:${API_PORT}:8000"
  ```

4. **构建并启动容器**

```bash
# 使用部署脚本（推荐）
# Linux/Mac系统
bash deploy_server.sh

# Windows系统
deploy_server.bat

# 或手动执行
docker-compose build
docker-compose up -d
```

5. **验证服务状态**

```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs

# 测试Web界面
curl http://服务器IP:5000

# 测试API接口
curl http://服务器IP:8000/api/status
```

6. **访问服务**

- Web界面: http://服务器IP:5000
- API接口: http://服务器IP:8000/api

### 服务器部署

#### 准备服务器环境

1. **更新系统并安装依赖**

```bash
# Ubuntu/Debian系统
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git python3 python3-pip python3-venv

# CentOS/RHEL系统
sudo yum update -y
sudo yum install -y curl git python3 python3-pip
```

2. **安装Docker和Docker Compose**

```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 将当前用户添加到docker组
sudo usermod -aG docker $USER
# 注销并重新登录以应用更改
```

#### 部署应用

1. **克隆代码库**

```bash
git clone https://github.com/yourusername/ai-text-generator.git
cd ai-text-generator
```

2. **指定服务器IP地址**

在Linux/Mac系统上，编辑`deploy_server.sh`文件，找到以下部分并修改IP地址：

```bash
# 检查必要的端口是否被占用
print_color "$YELLOW" "[2/12] 检查端口占用情况..."
WEB_PORT=5000
API_PORT=8000
```

同时，您需要创建或修改`docker-compose.override.yml`文件：

```bash
services:
  web:
    ports: []
    ports:
      - "5000:5000"
      - "8000:8000"
```

3. **运行部署脚本**

```bash
bash deploy_server.sh
```

该脚本会自动:
- 检查环境依赖
- 创建必要的目录
- 配置环境变量
- 构建Docker镜像
- 启动服务
- 验证服务状态

3. **配置防火墙**

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 5000/tcp
sudo ufw allow 8000/tcp

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

#### 配置HTTPS（推荐）

1. **安装Nginx和Certbot**

```bash
# Ubuntu/Debian
sudo apt install nginx certbot python3-certbot-nginx -y
```

2. **获取SSL证书**

```bash
sudo certbot --nginx -d yourdomain.com
```

3. **配置Nginx反向代理**

```bash
sudo nano /etc/nginx/sites-available/ai-text-generator
```

添加以下配置:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Web界面
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API接口
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. **启用配置并重启Nginx**

```bash
sudo ln -s /etc/nginx/sites-available/ai-text-generator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 设置开机自启动

```bash
sudo systemctl enable docker
```

## GitHub上传与管理

### 初始化Git仓库

如果您要从零开始创建GitHub仓库，请按以下步骤操作：

1. **初始化本地Git仓库**

```bash
cd ai-text-generator
git init
```

2. **添加.gitignore文件**

创建`.gitignore`文件以排除不需要版本控制的文件：

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# 虚拟环境
venv/
ENV/

# 数据和日志
data/
logs/
*.log
*.db
*.sqlite3

# 环境变量
.env

# IDE相关
.idea/
.vscode/
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db
```

3. **添加文件并提交**

```bash
git add .
git commit -m "初始提交"
```

### 创建GitHub仓库

1. **登录GitHub并创建新仓库**

- 访问 https://github.com/new
- 输入仓库名称：`ai-text-generator`
- 添加描述：`基于人工智能的文本生成工具`
- 选择是否公开或私有
- 点击"创建仓库"

2. **关联远程仓库并推送代码**

```bash
git remote add origin https://github.com/yourusername/ai-text-generator.git
git branch -M main
git push -u origin main
```

### 管理代码版本

1. **创建功能分支**

```bash
git checkout -b feature/new-feature
```

2. **提交更改**

```bash
git add .
git commit -m "添加新功能：功能描述"
```

3. **推送到GitHub**

```bash
git push origin feature/new-feature
```

4. **创建Pull Request**

- 访问GitHub仓库页面
- 点击"Compare & pull request"
- 填写PR描述
- 点击"Create pull request"

5. **合并Pull Request**

- 审查代码
- 解决冲突（如有）
- 点击"Merge pull request"

### 发布版本

1. **创建标签**

```bash
git tag -a v1.0.0 -m "第一个正式版本"
git push origin v1.0.0
```

2. **在GitHub上创建Release**

- 访问仓库的"Releases"页面
- 点击"Draft a new release"
- 选择标签：v1.0.0
- 填写发布标题和说明
- 上传构建好的可执行文件（如有）
- 点击"Publish release"

## 打包为可执行文件

### 完全独立的可执行文件打包

为了创建完全独立的可执行文件（无需任何外部依赖），我们提供了一个专门的打包脚本。这种方式打包的程序可以在任何Windows系统上运行，无需安装Python或其他依赖。

1. **准备打包脚本**

创建一个名为`build_standalone.bat`的文件，包含以下内容：

```batch
@echo off
echo ===================================================
echo AI文本生成器 - 独立可执行文件打包脚本
echo ===================================================
echo.

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python 3.8或更高版本。
    pause
    exit /b 1
)

REM 安装和升级依赖
echo [步骤1] 安装和升级依赖...
python -m pip install --upgrade pip
python -m pip install --upgrade pyinstaller
python -m pip install --upgrade setuptools wheel
python -m pip install -r requirements.txt --upgrade

REM 清理之前的构建
echo [步骤2] 清理之前的构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
for /d /r . %%d in (*.egg-info) do @if exist "%%d" rmdir /s /q "%%d"

REM 创建必要的目录
echo [步骤3] 创建必要的目录...
if not exist logs mkdir logs
if not exist data mkdir data
if not exist data\cache mkdir data\cache
if not exist data\uploads mkdir data\uploads
if not exist data\outputs mkdir data\outputs
if not exist templates mkdir templates

REM 创建spec文件
echo [步骤4] 创建打包配置...
echo # -*- mode: python -*- > standalone.spec
echo import os >> standalone.spec
echo import sys >> standalone.spec
echo from PyInstaller.utils.hooks import collect_all, collect_submodules >> standalone.spec
echo. >> standalone.spec
echo block_cipher = None >> standalone.spec
echo. >> standalone.spec
echo # 收集所有必要的依赖 >> standalone.spec
echo datas = [('src/web/templates', 'src/web/templates'), >> standalone.spec
echo          ('src/web/static', 'src/web/static'), >> standalone.spec
echo          ('src/config', 'src/config'), >> standalone.spec
echo          ('resources', 'resources')] >> standalone.spec
echo. >> standalone.spec
echo binaries = [] >> standalone.spec
echo hiddenimports = ['src.web.routes.main', 'src.web.routes.auth', 'src.web.routes.paper_module'] >> standalone.spec
echo. >> standalone.spec
echo # 收集可能的问题库 >> standalone.spec
echo packages = ['tkinter', 'PIL', 'cryptography', 'requests', 'numpy', 'pandas', 'matplotlib', 'docx'] >> standalone.spec
echo. >> standalone.spec
echo for package in packages: >> standalone.spec
echo     try: >> standalone.spec
echo         pkg_data = collect_all(package) >> standalone.spec
echo         datas.extend(pkg_data[0]) >> standalone.spec
echo         binaries.extend(pkg_data[1]) >> standalone.spec
echo         hiddenimports.extend(pkg_data[2]) >> standalone.spec
echo         hiddenimports.extend(collect_submodules(package)) >> standalone.spec
echo     except Exception as e: >> standalone.spec
echo         print(f"Warning: Could not collect {package}: {e}") >> standalone.spec
echo. >> standalone.spec
echo # 添加系统DLL >> standalone.spec
echo sys_dlls = [] >> standalone.spec
echo if sys.platform == 'win32': >> standalone.spec
echo     sys_dll_paths = ['C:\\Windows\\System32\\vcruntime140.dll', >> standalone.spec
echo                      'C:\\Windows\\System32\\vcruntime140_1.dll', >> standalone.spec
echo                      'C:\\Windows\\System32\\msvcp140.dll', >> standalone.spec
echo                      'C:\\Windows\\System32\\msvcp140_1.dll', >> standalone.spec
echo                      'C:\\Windows\\System32\\msvcp140_2.dll'] >> standalone.spec
echo     for dll_path in sys_dll_paths: >> standalone.spec
echo         if os.path.exists(dll_path): >> standalone.spec
echo             sys_dlls.append((dll_path, '.')) >> standalone.spec
echo     binaries.extend(sys_dlls) >> standalone.spec
echo. >> standalone.spec
echo a = Analysis( >> standalone.spec
echo     ['main.py'], >> standalone.spec
echo     pathex=[], >> standalone.spec
echo     binaries=binaries, >> standalone.spec
echo     datas=datas, >> standalone.spec
echo     hiddenimports=hiddenimports, >> standalone.spec
echo     hookspath=[], >> standalone.spec
echo     hooksconfig={}, >> standalone.spec
echo     runtime_hooks=[], >> standalone.spec
echo     excludes=[], >> standalone.spec
echo     win_no_prefer_redirects=False, >> standalone.spec
echo     win_private_assemblies=False, >> standalone.spec
echo     cipher=block_cipher, >> standalone.spec
echo     noarchive=False, >> standalone.spec
echo ) >> standalone.spec
echo. >> standalone.spec
echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher) >> standalone.spec
echo. >> standalone.spec
echo exe = EXE( >> standalone.spec
echo     pyz, >> standalone.spec
echo     a.scripts, >> standalone.spec
echo     a.binaries, >> standalone.spec
echo     a.zipfiles, >> standalone.spec
echo     a.datas, >> standalone.spec
echo     [], >> standalone.spec
echo     name='AI文本生成器', >> standalone.spec
echo     debug=False, >> standalone.spec
echo     bootloader_ignore_signals=False, >> standalone.spec
echo     strip=False, >> standalone.spec
echo     upx=True, >> standalone.spec
echo     upx_exclude=[], >> standalone.spec
echo     runtime_tmpdir=None, >> standalone.spec
echo     console=False, >> standalone.spec
echo     disable_windowed_traceback=False, >> standalone.spec
echo     argv_emulation=False, >> standalone.spec
echo     target_arch=None, >> standalone.spec
echo     codesign_identity=None, >> standalone.spec
echo     entitlements_file=None, >> standalone.spec
echo     version='file_version_info.txt', >> standalone.spec
echo     icon='resources\\icon.ico', >> standalone.spec
echo ) >> standalone.spec

REM 创建版本信息文件
echo [步骤5] 创建版本信息文件...
echo # UTF-8 > file_version_info.txt
echo # > file_version_info.txt
echo # For more details about fixed file info 'ffi' see: > file_version_info.txt
echo # http://msdn.microsoft.com/en-us/library/ms646997.aspx > file_version_info.txt
echo VSVersionInfo( > file_version_info.txt
echo   ffi=FixedFileInfo( > file_version_info.txt
echo     # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4) > file_version_info.txt
echo     # Set not needed items to zero 0. > file_version_info.txt
echo     filevers=(1, 0, 0, 0), > file_version_info.txt
echo     prodvers=(1, 0, 0, 0), > file_version_info.txt
echo     # Contains a bitmask that specifies the valid bits 'flags' > file_version_info.txt
echo     mask=0x3f, > file_version_info.txt
echo     # Contains a bitmask that specifies the Boolean attributes of the file. > file_version_info.txt
echo     flags=0x0, > file_version_info.txt
echo     # The operating system for which this file was designed. > file_version_info.txt
echo     # 0x4 - NT and there is no need to change it. > file_version_info.txt
echo     OS=0x40004, > file_version_info.txt
echo     # The general type of file. > file_version_info.txt
echo     # 0x1 - the file is an application. > file_version_info.txt
echo     fileType=0x1, > file_version_info.txt
echo     # The function of the file. > file_version_info.txt
echo     # 0x0 - the function is not defined for this fileType > file_version_info.txt
echo     subtype=0x0, > file_version_info.txt
echo     # Creation date and time stamp. > file_version_info.txt
echo     date=(0, 0) > file_version_info.txt
echo   ), > file_version_info.txt
echo   kids=[ > file_version_info.txt
echo     StringFileInfo( > file_version_info.txt
echo       [ > file_version_info.txt
echo       StringTable( > file_version_info.txt
echo         u'080404b0', > file_version_info.txt
echo         [StringStruct(u'CompanyName', u'AI Text Generator'), > file_version_info.txt
echo         StringStruct(u'FileDescription', u'AI文本生成器'), > file_version_info.txt
echo         StringStruct(u'FileVersion', u'1.0.0'), > file_version_info.txt
echo         StringStruct(u'InternalName', u'AI文本生成器'), > file_version_info.txt
echo         StringStruct(u'LegalCopyright', u'Copyright (C) 2023'), > file_version_info.txt
echo         StringStruct(u'OriginalFilename', u'AI文本生成器.exe'), > file_version_info.txt
echo         StringStruct(u'ProductName', u'AI文本生成器'), > file_version_info.txt
echo         StringStruct(u'ProductVersion', u'1.0.0')] > file_version_info.txt
echo       ) > file_version_info.txt
echo       ] > file_version_info.txt
echo     ), > file_version_info.txt
echo     VarFileInfo([VarStruct(u'Translation', [2052, 1200])]) > file_version_info.txt
echo   ] > file_version_info.txt
echo ) > file_version_info.txt

REM 使用spec文件构建
echo [步骤6] 开始构建独立可执行文件...
pyinstaller --clean --noconfirm standalone.spec

REM 创建安装包目录
echo [步骤7] 创建安装包目录结构...
mkdir "dist\安装包"
mkdir "dist\安装包\AI文本生成器"
xcopy "dist\AI文本生成器.exe" "dist\安装包\AI文本生成器\" /y
mkdir "dist\安装包\AI文本生成器\data"
mkdir "dist\安装包\AI文本生成器\logs"
mkdir "dist\安装包\AI文本生成器\templates"
copy "README.md" "dist\安装包\AI文本生成器\使用说明.txt"

REM 创建安装脚本
echo [步骤8] 创建安装脚本...
echo @echo off > "dist\安装包\安装.bat"
echo echo 正在安装AI文本生成器... >> "dist\安装包\安装.bat"
echo mkdir "%%USERPROFILE%%\Documents\AI文本生成器" 2>nul >> "dist\安装包\安装.bat"
echo xcopy /E /I /Y "AI文本生成器" "%%USERPROFILE%%\Documents\AI文本生成器" >> "dist\安装包\安装.bat"
echo echo 创建桌面快捷方式... >> "dist\安装包\安装.bat"
echo powershell "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%%USERPROFILE%%\Desktop\AI文本生成器.lnk'); $Shortcut.TargetPath = '%%USERPROFILE%%\Documents\AI文本生成器\AI文本生成器.exe'; $Shortcut.Save()" >> "dist\安装包\安装.bat"
echo echo 安装完成！ >> "dist\安装包\安装.bat"
echo echo 程序已安装到您的文档文件夹中，并在桌面创建了快捷方式。 >> "dist\安装包\安装.bat"
echo pause >> "dist\安装包\安装.bat"
```

2. **运行打包脚本**

双击运行`build_standalone.bat`脚本，或在命令行中执行：

```bash
build_standalone.bat
```

脚本会自动执行以下操作：
- 安装和升级必要的依赖
- 清理之前的构建文件
- 创建必要的目录
- 生成打包配置文件
- 构建独立可执行文件
- 创建安装包目录结构
- 生成安装脚本

3. **打包结果**

打包完成后，您将获得：
- 独立可执行文件：`dist\AI文本生成器.exe`
- 完整安装包：`dist\安装包\`文件夹

4. **分发给用户**

将`dist\安装包\`文件夹发送给用户，用户只需运行其中的`安装.bat`即可完成安装。安装程序会：
- 将应用程序复制到用户的文档文件夹中
- 在桌面创建快捷方式
- 保留必要的数据目录结构

### 使用PyInstaller直接打包

### Windows系统打包

项目提供了自动化打包脚本`build_all.bat`，可以一键生成Windows可执行文件：

1. **运行打包脚本**

```bash
.\build_all.bat
```

该脚本会自动：
- 检查Python环境
- 创建并激活虚拟环境
- 安装必要依赖
- 运行安全检查
- 清理旧的构建文件
- 创建版本信息
- 使用PyInstaller打包应用
- 创建必要的数据目录
- 复制配置文件

2. **手动打包步骤**

如果自动脚本无法工作，可以手动执行以下步骤：

```bash
# 安装PyInstaller
pip install pyinstaller

# 执行打包
pyinstaller --clean ^
    --add-data "src/web/templates;src/web/templates" ^
    --add-data "src/web/static;src/web/static" ^
    --add-data "src/config;src/config" ^
    --hidden-import=src.web.routes.main ^
    --hidden-import=src.web.routes.auth ^
    --hidden-import=src.web.routes.paper_module ^
    --name ai_text_generator ^
    --icon=resources/icon.ico ^
    --noconsole ^
    --onefile ^
    main.py
```

3. **打包结果**

成功打包后，可执行文件位于`dist/ai_text_generator.exe`。

### Linux系统打包

在Linux系统上，可以使用`build_all.sh`脚本进行打包：

```bash
# 赋予脚本执行权限
chmod +x build_all.sh

# 执行打包脚本
./build_all.sh
```

### 分发打包后的应用

1. **创建安装包（可选）**

可以使用Inno Setup等工具创建安装程序：
- 下载并安装Inno Setup: https://jrsoftware.org/isinfo.php
- 创建安装脚本(.iss文件)
- 编译生成安装程序

2. **发布可执行文件**

将打包好的可执行文件和必要的数据文件一起分发：
- 上传到GitHub Releases
- 分享下载链接
- 提供安装说明

## 使用指南

### 论文模块化生成

1. **访问Web界面的论文模块化生成页面**
2. **填写基本信息**
   - 论文标题
   - 论文大纲
   - 学历等级（大专、本科、硕士、博士）
   - 专业领域（计算机科学、经济学等）
3. **选择生成模块**
   - 摘要：自动生成符合学术规范的摘要
   - 关键词：提取主题相关的关键词
   - 引言：生成研究背景、意义和目的
   - 文献综述：自动生成相关研究文献的综述
   - 研究方法：根据研究主题生成适当的研究方法
   - 结果分析：生成数据分析和结果讨论
   - 结论：总结研究发现和贡献
   - 参考文献：生成符合引用规范的参考文献列表
4. **调整生成结果**
   - 使用自定义提示词细化生成内容
   - 调整风格和格式
   - 保存或导出结果

### API调用示例

```python
import requests
import json

# 生成中文摘要
def generate_abstract_cn(title, outline, subject="通用", education_level="本科"):
    url = "http://localhost:5000/api/paper_module/generate_abstract_cn"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "title": title,
        "outline": outline,
        "subject": subject,
        "education_level": education_level
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# 示例调用
title = "人工智能在教育领域的应用研究"
outline = """
# 引言
## 研究背景
## 研究意义
# 文献综述
## 国内研究现状
## 国外研究现状
# 研究方法
## 理论框架
## 研究设计
# 结果分析
## 数据分析
## 结果讨论
# 结论
"""

result = generate_abstract_cn(title, outline, "计算机科学", "硕士")
print(result)
```

### 桌面客户端使用

1. **启动应用**
   - 双击`ai_text_generator.exe`运行程序
   - 首次运行会自动创建必要的数据目录

2. **使用界面**
   - 导航至所需功能模块
   - 填写必要信息
   - 点击生成按钮处理文本
   - 查看、编辑和保存结果

## 安全性与性能

### 安全性措施

1. **输入验证与过滤**
   - 所有用户输入经过严格验证和过滤，防止SQL注入、XSS攻击等
   - 使用bleach库净化HTML内容
   - 实现了自定义验证器，支持多种数据类型验证

2. **身份认证与授权**
   - 实现多角色权限控制（管理员/普通用户）
   - 敏感操作需要身份验证
   - 使用Flask-Login管理用户会话
   - 密码使用bcrypt算法加密存储

3. **HTTPS通信**
   - 生产环境强制使用HTTPS保护数据传输
   - 配置了严格的内容安全策略(CSP)
   - 启用HSTS头，防止SSL剥离攻击

4. **CSRF防护**
   - 为所有表单添加CSRF Token机制
   - 使用Flask-WTF提供的CSRF保护
   - API接口使用JWT认证

5. **其他安全措施**
   - 设置了安全的Cookie属性（HttpOnly, Secure, SameSite）
   - 添加了X-Content-Type-Options, X-Frame-Options等安全头
   - 实现了请求频率限制，防止暴力攻击

### 性能优化

1. **资源管理**
   - 自动关闭未使用的数据库连接
   - 文件句柄使用后正确释放
   - 使用连接池管理数据库连接

2. **超时机制**
   - 为网络请求、数据库查询等设置超时阈值
   - 长时间运行的任务使用异步处理
   - 实现了请求超时自动中断机制

3. **内存管理**
   - 监控内存占用，避免内存泄漏
   - 大型操作使用流式处理减少内存占用
   - 定期清理临时文件和缓存

4. **缓存策略**
   - 静态资源设置合理的缓存策略
   - 频繁使用的API结果进行缓存
   - 使用Redis缓存会话和常用数据

## 维护与故障排除

### 日志查看

系统日志位于`logs/`目录，包含以下日志文件：

- `app.log`: 应用程序主日志
- `access.log`: 访问日志
- `error.log`: 错误日志

查看日志的命令：

```bash
# 查看最近的应用日志
tail -f logs/app.log

# 查看Docker容器日志
docker-compose logs -f web
```

### 常见错误解决方案

#### 1. EXE打开出现"无法定位序数380于动态链接库"错误

这是由于缺少必要的Visual C++ Redistributable库或DLL文件导致的。解决方法：

1. 运行`fix_dll_error_new.bat`脚本，它会自动：
   - 检查并安装Visual C++ Redistributable
   - 复制必要的DLL文件到应用程序目录
   - 创建修复后的可执行文件

2. 如果问题仍然存在，请尝试：
   - 使用`build_standalone.bat`脚本重新打包，它会创建完全独立的可执行文件
   - 确保系统已安装最新的Windows更新

#### 2. Docker部署时出现"port is already allocated"错误

这表示指定的端口已被其他服务占用。解决方法：

1. 检查端口占用情况：
   ```bash
   # Linux/Mac
   netstat -tuln | grep 5000
   netstat -tuln | grep 8000
   
   # Windows
   netstat -ano | findstr 5000
   netstat -ano | findstr 8000
   ```

2. 修改端口映射：
   - 编辑`docker-compose.yml`或创建`docker-compose.override.yml`
   - 将端口映射改为其他未被占用的端口
   ```yaml
   ports:
     - "服务器IP:5001:5000"  # 将外部端口从5000改为5001
     - "服务器IP:8001:8000"  # 将外部端口从8000改为8001
   ```

#### 3. 服务器部署后无法访问Web界面或API

可能的原因包括防火墙设置、IP地址配置错误或服务未正常启动。解决方法：

1. 检查服务状态：
   ```bash
   docker-compose ps
   ```

2. 检查日志：
   ```bash
   docker-compose logs
   ```

3. 确认防火墙设置：
   ```bash
   # Ubuntu/Debian
   sudo ufw status
   
   # CentOS/RHEL
   sudo firewall-cmd --list-all
   ```

4. 验证IP地址配置：
   - 确保使用了正确的服务器IP地址
   - 如果服务器有多个IP，尝试使用0.0.0.0绑定所有接口

### 数据备份与恢复

定期备份数据是很重要的，特别是在生产环境中：

```bash
# 备份数据目录
tar -czvf backup-$(date +%Y%m%d).tar.gz data/

# 备份数据库（如果使用外部数据库）
pg_dump -U username dbname > backup-$(date +%Y%m%d).sql

# 恢复数据
tar -xzvf backup-20231015.tar.gz
```

系统也内置了自动备份功能，配置在docker-compose.yml中的backup服务。

### 更新系统

```bash
# 拉取最新代码
git pull

# 重建Docker镜像
docker-compose build

# 重启服务
docker-compose up -d
```

### 常见错误排查

1. **服务无法启动**
   - 检查端口是否被占用: `netstat -tuln | grep 5000`
   - 检查日志文件: `docker-compose logs`
   - 验证环境变量配置: `.env`文件设置

2. **生成功能失败**
   - 检查网络连接
   - 验证API密钥是否有效
   - 检查请求参数格式

3. **页面无法访问**
   - 确认服务正在运行: `docker-compose ps`
   - 检查防火墙设置: `sudo ufw status`
   - 验证Nginx配置(如使用): `nginx -t`

## 常见问题解答

1. **Q: 如何修改服务端口?**
   A: 需要同时修改多处配置：
   - 编辑`.env`文件中的`FLASK_PORT`和`API_PORT`配置项
   - 更新docker-compose.yml中的端口映射
   - 修改Dockerfile中的EXPOSE指令和CMD命令
   - 如果使用了docker-compose.override.yml，也需要更新其中的端口映射
   
   Web界面默认使用5000端口，API接口默认使用8000端口

2. **Q: 如何更换AI模型?**
   A: 编辑`.env`文件中的`AI_MODEL`配置项，支持多种模型接口

3. **Q: 如何设置自定义提示词模板?**
   A: 在管理界面的"提示词模板"部分添加或编辑模板

4. **Q: 系统报错"连接超时"怎么办?**
   A: 检查网络连接和API密钥配置，或增加`REQUEST_TIMEOUT`配置值

5. **Q: 如何扩展系统支持新的文本生成功能?**
   A: 参考开发文档，在`src/models`目录添加新的生成器类

6. **Q: 打包后的程序启动失败怎么办?**
   A: 有几种解决方法：
   - 运行`fix_dll_error_new.bat`脚本修复常见的DLL错误
   - 使用`build_standalone.bat`创建完全独立的可执行文件
   - 安装Visual C++ Redistributable 2015-2022
   - 使用`--debug`参数启动查看详细错误信息：`"AI文本生成器.exe" --debug > debug.log`

7. **Q: Docker部署时出现"port is already allocated"错误?**
   A: 端口已被占用，解决方法：
   - 使用`netstat -tuln`命令查看当前端口占用情况
   - 停止占用端口的服务：`sudo kill $(sudo lsof -t -i:5000)`
   - 或修改docker-compose.yml，使用其他未被占用的端口

8. **Q: 如何指定服务器IP地址进行部署?**
   A: 有三种方法：
   
   - **方法1**: 在Windows系统上，编辑deploy_server.bat文件中的IP地址`154.201.65.63`
   - **方法2**: 在Linux系统上，创建docker-compose.override.yml文件指定IP地址
   - **方法3**: 在.env文件中设置SERVER_IP环境变量
   
   注意：如果您的服务器有多个IP地址，请使用对外可访问的IP地址

9. **Q: 如何创建完全独立的可执行文件?**
   A: 使用`build_standalone.bat`脚本，它会创建一个不依赖外部DLL的可执行文件，并生成安装包

10. **Q: 如何确保Web界面和API接口都正常工作?**
    A: 部署后进行以下测试：
    - 访问Web界面: http://服务器IP:5000
    - 测试API接口: http://服务器IP:8000/api/status
    - 检查Docker容器状态: `docker-compose ps`
    - 查看日志: `docker-compose logs`

## 贡献指南

我们欢迎并感谢任何形式的贡献，包括但不限于功能改进、bug修复、文档完善等。

### 贡献流程

1. **Fork项目仓库**
   - 访问 https://github.com/yourusername/ai-text-generator
   - 点击右上角的"Fork"按钮

2. **克隆你的Fork**
   ```bash
   git clone https://github.com/your-username/ai-text-generator.git
   cd ai-text-generator
   ```

3. **创建功能分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **进行开发并提交更改**
   ```bash
   git add .
   git commit -m 'Add some amazing feature'
   ```

5. **推送到GitHub**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **创建Pull Request**
   - 访问你的仓库
   - 点击"Compare & pull request"
   - 填写PR描述
   - 提交PR

### 代码规范

- 遵循PEP 8 Python代码风格指南
- 添加适当的注释和文档字符串
- 编写单元测试
- 保持代码简洁清晰

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

---

*本文档最后更新于：2023年11月30日*

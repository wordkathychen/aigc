@echo off
setlocal enabledelayedexpansion

:: 设置颜色代码
set "GREEN=92"
set "YELLOW=93"
set "RED=91"
set "BLUE=94"
set "MAGENTA=95"
set "CYAN=96"
set "WHITE=97"

:: 显示彩色文本函数
call :PrintColorText %CYAN% "====================================================="
call :PrintColorText %CYAN% "       AI Text Generator 打包工具 (Windows)          "
call :PrintColorText %CYAN% "====================================================="
echo.

:: 检查Python是否安装
call :PrintColorText %YELLOW% "[1/10] 检查Python环境..."
python --version > nul 2>&1
if %errorlevel% neq 0 (
    call :PrintColorText %RED% "错误: 未找到Python，请先安装Python 3.8或更高版本。"
    exit /b 1
)

:: 检查Python版本
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%a"
echo 检测到Python版本: %PYTHON_VERSION%

:: 检查虚拟环境
call :PrintColorText %YELLOW% "[2/10] 检查并创建虚拟环境..."
if not exist "venv\" (
    echo 创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        call :PrintColorText %RED% "错误: 创建虚拟环境失败。"
        exit /b 1
    )
    call :PrintColorText %GREEN% "虚拟环境创建成功。"
) else (
    echo 虚拟环境已存在。
)

:: 激活虚拟环境
call :PrintColorText %YELLOW% "[3/10] 激活虚拟环境..."
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    call :PrintColorText %RED% "错误: 激活虚拟环境失败。"
    exit /b 1
)
call :PrintColorText %GREEN% "虚拟环境激活成功。"

:: 安装依赖
call :PrintColorText %YELLOW% "[4/10] 安装依赖..."
pip install -r requirements.txt
if %errorlevel% neq 0 (
    call :PrintColorText %RED% "错误: 安装依赖失败。"
    exit /b 1
)
pip install pyinstaller
if %errorlevel% neq 0 (
    call :PrintColorText %RED% "错误: 安装PyInstaller失败。"
    exit /b 1
)
call :PrintColorText %GREEN% "依赖安装成功。"

:: 运行安全检查
call :PrintColorText %YELLOW% "[5/10] 运行安全检查..."
echo 检查依赖包安全性...
pip install safety
if %errorlevel% neq 0 (
    call :PrintColorText %RED% "警告: 安装safety工具失败，跳过依赖安全检查。"
) else (
    safety check
    if %errorlevel% neq 0 (
        call :PrintColorText %RED% "警告: 发现依赖包存在安全漏洞，请检查上述输出并考虑更新相关依赖。"
        echo 是否继续打包? (y/n)
        set /p CONTINUE=
        if /i "!CONTINUE!" neq "y" (
            call :PrintColorText %RED% "用户取消打包过程。"
            exit /b 1
        )
    ) else (
        call :PrintColorText %GREEN% "依赖包安全检查通过。"
    )
)

echo 运行代码静态分析...
pip install pylint
if %errorlevel% neq 0 (
    call :PrintColorText %RED% "警告: 安装pylint工具失败，跳过代码静态分析。"
) else (
    pylint src --errors-only --disable=import-error
    if %errorlevel% neq 0 (
        call :PrintColorText %RED% "警告: 代码静态分析发现错误，请检查上述输出。"
        echo 是否继续打包? (y/n)
        set /p CONTINUE=
        if /i "!CONTINUE!" neq "y" (
            call :PrintColorText %RED% "用户取消打包过程。"
            exit /b 1
        )
    ) else (
        call :PrintColorText %GREEN% "代码静态分析通过。"
    )
)

:: 清理旧的构建文件
call :PrintColorText %YELLOW% "[6/10] 清理旧的构建文件..."
if exist "build\" (
    rmdir /s /q build
)
if exist "dist\" (
    rmdir /s /q dist
)
if exist "*.spec" (
    del /q *.spec
)
call :PrintColorText %GREEN% "清理完成。"

:: 创建版本信息文件
call :PrintColorText %YELLOW% "[7/10] 创建版本信息..."
echo Creating version file...
echo VERSION = '1.0.0' > src\version.py
echo BUILD_DATE = '%date%' >> src\version.py
echo BUILD_TIME = '%time%' >> src\version.py
call :PrintColorText %GREEN% "版本信息创建完成。"

:: 打包应用
call :PrintColorText %YELLOW% "[8/10] 打包应用..."
pyinstaller --clean ^
    --add-data "src/web/templates;src/web/templates" ^
    --add-data "src/web/static;src/web/static" ^
    --add-data "src/config;src/config" ^
    --hidden-import=src.web.routes.main ^
    --hidden-import=src.web.routes.auth ^
    --hidden-import=src.web.routes.admin ^
    --hidden-import=src.web.routes.api ^
    --hidden-import=src.web.routes.paper_module ^
    --hidden-import=src.web.routes.prompt_templates ^
    --hidden-import=src.web.routes.annotation ^
    --hidden-import=src.models.paper_generator ^
    --hidden-import=flask_login ^
    --hidden-import=flask_wtf ^
    --hidden-import=flask_wtf.csrf ^
    --hidden-import=flask_sqlalchemy ^
    --hidden-import=flask_migrate ^
    --hidden-import=flask_jwt_extended ^
    --hidden-import=flask_cors ^
    --hidden-import=werkzeug.security ^
    --hidden-import=jinja2 ^
    --hidden-import=sqlalchemy ^
    --hidden-import=bleach ^
    --hidden-import=markdown ^
    --hidden-import=cryptography ^
    --name ai_text_generator ^
    --icon=resources/icon.ico ^
    --noconsole ^
    --onefile ^
    main.py

if %errorlevel% neq 0 (
    call :PrintColorText %RED% "错误: 打包应用失败。"
    exit /b 1
)
call :PrintColorText %GREEN% "应用打包成功。"

:: 创建数据目录
call :PrintColorText %YELLOW% "[9/10] 创建数据目录..."
if not exist "dist\data\" (
    mkdir dist\data
)
if not exist "dist\logs\" (
    mkdir dist\logs
)
call :PrintColorText %GREEN% "数据目录创建完成。"

:: 复制配置文件
call :PrintColorText %YELLOW% "[10/10] 复制配置文件..."
copy .env.example dist\.env
if %errorlevel% neq 0 (
    call :PrintColorText %RED% "警告: 复制.env文件失败。"
)
call :PrintColorText %GREEN% "配置文件复制完成。"

:: 完成
call :PrintColorText %CYAN% "====================================================="
call :PrintColorText %GREEN% "打包完成! 可执行文件位于 dist/ai_text_generator.exe"
call :PrintColorText %CYAN% "====================================================="

:: 检查打包后的文件大小
for %%F in (dist\ai_text_generator.exe) do (
    set size=%%~zF
    set /a size_mb=!size! / 1048576
    call :PrintColorText %YELLOW% "可执行文件大小: !size_mb! MB"
)

:: 检查打包后的文件是否存在
if not exist "dist\ai_text_generator.exe" (
    call :PrintColorText %RED% "警告: 未找到打包后的可执行文件，打包可能失败。"
)

:: 询问是否运行病毒扫描
echo 是否对生成的可执行文件进行病毒扫描? (y/n)
set /p SCAN_VIRUS=
if /i "%SCAN_VIRUS%" equ "y" (
    call :PrintColorText %YELLOW% "正在扫描可执行文件..."
    if exist "C:\Program Files\Windows Defender\MpCmdRun.exe" (
        "C:\Program Files\Windows Defender\MpCmdRun.exe" -Scan -ScanType 3 -File "dist\ai_text_generator.exe"
        if %errorlevel% neq 0 (
            call :PrintColorText %RED% "警告: 病毒扫描发现问题，请检查Windows Defender日志。"
        ) else (
            call :PrintColorText %GREEN% "病毒扫描完成，未发现问题。"
        )
    ) else (
        call :PrintColorText %RED% "警告: 未找到Windows Defender命令行工具，无法执行扫描。"
    )
)

:: 询问是否运行测试
echo 是否运行打包后的应用测试? (y/n)
set /p RUN_TEST=
if /i "%RUN_TEST%" equ "y" (
    call :PrintColorText %YELLOW% "启动应用进行测试..."
    start "" "dist\ai_text_generator.exe"
)

goto :eof

:PrintColorText
echo [%~1m%~2[0m
goto :eof 
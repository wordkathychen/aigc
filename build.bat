@echo off
echo 开始打包AI论文生成助手...

rem 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本。
    pause
    exit /b 1
)

rem 检查是否已安装必要的包
echo 检查并安装必要的包...
python -m pip install -r requirements.txt
python -m pip install pyinstaller

rem 清理之前的构建
echo 清理之前的构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

rem 创建必要的目录
echo 创建必要的目录...
if not exist logs mkdir logs
if not exist data mkdir data
if not exist templates mkdir templates

rem 使用spec文件构建
echo 开始构建...
pyinstaller ai_text_generator.spec

echo 打包完成！
echo 可执行文件位于 dist\AI论文生成助手\ 目录
pause 
@echo off
echo 开始修复并打包AI文本生成器...

rem 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本。
    pause
    exit /b 1
)

rem 检查是否已安装Visual C++ Redistributable
echo 检查Visual C++ Redistributable...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" /v Version >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未找到Visual C++ Redistributable 2015-2022
    echo 正在下载并安装...
    powershell -Command "Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile 'vc_redist.x64.exe'"
    vc_redist.x64.exe /install /quiet /norestart
    echo Visual C++ Redistributable安装完成
)

rem 安装和升级依赖
echo 安装和升级依赖...
python -m pip install --upgrade pip
python -m pip install --upgrade pyinstaller
python -m pip install --upgrade setuptools wheel
python -m pip install -r requirements.txt --upgrade

rem 清理之前的构建
echo 清理之前的构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
for /d /r . %%d in (*.egg-info) do @if exist "%%d" rmdir /s /q "%%d"

rem 创建必要的目录
echo 创建必要的目录...
if not exist logs mkdir logs
if not exist data mkdir data
if not exist templates mkdir templates

rem 使用spec文件构建
echo 开始构建...
pyinstaller --clean ai_text_generator.spec

rem 复制DLL文件到打包目录
echo 复制系统DLL文件...
copy C:\Windows\System32\vcruntime140.dll dist\ai_text_generator\vcruntime140.dll
copy C:\Windows\System32\vcruntime140_1.dll dist\ai_text_generator\vcruntime140_1.dll
copy C:\Windows\System32\msvcp140.dll dist\ai_text_generator\msvcp140.dll

echo 打包完成！
echo 可执行文件位于 dist\ai_text_generator\ 目录
pause 
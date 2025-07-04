@echo off
echo ===================================================
echo AI文本生成器 - DLL错误修复脚本
echo ===================================================
echo.

REM 确认管理员权限
NET SESSION >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 请以管理员身份运行此脚本
    echo 右键点击脚本，选择"以管理员身份运行"
    pause
    exit /b 1
)

echo [步骤1] 检查Visual C++ Redistributable...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" /v Version >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 未找到Visual C++ Redistributable 2015-2022
    echo [信息] 正在下载并安装Visual C++ Redistributable...
    
    powershell -Command "Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile 'vc_redist.x64.exe'"
    vc_redist.x64.exe /install /quiet /norestart
    
    echo [信息] Visual C++ Redistributable安装完成
) else (
    echo [信息] Visual C++ Redistributable已安装
)

echo [步骤2] 复制系统DLL文件到应用程序目录...
if not exist "dist\ai_text_generator" (
    echo [错误] 未找到应用程序目录，请确保已执行打包操作
    pause
    exit /b 1
)

echo [信息] 复制必要的DLL文件...
copy C:\Windows\System32\vcruntime140.dll dist\ai_text_generator\vcruntime140.dll
copy C:\Windows\System32\vcruntime140_1.dll dist\ai_text_generator\vcruntime140_1.dll 2>nul
copy C:\Windows\System32\msvcp140.dll dist\ai_text_generator\msvcp140.dll 2>nul
copy C:\Windows\System32\msvcp140_1.dll dist\ai_text_generator\msvcp140_1.dll 2>nul
copy C:\Windows\System32\msvcp140_2.dll dist\ai_text_generator\msvcp140_2.dll 2>nul
copy C:\Windows\System32\api-ms-win-crt-runtime-l1-1-0.dll dist\ai_text_generator\api-ms-win-crt-runtime-l1-1-0.dll 2>nul
copy C:\Windows\System32\api-ms-win-crt-heap-l1-1-0.dll dist\ai_text_generator\api-ms-win-crt-heap-l1-1-0.dll 2>nul
copy C:\Windows\System32\api-ms-win-crt-math-l1-1-0.dll dist\ai_text_generator\api-ms-win-crt-math-l1-1-0.dll 2>nul
copy C:\Windows\System32\api-ms-win-crt-stdio-l1-1-0.dll dist\ai_text_generator\api-ms-win-crt-stdio-l1-1-0.dll 2>nul
copy C:\Windows\System32\api-ms-win-crt-locale-l1-1-0.dll dist\ai_text_generator\api-ms-win-crt-locale-l1-1-0.dll 2>nul

echo [步骤3] 修改spec文件，准备重新打包...
echo import sys > rebuild_fixed.py
echo from PyInstaller.utils.hooks import collect_all >> rebuild_fixed.py
echo >> rebuild_fixed.py
echo packages = ['tkinter', 'PIL', 'cryptography', 'requests'] >> rebuild_fixed.py
echo datas = [] >> rebuild_fixed.py
echo binaries = [] >> rebuild_fixed.py
echo hiddenimports = [] >> rebuild_fixed.py
echo >> rebuild_fixed.py
echo for package in packages: >> rebuild_fixed.py
echo     try: >> rebuild_fixed.py
echo         tmp_ret = collect_all(package) >> rebuild_fixed.py
echo         datas.extend(tmp_ret[0]) >> rebuild_fixed.py
echo         binaries.extend(tmp_ret[1]) >> rebuild_fixed.py
echo         hiddenimports.extend(tmp_ret[2]) >> rebuild_fixed.py
echo     except Exception as e: >> rebuild_fixed.py
echo         print(f"Error collecting {package}: {e}") >> rebuild_fixed.py
echo >> rebuild_fixed.py
echo print("COLLECT_ALL_RESULT = {") >> rebuild_fixed.py
echo print("    'datas': datas,") >> rebuild_fixed.py
echo print("    'binaries': binaries,") >> rebuild_fixed.py
echo print("    'hiddenimports': hiddenimports") >> rebuild_fixed.py
echo print("}") >> rebuild_fixed.py

python rebuild_fixed.py > collect_all_result.py

echo [步骤4] 创建修复后的可执行文件...
echo @echo off > rebuild.bat
echo pyinstaller --clean --noconfirm ^
    --add-data "src/web/templates;src/web/templates" ^
    --add-data "src/web/static;src/web/static" ^
    --add-data "src/config;src/config" ^
    --add-binary "C:\Windows\System32\vcruntime140.dll;." ^
    --add-binary "C:\Windows\System32\msvcp140.dll;." ^
    --add-binary "C:\Windows\System32\api-ms-win-crt-runtime-l1-1-0.dll;." ^
    --name "ai_text_generator_fixed" ^
    --icon "resources\icon.ico" ^
    --noconsole main.py >> rebuild.bat

echo.
echo ===================================================
echo 修复步骤已完成!
echo.
echo 请尝试以下操作:
echo 1. 运行rebuild.bat重新构建应用程序
echo 2. 如果问题仍然存在，请安装最新的Windows更新
echo 3. 确保已安装Visual C++ Redistributable 2015-2022
echo ===================================================

pause

@echo off
echo ===================================================
echo AI Text Generator - Standalone Packager (Direct Mode)
echo ===================================================
echo.

setlocal
set WORKING_DIR=%~dp0
cd /d "%WORKING_DIR%"

REM Check if main file exists
if not exist "main.py" (
    echo [ERROR] main.py not found
    echo Please place this script in project root
    pause
    exit /b 1
)

echo [Step 1] Creating isolated environment...
python -m venv pyinstaller_env
call pyinstaller_env\Scripts\activate

echo [Step 2] Direct PyInstaller installation from PyPI...
python -m pip install --upgrade --no-index -f https://download.pytorch.org/whl/torch_stable.html pip setuptools wheel || (
    echo [ERROR] Failed to update pip/setuptools/wheel
    echo Try running: python -m ensurepip
    pause
    exit /b
)

REM This alternative method bypasses the problematic wheel file
echo Installing PyInstaller directly...
python -m pip install --no-deps PyInstaller

echo [Step 3] Creating minimal requirements file...
echo aiohttp==3.9.5 > minimal-requirements.txt
echo jinja2==3.1.3 >> minimal-requirements.txt
echo pandas==2.2.0 >> minimal-requirements.txt
echo numpy==1.26.4 >> minimal-requirements.txt
echo requests==2.32.0 >> minimal-requirements.txt

echo [Step 4] Installing core dependencies only...
python -m pip install -r minimal-requirements.txt

echo [Step 5] Cleaning build directories...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
rmdir /s /q __pycache__ 2>nul

echo [Step 6] Building executable directly...
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --name "AI_Text_Generator" ^
  --add-data "src/web/templates;templates" ^
  --add-data "src/web/static;static" ^
  --add-data "src/config;config" ^
  --add-data "resources;resources" ^
  --add-data "data;data" ^
  --add-data "templates;templates_app" ^
  --hidden-import "src.web.routes.main" ^
  --hidden-import "src.web.routes.auth" ^
  --hidden-import "src.web.routes.paper_module" ^
  --icon "resources\icon.ico" ^
  --noconsole ^
  "main.py"

if not exist "dist\AI_Text_Generator.exe" (
    echo [CRITICAL] EXE file not created!
    echo Possible reasons:
    echo 1. Missing project files - Verify paths
    echo 2. Python path issues - Run as Administrator
    echo 3. Dependency conflicts - Check requirements.txt
    echo Debug: Try building manually with:
    echo   python -m PyInstaller --onefile main.py
    pause
    exit /b 1
)

echo [Step 7] Creating deployment package...
mkdir dist\Deployment 2>nul
copy "dist\AI_Text_Generator.exe" "dist\Deployment\" >nul

REM Creating minimal directory structure
mkdir dist\Deployment\templates 2>nul
mkdir dist\Deployment\static 2>nul
mkdir dist\Deployment\config 2>nul
mkdir dist\Deployment\resources 2>nul

REM Only copy essential files
if exist "src\web\templates" xcopy "src\web\templates\*.*" "dist\Deployment\templates\" /e /q /y /i
if exist "src\web\static" xcopy "src\web\static\*.*" "dist\Deployment\static\" /e /q /y /i
if exist "src\config" xcopy "src\config\*.*" "dist\Deployment\config\" /e /q /y /i
if exist "resources" xcopy "resources\*.*" "dist\Deployment\resources\" /e /q /y /i
if exist "data" xcopy "data\*.*" "dist\Deployment\data\" /e /q /y /i

echo [Step 8] Creating reliable installer script...
> dist\Deployment\Install_AI_Generator.bat (
    echo @echo off
    echo setlocal enabledelayedexpansion
    echo echo.
    echo echo ==================================================
    echo echo AI TEXT GENERATOR INSTALLER
    echo echo ==================================================
    echo.
    echo set "TARGET_DIR=%%USERPROFILE%%\Documents\AI_Text_Generator"
    echo set "SRC_DIR=%%~dp0"
    echo set "EXE_NAME=AI_Text_Generator.exe"
    echo set "TARGET_EXE=!TARGET_DIR!\!EXE_NAME!"
    echo.
    echo REM Create destination directory
    echo if not exist "!TARGET_DIR!\" (
    echo     mkdir "!TARGET_DIR!"
    echo     echo Created directory: !TARGET_DIR!
    echo )
    echo.
    echo REM Cleanup previous installation
    echo if exist "!TARGET_EXE!" (
    echo     echo Found existing version. Backing up...
    echo     move /Y "!TARGET_EXE!" "!TARGET_EXE!.bak"
    echo )
    echo.
    echo REM Copy files
    echo echo Copying files from: !SRC_DIR!
    echo echo                to: !TARGET_DIR!
    echo xcopy "!SRC_DIR!*.*" "!TARGET_DIR!\" /e /y /q /i
    echo.
    echo if exist "!TARGET_EXE!" (
    echo     echo Application installed: !TARGET_EXE!
    echo     echo.
    echo     echo Creating desktop shortcut...
    echo     set "DESKTOP_PATH=%%USERPROFILE%%\Desktop"
    echo     set "LINK_PATH=!DESKTOP_PATH!\!EXE_NAME!.lnk"
    echo     
    echo     REM Create shortcut using PowerShell
    echo     powershell -command ^
    echo         "$WshShell = New-Object -ComObject WScript.Shell;" ^
    echo         "$Shortcut = $WshShell.CreateShortcut('!LINK_PATH!');" ^
    echo         "$Shortcut.TargetPath = '!TARGET_EXE!';" ^
    echo         "$Shortcut.WorkingDirectory = '!TARGET_DIR!';" ^
    echo         "$Shortcut.Save()"
    echo     
    echo     echo Created shortcut: !LINK_PATH!
    echo ) else (
    echo     echo [ERROR] Installation failed! EXE not found
    echo     echo Check paths: !TARGET_EXE!
    echo )
    echo.
    echo echo ==================================================
    echo echo INSTALLATION COMPLETE
    echo echo ==================================================
    echo.
    echo pause
)

echo.
echo ===================================================
echo [SUCCESS] Packaging finished!
echo.
echo Files ready for distribution:
echo   dist\Deployment\
echo.
echo HOW TO DISTRIBUTE:
echo 1. Copy the entire 'dist\Deployment' folder
echo 2. Give to users - they run 'Install_AI_Generator.bat'
REM Add version information
echo %DATE% %TIME% > dist\Deployment\version.txt
echo Built on Windows >> dist\Deployment\version.txt
echo ===================================================
echo.
pause

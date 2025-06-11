@echo off
echo ===================================================
echo AI文本生成器 - 服务器部署脚本
echo ===================================================
echo.

REM 检查Docker是否安装
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到Docker，请先安装Docker并确保其在系统PATH中
    goto :error
)

REM 检查Docker Compose是否安装
where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到Docker Compose，请先安装Docker Compose
    goto :error
)

REM 检查.env文件是否存在
if not exist ".env" (
    echo [信息] 未找到.env文件，将使用默认配置
    echo [信息] 建议复制env.example为.env并修改配置
    
    set /p CONTINUE=是否继续部署? (y/n): 
    if /i not "%CONTINUE%"=="y" (
        echo [信息] 部署已取消
        goto :eof
    )
) else (
    echo [信息] 已找到.env文件，将使用其中的配置
)

echo [步骤1] 创建必要的目录...
if not exist "data\uploads\annotations" mkdir data\uploads\annotations
if not exist "data\uploads\outputs" mkdir data\uploads\outputs
if not exist "data\uploads\templates" mkdir data\uploads\templates
if not exist "logs" mkdir logs

echo [步骤2] 构建Docker镜像...
docker-compose build
if %errorlevel% neq 0 (
    echo [错误] Docker镜像构建失败
    goto :error
)

echo [步骤3] 启动Docker容器...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [错误] Docker容器启动失败
    goto :error
)

echo [步骤4] 检查容器状态...
timeout /t 5 /nobreak > nul
docker-compose ps | findstr "ai-text-generator-web" | findstr "Up"
if %errorlevel% neq 0 (
    echo [警告] 容器可能未正常启动，请检查日志
    docker-compose logs
) else (
    echo [成功] 容器已成功启动
)

REM 获取服务器IP地址
for /f "tokens=1-2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
    set IP=%%b
)
set IP=%IP:~1%

REM 获取端口
set WEB_PORT=5000
if exist ".env" (
    for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr "WEB_PORT"') do (
        set WEB_PORT=%%b
    )
)

echo.
echo ===================================================
echo 部署完成!
echo.
echo Web后台已部署，可通过以下方式访问:
echo   - 管理界面: http://%IP%:%WEB_PORT%
echo   - API接口: http://%IP%:%WEB_PORT%/api
echo.
echo 客户端配置:
echo   - 在客户端设置中将服务器地址设为: http://%IP%:%WEB_PORT%/api
echo.
echo 管理命令:
echo   - 查看日志: docker-compose logs
echo   - 重启服务: docker-compose restart
echo   - 停止服务: docker-compose down
echo ===================================================
goto :eof

:error
echo.
echo 部署过程中出现错误，请检查上述错误信息。
exit /b 1 
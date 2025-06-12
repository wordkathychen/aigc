@echo off
echo 开始修复DLL问题...

rem 设置VCRUNTIME路径
set VCRUNTIME_PATH=C:\Windows\System32\vcruntime140.dll
set VCRUNTIME_PATH_DIST=.\dist\ai_text_generator\vcruntime140.dll

rem 复制系统DLL到dist目录
echo 复制系统DLL文件...
if exist %VCRUNTIME_PATH% (
    copy %VCRUNTIME_PATH% %VCRUNTIME_PATH_DIST%
    echo 已复制 vcruntime140.dll
) else (
    echo 警告: 未找到 vcruntime140.dll
)

rem 检查是否需要Visual C++ Redistributable
echo 检查Visual C++ Redistributable...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" /v Version >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未找到Visual C++ Redistributable 2015-2022
    echo 请从Microsoft官方网站下载并安装Visual C++ Redistributable 2015-2022
    echo 下载链接: https://aka.ms/vs/17/release/vc_redist.x64.exe
    start https://aka.ms/vs/17/release/vc_redist.x64.exe
) else (
    echo Visual C++ Redistributable已安装
)

echo 修复完成!
echo 请重新运行build.bat构建应用程序
pause 
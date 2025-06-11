"""
打包脚本 - 使用PyInstaller将应用程序打包为可执行文件

用法:
    python setup.py

依赖:
    - PyInstaller
    - 所有项目依赖项（见requirements.txt）
"""

import os
import sys
import shutil
import subprocess
import platform

def clean_build_dirs():
    """清理之前的构建目录"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理 {dir_name} 目录...")
            shutil.rmtree(dir_name)

def create_directories():
    """创建必要的目录"""
    dirs_to_create = ['logs', 'data', 'templates']
    for dir_name in dirs_to_create:
        os.makedirs(dir_name, exist_ok=True)
        # 创建一个空的.keep文件以确保目录被包含
        with open(os.path.join(dir_name, '.keep'), 'w') as f:
            pass

def copy_resources():
    """复制资源文件"""
    # 复制模板文件
    if os.path.exists('templates'):
        template_dest = os.path.join('dist', 'AI论文生成助手', 'templates')
        os.makedirs(template_dest, exist_ok=True)
        for file in os.listdir('templates'):
            if file.endswith('.docx'):
                shutil.copy(
                    os.path.join('templates', file),
                    os.path.join(template_dest, file)
                )
    
    # 复制其他必要的资源文件
    resource_files = ['README.md', 'LICENSE']
    for file in resource_files:
        if os.path.exists(file):
            shutil.copy(file, os.path.join('dist', 'AI论文生成助手', file))

def build_executable():
    """使用PyInstaller构建可执行文件"""
    icon_path = ''
    if os.path.exists('icon.ico'):
        icon_path = '--icon=icon.ico'
    
    # 根据操作系统确定数据分隔符
    separator = ';' if platform.system() == 'Windows' else ':'
    
    # 基本PyInstaller命令
    cmd = [
        'pyinstaller',
        '--name=AI论文生成助手',
        '--onedir',  # 创建单个目录而不是单个文件
        '--windowed',  # 不显示控制台窗口
        '--noconfirm',  # 覆盖输出目录
        f'--add-data=templates{separator}templates',  # 添加模板目录
    ]
    
    # 添加图标（如果存在）
    if icon_path:
        cmd.append(icon_path)
    
    # 添加主文件
    cmd.append('src/main.py')
    
    print("执行打包命令:", ' '.join(cmd))
    subprocess.call(cmd)

def main():
    """主函数"""
    print("开始打包AI论文生成助手...")
    
    # 检查PyInstaller是否已安装
    try:
        import PyInstaller
    except ImportError:
        print("未找到PyInstaller，正在安装...")
        subprocess.call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # 清理旧的构建文件
    clean_build_dirs()
    
    # 创建必要的目录
    create_directories()
    
    # 构建可执行文件
    build_executable()
    
    # 复制资源文件
    copy_resources()
    
    print("打包完成！可执行文件位于 dist/AI论文生成助手/ 目录")

if __name__ == "__main__":
    main() 
from typing import List, Optional
import sys
import os
import tkinter as tk
from tkinter import messagebox

# 获取应用程序的基础路径
def get_base_path():
    """获取应用程序的基础路径，兼容PyInstaller打包"""
    if getattr(sys, 'frozen', False):
        # 如果是PyInstaller打包的应用
        return os.path.dirname(sys.executable)
    else:
        # 如果是直接运行的脚本
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 设置基础路径
base_path = get_base_path()
sys.path.append(base_path)

# 确保日志目录存在
logs_dir = os.path.join(base_path, "logs")
os.makedirs(logs_dir, exist_ok=True)

# 确保数据目录存在
data_dir = os.path.join(base_path, "data")
os.makedirs(data_dir, exist_ok=True)

from src.models.deepseek import DeepseekAPI
from src.utils.outline_generator import OutlineGenerator 
from src.utils.text_processor import TextProcessor
from src.utils.logger import setup_logger
from src.config.settings import MIN_WORDS, MAX_WORDS
from src.gui.login import LoginWindow

logger = setup_logger(__name__)

def get_valid_input(prompt: str, validator, error_msg: str) -> Optional[str]:
    """获取并验证用户输入"""
    while True:
        try:
            user_input = input(prompt).strip()
            if user_input.lower() in ('q', 'quit'):
                return None
            validator(user_input)
            return user_input
        except ValueError as e:
            print(f"错误: {error_msg}")
            logger.warning(f"输入验证失败: {str(e)}")

def validate_title(title: str) -> None:
    """验证标题"""
    if not title:
        raise ValueError("标题不能为空")
    if len(title) > 100:
        raise ValueError("标题过长")

def validate_words(words_str: str) -> None:
    """验证字数"""
    try:
        words = int(words_str)
        if not MIN_WORDS <= words <= MAX_WORDS:
            raise ValueError
    except ValueError:
        raise ValueError(f"请输入 {MIN_WORDS} 到 {MAX_WORDS} 之间的整数")

def main() -> None:
    try:
        # 获取用户输入
        title = get_valid_input(
            "请输入文章题目 (输入 q 退出): ",
            validate_title,
            "标题格式不正确"
        )
        if not title:
            return

        words_str = get_valid_input(
            f"请输入总字数 ({MIN_WORDS}-{MAX_WORDS}): ",
            validate_words,
            f"请输入 {MIN_WORDS} 到 {MAX_WORDS} 之间的整数"
        )
        if not words_str:
            return
            
        total_words = int(words_str)
        
        # 初始化组件
        outline_generator = OutlineGenerator()
        processor = TextProcessor(total_words)
        deepseek = DeepseekAPI()
        
        # 生成大纲
        logger.info(f"开始为《{title}》生成大纲")
        outline = outline_generator.generate_outline(title)
        
        # 显示大纲并等待确认
        print("\n生成的大纲：")
        for idx, section in enumerate(outline, 1):
            print(f"{idx}. {section}")
        
        if input("\n是否接受该大纲？(y/n): ").lower() != 'y':
            print("请重新运行程序生成新的大纲")
            return
        
        # 分配字数
        word_distribution = processor.distribute_words(len(outline))
        
        # 生成内容
        print("\n开始生成内容...\n")
        for section, words in zip(outline, word_distribution):
            content = deepseek.generate_content(title, section, words)
            print(f"\n{section} (目标字数: {words}):")
            print(content)
            print("-" * 50)
            
        logger.info("文章生成完成")
        
    except KeyboardInterrupt:
        print("\n程序已终止")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        print(f"发生错误: {str(e)}")
        sys.exit(1)

def run_gui():
    """启动GUI应用"""
    try:
        # 创建主窗口
        root = tk.Tk()
        app = LoginWindow(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"程序启动失败: {str(e)}")
        messagebox.showerror("错误", f"程序启动失败: {str(e)}")

if __name__ == "__main__":
    run_gui()
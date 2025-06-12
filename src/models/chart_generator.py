from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from docx.shared import Inches
from utils.exceptions import ChartError
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ChartGenerator:
    def __init__(self):
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        self.style = 'seaborn'
        
    def generate_line_chart(self, 
                          data: Dict[str, List[float]], 
                          title: str,
                          xlabel: str,
                          ylabel: str,
                          save_path: Optional[str] = None) -> str:
        """生成折线图"""
        try:
            plt.style.use(self.style)
            plt.figure(figsize=(10, 6))
            
            for label, values in data.items():
                plt.plot(values, label=label, marker='o')
            
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.legend()
            plt.grid(True)
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                return save_path
            
            return plt.gcf()
            
        except Exception as e:
            logger.error(f"生成折线图失败: {str(e)}")
            raise ChartError(f"无法生成折线图: {str(e)}")
    
    def generate_bar_chart(self,
                         data: Dict[str, float],
                         title: str,
                         xlabel: str,
                         ylabel: str,
                         save_path: Optional[str] = None) -> str:
        """生成柱状图"""
        try:
            plt.style.use(self.style)
            plt.figure(figsize=(10, 6))
            
            x = list(data.keys())
            y = list(data.values())
            
            plt.bar(x, y)
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            
            # 在柱子上添加数值标签
            for i, v in enumerate(y):
                plt.text(i, v, str(v), ha='center', va='bottom')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                return save_path
            
            return plt.gcf()
            
        except Exception as e:
            logger.error(f"生成柱状图失败: {str(e)}")
            raise ChartError(f"无法生成柱状图: {str(e)}")
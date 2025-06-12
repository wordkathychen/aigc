from typing import List
import logging
from src.models.deepseek import DeepseekAPI
from src.config.settings import MIN_SECTIONS, MAX_SECTIONS
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class OutlineGenerator:
    def __init__(self):
        self.deepseek = DeepseekAPI()
    
    def generate_outline(self, title: str, level: str = "二级大纲") -> List[str]:
        """
        根据标题生成文章大纲
        Args:
            title: 文章标题
            level: 大纲级别("二级大纲" or "三级大纲")
        """
        prompt = self._create_prompt(title, level)
        
        try:
            response = self.deepseek.generate_content(title, "大纲生成", 200)
            outline = self._parse_outline(response)
            
            if not outline or len(outline) < MIN_SECTIONS:
                logger.warning(f"生成的大纲节数不足，使用默认大纲")
                return self._get_default_outline()
                
            return outline[:MAX_SECTIONS]
            
        except Exception as e:
            logger.error(f"生成大纲失败: {str(e)}")
            return self._get_default_outline()
    
    def _create_prompt(self, title: str, level: str) -> str:
        return f"""
        请为题目《{title}》生成一个{level}的论文大纲，
        要求：
        1. 层次分明，逻辑清晰
        2. 包含{MIN_SECTIONS}-{MAX_SECTIONS}个主要章节
        3. 每个标题简短精炼
        4. 符合学术论文规范
        5. 包含引言和结论部分
        只需要返回标题列表，每行一个标题，无需编号和其他说明
        """
    
    def _parse_outline(self, response: str) -> List[str]:
        """解析API返回的大纲文本"""
        lines = []
        for line in response.split('\n'):
            # 清理行
            line = line.strip()
            # 移除数字编号
            line = ''.join([c for c in line if not c.isdigit() and c not in '.-、'])
            line = line.strip()
            if line and len(line) <= 50:  # 确保标题不会太长
                lines.append(line)
        return lines
    
    def _get_default_outline(self) -> List[str]:
        """返回默认大纲结构"""
        return [
            "绪论",
            "文献综述",
            "研究方法",
            "实验结果与分析",
            "结论与展望"
        ]
"""
大纲生成模块
负责根据论文主题生成论文大纲
"""

import json
from typing import Dict, List, Any, Optional, Union
from src.models.deepseek import DeepseekAPI
from src.utils.logger import setup_logger
from src.config.settings import PAPER_TYPES

logger = setup_logger(__name__)

class OutlineGenerator:
    """论文大纲生成器"""
    
    def __init__(self):
        """初始化大纲生成器"""
        self.api = DeepseekAPI()
        logger.info("初始化大纲生成器")
    
    def generate_outline(self, 
                         title: str, 
                         paper_type: str = "毕业论文", 
                         subject: str = "通用", 
                         education_level: str = "本科", 
                         word_count: int = 6000) -> List[Dict]:
        """生成论文大纲
        
        Args:
            title: 论文标题
            paper_type: 论文类型（毕业论文、期刊论文等）
            subject: 学科领域
            education_level: 教育水平（大专、本科、研究生）
            word_count: 论文总字数
            
        Returns:
            List[Dict]: 大纲结构，包含标题和子标题
        """
        # 获取论文类型配置
        paper_config = PAPER_TYPES.get(paper_type, PAPER_TYPES["毕业论文"])
        
        # 构建提示词
        prompt = self._build_outline_prompt(
            title, paper_type, subject, education_level, 
            word_count, paper_config
        )
        
        # 调用API生成大纲
        try:
            logger.info(f"开始生成大纲: {title}")
            response = self.api.generate_content(
                prompt, 
                f"生成{paper_type}大纲"
            )
            
            # 解析大纲
            outline = self._parse_outline_response(response)
            logger.info(f"大纲生成成功，共{len(outline)}个主要部分")
            
            return outline
            
        except Exception as e:
            logger.error(f"大纲生成失败: {str(e)}")
            # 返回简单的默认大纲
            return self._generate_default_outline(paper_config)
    
    def _build_outline_prompt(self, 
                             title: str, 
                             paper_type: str, 
                             subject: str, 
                             education_level: str, 
                             word_count: int, 
                             paper_config: Dict) -> str:
        """构建大纲生成提示词
        
        Args:
            title: 论文标题
            paper_type: 论文类型
            subject: 学科领域
            education_level: 教育水平
            word_count: 论文总字数
            paper_config: 论文类型配置
            
        Returns:
            str: 提示词
        """
        # 是否需要摘要和参考文献
        requires_abstract = paper_config.get("requires_abstract", True)
        requires_references = paper_config.get("requires_references", True)
        
        # 构建提示词
        prompt = f"""
        请为以下论文生成一个详细的三级大纲结构：
        
        论文标题：{title}
        论文类型：{paper_type}
        学科领域：{subject}
        教育水平：{education_level}
        总字数要求：约{word_count}字
        
        大纲要求：
        1. 大纲应包含三级标题（章、节、小节）
        2. 章节编号使用"1"、"1.1"、"1.1.1"的格式
        3. 每个章节标题应准确、简洁，能够清晰表达内容
        4. 大纲结构要符合{paper_type}的标准格式
        5. 内容应与{subject}学科相关，符合{education_level}水平
        6. 请确保内容的连贯性和逻辑性
        
        {f"7. 请包含摘要和英文摘要（Abstract）" if requires_abstract else ""}
        {f"8. 请包含参考文献部分" if requires_references else ""}
        
        请以JSON格式返回大纲，格式如下：
        ```json
        [
          {{
            "title": "章标题",
            "subtitles": [
              {{
                "title": "节标题",
                "subtitles": [
                  {{
                    "title": "小节标题"
                  }}
                ]
              }}
            ]
          }}
        ]
        ```
        
        请注意，每级标题都应该有一个"title"字段，如果有子标题，则应包含"subtitles"数组。
        请确保JSON格式正确，可以被解析。
        """
        
        return prompt
    
    def _parse_outline_response(self, response: str) -> List[Dict]:
        """解析API响应，提取大纲结构
        
        Args:
            response: API响应文本
            
        Returns:
            List[Dict]: 解析后的大纲结构
        """
        try:
            # 查找JSON部分
            start_idx = response.find("[")
            end_idx = response.rfind("]") + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                outline = json.loads(json_str)
                return outline
            else:
                # 尝试解析整个响应
                outline = json.loads(response)
                return outline
                
        except json.JSONDecodeError as e:
            logger.error(f"解析大纲JSON失败: {str(e)}")
            logger.debug(f"API响应: {response}")
            
            # 尝试手动解析
            return self._manual_parse_outline(response)
    
    def _manual_parse_outline(self, response: str) -> List[Dict]:
        """手动解析大纲文本
        
        Args:
            response: API响应文本
            
        Returns:
            List[Dict]: 解析后的大纲结构
        """
        outline = []
        current_chapter = None
        current_section = None
        
        lines = response.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 尝试识别章节编号模式
            if line.startswith("# ") or line.startswith("1. ") or line.startswith("第一章") or line.startswith("一、"):
                # 章级标题
                title = line.split(" ", 1)[1] if " " in line else line
                current_chapter = {"title": title, "subtitles": []}
                outline.append(current_chapter)
                current_section = None
            elif line.startswith("## ") or line.startswith("1.1 ") or line.startswith("（一）"):
                # 节级标题
                if current_chapter is None:
                    current_chapter = {"title": "默认章", "subtitles": []}
                    outline.append(current_chapter)
                    
                title = line.split(" ", 1)[1] if " " in line else line
                current_section = {"title": title, "subtitles": []}
                current_chapter["subtitles"].append(current_section)
            elif line.startswith("### ") or line.startswith("1.1.1 ") or line.startswith("1）"):
                # 小节级标题
                if current_section is None:
                    if current_chapter is None:
                        current_chapter = {"title": "默认章", "subtitles": []}
                        outline.append(current_chapter)
                    current_section = {"title": "默认节", "subtitles": []}
                    current_chapter["subtitles"].append(current_section)
                    
                title = line.split(" ", 1)[1] if " " in line else line
                current_section["subtitles"].append({"title": title})
        
        # 如果没有解析出任何内容，返回默认大纲
        if not outline:
            logger.warning("手动解析大纲失败，使用默认大纲")
            return self._generate_default_outline({})
            
        return outline
    
    def _generate_default_outline(self, paper_config: Dict) -> List[Dict]:
        """生成默认大纲
        
        Args:
            paper_config: 论文类型配置
            
        Returns:
            List[Dict]: 默认大纲结构
        """
        sections = paper_config.get("sections", [
            "摘要", "引言", "研究方法", "结果", "讨论", "结论", "参考文献"
        ])
        
        outline = []
        for section in sections:
            chapter = {"title": section, "subtitles": []}
            
            # 为主要章节添加默认小节
            if section in ["研究方法", "结果", "讨论"]:
                chapter["subtitles"] = [
                    {"title": f"{section}的主要内容", "subtitles": [
                        {"title": "详细内容1"},
                        {"title": "详细内容2"}
                    ]}
                ]
                
            outline.append(chapter)
            
        logger.info("生成默认大纲")
        return outline 
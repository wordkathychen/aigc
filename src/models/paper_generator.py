from typing import Dict, List, Optional, Callable, Any
import asyncio
from .api_manager import APIManager
from src.config.settings import ARTICLE_CONFIG, EDUCATION_LEVELS, PROMPT_TEMPLATES
from src.utils.exceptions import GenerationError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PaperGenerator:
    def __init__(self, api_manager: APIManager):
        self.api = api_manager
        self.paper_type = "学术论文"  # 默认类型
        self.outline: List[Dict] = []
        self.content: Dict = {}
        
    def set_paper_type(self, paper_type: str):
        """设置论文类型"""
        if paper_type in PROMPT_TEMPLATES:
            self.paper_type = paper_type
        else:
            raise ValueError(f"不支持的论文类型: {paper_type}")

    async def generate_outline(self, title: str, keywords: List[str], 
                             education_level: str) -> List[Dict]:
        """生成论文大纲"""
        prompt = self._create_outline_prompt(title, keywords, education_level, "")
        try:
            response = await self.api.generate_content(prompt)
            self.outline = self._parse_outline(response)
            return self.outline
        except Exception as e:
            logger.error(f"大纲生成失败: {str(e)}")
            raise GenerationError(f"无法生成大纲: {str(e)}")
            
    async def generate_abstract(self, title: str, outline: List[Dict]) -> str:
        """生成摘要"""
        prompt = self._create_abstract_prompt(title, outline)
        try:
            response = await self.api.generate_content(
                prompt,
                max_tokens=ARTICLE_CONFIG['abstract_length']
            )
            return response.strip()
        except Exception as e:
            logger.error(f"摘要生成失败: {str(e)}")
            raise GenerationError(f"无法生成摘要: {str(e)}")
            
    async def generate_section(self, title: str, section: Dict, 
                             word_count: int) -> str:
        """生成章节内容"""
        prompt = self._create_section_prompt(title, section, word_count, "")
        try:
            response = await self.api.generate_content(
                prompt,
                max_tokens=word_count * 2
            )
            self.content[section['id']] = response
            return response
        except Exception as e:
            logger.error(f"章节生成失败: {str(e)}")
            raise GenerationError(f"无法生成章节内容: {str(e)}")
            
    def _create_outline_prompt(self, title: str, keywords: List[str], 
                             education_level: str, subject: str) -> str:
        """创建大纲生成提示词"""
        template = PROMPT_TEMPLATES[self.paper_type]["outline"]
        return template.format(
            title=title,
            keywords=", ".join(keywords),
            education_level=education_level,
            subject=subject
        )

    def _create_abstract_prompt(self, title: str, outline: List[Dict]) -> str:
        """创建摘要生成提示词"""
        return f"""
        请为以下论文生成摘要：
        
        标题：{title}
        大纲：{outline}
        
        要求：
        1. 控制在{ARTICLE_CONFIG['abstract_length']}字左右
        2. 包含研究背景、主要观点和意义
        3. 写成一段话，不分点
        4. 语言简洁明了
        """
    
    def _create_section_prompt(self, title: str, section: Dict, 
                             word_count: int, subject: str) -> str:
        """创建章节内容生成提示词"""
        template = PROMPT_TEMPLATES[self.paper_type]["content"]
        return template.format(
            title=title,
            section=section['title'],
            word_count=word_count,
            subject=subject
        )
    
    def _create_content_prompt(self, section: Dict, title: str, 
                             word_count: int) -> str:
        """创建内容生成提示词"""
        needs_data = section.get('needs_data') == '是'
        needs_table = section.get('needs_table') == '是'
        
        prompt = f"""
        为论文《{title}》的章节【{section['title']}】生成内容
        要求字数：{word_count}字
        
        特殊要求：
        {f'- 需要包含相关数据支持论述' if needs_data else ''}
        {f'- 需要生成数据表格' if needs_table else ''}
        
        生成要求：
        1. 符合学术规范
        2. 论述严谨
        3. 层次分明
        4. 逻辑清晰
        """
        
        return prompt
    
    def _parse_outline(self, response: str) -> List[Dict]:
        """解析大纲响应"""
        # 这里需要根据实际API返回格式进行解析
        # 示例实现
        sections = []
        try:
            lines = response.strip().split('\n')
            current_chapter = None
            
            for line in lines:
                if not line.strip():
                    continue
                    
                if line.startswith('#'):  # 一级标题
                    current_chapter = {
                        'id': len(sections),
                        'title': line.strip('# '),
                        'subsections': []
                    }
                    sections.append(current_chapter)
                elif line.startswith('##') and current_chapter:  # 二级标题
                    subsection = {
                        'id': f"{current_chapter['id']}.{len(current_chapter['subsections'])}",
                        'title': line.strip('# ')
                    }
                    current_chapter['subsections'].append(subsection)
                    
            return sections
        except Exception as e:
            logger.error(f"大纲解析失败: {str(e)}")
            raise GenerationError(f"无法解析大纲: {str(e)}")

    async def generate_full_paper_with_new_order(self, config, progress_callback=None):
        """使用新的顺序生成完整论文（标题、摘要、关键词、Abstract、keywords、正文、参考文献、致谢）
        
        Args:
            config: 论文配置
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含生成结果的字典
        """
        # 重置停止标志
        self.stop_requested = False
        
        # 创建事件循环并执行异步方法
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                self._generate_paper_with_new_order_async(config, progress_callback)
            )
            return result
        finally:
            loop.close()
            
    async def _generate_paper_with_new_order_async(self, config, progress_callback=None):
        """异步使用新顺序生成论文（标题、中文摘要、关键词、Abstract、keywords、正文、参考文献、致谢）
        
        Args:
            config: 论文配置
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含生成结果的字典
        """
        title = config.get("title", "")
        paper_type = config.get("paper_type", "学术论文")
        subject = config.get("subject", "")
        education_level = config.get("education_level", "本科")
        word_count = config.get("word_count", 6000)
        outline = config.get("outline", [])
        requirements = config.get("requirements", {})
        template = config.get("template", "通用模板")
        
        # 初始化结果和进度
        result = {"content": "", "sections": {}}
        progress = 0.0
        
        try:
            # 1. 标题生成
            title_content = f"# {title}\n\n"
            result["content"] += title_content
            result["sections"]["标题"] = title_content
            
            progress += 0.05
            if progress_callback:
                progress_callback("标题", progress, result["content"])
            
            # 检查是否请求停止
            if self.stop_requested:
                return result
                
            # 2. 中文摘要生成
            abstract_prompt = self._create_abstract_prompt(title, outline, "中文")
            abstract = await self.api.generate_content(
                abstract_prompt, 
                max_tokens=300
            )
            abstract_content = f"## 摘要\n\n{abstract}\n\n"
            result["content"] += abstract_content
            result["sections"]["摘要"] = abstract_content
            
            progress += 0.10
            if progress_callback:
                progress_callback("中文摘要", progress, result["content"])
            
            # 检查是否请求停止
            if self.stop_requested:
                return result
                
            # 3. 关键词生成
            keywords_prompt = self._create_keywords_prompt(title, abstract)
            keywords = await self.api.generate_content(
                keywords_prompt,
                max_tokens=100
            )
            keywords_content = f"**关键词**: {keywords}\n\n"
            result["content"] += keywords_content
            result["sections"]["关键词"] = keywords_content
            
            progress += 0.05
            if progress_callback:
                progress_callback("关键词", progress, result["content"])
            
            # 检查是否请求停止
            if self.stop_requested:
                return result
                
            # 4. 英文Abstract生成
            english_abstract_prompt = self._create_abstract_prompt(title, outline, "英文")
            english_abstract = await self.api.generate_content(
                english_abstract_prompt,
                max_tokens=300
            )
            english_abstract_content = f"## Abstract\n\n{english_abstract}\n\n"
            result["content"] += english_abstract_content
            result["sections"]["Abstract"] = english_abstract_content
            
            progress += 0.10
            if progress_callback:
                progress_callback("英文摘要", progress, result["content"])
            
            # 检查是否请求停止
            if self.stop_requested:
                return result
                
            # 5. 英文Keywords生成
            english_keywords_prompt = self._create_keywords_prompt(title, english_abstract, "英文")
            english_keywords = await self.api.generate_content(
                english_keywords_prompt,
                max_tokens=100
            )
            english_keywords_content = f"**Keywords**: {english_keywords}\n\n"
            result["content"] += english_keywords_content
            result["sections"]["Keywords"] = english_keywords_content
            
            progress += 0.05
            if progress_callback:
                progress_callback("英文关键词", progress, result["content"])
            
            # 检查是否请求停止
            if self.stop_requested:
                return result
                
            # 6. 正文生成 - 使用新的按最小级别标题生成方法
            # 计算正文部分的字数 (总字数的70%)
            body_word_count = int(word_count * 0.7)
            
            # 使用新的生成方法
            content = await self._generate_all_sections(
                title=title,
                outline=outline,
                total_word_count=body_word_count,
                subject=subject,
                education_level=education_level,
                requirements=requirements,
                progress_callback=progress_callback,
                base_progress=0.35,  # 前面已完成35%的进度
                section_progress=0.5 / max(len(self._extract_min_level_sections(outline)), 1)  # 正文占50%的进度
            )
            
            result["content"] += content
            progress = 0.85  # 正文完成后的进度
            
            # 检查是否请求停止
            if self.stop_requested:
                return result
                
            # 7. 参考文献生成
            ref_prompt = self._create_references_prompt(title, subject)
            references = await self.api.generate_content(
                ref_prompt,
                max_tokens=500
            )
            ref_content = f"## 参考文献\n\n{references}\n\n"
            result["content"] += ref_content
            result["sections"]["参考文献"] = ref_content
            
            progress += 0.10
            if progress_callback:
                progress_callback("参考文献", progress, result["content"])
            
            # 检查是否请求停止
            if self.stop_requested:
                return result
                
            # 8. 致谢生成
            acknowledgement_prompt = self._create_acknowledgement_prompt(title, subject)
            acknowledgement = await self.api.generate_content(
                acknowledgement_prompt,
                max_tokens=200
            )
            acknowledgement_content = f"## 致谢\n\n{acknowledgement}\n\n"
            result["content"] += acknowledgement_content
            result["sections"]["致谢"] = acknowledgement_content
            
            progress = 1.0
            if progress_callback:
                progress_callback("致谢", progress, result["content"])
            
            return result
            
        except Exception as e:
            logger.error(f"生成论文失败: {str(e)}")
            # 添加错误信息
            result["content"] += f"\n\n*生成过程中出错: {str(e)}*"
            return result
    
    def _create_abstract_prompt(self, title, outline, language="中文"):
        """创建摘要生成提示词"""
        lang_text = "英文" if language == "英文" else "中文"
        return f"""
        请为以下论文生成{lang_text}摘要：
        
        标题：{title}
        大纲：{outline}
        
        要求：
        1. 用{lang_text}撰写
        2. 控制在250-300字左右
        3. 包含研究背景、主要观点和意义
        4. 写成一段话，不分点
        5. 语言简洁明了
        6. 符合学术规范
        """
    
    def _create_keywords_prompt(self, title, abstract, language="中文"):
        """创建关键词生成提示词"""
        lang_text = "英文" if language == "英文" else "中文"
        return f"""
        根据以下论文标题和摘要，生成3-5个{lang_text}关键词：
        
        标题：{title}
        摘要：{abstract}
        
        要求：
        1. 用{lang_text}表述
        2. 准确反映文章核心主题
        3. 选取具有学术意义的词汇
        4. 关键词之间用逗号分隔
        """
    
    def _create_references_prompt(self, title, subject):
        """创建参考文献生成提示词"""
        return f"""
        请为论文《{title}》生成15个参考文献，学科领域是{subject}。
        
        要求：
        1. 遵循GB/T 7714-2015格式
        2. 包含中英文文献，以中文为主
        3. 包含期刊、专著、学位论文等不同类型
        4. 大部分为近5年内的文献
        5. 所有文献必须真实存在，不可编造
        6. 每个参考文献占一行，前面标注序号
        """
    
    def _create_acknowledgement_prompt(self, title, subject):
        """创建致谢生成提示词"""
        return f"""
        请为论文《{title}》生成致谢部分，学科领域是{subject}。
        
        要求：
        1. 简洁真诚，字数200字左右
        2. 感谢指导教师和各方支持
        3. 表达自己的成长和收获
        4. 语言得体，情感真挚
        """
    
    def _flatten_outline(self, outline):
        """将嵌套大纲展平为一维列表"""
        result = []
        if not outline:
            return result
            
        for item in outline:
            if isinstance(item, dict):
                result.append(item)
                if 'subtitles' in item:
                    result.extend(self._flatten_outline(item['subtitles']))
            else:
                result.append({"title": item})
                
        return result
        
    async def _generate_all_sections(self, title, outline, total_word_count, subject, education_level, requirements, progress_callback=None, base_progress=0.0, section_progress=0.05):
        """异步生成所有章节内容
        
        Args:
            title: 论文标题
            outline: 论文大纲
            total_word_count: 总字数
            subject: 学科
            education_level: 教育水平
            requirements: 特殊要求
            progress_callback: 进度回调
            base_progress: 基础进度
            section_progress: 每个章节的进度增量
            
        Returns:
            str: 所有章节的内容
        """
        all_content = ""
        current_progress = base_progress
        
        # 找出所有最小级别标题
        min_level_sections = self._extract_min_level_sections(outline)
        section_count = len(min_level_sections)
        
        # 计算每个章节的平均字数
        words_per_section = self._calculate_section_word_counts(min_level_sections, total_word_count)
        
        # 为每个最小级别标题生成内容
        for i, section_info in enumerate(min_level_sections):
            section_path = section_info["path"]
            section_title = section_info["title"]
            section_level = section_info["level"]
            section_word_count = words_per_section[i]
            
            # 构建完整章节标题路径
            full_title = " > ".join(section_path)
            
            # 生成章节内容
            logger.info(f"生成章节内容: {full_title}, 字数: {section_word_count}")
            
            # 构建章节提示词
            prompt = self._create_section_prompt(
                title=title,
                section=full_title,
                word_count=section_word_count,
                subject=subject,
                education_level=education_level,
                requirements=requirements
            )
            
            # 生成章节内容
            try:
                section_content = await self.api.generate_content(
                    prompt,
                    max_tokens=self._estimate_tokens(section_word_count * 2)
                )
                
                # 处理章节内容
                section_content = self._process_section_content(section_content, section_level, section_title)
                
                # 添加到总内容
                all_content += section_content + "\n\n"
                
                # 更新进度
                current_progress += section_progress
                if progress_callback:
                    progress_callback(section_title, current_progress, all_content)
                    
                # 检查是否请求停止
                if self.stop_requested:
                    break
                
            except Exception as e:
                logger.error(f"生成章节内容失败: {str(e)}")
                # 添加错误提示
                all_content += f"## {section_title}\n\n*内容生成失败: {str(e)}*\n\n"
        
        return all_content

    def _extract_min_level_sections(self, outline):
        """提取最小级别的章节
        
        Args:
            outline: 大纲
            
        Returns:
            List: 最小级别章节列表
        """
        min_level_sections = []
        max_level = 0
        
        # 首先找出最大级别
        def find_max_level(items, current_level=1):
            nonlocal max_level
            max_level = max(max_level, current_level)
            
            for item in items:
                if isinstance(item, dict) and "children" in item:
                    find_max_level(item["children"], current_level + 1)
        
        find_max_level(outline)
        
        # 然后提取最小级别的章节
        def extract_sections(items, current_path=None, current_level=1):
            if current_path is None:
                current_path = []
            
            for item in items:
                if isinstance(item, str):
                    # 如果当前级别是最大级别，添加到结果中
                    if current_level == max_level:
                        min_level_sections.append({
                            "path": current_path + [item],
                            "title": item,
                            "level": current_level
                        })
                elif isinstance(item, dict) and "title" in item and "children" in item:
                    title = item["title"]
                    children = item["children"]
                    
                    if not children and current_level == max_level:
                        # 如果没有子节点且当前级别是最大级别
                        min_level_sections.append({
                            "path": current_path + [title],
                            "title": title,
                            "level": current_level
                        })
                    elif not children:
                        # 如果没有子节点但不是最大级别，也视为最小级别
                        min_level_sections.append({
                            "path": current_path + [title],
                            "title": title,
                            "level": current_level
                        })
                    else:
                        # 递归处理子节点
                        extract_sections(children, current_path + [title], current_level + 1)
        
        extract_sections(outline)
        return min_level_sections

    def _calculate_section_word_counts(self, sections, total_word_count):
        """计算每个章节的字数
        
        Args:
            sections: 章节列表
            total_word_count: 总字数
            
        Returns:
            List: 每个章节的字数列表
        """
        section_count = len(sections)
        if section_count == 0:
            return []
        
        # 基础分配：每个章节平均分配
        base_words_per_section = total_word_count // section_count
        
        # 初始分配
        word_counts = [base_words_per_section] * section_count
        
        # 分配剩余字数
        remaining_words = total_word_count - (base_words_per_section * section_count)
        for i in range(remaining_words):
            word_counts[i % section_count] += 1
        
        # 调整特殊章节的字数
        for i, section in enumerate(sections):
            title = section["title"].lower()
            
            # 摘要和结论通常较短
            if "摘要" in title or "abstract" in title:
                word_counts[i] = min(word_counts[i], 300)
            elif "结论" in title or "conclusion" in title:
                word_counts[i] = min(word_counts[i], total_word_count // 10)
            elif "引言" in title or "introduction" in title:
                word_counts[i] = min(word_counts[i], total_word_count // 8)
        
        # 重新分配调整后剩余的字数
        adjusted_total = sum(word_counts)
        if adjusted_total < total_word_count:
            remaining = total_word_count - adjusted_total
            # 主要分配给正文部分
            main_sections = [i for i, s in enumerate(sections) 
                            if not any(kw in s["title"].lower() 
                                    for kw in ["摘要", "abstract", "结论", "conclusion", "引言", "introduction"])]
            
            if main_sections:
                words_per_main = remaining // len(main_sections)
                for i in main_sections:
                    word_counts[i] += words_per_main
                
                # 处理剩余的零头
                remaining_after = remaining - (words_per_main * len(main_sections))
                for i in range(remaining_after):
                    if i < len(main_sections):
                        word_counts[main_sections[i]] += 1
        
        return word_counts

    def _process_section_content(self, content, level, title):
        """处理章节内容，添加适当的标题标记
        
        Args:
            content: 章节内容
            level: 章节级别
            title: 章节标题
            
        Returns:
            str: 处理后的章节内容
        """
        # 移除内容中可能包含的标题
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            if line.strip().startswith('#'):
                # 检查是否与章节标题相似
                line_title = line.strip('#').strip()
                if self._is_similar_title(line_title, title):
                    continue
            filtered_lines.append(line)
        
        content = '\n'.join(filtered_lines)
        
        # 添加适当级别的标题
        header_marks = '#' * level
        return f"{header_marks} {title}\n\n{content.strip()}"

    def _is_similar_title(self, title1, title2):
        """检查两个标题是否相似
        
        Args:
            title1: 第一个标题
            title2: 第二个标题
            
        Returns:
            bool: 是否相似
        """
        # 简单的相似度检查
        title1 = title1.lower().strip()
        title2 = title2.lower().strip()
        
        # 完全匹配
        if title1 == title2:
            return True
        
        # 包含关系
        if title1 in title2 or title2 in title1:
            return True
        
        # 计算编辑距离可以进一步提高准确性
        return False

    def _estimate_tokens(self, word_count):
        """估算字数对应的token数量
        
        Args:
            word_count: 字数
            
        Returns:
            int: 估算的token数量
        """
        # 中文大约1个字对应1.5个token
        return int(word_count * 1.5)

    def _create_section_prompt(self, title, section, word_count, subject, education_level, requirements):
        """创建章节提示词
        
        Args:
            title: 论文标题
            section: 章节路径
            word_count: 字数要求
            subject: 学科
            education_level: 教育水平
            requirements: 特殊要求
            
        Returns:
            str: 提示词
        """
        prompt = f"""
        请为{education_level}论文《{title}》的章节"{section}"撰写内容。

        要求：
        1. 字数控制在{word_count}字左右
        2. 学科领域：{subject}
        3. 内容符合学术规范，逻辑清晰，论述严谨
        4. 不要包含标题，直接开始正文内容
        5. 适当引用相关研究和数据支持论点
        """
        
        # 添加特殊要求
        if requirements:
            for key, value in requirements.items():
                if value and key in ["academic_style", "professional_terms", "data_citation", "logical_structure"]:
                    if key == "academic_style" and value:
                        prompt += "\n6. 使用学术性语言，避免口语化表达"
                    elif key == "professional_terms" and value:
                        prompt += "\n7. 使用专业术语和概念"
                    elif key == "data_citation" and value:
                        prompt += "\n8. 增加数据引用和实证支持"
                    elif key == "logical_structure" and value:
                        prompt += "\n9. 确保段落间逻辑连贯，有明确的论证结构"
        
        return prompt

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List

class OutlineEditor(tk.Toplevel):
    def __init__(self, parent, outline_data: Dict, callback):
        super().__init__(parent)
        self.title("大纲编辑器")
        self.outline_data = outline_data
        self.callback = callback
        self.data_requirements = {}  # 存储需要数据支持的章节
        self.table_requirements = {}  # 存储需要表格的章节
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 大纲编辑区
        outline_frame = ttk.LabelFrame(main_frame, text="大纲内容")
        outline_frame.pack(fill='both', expand=True, pady=5)
        
        self.outline_tree = ttk.Treeview(outline_frame, columns=('data', 'table'))
        self.outline_tree.heading('#0', text='章节')
        self.outline_tree.heading('data', text='需要数据')
        self.outline_tree.heading('table', text='需要表格')
        self.outline_tree.pack(fill='both', expand=True)
        
        # 加载大纲数据
        self._load_outline(self.outline_data)
        
        # 按钮区
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="添加子节点", 
                  command=self._add_child).pack(side='left', padx=5)
        ttk.Button(button_frame, text="删除节点", 
                  command=self._delete_node).pack(side='left', padx=5)
        ttk.Button(button_frame, text="编辑节点", 
                  command=self._edit_node).pack(side='left', padx=5)
        ttk.Button(button_frame, text="确认修改", 
                  command=self._confirm_changes).pack(side='right', padx=5)
                  
    def _load_outline(self, outline_data: Dict, parent=''):
        """加载大纲数据到树形控件"""
        for section in outline_data:
            section_id = self.outline_tree.insert(
                parent, 'end', text=section['title'],
                values=('否', '否')
            )
            if 'subsections' in section:
                self._load_outline(section['subsections'], section_id)
                
    def _add_child(self):
        """添加子节点"""
        selected = self.outline_tree.selection()
        if not selected:
            parent = ''  # 根节点
        else:
            parent = selected[0]
            
        dialog = SectionDialog(self, "添加章节")
        if dialog.result:
            self.outline_tree.insert(
                parent, 'end', text=dialog.result['title'],
                values=(dialog.result['needs_data'], dialog.result['needs_table'])
            )
            
    def _delete_node(self):
        """删除节点"""
        selected = self.outline_tree.selection()
        if selected:
            self.outline_tree.delete(selected)
            
    def _edit_node(self):
        """编辑节点"""
        selected = self.outline_tree.selection()
        if not selected:
            return
            
        item = selected[0]
        current_data = {
            'title': self.outline_tree.item(item, 'text'),
            'needs_data': self.outline_tree.item(item, 'values')[0],
            'needs_table': self.outline_tree.item(item, 'values')[1]
        }
        
        dialog = SectionDialog(self, "编辑章节", current_data)
        if dialog.result:
            self.outline_tree.item(
                item, 
                text=dialog.result['title'],
                values=(dialog.result['needs_data'], dialog.result['needs_table'])
            )
            
    def _confirm_changes(self):
        """确认修改"""
        outline_data = self._get_outline_data()
        self.callback(outline_data)
        self.destroy()
        
    def _get_outline_data(self) -> Dict:
        """获取修改后的大纲数据"""
        def recursive_get(item=''):
            result = []
            children = self.outline_tree.get_children(item)
            for child in children:
                node = {
                    'title': self.outline_tree.item(child, 'text'),
                    'needs_data': self.outline_tree.item(child, 'values')[0],
                    'needs_table': self.outline_tree.item(child, 'values')[1]
                }
                
                sub_children = self.outline_tree.get_children(child)
                if sub_children:
                    node['subsections'] = recursive_get(child)
                    
                result.append(node)
            return result
            
        return recursive_get()

class SectionDialog(tk.Toplevel):
    def __init__(self, parent, title, initial_data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x200")
        self.result = None
        self.initial_data = initial_data or {
            'title': '',
            'needs_data': '否',
            'needs_table': '否'
        }
        
        self.setup_ui()
        self.transient(parent)
        self.grab_set()
        self.wait_window()
        
    def setup_ui(self):
        # 标题输入
        ttk.Label(self, text="章节标题:").pack(pady=(10, 0))
        self.title_var = tk.StringVar(value=self.initial_data['title'])
        ttk.Entry(self, textvariable=self.title_var, width=30).pack(pady=5)
        
        # 需要数据支持
        data_frame = ttk.Frame(self)
        data_frame.pack(fill='x', pady=5)
        ttk.Label(data_frame, text="需要数据支持:").pack(side='left', padx=5)
        self.data_var = tk.StringVar(value=self.initial_data['needs_data'])
        ttk.Radiobutton(data_frame, text="是", variable=self.data_var, 
                       value="是").pack(side='left')
        ttk.Radiobutton(data_frame, text="否", variable=self.data_var, 
                       value="否").pack(side='left')
        
        # 需要表格
        table_frame = ttk.Frame(self)
        table_frame.pack(fill='x', pady=5)
        ttk.Label(table_frame, text="需要表格:").pack(side='left', padx=5)
        self.table_var = tk.StringVar(value=self.initial_data['needs_table'])
        ttk.Radiobutton(table_frame, text="是", variable=self.table_var, 
                       value="是").pack(side='left')
        ttk.Radiobutton(table_frame, text="否", variable=self.table_var, 
                       value="否").pack(side='left')
        
        # 确认按钮
        ttk.Button(self, text="确认", command=self._confirm).pack(pady=10)
        
    def _confirm(self):
        """确认输入"""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("错误", "章节标题不能为空")
            return
            
        self.result = {
            'title': title,
            'needs_data': self.data_var.get(),
            'needs_table': self.table_var.get()
        }
        self.destroy()

class PaperGeneratorModel:
    """论文生成模型类"""
    
    def __init__(self):
        """初始化论文生成模型"""
        self.api = APIManager()
        self.stop_requested = False
        self.paper_content = ""
        
    def stop_generation(self):
        """停止生成过程"""
        self.stop_requested = True        
    def generate_full_paper(self, config, progress_callback=None):
        """生成完整论文
        
        Args:
            config: 论文配置信息
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含生成结果的字典
        """
        # 重置停止标志
        self.stop_requested = False
        
        # 创建事件循环并执行异步方法
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                self._generate_paper_async(config, progress_callback)
            )
            return result
        finally:
            loop.close()
    
    async def _generate_paper_async(self, config, progress_callback=None):
        """异步生成论文内容"""
        title = config.get("title", "")
        paper_type = config.get("paper_type", "学术论文")
        subject = config.get("subject", "")
        education_level = config.get("education_level", "本科")
        word_count = config.get("word_count", 6000)
        outline = config.get("outline", [])
        requirements = config.get("requirements", {})
        
        # 初始化结果和进度
        result = {"content": "", "sections": {}}
        progress = 0.0
        
        try:
            # 生成标题和摘要
            title_content = f"# {title}\n\n"
            result["content"] += title_content
            result["sections"]["标题"] = title_content
            
            progress += 0.05
            if progress_callback:
                progress_callback("标题", progress, result["content"])
            
            # 检查是否请求停止
            if self.stop_requested:
                return result
            
            # 生成摘要
            abstract_prompt = f"""
            请为论文《{title}》生成摘要，学科领域是{subject}，教育级别是{education_level}。
            
            大纲:
            {outline}
            
            要求:
            1. 控制在250字左右
            2. 包含研究背景、主要方法和主要结论
            3. 语言简洁明了
            4. 符合学术规范
            """
            
            abstract = await self.api.generate_content(
                abstract_prompt,
                max_tokens=300
            )
            
            abstract_content = f"## 摘要\n\n{abstract}\n\n"
            result["content"] += abstract_content
            result["sections"]["摘要"] = abstract_content
            
            progress += 0.10
            if progress_callback:
                progress_callback("摘要", progress, result["content"])
            
            # 检查是否请求停止
            if self.stop_requested:
                return result
            
            # 生成正文
            flat_outline = self._flatten_outline(outline)
            total_sections = len(flat_outline)
            section_progress = 0.8 / total_sections if total_sections > 0 else 0
            
            # 为每个章节分配字数
            remaining_words = word_count
            sections_weights = []
            
            for section in flat_outline:
                # 标题和摘要占比较小
                if section.get('title', '').lower() in ['摘要', 'abstract', '参考文献']:
                    weight = 0.05
                # 引言和结论占比中等
                elif section.get('title', '').lower() in ['引言', '绪论', '前言', '结论', '总结']:
                    weight = 0.10
                # 其他章节平均分配
                else:
                    weight = 0.15
                    
                sections_weights.append(weight)
                
            # 规范化权重
            total_weight = sum(sections_weights)
            sections_weights = [w / total_weight for w in sections_weights]
            
            # 分配字数
            sections_words = [int(w * word_count) for w in sections_weights]
            
            # 生成各章节内容
            for i, (section, words) in enumerate(zip(flat_outline, sections_words)):
                # 检查是否请求停止
                if self.stop_requested:
                    return result
                
                section_title = section.get('title', f'章节{i+1}')
                
                # 生成章节内容
                section_prompt = f"""
                为{education_level}论文《{title}》的"{section_title}"章节生成内容:
                
                字数要求: {words}字
                学科领域: {subject}
                论文类型: {paper_type}
                
                要求:
                1. 符合学术规范，论证严谨
                2. 内容充实，结构清晰
                3. 使用恰当的专业术语
                4. 语言流畅，避免AI痕迹
                """
                
                section_content = await self.api.generate_content(
                    section_prompt,
                    max_tokens=words * 2
                )
                
                # 根据章节级别确定标题格式
                heading_level = '#' * (2 + section.get('level', 0))
                formatted_section = f"{heading_level} {section_title}\n\n{section_content}\n\n"
                
                result["content"] += formatted_section
                result["sections"][section_title] = formatted_section
                
                # 更新进度
                progress = 0.15 + section_progress * (i + 1)
                if progress_callback:
                    progress_callback(section_title, progress, result["content"])
            
            # 检查是否请求停止
            if self.stop_requested:
                return result
            
            # 生成参考文献
            refs_prompt = f"""
            为论文《{title}》生成10个参考文献:
            
            学科: {subject}
            教育级别: {education_level}
            
            要求:
            1. 遵循GB/T 7714-2015引用格式
            2. 大部分为近五年内的文献
            3. 包含中英文文献
            4. 文献必须真实存在
            """
            
            references = await self.api.generate_content(
                refs_prompt,
                max_tokens=500
            )
            
            ref_content = f"## 参考文献\n\n{references}\n\n"
            result["content"] += ref_content
            result["sections"]["参考文献"] = ref_content
            
            progress = 1.0
            if progress_callback:
                progress_callback("完成", progress, result["content"])
            
            return result
            
        except Exception as e:
            logger.error(f"论文生成失败: {str(e)}")
            if progress_callback:
                progress_callback("生成失败", progress, result["content"])
            raise GenerationError(f"论文生成失败: {str(e)}")
    
    def _flatten_outline(self, outline):
        """将嵌套大纲展平为一维列表"""
        result = []
        
        if not outline:
            return result
            
        for item in outline:
            if isinstance(item, dict):
                result.append(item)
                if 'subtitles' in item:
                    result.extend(self._flatten_outline(item['subtitles']))
            else:
                result.append({"title": item})
                
        return result
    
    def generate_full_paper_with_new_order(self, config, progress_callback=None):
        """使用新的顺序生成完整论文（标题、摘要、关键词、Abstract、keywords、正文、参考文献、致谢）
        
        Args:
            config: 论文配置
            progress_callback: 进度回调函数
            
        Returns:
            Dict: 包含生成结果的字典
        """
        # 重置停止标志
        self.stop_requested = False
        
        # 创建事件循环并执行异步方法
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                self._generate_paper_with_new_order_async(config, progress_callback)
            )
            return result
        finally:
            loop.close()

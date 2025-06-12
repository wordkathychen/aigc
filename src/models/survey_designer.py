from typing import List, Dict, Any, Optional
import json
import random
import pandas as pd
import matplotlib.pyplot as plt
from utils.exceptions import SurveyError
from utils.logger import setup_logger
from utils.api_manager import APIManager
import os
import re
import numpy as np
from src.models.deepseek import DeepseekAPI
from src.utils.file_handler import FileHandler

logger = setup_logger(__name__)

class SurveyGenerator:
    """问卷生成器"""
    
    def __init__(self):
        """初始化问卷生成器"""
        self.api = DeepseekAPI()
        self.file_handler = FileHandler()
        logger.info("初始化问卷生成器")
    
    def generate_survey_from_text(self, title: str, content: str) -> str:
        """根据文本内容生成完整问卷
        
        Args:
            title: 问卷标题
            content: 问卷内容描述或现有问题
            
        Returns:
            str: 格式化的问卷内容
        """
        # 判断content是否已经是问卷格式
        if self._is_survey_format(content):
            # 内容已经是问卷格式，进行标准化和美化
            return self._format_survey(title, content)
        else:
            # 内容是描述性文本，需要生成问卷
            return self._generate_survey(title, content)
    
    def generate_survey_from_data(self, title: str, data_file: str) -> str:
        """根据数据文件反向生成问卷
        
        Args:
            title: 问卷标题
            data_file: 数据文件路径（Excel或CSV）
            
        Returns:
            str: 格式化的问卷内容
        """
        try:
            # 读取数据文件
            if data_file.endswith('.csv'):
                df = pd.read_csv(data_file)
            else:
                df = pd.read_excel(data_file)
            
            # 获取列名作为问题
            columns = df.columns.tolist()
            
            # 分析数据类型，推断问题类型
            survey_structure = self._analyze_data_structure(df)
            
            # 生成问卷
            return self._generate_survey_from_structure(title, survey_structure)
            
        except Exception as e:
            logger.error(f"从数据生成问卷失败: {str(e)}")
            raise
    
    def _is_survey_format(self, content: str) -> bool:
        """判断内容是否已经是问卷格式
        
        Args:
            content: 文本内容
            
        Returns:
            bool: 是否为问卷格式
        """
        # 问卷格式的特征：包含问题编号、选项标记等
        question_pattern = r'\d+[\s.、）\)]+.+[\?？]'
        option_pattern = r'[A-Za-z][\s.、）\)]+.+'
        
        # 检查是否包含问题和选项格式
        has_questions = bool(re.search(question_pattern, content))
        has_options = bool(re.search(option_pattern, content))
        
        return has_questions and has_options
    
    def _format_survey(self, title: str, content: str) -> str:
        """格式化问卷内容
        
        Args:
            title: 问卷标题
            content: 问卷内容
            
        Returns:
            str: 格式化后的问卷
        """
        # 构建提示词
        prompt = f"""
        请将以下问卷内容进行标准化和美化排版：
        
        问卷标题：{title}
        
        问卷内容：
        {content}
        
        要求：
        1. 保持原有问题和选项
        2. 标准化问题编号格式，使用"1."、"2."等
        3. 标准化选项标记，使用"A."、"B."等
        4. 区分单选题、多选题、填空题、量表题和开放题
        5. 优化排版，使问卷结构清晰
        6. 对每道题目进行适当的说明，使问卷更专业
        
        请返回美化后的完整问卷内容。
        """
        
        # 调用API进行格式化
        try:
            response = self.api.generate_content(prompt, "格式化问卷")
            logger.info("问卷格式化成功")
            
            # 添加问卷标题
            formatted = f"# {title}\n\n{response}"
            return formatted
            
        except Exception as e:
            logger.error(f"问卷格式化失败: {str(e)}")
            # 简单处理，添加标题后返回原内容
            return f"# {title}\n\n{content}"
    
    def _generate_survey(self, title: str, description: str) -> str:
        """根据描述生成问卷
        
        Args:
            title: 问卷标题
            description: 问卷描述
            
        Returns:
            str: 生成的问卷内容
        """
        # 构建提示词
        prompt = f"""
        请根据以下要求生成一份完整的调查问卷：
        
        问卷标题：{title}
        问卷描述/要求：
        {description}
        
        要求：
        1. 生成的问卷应包含多种题型，包括单选题、多选题、填空题、量表题和开放题
        2. 问题应与问卷主题紧密相关，逻辑性强
        3. 每道题应有明确的题型标注
        4. 选项应合理、全面，涵盖可能的回答
        5. 问卷整体结构应包含基本信息收集、核心问题和结束语
        6. 使用标准的问卷格式，问题编号清晰
        7. 整体问卷长度适中，不宜过长或过短
        
        请返回完整的问卷内容，使用清晰的格式。
        """
        
        # 调用API生成问卷
        try:
            response = self.api.generate_content(prompt, "生成问卷")
            logger.info("问卷生成成功")
            
            # 添加问卷标题
            generated = f"# {title}\n\n{response}"
            return generated
            
        except Exception as e:
            logger.error(f"问卷生成失败: {str(e)}")
            # 返回简单的默认问卷
            return f"""
            # {title}
            
            ## 基本信息
            
            1. 您的性别是？
            A. 男
            B. 女
            
            2. 您的年龄段是？
            A. 18岁以下
            B. 18-25岁
            C. 26-35岁
            D. 36-45岁
            E. 46岁以上
            
            3. 您的最高学历是？
            A. 高中及以下
            B. 大专
            C. 本科
            D. 硕士
            E. 博士及以上
            
            ## 问卷正文
            
            4. 这是一个示例问题？
            A. 选项1
            B. 选项2
            C. 选项3
            
            5. 您对此问卷的建议？（开放题）
            __________
            
            感谢您的参与！
            """.strip()
    
    def _analyze_data_structure(self, df: pd.DataFrame) -> List[Dict]:
        """分析数据结构，推断问题类型
        
        Args:
            df: 数据框
            
        Returns:
            List[Dict]: 问题结构列表
        """
        structure = []
        
        for col in df.columns:
            # 跳过ID列
            if col.lower() in ['id', 'index', 'no.', 'no', '编号']:
                continue
                
            # 分析列数据
            data = df[col].dropna()
            if len(data) == 0:
                continue
                
            # 判断数据类型和取值特征
            unique_values = data.unique()
            unique_count = len(unique_values)
            
            # 推断问题类型
            question_type = "单选题"  # 默认为单选题
            options = []
            
            if unique_count <= 10:
                # 可能是单选题或多选题
                if any(',' in str(val) or ';' in str(val) or '、' in str(val) for val in unique_values):
                    question_type = "多选题"
                    # 提取所有选项
                    all_options = []
                    for val in unique_values:
                        options_list = re.split(r'[,;、]', str(val))
                        all_options.extend([opt.strip() for opt in options_list])
                    options = list(set(all_options))
                else:
                    question_type = "单选题"
                    options = [str(val) for val in unique_values]
            elif all(isinstance(val, (int, float)) for val in unique_values):
                if min(unique_values) >= 1 and max(unique_values) <= 10:
                    # 可能是量表题
                    question_type = "量表题"
                    options = list(range(int(min(unique_values)), int(max(unique_values))+1))
                else:
                    # 可能是填空题（数值）
                    question_type = "填空题"
            else:
                # 长文本，可能是开放题
                if data.apply(lambda x: len(str(x))).mean() > 20:
                    question_type = "开放题"
                else:
                    question_type = "填空题"
            
            # 构建问题结构
            structure.append({
                "question": col,
                "type": question_type,
                "options": options if question_type in ["单选题", "多选题", "量表题"] else []
            })
        
        return structure
    
    def _generate_survey_from_structure(self, title: str, structure: List[Dict]) -> str:
        """根据结构生成问卷
        
        Args:
            title: 问卷标题
            structure: 问题结构列表
            
        Returns:
            str: 生成的问卷内容
        """
        # 构建提示词
        structure_json = json.dumps(structure, ensure_ascii=False, indent=2)
        
        prompt = f"""
        请根据以下结构生成一份完整的调查问卷：
        
        问卷标题：{title}
        
        问卷结构：
        {structure_json}
        
        要求：
        1. 根据提供的结构生成问卷，保持问题类型和选项
        2. 美化问题表述，使其更专业、更符合问卷设计规范
        3. 添加必要的分组标题，如"基本信息"、"核心问题"等
        4. 使用标准的问卷格式，问题编号清晰
        5. 为问卷添加简短的介绍和结束语
        
        请返回完整的问卷内容，使用清晰的格式。
        """
        
        # 调用API生成问卷
        try:
            response = self.api.generate_content(prompt, "根据结构生成问卷")
            logger.info("根据结构生成问卷成功")
            
            # 添加问卷标题
            generated = f"# {title}\n\n{response}"
            return generated
            
        except Exception as e:
            logger.error(f"根据结构生成问卷失败: {str(e)}")
            
            # 手动构建问卷
            survey = f"# {title}\n\n"
            survey += "## 问卷说明\n\n"
            survey += "感谢您参与本次调查。请根据实际情况填写以下问题，您的回答将对我们的研究有重要帮助。\n\n"
            survey += "## 问卷内容\n\n"
            
            for i, item in enumerate(structure, 1):
                question = item["question"]
                q_type = item["type"]
                options = item["options"]
                
                survey += f"{i}. {question}"
                if q_type == "多选题":
                    survey += "（多选）"
                survey += "\n"
                
                if q_type in ["单选题", "多选题"]:
                    for j, opt in enumerate(options):
                        opt_label = chr(65 + j)  # A, B, C...
                        survey += f"{opt_label}. {opt}\n"
                elif q_type == "量表题":
                    scale = " ".join(str(o) for o in options)
                    survey += f"{scale}\n"
                elif q_type in ["填空题", "开放题"]:
                    survey += "__________\n"
                
                survey += "\n"
            
            survey += "## 问卷结束\n\n"
            survey += "感谢您完成本次问卷调查！您的反馈对我们非常重要。\n"
            
            return survey

class SurveyDataGenerator:
    """问卷数据生成器"""
    
    def __init__(self):
        """初始化问卷数据生成器"""
        self.api = DeepseekAPI()
        self.file_handler = FileHandler()
        logger.info("初始化问卷数据生成器")
    
    def generate_data_from_text(self, title: str, content: str, count: int = 100, bias: str = "随机") -> pd.DataFrame:
        """根据问卷文本生成数据
        
        Args:
            title: 问卷标题
            content: 问卷内容
            count: 生成数据条数
            bias: 数据倾向（随机、积极、中立、消极）
            
        Returns:
            pd.DataFrame: 生成的数据
        """
        # 解析问卷结构
        questions = self._parse_survey(content)
        
        # 调用API生成数据
        return self._generate_data(title, questions, count, bias)
    
    def generate_data_from_file(self, file_path: str, count: int = 100, bias: str = "随机") -> pd.DataFrame:
        """根据问卷文件生成数据
        
        Args:
            file_path: 问卷文件路径
            count: 生成数据条数
            bias: 数据倾向（随机、积极、中立、消极）
            
        Returns:
            pd.DataFrame: 生成的数据
        """
        try:
            # 读取问卷文件
            content = self.file_handler.read_file(file_path)
            
            # 提取标题（假设第一行是标题）
            lines = content.split('\n')
            title = lines[0].strip('#').strip() if lines else "问卷调查"
            
            # 生成数据
            return self.generate_data_from_text(title, content, count, bias)
            
        except Exception as e:
            logger.error(f"从文件生成问卷数据失败: {str(e)}")
            raise
    
    def _parse_survey(self, content: str) -> List[Dict]:
        """解析问卷内容，提取问题和选项
        
        Args:
            content: 问卷内容
            
        Returns:
            List[Dict]: 问题结构列表
        """
        questions = []
        current_question = None
        
        # 使用正则表达式匹配问题和选项
        question_pattern = r'^\s*(\d+)[\s.、）\)]+(.+?)(\（多选\）|\（单选\）|\（填空\）|\（开放题\）)?[\?？]?\s*$'
        option_pattern = r'^\s*([A-Za-z])[\s.、）\)]+(.+)\s*$'
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # 匹配问题
            question_match = re.match(question_pattern, line)
            if question_match:
                # 保存上一个问题
                if current_question:
                    questions.append(current_question)
                
                # 提取问题编号、内容和类型
                q_num, q_text, q_type_hint = question_match.groups()
                
                # 确定问题类型
                q_type = "单选题"  # 默认为单选题
                if q_type_hint:
                    if "多选" in q_type_hint:
                        q_type = "多选题"
                    elif "填空" in q_type_hint:
                        q_type = "填空题"
                    elif "开放" in q_type_hint:
                        q_type = "开放题"
                
                current_question = {
                    "number": int(q_num),
                    "text": q_text.strip(),
                    "type": q_type,
                    "options": []
                }
                continue
            
            # 匹配选项
            option_match = re.match(option_pattern, line)
            if option_match and current_question:
                opt_label, opt_text = option_match.groups()
                current_question["options"].append({
                    "label": opt_label,
                    "text": opt_text.strip()
                })
                continue
            
            # 检查是否为量表题
            if current_question and re.match(r'^\s*\d+(\s+\d+)*\s*$', line):
                current_question["type"] = "量表题"
                scale_values = [int(val) for val in line.split() if val.isdigit()]
                current_question["options"] = [
                    {"label": str(val), "text": str(val)} for val in scale_values
                ]
                continue
        
        # 添加最后一个问题
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def _generate_data(self, title: str, questions: List[Dict], count: int, bias: str) -> pd.DataFrame:
        """生成问卷数据
        
        Args:
            title: 问卷标题
            questions: 问题结构列表
            count: 生成数据条数
            bias: 数据倾向（随机、积极、中立、消极）
            
        Returns:
            pd.DataFrame: 生成的数据
        """
        # 小样本量直接生成，大样本量使用模拟生成
        if count <= 20:
            # 使用API生成真实数据
            return self._generate_data_with_api(title, questions, count, bias)
        else:
            # 使用API生成少量真实数据，然后模拟扩展
            sample_data = self._generate_data_with_api(title, questions, 20, bias)
            return self._expand_data(sample_data, count)
    
    def _generate_data_with_api(self, title: str, questions: List[Dict], count: int, bias: str) -> pd.DataFrame:
        """使用API生成问卷数据
        
        Args:
            title: 问卷标题
            questions: 问题结构列表
            count: 生成数据条数
            bias: 数据倾向（随机、积极、中立、消极）
            
        Returns:
            pd.DataFrame: 生成的数据
        """
        # 构建问卷结构JSON
        questions_json = json.dumps(questions, ensure_ascii=False, indent=2)
        
        # 构建提示词
        prompt = f"""
        请生成{count}条问卷数据，问卷结构如下：
        
        问卷标题：{title}
        数据倾向：{bias}（随机/积极/中立/消极）
        
        问卷结构：
        {questions_json}
        
        要求：
        1. 生成的数据应合理、多样化，符合真实调查场景
        2. 不同问题之间的回答应保持一致性和逻辑性
        3. 对于单选题，回答应为选项标签（如A、B、C）
        4. 对于多选题，回答应为选项标签组合（如A,C,D）
        5. 对于填空题和开放题，生成合理的文本回答
        6. 对于量表题，回答应为量表数值
        7. 数据倾向为"{bias}"，数据分布应符合此倾向
        
        请以JSON数组格式返回数据，每条数据包含所有问题的回答，格式如下：
        ```json
        [
          {{
            "问题1": "回答1",
            "问题2": "回答2",
            ...
          }},
          ...
        ]
        ```
        
        请确保JSON格式正确，可以被解析。
        """
        
        # 调用API生成数据
        try:
            response = self.api.generate_content(prompt, "生成问卷数据")
            logger.info(f"问卷数据生成成功，数量: {count}，倾向: {bias}")
            
            # 解析JSON
            # 提取JSON部分
            json_pattern = r'\[\s*\{.*\}\s*\]'
            json_match = re.search(json_pattern, response, re.DOTALL)
            
            if json_match:
                json_text = json_match.group(0)
                data = json.loads(json_text)
            else:
                # 尝试直接解析
                data = json.loads(response)
            
            # 转换为DataFrame
            df = pd.DataFrame(data)
            return df
            
        except Exception as e:
            logger.error(f"问卷数据生成失败: {str(e)}")
            
            # 手动生成简单数据
            data = []
            for _ in range(count):
                entry = {}
                for q in questions:
                    q_text = q["text"]
                    q_type = q["type"]
                    options = q["options"]
                    
                    if q_type == "单选题" and options:
                        entry[q_text] = random.choice([opt["label"] for opt in options])
                    elif q_type == "多选题" and options:
                        # 随机选择1-3个选项
                        num_choices = random.randint(1, min(3, len(options)))
                        selected = random.sample([opt["label"] for opt in options], num_choices)
                        entry[q_text] = ",".join(selected)
                    elif q_type == "量表题" and options:
                        entry[q_text] = random.choice([opt["label"] for opt in options])
                    elif q_type == "填空题":
                        entry[q_text] = "示例回答"
                    elif q_type == "开放题":
                        entry[q_text] = "这是一个示例的开放式问题回答。"
                
                data.append(entry)
            
            return pd.DataFrame(data)
    
    def _expand_data(self, sample_data: pd.DataFrame, target_count: int) -> pd.DataFrame:
        """扩展数据集
        
        Args:
            sample_data: 样本数据
            target_count: 目标数据量
            
        Returns:
            pd.DataFrame: 扩展后的数据
        """
        # 分析每列的数据类型和可能值
        column_types = {}
        column_values = {}
        
        for col in sample_data.columns:
            values = sample_data[col].dropna().unique()
            
            # 判断列类型
            if all(',' in str(val) for val in values):
                column_types[col] = "多选题"
                # 收集所有可能的选项
                all_options = set()
                for val in values:
                    options = str(val).split(',')
                    all_options.update(options)
                column_values[col] = list(all_options)
            elif all(len(str(val)) <= 2 for val in values):
                column_types[col] = "单选题"
                column_values[col] = values
            elif all(str(val).isdigit() and int(val) <= 10 for val in values if str(val).isdigit()):
                column_types[col] = "量表题"
                column_values[col] = values
            else:
                column_types[col] = "文本题"
                column_values[col] = values
        
        # 生成新数据
        new_data = []
        for _ in range(target_count - len(sample_data)):
            entry = {}
            
            for col in sample_data.columns:
                col_type = column_types[col]
                
                if col_type == "多选题":
                    # 随机选择1-3个选项
                    all_options = column_values[col]
                    num_choices = random.randint(1, min(3, len(all_options)))
                    selected = random.sample(all_options, num_choices)
                    entry[col] = ",".join(selected)
                elif col_type in ["单选题", "量表题"]:
                    # 随机选择一个值
                    entry[col] = random.choice(column_values[col])
                else:
                    # 文本题，随机选择一个样本值
                    entry[col] = random.choice(column_values[col])
            
            new_data.append(entry)
        
        # 合并原始样本和新生成的数据
        expanded_data = pd.concat([sample_data, pd.DataFrame(new_data)], ignore_index=True)
        return expanded_data

class SurveyDesigner:
    def __init__(self, api_manager: APIManager):
        self.api = api_manager
        self.question_types = {
            'single_choice': '单选题',
            'multiple_choice': '多选题',
            'scale': '量表题',
            'open_ended': '开放题',
            'matrix': '矩阵量表题'
        }
    
    def generate_questionnaire(self, 
                             title: str,
                             topics: List[str],
                             num_questions: int = 20) -> Dict[str, Any]:
        """生成问卷"""
        try:
            questions = []
            section_count = len(topics)
            questions_per_section = num_questions // section_count
            
            for topic in topics:
                section_questions = self._generate_section_questions(
                    topic, 
                    questions_per_section
                )
                questions.extend(section_questions)
            
            return {
                'title': title,
                'introduction': self._generate_introduction(title, topics),
                'questions': questions,
                'demographic_questions': self._generate_demographic_questions()
            }
        except Exception as e:
            logger.error(f"问卷生成失败: {str(e)}")
            raise SurveyError(f"无法生成问卷: {str(e)}")
    
    def generate_dummy_data(self, 
                          questionnaire: Dict[str, Any],
                          num_responses: int = 100) -> List[Dict]:
        """生成虚拟问卷数据"""
        try:
            responses = []
            for _ in range(num_responses):
                response = {}
                for question in questionnaire['questions']:
                    response[question['id']] = self._generate_random_answer(question)
                responses.append(response)
            return responses
        except Exception as e:
            logger.error(f"生成虚拟数据失败: {str(e)}")
            raise SurveyError(f"无法生成虚拟数据: {str(e)}")
    
    def export_to_wenjuanxing(self, questionnaire: Dict[str, Any]) -> str:
        """导出为问卷星格式"""
        try:
            # 转换为问卷星支持的格式
            wjx_format = {
                'title': questionnaire['title'],
                'description': questionnaire['introduction'],
                'questions': []
            }
            
            for q in questionnaire['questions']:
                wjx_q = self._convert_to_wjx_format(q)
                wjx_format['questions'].append(wjx_q)
            
            return json.dumps(wjx_format, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"导出问卷失败: {str(e)}")
            raise SurveyError(f"无法导出问卷: {str(e)}")
    
    def generate_from_data(self, data: pd.DataFrame, target_variable: str, 
                          survey_type: str) -> Dict:
        """从数据反向生成问卷"""
        prompt = self._create_data_based_prompt(data, target_variable, survey_type)
        try:
            response = self.api.generate_text(prompt)
            return self._parse_survey_response(response)
        except Exception as e:
            logger.error(f"生成问卷失败: {str(e)}")
            raise

    def generate_new_survey(self, topic: str, target_audience: str,
                          survey_type: str, question_count: int) -> Dict:
        """直接生成新问卷"""
        prompt = self._create_new_survey_prompt(
            topic, target_audience, survey_type, question_count
        )
        try:
            response = self.api.generate_text(prompt)
            return self._parse_survey_response(response)
        except Exception as e:
            logger.error(f"生成问卷失败: {str(e)}")
            raise

    def _create_data_based_prompt(self, data: pd.DataFrame, 
                                target_variable: str,
                                survey_type: str) -> str:
        """创建基于数据的问卷生成提示词"""
        variables = data.columns.tolist()
        prompt = f"""
        基于以下数据变量设计一份{survey_type}问卷：
        目标变量：{target_variable}
        相关变量：{', '.join(variables)}
        
        要求：
        1. 问题要覆盖所有相关变量
        2. 问题类型包含单选、多选和量表
        3. 确保问题逻辑合理
        4. 生成15-20个问题
        """
        return prompt

    def _create_new_survey_prompt(self, topic: str, target_audience: str,
                                survey_type: str, question_count: int) -> str:
        """创建新问卷生成提示词"""
        prompt = f"""
        请设计一份关于{topic}的{survey_type}问卷：
        目标受众：{target_audience}
        问题数量：{question_count}
        
        要求：
        1. 问题类型多样化
        2. 符合目标受众特点
        3. 确保问题逻辑性
        4. 适当添加填空题
        """
        return prompt

    def _parse_survey_response(self, response: str) -> Dict:
        """解析API返回的问卷内容"""
        # 实现解析逻辑
        return {
            "questions": [],
            "metadata": {}
        }

    def _generate_section_questions(self, topic: str, num_questions: int) -> List[Dict]:
        """生成特定主题的问题"""
        questions = []
        question_types = list(self.question_types.keys())
        
        for i in range(num_questions):
            q_type = random.choice(question_types)
            question = {
                'id': f"{topic}_{i+1}",
                'type': q_type,
                'topic': topic,
                'content': self._generate_question_content(topic, q_type),
                'options': self._generate_options(q_type) if q_type != 'open_ended' else None,
                'required': True
            }
            questions.append(question)
        
        return questions
    
    def _generate_question_content(self, topic: str, q_type: str) -> str:
        """根据主题和类型生成问题内容"""
        templates = {
            'single_choice': [
                f"您对{topic}的态度是？",
                f"您认为{topic}的重要程度如何？",
                f"您是否同意关于{topic}的观点？"
            ],
            'multiple_choice': [
                f"以下哪些因素影响了{topic}？",
                f"在{topic}方面，您考虑的主要因素有哪些？",
                f"关于{topic}，您认为需要改进的方面有哪些？"
            ],
            'scale': [
                f"请对{topic}的满意度进行评分",
                f"您对{topic}的认可程度是？",
                f"请评价{topic}的实用性"
            ],
            'matrix': [
                f"请评价{topic}的以下几个方面",
                f"对于{topic}的各项指标，您的评价是？",
                f"请对{topic}的不同维度进行打分"
            ]
        }
        
        return random.choice(templates.get(q_type, [f"请描述您对{topic}的看法"]))
    
    def _generate_options(self, q_type: str) -> List[str]:
        """生成选项"""
        options = {
            'single_choice': [
                ['非常同意', '同意', '一般', '不同意', '非常不同意'],
                ['很重要', '重要', '一般', '不重要', '很不重要'],
                ['是', '否', '不确定']
            ],
            'multiple_choice': [
                ['质量因素', '价格因素', '服务因素', '使用体验', '其他'],
                ['技术水平', '管理效率', '团队协作', '创新能力', '市场反应'],
                ['制度完善', '流程优化', '人员培训', '资源配置', '考核机制']
            ],
            'scale': [
                [str(i) for i in range(1, 11)],  # 1-10分
                ['很不满意', '不满意', '一般', '满意', '很满意']
            ],
            'matrix': [
                ['非常好', '较好', '一般', '较差', '非常差']
            ]
        }
        
        return random.choice(options.get(q_type, []))

class SurveyAnalyzer:
    def __init__(self, survey_data: List[Dict], questionnaire: Dict):
        self.data = pd.DataFrame(survey_data)
        self.questionnaire = questionnaire
        
    def basic_analysis(self) -> Dict[str, Any]:
        """基础统计分析"""
        results = {}
        
        for question in self.questionnaire['questions']:
            q_id = question['id']
            if question['type'] in ['single_choice', 'multiple_choice']:
                results[q_id] = {
                    'frequency': self.data[q_id].value_counts(),
                    'percentage': self.data[q_id].value_counts(normalize=True) * 100
                }
            elif question['type'] == 'scale':
                results[q_id] = {
                    'mean': self.data[q_id].mean(),
                    'std': self.data[q_id].std(),
                    'median': self.data[q_id].median()
                }
                
        return results
    
    def generate_charts(self, output_dir: str):
        """生成分析图表"""
        for question in self.questionnaire['questions']:
            q_id = question['id']
            
            if question['type'] in ['single_choice', 'multiple_choice']:
                plt.figure(figsize=(10, 6))
                self.data[q_id].value_counts().plot(kind='bar')
                plt.title(question['content'])
                plt.tight_layout()
                plt.savefig(f"{output_dir}/{q_id}_distribution.png")
                plt.close()
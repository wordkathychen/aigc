"""
提示词模板管理模块
用于管理和存储各种类型的提示词模板
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.web import db

class PromptTemplate(db.Model):
    """提示词模板模型"""
    
    __tablename__ = 'prompt_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    template_type = db.Column(db.String(50), nullable=False)  # 模板类型：论文、批注、摘要等
    content = db.Column(db.Text, nullable=False)  # 模板内容
    variables = db.Column(db.Text, nullable=True)  # 变量列表，JSON格式
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<PromptTemplate {self.name}>'
    
    @staticmethod
    def get_template_by_name(name):
        """根据名称获取模板"""
        return PromptTemplate.query.filter_by(name=name, is_active=True).first()
    
    @staticmethod
    def get_templates_by_type(template_type):
        """根据类型获取模板列表"""
        return PromptTemplate.query.filter_by(template_type=template_type, is_active=True).all()
    
    @staticmethod
    def get_all_active_templates():
        """获取所有启用的模板"""
        return PromptTemplate.query.filter_by(is_active=True).all()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'template_type': self.template_type,
            'content': self.content,
            'variables': self.variables,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# 预定义模板类型
TEMPLATE_TYPES = [
    'paper_abstract',      # 论文摘要
    'paper_introduction',  # 论文引言
    'paper_section',       # 论文章节
    'paper_conclusion',    # 论文结论
    'paper_references',    # 论文参考文献
    'annotation',          # 批注处理
    'text_generation',     # 文本生成
    'survey',              # 问卷设计
    'ppt',                 # PPT生成
    'custom'               # 自定义
]

def init_default_templates():
    """初始化默认提示词模板"""
    default_templates = [
        {
            'name': '论文摘要模板',
            'description': '用于生成论文摘要的提示词模板',
            'template_type': 'paper_abstract',
            'content': '''请为{education_level}论文《{title}》生成一篇{language}摘要。

要求：
1. 字数控制在{word_count}字左右
2. 学科领域：{subject}
3. 清晰概述论文的研究目的、方法、结果和结论
4. 语言精炼、准确，符合学术写作规范
5. 突出论文的创新点和研究价值''',
            'variables': '{"education_level":"教育水平","title":"论文标题","language":"语言","word_count":"字数","subject":"学科"}'
        },
        {
            'name': '论文章节模板',
            'description': '用于生成论文章节内容的提示词模板',
            'template_type': 'paper_section',
            'content': '''请为{education_level}论文《{title}》的章节"{section}"撰写内容。

要求：
1. 字数控制在{word_count}字左右
2. 学科领域：{subject}
3. 内容符合学术规范，逻辑清晰，论述严谨
4. 不要包含标题，直接开始正文内容
5. 适当引用相关研究和数据支持论点
6. 使用学术性语言，避免口语化表达
7. 使用专业术语和概念
8. 增加数据引用和实证支持
9. 确保段落间逻辑连贯，有明确的论证结构''',
            'variables': '{"education_level":"教育水平","title":"论文标题","section":"章节名称","word_count":"字数","subject":"学科"}'
        },
        {
            'name': '批注处理模板',
            'description': '用于处理文档批注的提示词模板',
            'template_type': 'annotation',
            'content': '''请根据以下批注修改文本内容:

文本上下文: "{text_context}"

批注要求: "{annotation_content}"

请直接提供修改后的完整文本段落，不要添加任何解释。确保修改后的文本符合批注要求，同时保持原文的风格和语气。如果批注内容不明确，请尽量保留原文的主要信息。''',
            'variables': '{"text_context":"原文内容","annotation_content":"批注内容"}'
        },
        {
            'name': '问卷设计模板',
            'description': '用于设计调查问卷的提示词模板',
            'template_type': 'survey',
            'content': '''请根据以下主题设计一份调查问卷:

主题: {topic}
目标受众: {audience}
问卷目的: {purpose}

要求:
1. 设计{question_count}个问题
2. 包含单选题、多选题和开放性问题
3. 问题应该清晰、简洁、不带偏见
4. 按照合理的逻辑顺序排列问题
5. 使用适当的量表（如李克特量表）
6. 提供明确的填写指导

请以标准问卷格式输出，包括问卷标题、简介和问题编号。''',
            'variables': '{"topic":"问卷主题","audience":"目标受众","purpose":"问卷目的","question_count":"问题数量"}'
        }
    ]
    
    # 检查是否已存在，不存在则创建
    for template in default_templates:
        existing = PromptTemplate.query.filter_by(name=template['name']).first()
        if not existing:
            new_template = PromptTemplate(
                name=template['name'],
                description=template['description'],
                template_type=template['template_type'],
                content=template['content'],
                variables=template['variables'],
                is_active=True
            )
            db.session.add(new_template)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"初始化默认提示词模板失败: {str(e)}") 
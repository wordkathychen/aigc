"""
全局配置文件
包含应用程序的所有全局配置项
"""

import os
import sys
import secrets
from datetime import timedelta

# 应用程序信息
APP_NAME = "AI文本生成助手"
APP_VERSION = "1.0.0"

# 获取应用程序根目录
def get_base_path():
    """获取应用程序基础路径，适配PyInstaller环境"""
    if getattr(sys, 'frozen', False):
        # PyInstaller环境
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

BASE_PATH = get_base_path()
DATA_PATH = os.path.join(BASE_PATH, 'data')
LOGS_PATH = os.path.join(BASE_PATH, 'logs')
TEMPLATES_PATH = os.path.join(BASE_PATH, 'templates')

# 确保目录存在
for path in [DATA_PATH, LOGS_PATH, TEMPLATES_PATH]:
    os.makedirs(path, exist_ok=True)

# 数据库设置
DATABASE_PATH = os.path.join(DATA_PATH, 'database.sqlite')

# API 设置
DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_API_KEY"  # 实际使用时替换为真实的API密钥
DEEPSEEK_API_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"

# PPT生成API设置
PPT_APP_ID = "eade5980"  # 讯飞PPT生成API的ID
PPT_API_SECRET = "ZTg5YTVlYzQ0MmQ1Njg1YjgzOWQ1ZDhh"  # 讯飞PPT生成API的密钥

# 生成设置
MAX_TOKENS = 4096
MAX_CONTEXT_LENGTH = 8192
DETECTION_THRESHOLD = 0.7
MAX_RETRY_COUNT = 3
REQUEST_TIMEOUT = 60

# 缓存设置
CACHE_ENABLED = True
CACHE_EXPIRE_DAYS = 7
CACHE_DIR = os.path.join(DATA_PATH, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# 日志设置
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
MAX_LOG_FILES = 5

# 应用程序设置
DEFAULT_THEME = "light"  # light, dark
DEFAULT_FONT_SIZE = 12
DEFAULT_LANGUAGE = "zh-CN"

# 字数分配比例
WORD_COUNT_RATIO = {
    "摘要": 0.05,
    "引言": 0.1,
    "正文": 0.7,
    "结论": 0.1,
    "参考文献": 0.05
}

# 论文类型配置
PAPER_TYPES = {
    "毕业论文": {
        "sections": ["摘要", "Abstract", "引言", "研究背景", "文献综述", "研究方法", "实验结果", "讨论", "结论", "参考文献"],
        "requires_abstract": True,
        "requires_references": True
    },
    "期刊论文": {
        "sections": ["摘要", "Abstract", "关键词", "引言", "研究方法", "结果", "讨论", "结论", "参考文献"],
        "requires_abstract": True,
        "requires_keywords": True,
        "requires_references": True
    },
    "开题报告": {
        "sections": ["研究背景", "研究意义", "研究目标", "研究内容", "研究方法", "技术路线", "进度安排", "预期成果"],
        "requires_abstract": False,
        "requires_references": True
    },
    "实验报告": {
        "sections": ["实验目的", "实验原理", "实验设备", "实验步骤", "实验结果", "结果分析", "实验结论", "讨论"],
        "requires_abstract": False,
        "requires_references": False
    }
}

# Web后台配置
SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
UPLOAD_FOLDER = os.path.join(get_base_path(), "data", "uploads")
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# API配置
API_CONFIGS = {
    'deepseek': {
        'url': 'https://api.deepseek.com/v1/chat/completions',
        'model': 'deepseek-chat',
        'key': 'your-deepseek-key'
    },
    'openai': {
        'base_url': 'https://api.openai.com/v1',
        'default_model': 'gpt-3.5-turbo',
    },
    'azure': {
        'api_version': '2023-03-15-preview',
        'default_model': 'gpt-35-turbo',
    }
}

# DeepSeek API配置
MAX_RETRIES = 3
RETRY_DELAY = 1
TIMEOUT = 30
PROMPT_TEMPLATE = """
请为《{title}》的{section}章节生成内容，字数大约{word_count}字。
要求：
1. 符合学术论文规范
2. 行文流畅，逻辑清晰
3. 使用专业术语
4. 适当引用研究数据
"""

# 日志配置
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 文章字数限制
MIN_WORDS = 1000
MAX_WORDS = 50000

# 大纲章节限制
MIN_SECTIONS = 3
MAX_SECTIONS = 10

# 主题颜色
THEME_COLORS = {
    'primary': '#64ffda',
    'background': '#0a192f',
    'card': '#112240',
    'text': '#e6f1ff',
    'button': '#1e6f9e'
}

# 窗口大小
WINDOW_SIZE = "1200x800"

# 许可证配置
LICENSE_TYPES = {
    'count_limited': 'count',  # 按次数限制
    'time_limited': 'time'     # 按时间限制
}

# 教育级别配置
EDUCATION_LEVELS = {
    'college': {
        'model': 'gpt-4-mini',
        'max_tokens': 2048
    },
    'university': {
        'model': 'deepseek-v3',
        'max_tokens': 4096
    }
}

# 文档处理配置
WORD_TEMPLATES = {
    'thesis': 'templates/thesis.docx',
    'paper': 'templates/paper.docx',
    'report': 'templates/report.docx'
}

# SPSS分析类型
SPSS_ANALYSIS_TYPES = [
    '描述性统计分析',
    't检验',
    '卡方检验',
    '方差分析',
    '相关分析',
    '回归分析',
    '因子分析',
    '聚类分析'
]

# 文章生成配置
ARTICLE_CONFIG = {
    'abstract_length': 300,  # 摘要字数
    'title_max_length': 100,  # 标题最大长度
    'min_word_count': 1000,   # 最小字数
    'max_word_count': 20000,  # 最大字数
}

# 数据库配置
DATABASE_CONFIG = {
    'path': 'data/paper_generator.db',
    'backup_path': 'data/backup/',
    'journal_mode': 'WAL'
}

# 界面配置
UI_CONFIG = {
    'window_title': '论文生成助手',
    'window_size': '1200x800',
    'theme': 'dark',
    'font_family': '微软雅黑',
    'font_size': 12
}

PROMPT_TEMPLATES = {
    "学术论文": {
        "outline": """
        请为《{title}》生成一个符合{education_level}学术论文规范的详细大纲：
        学科领域：{subject}
        关键词：{keywords}
        
        要求：
        1. 严格遵循学术论文格式
        2. 包含绪论、文献综述、研究方法、结果分析、结论等章节
        3. 每章节3-4个子标题
        4. 确保逻辑严密性和学术性
        """,
        
        "content": """
        请为{education_level}学术论文《{title}》的{section}章节撰写内容：
        字数要求：{word_count}字
        学科领域：{subject}
        
        要求：
        1. 严格遵循学术规范
        2. 使用专业术语和引用
        3. 论证严谨，数据支撑
        4. 避免主观表述
        """
    },
    
    "综述论文": {
        "outline": """
        请为《{title}》生成一个文献综述类论文大纲：
        研究领域：{subject}
        关键词：{keywords}
        
        要求：
        1. 突出研究现状梳理
        2. 包含研究背景、文献回顾、研究趋势、问题与展望等
        3. 强调不同观点的对比
        """,
        
        "content": """
        请为综述论文《{title}》的{section}撰写内容：
        字数要求：{word_count}字
        研究领域：{subject}
        
        要求：
        1. 全面概述相关研究
        2. 对比不同观点
        3. 突出发展脉络
        4. 指出研究空白
        """
    },
    
    "调研报告": {
        "outline": """
        请为《{title}》生成调研报告大纲：
        调研主题：{subject}
        关键词：{keywords}
        
        要求：
        1. 包含调研背景、方法、数据分析、结论建议
        2. 突出实证研究
        3. 注重数据支撑
        """,
        
        "content": """
        请为调研报告《{title}》的{section}撰写内容：
        字数：{word_count}字
        调研主题：{subject}
        
        要求：
        1. 数据详实
        2. 分析深入
        3. 建议具体可行
        4. 图表配合说明
        """
    }
}

# 安全设置
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# 默认管理员账户
DEFAULT_ADMIN = {
    'username': 'admin',
    'password': 'admin123',  # 实际部署时应更改为强密码
    'email': 'admin@example.com'
}

# 教育水平列表
EDUCATION_LEVELS = ["大专", "本科", "硕士", "博士"]

# 文章类型
ARTICLE_TYPES = {
    "学术论文": "学术性研究论文，包含研究背景、方法、结果和讨论",
    "综述论文": "文献综述型论文，对某一领域的研究进行全面回顾和总结",
    "实验报告": "科学实验的详细记录和分析",
    "案例分析": "针对特定案例的深入分析和讨论",
    "毕业论文": "本科或研究生毕业论文",
    "调查报告": "基于调查数据的分析报告"
}
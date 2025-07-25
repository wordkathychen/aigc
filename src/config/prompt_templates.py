"""
论文生成的提示词模板配置
按照不同学历等级和专业领域进行分类
"""

# 学历等级
EDUCATION_LEVELS = ["大专", "本科", "硕士", "博士"]

# 专业领域
SUBJECT_AREAS = [
    "通用",
    "计算机科学",
    "经济学",
    "教育学",
    "管理学",
    "医学",
    "文学",
    "法学",
    "工学",
    "理学"
]

# 摘要生成模板 - 中文
ABSTRACT_CN_TEMPLATES = {
    # 通用模板
    "通用": {
        "大专": """
        请为以下论文生成中文摘要：
        
        标题：{title}
        大纲：{outline}
        
        要求：
        1. 控制在300字左右
        2. 包含研究背景、主要内容和结论
        3. 写成一段话，不分点
        4. 语言简洁明了
        5. 适合大专学历水平
        """,
        
        "本科": """
        请为以下论文生成中文摘要：
        
        标题：{title}
        大纲：{outline}
        
        要求：
        1. 控制在300字左右
        2. 包含研究背景、研究方法、主要观点和意义
        3. 写成一段话，不分点
        4. 语言简洁明了，符合学术规范
        5. 适合本科学历水平
        """,
        
        "硕士": """
        请为以下论文生成中文摘要：
        
        标题：{title}
        大纲：{outline}
        
        要求：
        1. 控制在400字左右
        2. 包含研究背景、研究方法、研究结果、主要观点和理论意义
        3. 写成一段话，不分点
        4. 语言简洁明了，符合学术规范
        5. 适合硕士研究生学历水平，体现一定的学术深度
        """,
        
        "博士": """
        请为以下论文生成中文摘要：
        
        标题：{title}
        大纲：{outline}
        
        要求：
        1. 控制在500字左右
        2. 包含研究背景、理论基础、研究方法、研究结果、主要观点、理论意义和实践价值
        3. 写成一段话，不分点
        4. 语言简洁明了，符合高级学术规范
        5. 适合博士研究生学历水平，体现较高的学术深度和创新性
        """
    },
    
    # 计算机科学
    "计算机科学": {
        "本科": """
        请为以下计算机科学领域的论文生成中文摘要：
        
        标题：{title}
        大纲：{outline}
        
        要求：
        1. 控制在300字左右
        2. 包含研究背景、技术方法、实验结果和结论
        3. 写成一段话，不分点
        4. 使用计算机专业术语，符合该领域学术规范
        5. 适合计算机专业本科学历水平
        """,
        
        "硕士": """
        请为以下计算机科学领域的论文生成中文摘要：
        
        标题：{title}
        大纲：{outline}
        
        要求：
        1. 控制在400字左右
        2. 包含研究背景、技术挑战、算法/模型设计、实验评估、结果和贡献
        3. 写成一段话，不分点
        4. 使用计算机专业术语，符合该领域学术规范
        5. 适合计算机专业硕士研究生学历水平，体现一定的技术深度和创新性
        """
    }
    # 可以继续添加其他专业的模板...
}

# 关键词生成模板 - 中文
KEYWORDS_CN_TEMPLATES = {
    # 通用模板
    "通用": {
        "大专": """
        请根据以下论文标题和摘要，提取3-5个关键词：
        
        标题：{title}
        摘要：{abstract}
        
        要求：
        1. 关键词应体现论文的核心内容
        2. 按重要性排序
        3. 每个关键词用分号隔开
        4. 适合大专学历水平
        """,
        
        "本科": """
        请根据以下论文标题和摘要，提取3-5个关键词：
        
        标题：{title}
        摘要：{abstract}
        
        要求：
        1. 关键词应体现论文的核心内容和研究领域
        2. 按重要性排序
        3. 每个关键词用分号隔开
        4. 适合本科学历水平
        """,
        
        "硕士": """
        请根据以下论文标题和摘要，提取4-6个关键词：
        
        标题：{title}
        摘要：{abstract}
        
        要求：
        1. 关键词应体现论文的核心内容、研究领域和理论基础
        2. 包含专业术语
        3. 按重要性排序
        4. 每个关键词用分号隔开
        5. 适合硕士研究生学历水平
        """,
        
        "博士": """
        请根据以下论文标题和摘要，提取5-7个关键词：
        
        标题：{title}
        摘要：{abstract}
        
        要求：
        1. 关键词应体现论文的核心内容、研究领域、理论基础和创新点
        2. 包含专业术语和学术概念
        3. 按重要性排序
        4. 每个关键词用分号隔开
        5. 适合博士研究生学历水平
        """
    }
    # 可以继续添加其他专业的模板...
}

# 英文摘要生成模板
ABSTRACT_EN_TEMPLATES = {
    # 通用模板
    "通用": {
        "大专": """
        请将以下中文摘要翻译成英文Abstract：
        
        论文标题：{title}
        中文摘要：{abstract_cn}
        
        要求：
        1. 翻译准确，符合基本英语表达习惯
        2. 保持原摘要的主要内容和结构
        3. 语言简洁明了
        4. 适合大专学历水平
        """,
        
        "本科": """
        请将以下中文摘要翻译成英文Abstract：
        
        论文标题：{title}
        中文摘要：{abstract_cn}
        
        要求：
        1. 翻译准确，符合学术英语表达习惯
        2. 保持原摘要的主要内容和结构
        3. 语言简洁明了，符合学术规范
        4. 适合本科学历水平
        """,
        
        "硕士": """
        请将以下中文摘要翻译成英文Abstract：
        
        论文标题：{title}
        中文摘要：{abstract_cn}
        
        要求：
        1. 翻译准确，符合高级学术英语表达习惯
        2. 保持原摘要的主要内容和结构
        3. 使用学术词汇和表达，符合国际学术规范
        4. 适合硕士研究生学历水平
        """,
        
        "博士": """
        请将以下中文摘要翻译成英文Abstract：
        
        论文标题：{title}
        中文摘要：{abstract_cn}
        
        要求：
        1. 翻译准确，符合高级学术英语表达习惯
        2. 保持原摘要的主要内容和结构
        3. 使用专业学术词汇和表达，符合国际高级学术规范
        4. 适合博士研究生学历水平，体现学术深度
        5. 可适当优化表达，使其更符合英语学术论文的表达习惯
        """
    }
    # 可以继续添加其他专业的模板...
}

# 英文关键词生成模板
KEYWORDS_EN_TEMPLATES = {
    # 通用模板
    "通用": {
        "大专": """
        请将以下中文关键词翻译成英文Keywords：
        
        论文标题：{title}
        中文关键词：{keywords_cn}
        
        要求：
        1. 翻译准确
        2. 保持原关键词的顺序
        3. 每个关键词首字母大写（专有名词除外）
        4. 以分号分隔
        """,
        
        "本科": """
        请将以下中文关键词翻译成英文Keywords：
        
        论文标题：{title}
        中文关键词：{keywords_cn}
        
        要求：
        1. 翻译准确，使用学科领域内的常用英文术语
        2. 保持原关键词的顺序
        3. 每个关键词首字母大写（专有名词除外）
        4. 以分号分隔
        """,
        
        "硕士": """
        请将以下中文关键词翻译成英文Keywords：
        
        论文标题：{title}
        中文关键词：{keywords_cn}
        
        要求：
        1. 翻译准确，使用学科领域内的专业英文术语
        2. 保持原关键词的顺序
        3. 每个关键词首字母大写（专有名词除外）
        4. 以分号分隔
        5. 必要时可使用复合词或短语以更准确表达学术概念
        """,
        
        "博士": """
        请将以下中文关键词翻译成英文Keywords：
        
        论文标题：{title}
        中文关键词：{keywords_cn}
        
        要求：
        1. 翻译准确，使用学科领域内的高级专业英文术语
        2. 保持原关键词的顺序
        3. 每个关键词首字母大写（专有名词除外）
        4. 以分号分隔
        5. 必要时可使用复合词或短语以更准确表达学术概念
        6. 确保术语符合该领域最新的国际学术表达
        """
    }
    # 可以继续添加其他专业的模板...
}

# 正文生成模板
BODY_TEMPLATES = {
    # 通用模板
    "通用": {
        "大专": """
        请为论文《{title}》生成以下章节的内容：
        
        章节路径：{section_path}
        章节标题：{section_title}
        目标字数：{word_count}字
        学科领域：{subject}
        
        要求：
        1. 严格控制在{word_count}字左右
        2. 内容要符合大专学历水平，概念解释清晰
        3. 语言流畅，逻辑清晰
        4. 紧扣章节标题进行论述
        5. 与论文整体主题《{title}》保持一致性
        """,
        
        "本科": """
        请为论文《{title}》生成以下章节的内容：
        
        章节路径：{section_path}
        章节标题：{section_title}
        目标字数：{word_count}字
        学科领域：{subject}
        
        要求：
        1. 严格控制在{word_count}字左右
        2. 内容要符合本科学历水平，论述有一定深度
        3. 语言流畅，逻辑清晰
        4. 紧扣章节标题进行论述
        5. 与论文整体主题《{title}》保持一致性
        6. 适当引用相关研究或数据支持论点
        """,
        
        "硕士": """
        请为论文《{title}》生成以下章节的内容：
        
        章节路径：{section_path}
        章节标题：{section_title}
        目标字数：{word_count}字
        学科领域：{subject}
        
        要求：
        1. 严格控制在{word_count}字左右
        2. 内容要符合硕士学历水平，论述有较深的学术深度
        3. 语言流畅，逻辑严密，论证充分
        4. 紧扣章节标题进行论述
        5. 与论文整体主题《{title}》保持一致性
        6. 引用相关研究或数据支持论点
        7. 使用专业术语和学术表达
        8. 体现一定的理论分析能力和批判思维
        """,
        
        "博士": """
        请为论文《{title}》生成以下章节的内容：
        
        章节路径：{section_path}
        章节标题：{section_title}
        目标字数：{word_count}字
        学科领域：{subject}
        
        要求：
        1. 严格控制在{word_count}字左右
        2. 内容要符合博士学历水平，论述有很高的学术深度
        3. 语言流畅，逻辑严密，论证充分
        4. 紧扣章节标题进行论述
        5. 与论文整体主题《{title}》保持一致性
        6. 引用相关研究或数据支持论点，包括最新的学术成果
        7. 使用专业术语和高级学术表达
        8. 体现深入的理论分析能力、批判思维和创新思考
        9. 探讨理论意义和实践价值
        """
    },
    
    # 计算机科学
    "计算机科学": {
        "本科": """
        请为计算机科学论文《{title}》生成以下章节的内容：
        
        章节路径：{section_path}
        章节标题：{section_title}
        目标字数：{word_count}字
        
        要求：
        1. 严格控制在{word_count}字左右
        2. 内容要符合计算机专业本科学历水平
        3. 使用计算机领域的专业术语和概念
        4. 紧扣章节标题进行论述
        5. 与论文整体主题《{title}》保持一致性
        6. 如涉及算法或技术方案，应包含基本原理解释
        7. 如涉及实验，应包含实验设计和结果分析
        """,
        
        "硕士": """
        请为计算机科学论文《{title}》生成以下章节的内容：
        
        章节路径：{section_path}
        章节标题：{section_title}
        目标字数：{word_count}字
        
        要求：
        1. 严格控制在{word_count}字左右
        2. 内容要符合计算机专业硕士学历水平
        3. 使用计算机领域的专业术语和概念
        4. 紧扣章节标题进行论述
        5. 与论文整体主题《{title}》保持一致性
        6. 如涉及算法或技术方案，应包含详细的原理解释和优化分析
        7. 如涉及实验，应包含完整的实验设计、评估指标、结果分析和对比
        8. 体现一定的技术创新性和学术深度
        """
    }
    # 可以继续添加其他专业的模板...
}

# 参考文献生成模板
REFERENCES_TEMPLATES = {
    # 通用模板
    "通用": {
        "大专": """
        请为论文《{title}》生成参考文献列表，学科领域是{subject}。
        
        要求：
        1. 生成8-10条参考文献
        2. 参考文献应真实可信
        3. 格式符合GB/T 7714-2015标准
        4. 以中文文献为主
        5. 按引用顺序编号排列
        """,
        
        "本科": """
        请为论文《{title}》生成参考文献列表，学科领域是{subject}。
        
        要求：
        1. 生成10-15条参考文献
        2. 参考文献应真实可信，包括近5年的研究成果
        3. 格式符合GB/T 7714-2015标准
        4. 包括中英文文献，以中文为主
        5. 按引用顺序编号排列
        """,
        
        "硕士": """
        请为论文《{title}》生成参考文献列表，学科领域是{subject}。
        
        要求：
        1. 生成15-20条参考文献
        2. 参考文献应真实可信，包括近3年的研究成果
        3. 格式符合GB/T 7714-2015标准
        4. 包括中英文文献，中英文比例大致为6:4
        5. 按引用顺序编号排列
        6. 包含期刊论文、会议论文、专著等多种类型
        """,
        
        "博士": """
        请为论文《{title}》生成参考文献列表，学科领域是{subject}。
        
        要求：
        1. 生成20-30条参考文献
        2. 参考文献应真实可信，包括最新的研究成果
        3. 格式符合GB/T 7714-2015标准
        4. 包括中英文文献，中英文比例大致为4:6
        5. 按引用顺序编号排列
        6. 包含高水平期刊论文、会议论文、专著等多种类型
        7. 包括该领域的经典文献和最新研究成果
        """
    }
    # 可以继续添加其他专业的模板...
}

# 致谢生成模板
ACKNOWLEDGEMENT_TEMPLATES = {
    # 通用模板
    "通用": {
        "大专": """
        请为论文《{title}》生成致谢部分，学科领域是{subject}。
        
        要求：
        1. 简洁真诚，字数200字左右
        2. 感谢指导教师和各方支持
        3. 表达自己的成长和收获
        4. 语言得体，情感真挚
        """,
        
        "本科": """
        请为论文《{title}》生成致谢部分，学科领域是{subject}。
        
        要求：
        1. 简洁真诚，字数200-300字左右
        2. 感谢指导教师和各方支持
        3. 表达自己的成长和收获
        4. 语言得体，情感真挚
        5. 提及论文写作过程中的关键帮助
        """,
        
        "硕士": """
        请为论文《{title}》生成致谢部分，学科领域是{subject}。
        
        要求：
        1. 简洁真诚，字数300-400字左右
        2. 感谢导师、评审专家和各方支持
        3. 表达自己的学术成长和研究收获
        4. 语言得体，情感真挚
        5. 提及研究过程中的关键帮助和支持
        6. 可提及科研项目或基金支持（如有）
        """,
        
        "博士": """
        请为论文《{title}》生成致谢部分，学科领域是{subject}。
        
        要求：
        1. 简洁真诚，字数400-500字左右
        2. 感谢导师团队、评审专家和各方支持
        3. 表达自己的学术成长和研究收获
        4. 语言得体，情感真挚
        5. 提及研究过程中的关键帮助和支持
        6. 提及科研项目或基金支持
        7. 可提及学术交流和国际合作（如有）
        """
    }
    # 可以继续添加其他专业的模板...
}

# 获取指定类型的模板
def get_template(template_type, subject, education_level):
    """获取指定类型、学科和学历等级的模板
    
    Args:
        template_type: 模板类型 (abstract_cn, keywords_cn, abstract_en, keywords_en, body, references, acknowledgement)
        subject: 学科领域
        education_level: 学历等级
        
    Returns:
        str: 对应的模板字符串
    """
    # 确定模板字典
    if template_type == "abstract_cn":
        templates = ABSTRACT_CN_TEMPLATES
    elif template_type == "keywords_cn":
        templates = KEYWORDS_CN_TEMPLATES
    elif template_type == "abstract_en":
        templates = ABSTRACT_EN_TEMPLATES
    elif template_type == "keywords_en":
        templates = KEYWORDS_EN_TEMPLATES
    elif template_type == "body":
        templates = BODY_TEMPLATES
    elif template_type == "references":
        templates = REFERENCES_TEMPLATES
    elif template_type == "acknowledgement":
        templates = ACKNOWLEDGEMENT_TEMPLATES
    else:
        raise ValueError(f"不支持的模板类型: {template_type}")
    
    # 如果学科存在特定模板，则使用该学科的模板
    if subject in templates and education_level in templates[subject]:
        return templates[subject][education_level]
    
    # 否则使用通用模板
    if education_level in templates["通用"]:
        return templates["通用"][education_level]
    
    # 如果没有找到匹配的模板，使用本科通用模板作为默认
    return templates["通用"]["本科"] 
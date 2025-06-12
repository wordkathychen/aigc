from typing import Any, Dict, List
import re
import os
from datetime import datetime
from .exceptions import ValidationError
from config.settings import *
import bleach
from html.parser import HTMLParser

class InputValidator:
    @staticmethod
    def validate_title(title: str) -> None:
        """验证论文标题"""
        if not isinstance(title, str):
            raise ValidationError("标题必须是字符串类型")
        
        title = title.strip()
        if not title:
            raise ValidationError("标题不能为空")
            
        if len(title) > MAX_TITLE_LENGTH:
            raise ValidationError(f"标题长度不能超过{MAX_TITLE_LENGTH}字符")
            
        if re.search(r'[<>"/\\|?*]', title):
            raise ValidationError("标题包含非法字符")

    @staticmethod
    def validate_word_count(count: Any) -> int:
        """验证字数输入"""
        try:
            if isinstance(count, str):
                # 处理"1万"这样的输入
                count = count.replace('万', '0000')
            
            count = int(count)
            if not MIN_WORDS <= count <= MAX_WORDS:
                raise ValidationError(f"字数必须在{MIN_WORDS}到{MAX_WORDS}之间")
            return count
            
        except ValueError:
            raise ValidationError("字数必须是整数")

    @staticmethod
    def validate_subject(subject: str) -> None:
        """验证学科领域"""
        if not isinstance(subject, str):
            raise ValidationError("学科必须是字符串类型")
            
        subject = subject.strip()
        if not subject:
            raise ValidationError("请选择学科领域")
            
        if subject not in VALID_SUBJECTS:
            raise ValidationError(f"无效的学科领域：{subject}")

    @staticmethod
    def validate_template(template: str) -> None:
        """验证模板选择"""
        if not isinstance(template, str):
            raise ValidationError("模板必须是字符串类型")
            
        template = template.strip()
        if not template:
            raise ValidationError("请选择文档模板")
            
        if template not in VALID_TEMPLATES:
            raise ValidationError(f"无效的模板类型：{template}")

    @staticmethod
    def validate_file_path(file_path: str, allowed_types: List[str]) -> None:
        """验证文件路径"""
        if not isinstance(file_path, str):
            raise ValidationError("文件路径必须是字符串类型")
            
        if not os.path.exists(file_path):
            raise ValidationError(f"文件不存在：{file_path}")
            
        if not os.path.isfile(file_path):
            raise ValidationError(f"不是有效的文件：{file_path}")
            
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in allowed_types:
            raise ValidationError(f"不支持的文件类型：{ext}")
            
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            raise ValidationError(f"文件大小超过限制：{MAX_FILE_SIZE/1024/1024}MB")

    @staticmethod
    def validate_date(date_str: str) -> datetime:
        """验证日期格式"""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValidationError("日期格式无效，应为：YYYY-MM-DD")

    @staticmethod
    def validate_email(email: str) -> None:
        """验证邮箱格式"""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("邮箱格式无效")

def validate_input(data, schema):
    """
    根据提供的模式验证输入数据
    
    Args:
        data: 要验证的数据字典
        schema: 验证模式字典，包含每个字段的验证规则
    
    Raises:
        ValidationError: 如果验证失败
    """
    errors = []
    
    for field, rules in schema.items():
        # 检查必填字段
        if rules.get('required', False) and (field not in data or not data.get(field)):
            errors.append(f"字段 '{field}' 是必填项")
            continue
        
        # 如果字段不存在且不是必填项，跳过其他验证
        if field not in data or data.get(field) is None:
            continue
            
        value = data.get(field)
        
        # 类型验证
        field_type = rules.get('type')
        if field_type:
            if field_type == 'string' and not isinstance(value, str):
                errors.append(f"字段 '{field}' 必须是字符串类型")
            elif field_type == 'integer':
                try:
                    int(value)
                except (ValueError, TypeError):
                    errors.append(f"字段 '{field}' 必须是整数类型")
            elif field_type == 'number':
                try:
                    float(value)
                except (ValueError, TypeError):
                    errors.append(f"字段 '{field}' 必须是数值类型")
            elif field_type == 'boolean' and not isinstance(value, bool):
                errors.append(f"字段 '{field}' 必须是布尔类型")
            elif field_type == 'array' and not isinstance(value, list):
                errors.append(f"字段 '{field}' 必须是数组类型")
            elif field_type == 'object' and not isinstance(value, dict):
                errors.append(f"字段 '{field}' 必须是对象类型")
        
        # 字符串特定验证
        if field_type == 'string' and isinstance(value, str):
            # 最小长度
            min_length = rules.get('min_length')
            if min_length is not None and len(value) < min_length:
                errors.append(f"字段 '{field}' 长度必须至少为 {min_length} 个字符")
            
            # 最大长度
            max_length = rules.get('max_length')
            if max_length is not None and len(value) > max_length:
                errors.append(f"字段 '{field}' 长度不能超过 {max_length} 个字符")
            
            # 正则表达式模式
            pattern = rules.get('pattern')
            if pattern and not re.match(pattern, value):
                errors.append(f"字段 '{field}' 不符合要求的格式")
        
        # 数值特定验证
        if field_type in ['integer', 'number']:
            try:
                num_value = int(value) if field_type == 'integer' else float(value)
                
                # 最小值
                minimum = rules.get('min')
                if minimum is not None and num_value < minimum:
                    errors.append(f"字段 '{field}' 必须大于或等于 {minimum}")
                
                # 最大值
                maximum = rules.get('max')
                if maximum is not None and num_value > maximum:
                    errors.append(f"字段 '{field}' 必须小于或等于 {maximum}")
            except (ValueError, TypeError):
                pass  # 类型错误已在前面处理
        
        # 数组特定验证
        if field_type == 'array' and isinstance(value, list):
            # 最小项数
            min_items = rules.get('min_items')
            if min_items is not None and len(value) < min_items:
                errors.append(f"字段 '{field}' 至少需要 {min_items} 个项")
            
            # 最大项数
            max_items = rules.get('max_items')
            if max_items is not None and len(value) > max_items:
                errors.append(f"字段 '{field}' 最多只能有 {max_items} 个项")
        
        # 枚举验证
        enum = rules.get('enum')
        if enum is not None and value not in enum:
            errors.append(f"字段 '{field}' 必须是以下值之一: {', '.join(map(str, enum))}")
    
    # 如果有错误，抛出异常
    if errors:
        raise ValidationError('\n'.join(errors))

def sanitize_html(html_content):
    """
    净化HTML内容，移除潜在的危险标签和属性
    
    Args:
        html_content: 要净化的HTML内容
    
    Returns:
        净化后的HTML内容
    """
    if not html_content:
        return ""
        
    # 允许的标签和属性
    allowed_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
        'strong', 'em', 'u', 'strike', 'i', 'b', 'ul', 'ol', 'li',
        'blockquote', 'pre', 'code', 'table', 'thead', 'tbody',
        'tr', 'th', 'td', 'a', 'img', 'div', 'span'
    ]
    
    allowed_attributes = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'table': ['border', 'cellpadding', 'cellspacing'],
        '*': ['class', 'style']
    }
    
    # 使用bleach库净化HTML
    clean_html = bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    
    return clean_html

class HTMLStripper(HTMLParser):
    """HTML解析器，用于从HTML中提取纯文本"""
    
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    
    def handle_data(self, d):
        self.text.append(d)
    
    def get_text(self):
        return ''.join(self.text)

def strip_html_tags(html_content):
    """
    从HTML内容中移除所有标签，仅保留纯文本
    
    Args:
        html_content: 包含HTML标签的内容
    
    Returns:
        移除所有HTML标签后的纯文本
    """
    if not html_content:
        return ""
        
    stripper = HTMLStripper()
    stripper.feed(html_content)
    return stripper.get_text()
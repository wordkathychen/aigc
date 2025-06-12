"""
Web表单模块
定义所有的表单类
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, DateTimeField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, NumberRange, ValidationError
import re

class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField('用户名', validators=[
        DataRequired('请输入用户名'),
        Length(1, 64, '用户名长度必须在1-64个字符之间')
    ])
    password = PasswordField('密码', validators=[
        DataRequired('请输入密码')
    ])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

class APIKeyForm(FlaskForm):
    """API密钥表单"""
    api_type = SelectField('API类型', choices=[
        ('deepseek', 'DeepSeek'),
        ('openai', 'OpenAI'),
        ('zhipu', '智谱AI'),
        ('xunfei', '讯飞星火'),
        ('baidu', '百度文心一言'),
        ('anthropic', 'Anthropic'),
        ('moonshot', 'Moonshot'),
        ('minimax', 'MiniMax'),
        ('cloudflare', 'Cloudflare'),
        ('dashscope', '通义千问'),
        ('github_models', 'GitHub Models'),
        ('guiji', '轨迹流动'),
        ('other', '其他')
    ], validators=[DataRequired('请选择API类型')])
    
    key_name = StringField('密钥名称', validators=[
        DataRequired('请输入密钥名称'),
        Length(1, 64, '名称长度必须在1-64个字符之间')
    ])
    
    api_key = StringField('API密钥', validators=[
        DataRequired('请输入API密钥'),
        Length(1, 255, '密钥长度必须在1-255个字符之间')
    ])
    
    api_endpoint = StringField('API端点', validators=[
        Optional(),
        Length(0, 255, '端点长度必须在0-255个字符之间')
    ])
    
    model_name = StringField('模型名称', validators=[
        Optional(),
        Length(0, 64, '模型名称长度必须在0-64个字符之间')
    ])
    
    priority = IntegerField('优先级', validators=[
        NumberRange(min=0, max=100, message='优先级必须在0-100之间')
    ], default=0)
    
    usage_limit = IntegerField('使用次数限制', validators=[
        Optional(),
        NumberRange(min=0, message='使用次数不能为负数')
    ])
    
    daily_limit = IntegerField('每日使用限制', validators=[
        Optional(),
        NumberRange(min=0, message='每日使用限制不能为负数')
    ])
    
    notes = TextAreaField('备注信息', validators=[
        Optional()
    ])
    
    is_active = BooleanField('启用')
    
    submit = SubmitField('保存')

class PromptTemplateForm(FlaskForm):
    """提示词模板表单"""
    name = StringField('模板名称', validators=[
        DataRequired('请输入模板名称'),
        Length(1, 64, '名称长度必须在1-64个字符之间')
    ])
    
    category = SelectField('模板类别', choices=[
        ('title', '标题生成'),
        ('abstract_zh', '中文摘要'),
        ('abstract_en', '英文摘要'),
        ('keywords_zh', '中文关键词'),
        ('keywords_en', '英文关键词'),
        ('content', '正文内容'),
        ('references', '参考文献'),
        ('acknowledgement', '致谢')
    ], validators=[DataRequired('请选择模板类别')])
    
    content = TextAreaField('模板内容', validators=[
        DataRequired('请输入模板内容')
    ])
    
    is_active = BooleanField('启用')
    
    submit = SubmitField('保存')

class MemberForm(FlaskForm):
    """会员表单"""
    username = StringField('用户名', validators=[
        DataRequired('请输入用户名'),
        Length(1, 64, '用户名长度必须在1-64个字符之间')
    ])
    
    password = PasswordField('密码', validators=[
        Optional(),
        Length(6, 20, '密码长度必须在6-20个字符之间')
    ])
    
    email = StringField('邮箱', validators=[
        Optional(),
        Email('请输入有效的邮箱地址')
    ])
    
    phone = StringField('手机号', validators=[
        Optional(),
        Length(11, 11, '请输入11位手机号')
    ])
    
    is_active = BooleanField('启用账号')
    
    submit = SubmitField('保存')
    
    def validate_phone(self, field):
        """验证手机号格式"""
        if field.data and not re.match(r'^1[3-9]\d{9}$', field.data):
            raise ValidationError('请输入有效的手机号')

class QuotaForm(FlaskForm):
    """额度表单"""
    total_credits = IntegerField('总额度', validators=[
        DataRequired('请输入总额度'),
        NumberRange(min=0, message='额度不能为负数')
    ])
    
    remaining_credits = IntegerField('剩余额度', validators=[
        DataRequired('请输入剩余额度'),
        NumberRange(min=0, message='额度不能为负数')
    ])
    
    total_tokens = IntegerField('总字数额度', validators=[
        DataRequired('请输入总字数额度'),
        NumberRange(min=0, message='字数额度不能为负数')
    ])
    
    remaining_tokens = IntegerField('剩余字数额度', validators=[
        DataRequired('请输入剩余字数额度'),
        NumberRange(min=0, message='字数额度不能为负数')
    ])
    
    expires_at = DateTimeField('过期时间', format='%Y-%m-%d %H:%M:%S', validators=[
        Optional()
    ])
    
    submit = SubmitField('保存')
    
    def validate_remaining_credits(self, field):
        """验证剩余额度不大于总额度"""
        if field.data > self.total_credits.data:
            raise ValidationError('剩余额度不能大于总额度')
    
    def validate_remaining_tokens(self, field):
        """验证剩余字数额度不大于总字数额度"""
        if field.data > self.total_tokens.data:
            raise ValidationError('剩余字数额度不能大于总字数额度')

class SchoolTemplateForm(FlaskForm):
    """学校模板表单"""
    school_name = StringField('学校名称', validators=[
        DataRequired('请输入学校名称'),
        Length(1, 64, '学校名称长度必须在1-64个字符之间')
    ])
    
    template_name = StringField('模板名称', validators=[
        DataRequired('请输入模板名称'),
        Length(1, 64, '模板名称长度必须在1-64个字符之间')
    ])
    
    template_file = FileField('模板文件', validators=[
        FileRequired('请选择模板文件'),
        FileAllowed(['docx'], '只允许上传Word文档(.docx)')
    ])
    
    format_rules = TextAreaField('格式规则(JSON)', validators=[
        Optional()
    ])
    
    is_active = BooleanField('启用')
    
    submit = SubmitField('保存')

class SensitiveWordForm(FlaskForm):
    """敏感词表单"""
    word = StringField('敏感词', validators=[
        DataRequired('请输入敏感词'),
        Length(1, 64, '敏感词长度必须在1-64个字符之间')
    ])
    
    is_active = BooleanField('启用')
    
    submit = SubmitField('保存')

class ModelConfigForm(FlaskForm):
    """AI模型配置表单"""
    task_type = SelectField('任务类型', choices=[
        ('title', '标题生成'),
        ('abstract_zh', '中文摘要'),
        ('abstract_en', '英文摘要'),
        ('keywords_zh', '中文关键词'),
        ('keywords_en', '英文关键词'),
        ('content', '正文内容'),
        ('references', '参考文献'),
        ('acknowledgement', '致谢')
    ], validators=[DataRequired('请选择任务类型')])
    
    education_level = SelectField('教育级别', choices=[
        ('college', '大专'),
        ('undergraduate', '本科'),
        ('master', '硕士'),
        ('doctor', '博士')
    ], validators=[DataRequired('请选择教育级别')])
    
    api_type = SelectField('API类型', choices=[
        ('deepseek', 'DeepSeek'),
        ('openai', 'OpenAI'),
        ('zhipu', '智谱AI'),
        ('xunfei', '讯飞星火'),
        ('baidu', '百度文心一言'),
        ('anthropic', 'Anthropic'),
        ('moonshot', 'Moonshot'),
        ('minimax', 'MiniMax'),
        ('other', '其他')
    ], validators=[DataRequired('请选择API类型')])
    
    model_name = StringField('模型名称', validators=[
        DataRequired('请输入模型名称'),
        Length(1, 64, '模型名称长度必须在1-64个字符之间')
    ])
    
    temperature = FloatField('温度参数', validators=[
        NumberRange(min=0, max=2.0, message='温度参数必须在0-2.0之间')
    ], default=0.7)
    
    max_tokens = IntegerField('最大Token数', validators=[
        NumberRange(min=100, message='最大Token数不能小于100')
    ], default=2000)
    
    top_p = FloatField('Top P', validators=[
        NumberRange(min=0, max=1.0, message='Top P必须在0-1.0之间')
    ], default=1.0)
    
    frequency_penalty = FloatField('频率惩罚', validators=[
        NumberRange(min=-2.0, max=2.0, message='频率惩罚必须在-2.0-2.0之间')
    ], default=0.0)
    
    presence_penalty = FloatField('存在惩罚', validators=[
        NumberRange(min=-2.0, max=2.0, message='存在惩罚必须在-2.0-2.0之间')
    ], default=0.0)
    
    is_active = BooleanField('启用')
    
    submit = SubmitField('保存') 
"""
Web后台数据模型
包含用户、API密钥、提示词模板、会员额度等模型
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
import uuid

@login_manager.user_loader
def load_user(user_id):
    """加载用户信息"""
    return AdminUser.query.get(int(user_id))

class AdminUser(db.Model, UserMixin):
    """管理员用户模型"""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'
    
    @property
    def password(self):
        """密码属性不可读"""
        raise AttributeError('密码不可直接读取')
    
    @password.setter
    def password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.now()
        db.session.commit()

class Member(db.Model):
    """会员用户模型"""
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # 关联会员额度表
    quota = db.relationship('MemberQuota', backref='member', uselist=False, cascade='all, delete-orphan')
    
    # 关联会员使用记录
    usage_records = db.relationship('UsageRecord', backref='member', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Member {self.username}>'
    
    @property
    def password(self):
        """密码属性不可读"""
        raise AttributeError('密码不可直接读取')
    
    @password.setter
    def password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

class MemberQuota(db.Model):
    """会员额度模型"""
    __tablename__ = 'member_quotas'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), unique=True)
    total_credits = db.Column(db.Integer, default=0)  # 总额度
    remaining_credits = db.Column(db.Integer, default=0)  # 剩余额度
    total_tokens = db.Column(db.Integer, default=0)  # 总字数额度
    remaining_tokens = db.Column(db.Integer, default=0)  # 剩余字数额度
    expires_at = db.Column(db.DateTime, nullable=True)  # 过期时间
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<MemberQuota 会员ID:{self.member_id} 剩余额度:{self.remaining_credits}>'
    
    def has_sufficient_credits(self, amount=1):
        """检查是否有足够的额度"""
        return self.remaining_credits >= amount
    
    def has_sufficient_tokens(self, amount=1):
        """检查是否有足够的字数额度"""
        return self.remaining_tokens >= amount
    
    def consume_credits(self, amount=1):
        """消费额度"""
        if self.has_sufficient_credits(amount):
            self.remaining_credits -= amount
            db.session.commit()
            return True
        return False
    
    def consume_tokens(self, amount=1):
        """消费字数额度"""
        if self.has_sufficient_tokens(amount):
            self.remaining_tokens -= amount
            db.session.commit()
            return True
        return False

class APIKey(db.Model):
    """API密钥模型"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    api_type = db.Column(db.String(64), index=True)  # API类型: deepseek, openai, zhipu, baidu, xunfei, etc.
    key_name = db.Column(db.String(64), index=True)  # 密钥别名
    api_key = db.Column(db.String(255))  # API密钥值
    api_endpoint = db.Column(db.String(255), nullable=True)  # API端点
    model_name = db.Column(db.String(64), nullable=True)  # 模型名称
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    usage_count = db.Column(db.Integer, default=0)  # 使用次数
    priority = db.Column(db.Integer, default=0)  # 优先级（数字越大优先级越高）
    usage_limit = db.Column(db.Integer, nullable=True)  # 使用次数限制
    daily_limit = db.Column(db.Integer, nullable=True)  # 每日使用次数限制
    reset_date = db.Column(db.DateTime, nullable=True)  # 重置日期
    notes = db.Column(db.Text, nullable=True)  # 备注信息
    
    def __repr__(self):
        return f'<APIKey {self.api_type}:{self.key_name}>'
        
    def is_usable(self):
        """判断密钥是否可用"""
        if not self.is_active:
            return False
            
        # 检查使用次数限制
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
            
        # 检查每日使用次数限制
        if self.daily_limit and self.reset_date:
            today = datetime.now().date()
            reset_day = self.reset_date.date()
            
            # 如果今天是重置日期之后的日期，重置计数
            if today > reset_day:
                self.reset_date = datetime.now()
                self.usage_count = 0
                db.session.commit()
                return True
                
        return True
        
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        db.session.commit()

class PromptTemplate(db.Model):
    """提示词模板模型"""
    __tablename__ = 'prompt_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)  # 模板名称
    category = db.Column(db.String(64), index=True)  # 模板类别: title, abstract, keywords, etc.
    content = db.Column(db.Text)  # 模板内容
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<PromptTemplate {self.category}:{self.name}>'

class SchoolTemplate(db.Model):
    """学校论文模板模型"""
    __tablename__ = 'school_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(64), index=True)  # 学校名称
    template_name = db.Column(db.String(64))  # 模板名称
    file_path = db.Column(db.String(255))  # 文件路径
    format_rules = db.Column(db.Text, nullable=True)  # 格式规则(JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<SchoolTemplate {self.school_name}:{self.template_name}>'

class UsageRecord(db.Model):
    """使用记录模型"""
    __tablename__ = 'usage_records'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    record_type = db.Column(db.String(64), index=True)  # 记录类型: generation, formatting, etc.
    credits_used = db.Column(db.Integer, default=0)  # 使用的额度
    tokens_used = db.Column(db.Integer, default=0)  # 使用的字数
    request_data = db.Column(db.Text, nullable=True)  # 请求数据(JSON)
    created_at = db.Column(db.DateTime, default=datetime.now)
    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<UsageRecord {self.record_type} 会员ID:{self.member_id}>'

class SensitiveWord(db.Model):
    """敏感词模型"""
    __tablename__ = 'sensitive_words'
    
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(64), unique=True, index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<SensitiveWord {self.word}>'

class ModelConfig(db.Model):
    """AI模型配置模型
    用于配置不同任务和教育级别使用的AI模型
    """
    __tablename__ = 'model_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    task_type = db.Column(db.String(64), index=True)  # 任务类型: title, abstract, content, etc.
    education_level = db.Column(db.String(64), index=True)  # 教育级别: college, undergraduate, master, doctor, etc.
    api_type = db.Column(db.String(64))  # API类型: deepseek, openai, etc.
    model_name = db.Column(db.String(64))  # 模型名称: deepseek-chat, gpt-4, etc.
    temperature = db.Column(db.Float, default=0.7)  # 温度参数
    max_tokens = db.Column(db.Integer, default=2000)  # 最大token数
    top_p = db.Column(db.Float, default=1.0)  # top_p参数
    frequency_penalty = db.Column(db.Float, default=0.0)  # 频率惩罚参数
    presence_penalty = db.Column(db.Float, default=0.0)  # 存在惩罚参数
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<ModelConfig {self.task_type}:{self.education_level} - {self.api_type}:{self.model_name}>' 
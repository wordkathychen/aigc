"""
管理员后台视图模块
处理后台页面的路由和逻辑
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func
from datetime import datetime, timedelta
import os
import json

from . import db
from .models import Member, MemberQuota, APIKey, PromptTemplate, SchoolTemplate, UsageRecord, SensitiveWord, ModelConfig
from .forms import APIKeyForm, PromptTemplateForm, MemberForm, QuotaForm, SchoolTemplateForm, SensitiveWordForm, ModelConfigForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """管理员仪表盘"""
    # 获取今日数据
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 今日新增会员数
    today_members = Member.query.filter(Member.created_at >= today).count()
    
    # 今日额度消耗
    today_credits = db.session.query(func.sum(UsageRecord.credits_used)).filter(UsageRecord.created_at >= today).scalar() or 0
    
    # 今日生成次数
    today_generations = UsageRecord.query.filter(UsageRecord.created_at >= today).count()
    
    # 昨日数据
    yesterday = today - timedelta(days=1)
    yesterday_members = Member.query.filter(Member.created_at >= yesterday, Member.created_at < today).count()
    yesterday_credits = db.session.query(func.sum(UsageRecord.credits_used)).filter(UsageRecord.created_at >= yesterday, UsageRecord.created_at < today).scalar() or 0
    yesterday_generations = UsageRecord.query.filter(UsageRecord.created_at >= yesterday, UsageRecord.created_at < today).count()
    
    # 总体数据
    total_members = Member.query.count()
    total_credits_used = db.session.query(func.sum(UsageRecord.credits_used)).scalar() or 0
    total_generations = UsageRecord.query.count()
    
    # 近7天统计数据
    days = []
    member_counts = []
    usage_counts = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        next_day = day + timedelta(days=1)
        days.append(day.strftime('%m-%d'))
        
        member_count = Member.query.filter(Member.created_at >= day, Member.created_at < next_day).count()
        member_counts.append(member_count)
        
        usage_count = UsageRecord.query.filter(UsageRecord.created_at >= day, UsageRecord.created_at < next_day).count()
        usage_counts.append(usage_count)
    
    # 获取当前时间
    now = datetime.now()
    
    return render_template('admin/dashboard.html',
                          today_members=today_members,
                          today_credits=today_credits,
                          today_generations=today_generations,
                          yesterday_members=yesterday_members,
                          yesterday_credits=yesterday_credits,
                          yesterday_generations=yesterday_generations,
                          total_members=total_members,
                          total_credits_used=total_credits_used,
                          total_generations=total_generations,
                          days=days,
                          member_counts=member_counts,
                          usage_counts=usage_counts,
                          now=now)

@admin_bp.route('/api_keys')
@login_required
def api_keys():
    """API密钥管理"""
    api_keys = APIKey.query.all()
    return render_template('admin/api_keys.html', api_keys=api_keys)

@admin_bp.route('/api_keys/add', methods=['GET', 'POST'])
@login_required
def add_api_key():
    """添加API密钥"""
    form = APIKeyForm()
    if form.validate_on_submit():
        api_key = APIKey(
            api_type=form.api_type.data,
            key_name=form.key_name.data,
            api_key=form.api_key.data,
            api_endpoint=form.api_endpoint.data,
            model_name=form.model_name.data,
            is_active=form.is_active.data
        )
        db.session.add(api_key)
        db.session.commit()
        flash('API密钥添加成功', 'success')
        return redirect(url_for('admin.api_keys'))
    return render_template('admin/api_key_form.html', form=form, title='添加API密钥')

@admin_bp.route('/api_keys/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_api_key(id):
    """编辑API密钥"""
    api_key = APIKey.query.get_or_404(id)
    form = APIKeyForm(obj=api_key)
    if form.validate_on_submit():
        form.populate_obj(api_key)
        db.session.commit()
        flash('API密钥更新成功', 'success')
        return redirect(url_for('admin.api_keys'))
    return render_template('admin/api_key_form.html', form=form, title='编辑API密钥')

@admin_bp.route('/api_keys/delete/<int:id>')
@login_required
def delete_api_key(id):
    """删除API密钥"""
    api_key = APIKey.query.get_or_404(id)
    db.session.delete(api_key)
    db.session.commit()
    flash('API密钥删除成功', 'success')
    return redirect(url_for('admin.api_keys'))

@admin_bp.route('/prompt_templates')
@login_required
def prompt_templates():
    """提示词模板管理"""
    templates = PromptTemplate.query.all()
    return render_template('admin/prompt_templates.html', templates=templates)

@admin_bp.route('/prompt_templates/add', methods=['GET', 'POST'])
@login_required
def add_prompt_template():
    """添加提示词模板"""
    form = PromptTemplateForm()
    if form.validate_on_submit():
        template = PromptTemplate(
            name=form.name.data,
            category=form.category.data,
            content=form.content.data,
            is_active=form.is_active.data
        )
        db.session.add(template)
        db.session.commit()
        flash('提示词模板添加成功', 'success')
        return redirect(url_for('admin.prompt_templates'))
    return render_template('admin/prompt_template_form.html', form=form, title='添加提示词模板')

@admin_bp.route('/prompt_templates/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_prompt_template(id):
    """编辑提示词模板"""
    template = PromptTemplate.query.get_or_404(id)
    form = PromptTemplateForm(obj=template)
    if form.validate_on_submit():
        form.populate_obj(template)
        db.session.commit()
        flash('提示词模板更新成功', 'success')
        return redirect(url_for('admin.prompt_templates'))
    return render_template('admin/prompt_template_form.html', form=form, title='编辑提示词模板')

@admin_bp.route('/prompt_templates/delete/<int:id>')
@login_required
def delete_prompt_template(id):
    """删除提示词模板"""
    template = PromptTemplate.query.get_or_404(id)
    db.session.delete(template)
    db.session.commit()
    flash('提示词模板删除成功', 'success')
    return redirect(url_for('admin.prompt_templates'))

@admin_bp.route('/members')
@login_required
def members():
    """会员管理"""
    members_list = Member.query.all()
    return render_template('admin/members.html', members=members_list)

@admin_bp.route('/members/add', methods=['GET', 'POST'])
@login_required
def add_member():
    """添加会员"""
    form = MemberForm()
    if form.validate_on_submit():
        member = Member(
            username=form.username.data,
            email=form.email.data,
            phone=form.phone.data,
            is_active=form.is_active.data
        )
        if form.password.data:
            member.password = form.password.data
        db.session.add(member)
        db.session.flush()  # 获取member.id
        
        # 创建默认额度
        quota = MemberQuota(
            member_id=member.id,
            total_credits=0,
            remaining_credits=0,
            total_tokens=0,
            remaining_tokens=0
        )
        db.session.add(quota)
        db.session.commit()
        
        flash('会员添加成功', 'success')
        return redirect(url_for('admin.members'))
    return render_template('admin/member_form.html', form=form, title='添加会员')

@admin_bp.route('/members/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_member(id):
    """编辑会员"""
    member = Member.query.get_or_404(id)
    form = MemberForm(obj=member)
    if form.validate_on_submit():
        # 仅当提供了密码时才更新密码
        if form.password.data:
            member.password = form.password.data
        
        # 更新其他字段
        member.username = form.username.data
        member.email = form.email.data
        member.phone = form.phone.data
        member.is_active = form.is_active.data
        
        db.session.commit()
        flash('会员更新成功', 'success')
        return redirect(url_for('admin.members'))
    return render_template('admin/member_form.html', form=form, title='编辑会员')

@admin_bp.route('/members/quota/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_member_quota(id):
    """编辑会员额度"""
    member = Member.query.get_or_404(id)
    quota = member.quota or MemberQuota(member_id=member.id)
    
    form = QuotaForm(obj=quota)
    if form.validate_on_submit():
        form.populate_obj(quota)
        
        if not quota.id:  # 如果是新创建的额度
            db.session.add(quota)
        
        db.session.commit()
        flash('会员额度更新成功', 'success')
        return redirect(url_for('admin.members'))
    
    return render_template('admin/quota_form.html', form=form, member=member, title='编辑会员额度')

@admin_bp.route('/members/delete/<int:id>')
@login_required
def delete_member(id):
    """删除会员"""
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    flash('会员删除成功', 'success')
    return redirect(url_for('admin.members'))

@admin_bp.route('/school_templates')
@login_required
def school_templates():
    """学校模板管理"""
    templates = SchoolTemplate.query.all()
    return render_template('admin/school_templates.html', templates=templates)

@admin_bp.route('/school_templates/add', methods=['GET', 'POST'])
@login_required
def add_school_template():
    """添加学校模板"""
    form = SchoolTemplateForm()
    if form.validate_on_submit():
        # 保存模板文件
        filename = secure_filename(form.template_file.data.filename)
        school_name = secure_filename(form.school_name.data)
        template_name = secure_filename(form.template_name.data)
        unique_filename = f"{school_name}_{template_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(os.path.join(upload_folder, 'templates'), exist_ok=True)
        file_path = os.path.join(upload_folder, 'templates', unique_filename)
        
        form.template_file.data.save(file_path)
        
        # 创建模板记录
        template = SchoolTemplate(
            school_name=form.school_name.data,
            template_name=form.template_name.data,
            file_path=file_path,
            format_rules=form.format_rules.data,
            is_active=form.is_active.data
        )
        db.session.add(template)
        db.session.commit()
        
        flash('学校模板添加成功', 'success')
        return redirect(url_for('admin.school_templates'))
    
    return render_template('admin/school_template_form.html', form=form, title='添加学校模板')

@admin_bp.route('/school_templates/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_school_template(id):
    """编辑学校模板"""
    template = SchoolTemplate.query.get_or_404(id)
    form = SchoolTemplateForm(obj=template)
    
    if form.validate_on_submit():
        # 如果上传了新文件
        if form.template_file.data:
            # 删除旧文件
            if os.path.exists(template.file_path):
                os.remove(template.file_path)
            
            # 保存新文件
            filename = secure_filename(form.template_file.data.filename)
            school_name = secure_filename(form.school_name.data)
            template_name = secure_filename(form.template_name.data)
            unique_filename = f"{school_name}_{template_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
            
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(os.path.join(upload_folder, 'templates'), exist_ok=True)
            file_path = os.path.join(upload_folder, 'templates', unique_filename)
            
            form.template_file.data.save(file_path)
            template.file_path = file_path
        
        # 更新其他字段
        template.school_name = form.school_name.data
        template.template_name = form.template_name.data
        template.format_rules = form.format_rules.data
        template.is_active = form.is_active.data
        
        db.session.commit()
        flash('学校模板更新成功', 'success')
        return redirect(url_for('admin.school_templates'))
    
    return render_template('admin/school_template_form.html', form=form, title='编辑学校模板')

@admin_bp.route('/school_templates/download/<int:id>')
@login_required
def download_school_template(id):
    """下载学校模板"""
    template = SchoolTemplate.query.get_or_404(id)
    directory = os.path.dirname(template.file_path)
    filename = os.path.basename(template.file_path)
    return send_from_directory(directory, filename, as_attachment=True)

@admin_bp.route('/school_templates/delete/<int:id>')
@login_required
def delete_school_template(id):
    """删除学校模板"""
    template = SchoolTemplate.query.get_or_404(id)
    
    # 删除文件
    if os.path.exists(template.file_path):
        os.remove(template.file_path)
    
    # 删除记录
    db.session.delete(template)
    db.session.commit()
    
    flash('学校模板删除成功', 'success')
    return redirect(url_for('admin.school_templates'))

@admin_bp.route('/sensitive_words')
@login_required
def sensitive_words():
    """敏感词管理"""
    words = SensitiveWord.query.all()
    return render_template('admin/sensitive_words.html', words=words)

@admin_bp.route('/sensitive_words/add', methods=['GET', 'POST'])
@login_required
def add_sensitive_word():
    """添加敏感词"""
    form = SensitiveWordForm()
    if form.validate_on_submit():
        word = SensitiveWord(
            word=form.word.data,
            is_active=form.is_active.data
        )
        db.session.add(word)
        db.session.commit()
        flash('敏感词添加成功', 'success')
        return redirect(url_for('admin.sensitive_words'))
    return render_template('admin/sensitive_word_form.html', form=form, title='添加敏感词')

@admin_bp.route('/sensitive_words/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_sensitive_word(id):
    """编辑敏感词"""
    word = SensitiveWord.query.get_or_404(id)
    form = SensitiveWordForm(obj=word)
    if form.validate_on_submit():
        form.populate_obj(word)
        db.session.commit()
        flash('敏感词更新成功', 'success')
        return redirect(url_for('admin.sensitive_words'))
    return render_template('admin/sensitive_word_form.html', form=form, title='编辑敏感词')

@admin_bp.route('/sensitive_words/delete/<int:id>')
@login_required
def delete_sensitive_word(id):
    """删除敏感词"""
    word = SensitiveWord.query.get_or_404(id)
    db.session.delete(word)
    db.session.commit()
    flash('敏感词删除成功', 'success')
    return redirect(url_for('admin.sensitive_words'))

@admin_bp.route('/usage_records')
@login_required
def usage_records():
    """使用记录"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    records = UsageRecord.query.order_by(UsageRecord.created_at.desc()).paginate(page=page, per_page=per_page)
    return render_template('admin/usage_records.html', records=records)

@admin_bp.route('/model_configs')
@login_required
def model_configs():
    """AI模型配置管理"""
    configs = ModelConfig.query.all()
    return render_template('admin/model_configs.html', configs=configs)

@admin_bp.route('/model_configs/add', methods=['GET', 'POST'])
@login_required
def add_model_config():
    """添加AI模型配置"""
    form = ModelConfigForm()
    if form.validate_on_submit():
        config = ModelConfig(
            task_type=form.task_type.data,
            education_level=form.education_level.data,
            api_type=form.api_type.data,
            model_name=form.model_name.data,
            temperature=form.temperature.data,
            max_tokens=form.max_tokens.data,
            top_p=form.top_p.data,
            frequency_penalty=form.frequency_penalty.data,
            presence_penalty=form.presence_penalty.data,
            is_active=form.is_active.data
        )
        db.session.add(config)
        db.session.commit()
        flash('AI模型配置添加成功', 'success')
        return redirect(url_for('admin.model_configs'))
    return render_template('admin/model_config_form.html', form=form, title='添加AI模型配置')

@admin_bp.route('/model_configs/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_model_config(id):
    """编辑AI模型配置"""
    config = ModelConfig.query.get_or_404(id)
    form = ModelConfigForm(obj=config)
    if form.validate_on_submit():
        form.populate_obj(config)
        db.session.commit()
        flash('AI模型配置更新成功', 'success')
        return redirect(url_for('admin.model_configs'))
    return render_template('admin/model_config_form.html', form=form, title='编辑AI模型配置')

@admin_bp.route('/model_configs/delete/<int:id>')
@login_required
def delete_model_config(id):
    """删除AI模型配置"""
    config = ModelConfig.query.get_or_404(id)
    db.session.delete(config)
    db.session.commit()
    flash('AI模型配置删除成功', 'success')
    return redirect(url_for('admin.model_configs'))

@admin_bp.route('/model_configs/api/get/<int:id>')
@login_required
def get_model_config(id):
    """获取模型配置详情API"""
    config = ModelConfig.query.get_or_404(id)
    return jsonify({
        'success': True,
        'config': {
            'id': config.id,
            'task_type': config.task_type,
            'education_level': config.education_level,
            'api_type': config.api_type,
            'model_name': config.model_name,
            'temperature': config.temperature,
            'max_tokens': config.max_tokens,
            'top_p': config.top_p,
            'frequency_penalty': config.frequency_penalty,
            'presence_penalty': config.presence_penalty,
            'is_active': config.is_active,
            'created_at': config.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': config.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })
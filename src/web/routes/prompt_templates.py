"""
提示词模板路由
处理提示词模板的CRUD操作
"""

import json
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from src.web import db
from src.web.models.prompt_template import PromptTemplate, TEMPLATE_TYPES

# 创建蓝图
prompt_bp = Blueprint('prompts', __name__, url_prefix='/prompts')

@prompt_bp.route('/', methods=['GET'])
@login_required
def index():
    """提示词模板列表页面"""
    templates = PromptTemplate.query.all()
    return render_template('prompts/index.html', templates=templates, template_types=TEMPLATE_TYPES)

@prompt_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_template():
    """添加提示词模板"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        template_type = request.form.get('template_type')
        content = request.form.get('content')
        variables = request.form.get('variables')
        
        # 验证必填字段
        if not name or not template_type or not content:
            flash('名称、类型和内容为必填项', 'error')
            return redirect(url_for('prompts.add_template'))
        
        # 检查名称是否已存在
        existing = PromptTemplate.query.filter_by(name=name).first()
        if existing:
            flash('模板名称已存在', 'error')
            return redirect(url_for('prompts.add_template'))
        
        # 验证变量格式
        if variables:
            try:
                json.loads(variables)
            except json.JSONDecodeError:
                flash('变量格式不正确，请使用有效的JSON格式', 'error')
                return redirect(url_for('prompts.add_template'))
        
        # 创建新模板
        template = PromptTemplate(
            name=name,
            description=description,
            template_type=template_type,
            content=content,
            variables=variables,
            is_active=True
        )
        
        db.session.add(template)
        
        try:
            db.session.commit()
            flash('提示词模板添加成功', 'success')
            return redirect(url_for('prompts.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加模板失败: {str(e)}', 'error')
            return redirect(url_for('prompts.add_template'))
    
    # GET请求，显示添加表单
    return render_template('prompts/form.html', template=None, template_types=TEMPLATE_TYPES)

@prompt_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_template(id):
    """编辑提示词模板"""
    template = PromptTemplate.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        template_type = request.form.get('template_type')
        content = request.form.get('content')
        variables = request.form.get('variables')
        is_active = 'is_active' in request.form
        
        # 验证必填字段
        if not name or not template_type or not content:
            flash('名称、类型和内容为必填项', 'error')
            return redirect(url_for('prompts.edit_template', id=id))
        
        # 检查名称是否已存在（排除当前模板）
        existing = PromptTemplate.query.filter(PromptTemplate.name == name, PromptTemplate.id != id).first()
        if existing:
            flash('模板名称已存在', 'error')
            return redirect(url_for('prompts.edit_template', id=id))
        
        # 验证变量格式
        if variables:
            try:
                json.loads(variables)
            except json.JSONDecodeError:
                flash('变量格式不正确，请使用有效的JSON格式', 'error')
                return redirect(url_for('prompts.edit_template', id=id))
        
        # 更新模板
        template.name = name
        template.description = description
        template.template_type = template_type
        template.content = content
        template.variables = variables
        template.is_active = is_active
        
        try:
            db.session.commit()
            flash('提示词模板更新成功', 'success')
            return redirect(url_for('prompts.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新模板失败: {str(e)}', 'error')
            return redirect(url_for('prompts.edit_template', id=id))
    
    # GET请求，显示编辑表单
    return render_template('prompts/form.html', template=template, template_types=TEMPLATE_TYPES)

@prompt_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_template(id):
    """删除提示词模板"""
    template = PromptTemplate.query.get_or_404(id)
    
    try:
        db.session.delete(template)
        db.session.commit()
        flash('提示词模板删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除模板失败: {str(e)}', 'error')
    
    return redirect(url_for('prompts.index'))

@prompt_bp.route('/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_template(id):
    """切换模板启用状态"""
    template = PromptTemplate.query.get_or_404(id)
    template.is_active = not template.is_active
    
    try:
        db.session.commit()
        status = '启用' if template.is_active else '禁用'
        flash(f'提示词模板已{status}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'更新模板状态失败: {str(e)}', 'error')
    
    return redirect(url_for('prompts.index'))

# API路由
@prompt_bp.route('/api/list', methods=['GET'])
@login_required
def api_list_templates():
    """API: 获取模板列表"""
    template_type = request.args.get('type')
    
    if template_type:
        templates = PromptTemplate.query.filter_by(template_type=template_type, is_active=True).all()
    else:
        templates = PromptTemplate.query.filter_by(is_active=True).all()
    
    return jsonify({
        'success': True,
        'templates': [template.to_dict() for template in templates]
    })

@prompt_bp.route('/api/get/<int:id>', methods=['GET'])
@login_required
def api_get_template(id):
    """API: 获取单个模板"""
    template = PromptTemplate.query.get_or_404(id)
    
    return jsonify({
        'success': True,
        'template': template.to_dict()
    })

@prompt_bp.route('/api/get_by_name/<string:name>', methods=['GET'])
@login_required
def api_get_template_by_name(name):
    """API: 根据名称获取模板"""
    template = PromptTemplate.query.filter_by(name=name, is_active=True).first()
    
    if not template:
        return jsonify({
            'success': False,
            'message': '模板不存在或已禁用'
        }), 404
    
    return jsonify({
        'success': True,
        'template': template.to_dict()
    }) 
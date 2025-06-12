"""
批注处理路由
处理PDF批注文件上传、分析和处理
"""

import os
import tempfile
import time
from flask import Blueprint, request, jsonify, render_template, current_app, send_file, url_for, redirect, flash, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from src.models.annotation_processor import annotation_processor
from src.models.api_manager import api_manager

# 创建蓝图
annotation_bp = Blueprint('annotation', __name__, url_prefix='/annotation')

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@annotation_bp.before_request
def before_request():
    """请求前处理，确保session可用"""
    if 'annotation_data' not in session:
        session['annotation_data'] = {}

@annotation_bp.route('/', methods=['GET'])
@login_required
def index():
    """批注处理首页"""
    return render_template('annotation/index.html')

@annotation_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """上传PDF文件并处理批注"""
    if 'file' not in request.files:
        flash('没有选择文件', 'error')
        return redirect(url_for('annotation.index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('没有选择文件', 'error')
        return redirect(url_for('annotation.index'))
    
    if file and allowed_file(file.filename):
        # 创建临时目录保存上传的文件
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'annotations')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 安全的文件名
        timestamp = int(time.time())
        filename = f"{timestamp}_{secure_filename(file.filename)}"
        filepath = os.path.join(upload_dir, filename)
        
        # 保存文件
        file.save(filepath)
        
        try:
            # 设置API管理器
            annotation_processor.api_manager = api_manager
            
            # 提取批注
            annotations = annotation_processor.extract_annotations(filepath)
            
            if not annotations:
                flash('未在PDF中找到任何批注', 'warning')
                return redirect(url_for('annotation.index'))
            
            # 处理批注
            annotation_processor.process_annotations()
            
            # 保存会话中的文件路径
            session['annotation_data'] = {
                'filepath': filepath,
                'filename': file.filename,
                'annotation_count': len(annotations),
                'timestamp': timestamp
            }
            
            # 重定向到预览页面
            return redirect(url_for('annotation.preview', file_id=timestamp))
        
        except Exception as e:
            flash(f'处理PDF批注时出错: {str(e)}', 'error')
            return redirect(url_for('annotation.index'))
    
    flash('不支持的文件类型，请上传PDF文件', 'error')
    return redirect(url_for('annotation.index'))

@annotation_bp.route('/preview/<int:file_id>', methods=['GET'])
@login_required
def preview(file_id):
    """预览批注和修改"""
    # 从会话中获取文件信息
    annotation_data = session.get('annotation_data')
    
    if annotation_data and annotation_data.get('timestamp') == file_id:
        filepath = annotation_data.get('filepath')
        filename = annotation_data.get('filename')
        
        if os.path.exists(filepath):
            # 获取处理结果
            annotations = annotation_processor.annotations
            
            return render_template(
                'annotation/preview.html',
                file_id=file_id,
                filename=filename,
                annotations=annotations
            )
    
    # 如果会话中没有数据，尝试从上传目录查找
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'annotations')
    
    # 查找对应的文件
    found_file = None
    for filename in os.listdir(upload_dir):
        if filename.startswith(f"{file_id}_"):
            found_file = filename
            break
    
    if not found_file:
        flash('找不到上传的文件', 'error')
        return redirect(url_for('annotation.index'))
    
    filepath = os.path.join(upload_dir, found_file)
    original_filename = found_file[found_file.index('_')+1:]
    
    try:
        # 重新处理文件
        annotation_processor.api_manager = api_manager
        annotation_processor.extract_annotations(filepath)
        annotation_processor.process_annotations()
        
        # 获取处理结果
        annotations = annotation_processor.annotations
        
        return render_template(
            'annotation/preview.html',
            file_id=file_id,
            filename=original_filename,
            annotations=annotations
        )
    except Exception as e:
        flash(f'处理PDF批注时出错: {str(e)}', 'error')
        return redirect(url_for('annotation.index'))

@annotation_bp.route('/download/<int:file_id>', methods=['GET'])
@login_required
def download(file_id):
    """下载修改后的文档"""
    # 从会话中获取文件信息
    annotation_data = session.get('annotation_data')
    
    if annotation_data and annotation_data.get('timestamp') == file_id:
        filepath = annotation_data.get('filepath')
        filename = annotation_data.get('filename')
        
        if os.path.exists(filepath):
            output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'outputs')
            os.makedirs(output_dir, exist_ok=True)
            
            filename_without_ext = os.path.splitext(filename)[0]
            output_filename = f"{filename_without_ext}_修改后.docx"
            output_path = os.path.join(output_dir, output_filename)
            
            try:
                output_path = annotation_processor.generate_corrected_document(output_path)
                return send_file(
                    output_path,
                    as_attachment=True,
                    download_name=output_filename,
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
            except Exception as e:
                flash(f'生成修改后文档时出错: {str(e)}', 'error')
                return redirect(url_for('annotation.preview', file_id=file_id))
    
    # 如果会话中没有数据，尝试从上传目录查找
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'annotations')
    output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找对应的文件
    found_file = None
    for filename in os.listdir(upload_dir):
        if filename.startswith(f"{file_id}_"):
            found_file = filename
            break
    
    if not found_file:
        flash('找不到上传的文件', 'error')
        return redirect(url_for('annotation.index'))
    
    filepath = os.path.join(upload_dir, found_file)
    original_filename = found_file[found_file.index('_')+1:]
    filename_without_ext = os.path.splitext(original_filename)[0]
    
    # 生成修改后的文档
    output_filename = f"{filename_without_ext}_修改后.docx"
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        # 确保已处理批注
        if not annotation_processor.annotations:
            annotation_processor.api_manager = api_manager
            annotation_processor.extract_annotations(filepath)
            annotation_processor.process_annotations()
            
        output_path = annotation_processor.generate_corrected_document(output_path)
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        flash(f'生成修改后文档时出错: {str(e)}', 'error')
        return redirect(url_for('annotation.preview', file_id=file_id))

@annotation_bp.route('/regenerate/<int:file_id>/<int:annotation_idx>', methods=['POST'])
@login_required
def regenerate(file_id, annotation_idx):
    """重新生成特定批注的替换文本"""
    try:
        # 获取新的自定义替换文本
        data = request.get_json()
        custom_text = data.get('custom_text', '')
        
        # 更新批注的替换文本
        annotations = annotation_processor.annotations
        if 0 <= annotation_idx < len(annotations):
            annotations[annotation_idx].replaced_text = custom_text
            annotations[annotation_idx].processed = True
            return jsonify({'success': True, 'message': '更新成功'})
        else:
            return jsonify({'success': False, 'message': '批注索引无效'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500 
"""
身份验证模块
处理用户登录、登出和鉴权
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from . import db
from .models import AdminUser
from .forms import LoginForm
from .config import Config
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """管理员登录"""
    # 如果用户已登录，重定向到管理界面
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
        
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # 查询用户
        user = AdminUser.query.filter_by(username=username).first()
        
        # 验证密码
        if user and user.verify_password(password):
            login_user(user, remember=form.remember.data)
            user.last_login = datetime.datetime.now()
            db.session.commit()
            
            # 获取请求中的next参数
            next_page = request.args.get('next')
            if not next_page or next_page.startswith('/'):
                next_page = url_for('admin.dashboard')
                
            # 记录IP和登录信息
            session['ip_address'] = request.remote_addr
            session['user_agent'] = request.user_agent.string
            
            flash('登录成功', 'success')
            return redirect(next_page)
        else:
            flash('用户名或密码错误', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """管理员登出"""
    logout_user()
    flash('您已退出登录', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.before_app_first_request
def create_default_admin():
    """创建默认管理员账号"""
    if AdminUser.query.filter_by(username=Config.DEFAULT_ADMIN_USERNAME).first() is None:
        default_admin = AdminUser(
            username=Config.DEFAULT_ADMIN_USERNAME,
            email='admin@example.com',
            is_active=True
        )
        default_admin.password = Config.DEFAULT_ADMIN_PASSWORD
        
        db.session.add(default_admin)
        db.session.commit() 
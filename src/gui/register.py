import tkinter as tk
from tkinter import ttk, messagebox
from utils.database import Database
from utils.exceptions import DatabaseError, ValidationError
from utils.validators import InputValidator
from config.settings import THEME_COLORS

class RegisterWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("注册新用户")
        self.window.geometry("400x600")
        self.window.configure(bg=THEME_COLORS['background'])
        
        self.db = Database()
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, style='Login.TFrame')
        main_frame.pack(padx=40, pady=40, fill='both', expand=True)
        
        # 标题
        ttk.Label(
            main_frame,
            text="注册新用户",
            font=('微软雅黑', 20, 'bold'),
            foreground=THEME_COLORS['primary'],
            background=THEME_COLORS['card']
        ).pack(pady=20)
        
        # 用户名
        self.username_var = tk.StringVar()
        ttk.Label(main_frame, text="用户名", style='Login.TLabel').pack(pady=(20,5))
        ttk.Entry(main_frame, textvariable=self.username_var, width=30).pack()
        
        # 邮箱
        self.email_var = tk.StringVar()
        ttk.Label(main_frame, text="邮箱", style='Login.TLabel').pack(pady=(20,5))
        ttk.Entry(main_frame, textvariable=self.email_var, width=30).pack()
        
        # 密码
        self.password_var = tk.StringVar()
        ttk.Label(main_frame, text="密码", style='Login.TLabel').pack(pady=(20,5))
        ttk.Entry(main_frame, textvariable=self.password_var, show="*", width=30).pack()
        
        # 确认密码
        self.confirm_password_var = tk.StringVar()
        ttk.Label(main_frame, text="确认密码", style='Login.TLabel').pack(pady=(20,5))
        ttk.Entry(main_frame, textvariable=self.confirm_password_var, show="*", width=30).pack()
        
        # 注册按钮
        ttk.Button(
            main_frame,
            text="注册",
            command=self.register,
            style='Login.TButton'
        ).pack(pady=30)
        
    def register(self):
        """处理注册逻辑"""
        try:
            username = self.username_var.get().strip()
            email = self.email_var.get().strip()
            password = self.password_var.get()
            confirm_password = self.confirm_password_var.get()
            
            # 验证输入
            InputValidator.validate_username(username)
            InputValidator.validate_email(email)
            InputValidator.validate_password(password)
            
            if password != confirm_password:
                raise ValidationError("两次输入的密码不一致")
            
            # 添加用户
            self.db.add_user(username, password, email)
            messagebox.showinfo("成功", "注册成功！请返回登录。")
            self.window.destroy()
            
        except ValidationError as e:
            messagebox.showerror("输入错误", str(e))
        except DatabaseError as e:
            messagebox.showerror("注册失败", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"发生未知错误: {str(e)}")
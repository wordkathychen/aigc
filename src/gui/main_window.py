"""
GUI主窗口模块
用于创建和管理应用程序的图形界面
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import threading
import queue

logger = logging.getLogger(__name__)

class MainWindow:
    """主窗口类"""
    
    def __init__(self, root):
        """初始化主窗口
        
        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title("AI文本生成器")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 设置应用图标
        try:
            icon_path = self._get_resource_path("resources/icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"设置图标失败: {str(e)}")
        
        # 创建消息队列
        self.queue = queue.Queue()
        
        # 创建UI组件
        self._create_menu()
        self._create_main_frame()
        
        # 定期检查消息队列
        self.root.after(100, self._process_queue)
    
    def _get_resource_path(self, relative_path):
        """获取资源文件的绝对路径
        
        Args:
            relative_path: 相对路径
            
        Returns:
            资源文件的绝对路径
        """
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            base_path = sys._MEIPASS
        else:
            # 如果是开发环境
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        return os.path.join(base_path, relative_path)
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建", command=self._new_file)
        file_menu.add_command(label="打开", command=self._open_file)
        file_menu.add_command(label="保存", command=self._save_file)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="批注处理", command=self._open_annotation_window)
        tools_menu.add_command(label="设置", command=self._open_settings)
        menubar.add_cascade(label="工具", menu=tools_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def _create_main_frame(self):
        """创建主框架"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建顶部控制区域
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建标签和输入框
        ttk.Label(control_frame, text="主题:").pack(side=tk.LEFT, padx=(0, 5))
        self.topic_entry = ttk.Entry(control_frame, width=40)
        self.topic_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(control_frame, text="字数:").pack(side=tk.LEFT, padx=(0, 5))
        self.word_count = ttk.Spinbox(control_frame, from_=100, to=10000, increment=100, width=10)
        self.word_count.set(1000)
        self.word_count.pack(side=tk.LEFT, padx=(0, 10))
        
        # 创建生成按钮
        self.generate_button = ttk.Button(control_frame, text="生成文本", command=self._generate_text)
        self.generate_button.pack(side=tk.RIGHT, padx=5)
        
        # 创建批注处理按钮
        self.annotation_button = ttk.Button(control_frame, text="批注处理", command=self._open_annotation_window)
        self.annotation_button.pack(side=tk.RIGHT, padx=5)
        
        # 创建分隔线
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=5)
        
        # 创建文本编辑区
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_editor = ScrolledText(text_frame, wrap=tk.WORD, font=("TkDefaultFont", 11))
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        
        # 创建状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _process_queue(self):
        """处理消息队列"""
        try:
            while True:
                message = self.queue.get_nowait()
                
                if message["type"] == "status":
                    self.status_var.set(message["text"])
                elif message["type"] == "result":
                    self.text_editor.delete(1.0, tk.END)
                    self.text_editor.insert(tk.END, message["text"])
                    self.status_var.set("生成完成")
                    self.generate_button.config(state=tk.NORMAL)
                elif message["type"] == "error":
                    messagebox.showerror("错误", message["text"])
                    self.status_var.set("就绪")
                    self.generate_button.config(state=tk.NORMAL)
                
                self.queue.task_done()
        
        except queue.Empty:
            pass
        
        # 继续检查队列
        self.root.after(100, self._process_queue)
    
    def _generate_text(self):
        """生成文本"""
        topic = self.topic_entry.get().strip()
        if not topic:
            messagebox.showwarning("警告", "请输入主题")
            return
        
        try:
            word_count = int(self.word_count.get())
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的字数")
            return
        
        # 禁用生成按钮
        self.generate_button.config(state=tk.DISABLED)
        self.status_var.set("正在生成文本...")
        
        # 在后台线程中生成文本
        threading.Thread(target=self._generate_text_thread, args=(topic, word_count), daemon=True).start()
    
    def _generate_text_thread(self, topic, word_count):
        """在后台线程中生成文本
        
        Args:
            topic: 主题
            word_count: 字数
        """
        try:
            # 这里应该调用实际的文本生成API
            # 示例代码，实际应用中应替换为真实的API调用
            from src.models.client_init import client_initializer
            
            # 检查Web后台连接
            if client_initializer.check_connection():
                self.queue.put({"type": "status", "text": "已连接到Web后台，正在生成文本..."})
                # 这里应该调用Web API生成文本
                # 示例代码
                import time
                time.sleep(2)  # 模拟API调用
                result = f"这是关于"{topic}"的AI生成文本，字数约{word_count}字。\n\n"
                result += "这只是一个示例文本，实际应用中应替换为真实的API调用结果。" * 10
            else:
                self.queue.put({"type": "status", "text": "使用本地模式生成文本..."})
                # 使用本地模式生成文本
                import time
                time.sleep(2)  # 模拟生成过程
                result = f"[本地模式] 这是关于"{topic}"的AI生成文本，字数约{word_count}字。\n\n"
                result += "这只是一个示例文本，实际应用中应替换为真实的本地生成结果。" * 10
            
            # 将结果放入队列
            self.queue.put({"type": "result", "text": result})
        
        except Exception as e:
            logger.error(f"生成文本失败: {str(e)}", exc_info=True)
            self.queue.put({"type": "error", "text": f"生成文本失败: {str(e)}"})
    
    def _new_file(self):
        """新建文件"""
        if messagebox.askyesno("确认", "是否清空当前内容？"):
            self.text_editor.delete(1.0, tk.END)
            self.topic_entry.delete(0, tk.END)
            self.status_var.set("新建文件")
    
    def _open_file(self):
        """打开文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(tk.END, content)
                self.status_var.set(f"已打开: {file_path}")
            
            except Exception as e:
                messagebox.showerror("错误", f"打开文件失败: {str(e)}")
    
    def _save_file(self):
        """保存文件"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                content = self.text_editor.get(1.0, tk.END)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                self.status_var.set(f"已保存: {file_path}")
            
            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败: {str(e)}")
    
    def _open_annotation_window(self):
        """打开批注处理窗口"""
        # 检查Web后台连接
        from src.models.client_init import client_initializer
        if not client_initializer.check_connection():
            messagebox.showwarning("警告", "无法连接到Web后台，批注处理功能需要Web后台支持")
            return
        
        # 提示用户在Web浏览器中访问批注处理页面
        messagebox.showinfo("批注处理", 
                          "批注处理功能将在Web浏览器中打开\n"
                          "请访问: http://localhost:5000/annotation")
        
        # 尝试打开浏览器
        try:
            import webbrowser
            webbrowser.open("http://localhost:5000/annotation")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开浏览器: {str(e)}")
    
    def _open_settings(self):
        """打开设置窗口"""
        # 创建设置窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("500x400")
        settings_window.grab_set()  # 模态窗口
        
        # 添加设置选项
        ttk.Label(settings_window, text="设置", font=("TkDefaultFont", 14, "bold")).pack(pady=10)
        
        # Web后台设置
        web_frame = ttk.LabelFrame(settings_window, text="Web后台设置")
        web_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 导入客户端配置
        from src.config.client_config import WEB_API_URL, WEB_ENABLED, save_user_config
        
        # 服务器地址设置
        ttk.Label(web_frame, text="服务器地址:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        server_url_var = tk.StringVar(value=WEB_API_URL)
        server_url_entry = ttk.Entry(web_frame, width=40, textvariable=server_url_var)
        server_url_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 启用Web后台选项
        web_enabled_var = tk.BooleanVar(value=WEB_ENABLED)
        web_enabled_check = ttk.Checkbutton(web_frame, text="启用Web后台功能", variable=web_enabled_var)
        web_enabled_check.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # 测试连接按钮
        def test_connection():
            url = server_url_var.get()
            if not url:
                messagebox.showwarning("警告", "请输入服务器地址")
                return
            
            # 显示测试中提示
            test_button.config(state=tk.DISABLED)
            test_label.config(text="正在测试连接...")
            settings_window.update()
            
            # 测试连接
            try:
                import requests
                response = requests.get(f"{url}/check_environment", timeout=5)
                if response.status_code == 200:
                    test_label.config(text="连接成功！", foreground="green")
                else:
                    test_label.config(text=f"连接失败: HTTP {response.status_code}", foreground="red")
            except Exception as e:
                test_label.config(text=f"连接错误: {str(e)}", foreground="red")
            
            # 恢复按钮状态
            test_button.config(state=tk.NORMAL)
        
        test_button = ttk.Button(web_frame, text="测试连接", command=test_connection)
        test_button.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        test_label = ttk.Label(web_frame, text="")
        test_label.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 用户认证设置
        auth_frame = ttk.LabelFrame(settings_window, text="用户认证")
        auth_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(auth_frame, text="用户名:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        username_entry = ttk.Entry(auth_frame, width=40)
        username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(auth_frame, text="密码:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        password_entry = ttk.Entry(auth_frame, width=40, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 登录按钮
        def login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            
            if not username or not password:
                messagebox.showwarning("警告", "请输入用户名和密码")
                return
            
            # 显示登录中提示
            login_button.config(state=tk.DISABLED)
            login_label.config(text="正在登录...")
            settings_window.update()
            
            # 尝试登录
            from src.models.client_init import client_initializer
            success, message = client_initializer.login(username, password)
            
            if success:
                login_label.config(text="登录成功！", foreground="green")
            else:
                login_label.config(text=f"登录失败: {message}", foreground="red")
            
            # 恢复按钮状态
            login_button.config(state=tk.NORMAL)
        
        login_button = ttk.Button(auth_frame, text="登录", command=login)
        login_button.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        login_label = ttk.Label(auth_frame, text="")
        login_label.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 按钮
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_settings():
            # 保存配置
            url = server_url_var.get()
            enabled = web_enabled_var.get()
            
            if save_user_config(web_api_url=url, web_enabled=enabled):
                messagebox.showinfo("成功", "设置已保存")
                settings_window.destroy()
            else:
                messagebox.showerror("错误", "保存设置失败")
        
        ttk.Button(button_frame, text="保存", command=save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
        AI文本生成器使用说明
        
        1. 输入主题和所需字数
        2. 点击"生成文本"按钮
        3. 等待文本生成完成
        4. 可以编辑生成的文本
        5. 使用"保存"功能保存文本
        
        批注处理功能:
        - 点击"批注处理"按钮
        - 在Web界面上传带批注的PDF文件
        - 系统会自动分析批注并修改文本
        - 可以下载修改后的文档
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("使用说明")
        help_window.geometry("500x400")
        
        help_text_widget = ScrolledText(help_window, wrap=tk.WORD)
        help_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)
    
    def _show_about(self):
        """显示关于信息"""
        about_text = """
        AI文本生成器
        
        版本: 1.0.0
        
        功能:
        - 智能文本生成
        - PDF批注处理
        - 文本编辑和保存
        
        © 2023 AI文本生成器团队
        """
        
        messagebox.showinfo("关于", about_text)


def start_application():
    """启动应用程序"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    start_application() 
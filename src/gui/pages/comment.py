from . import BasePage
from tkinter import ttk, scrolledtext
from tkinter import filedialog
import tkinter as tk
from tkinter import messagebox
from models.comment_processor import CommentProcessor
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CommentEditor(BasePage):
    def create_widgets(self):
        # 标题
        ttk.Label(
            self,
            text="批注修改",
            style='Title.TLabel'
        ).pack(pady=20)
        
        # 上传区域
        upload_frame = ttk.LabelFrame(self, text="文件上传", style='Card.TFrame')
        upload_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(
            upload_frame,
            text="上传带批注文档",
            command=self.upload_file
        ).pack(pady=10)
        
        # 批注列表
        comments_frame = ttk.LabelFrame(self, text="批注列表", style='Card.TFrame')
        comments_frame.pack(fill='x', padx=20, pady=10)
        
        self.comments_list = ttk.Treeview(
            comments_frame,
            columns=("location", "content", "status"),
            show="headings"
        )
        
        self.comments_list.heading("location", text="位置")
        self.comments_list.heading("content", text="批注内容")
        self.comments_list.heading("status", text="状态")
        
        self.comments_list.pack(fill='x', padx=5, pady=5)
        
        # 修改区域
        edit_frame = ttk.LabelFrame(self, text="修改区域", style='Card.TFrame')
        edit_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.edit_text = scrolledtext.ScrolledText(edit_frame)
        self.edit_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 操作按钮
        button_frame = ttk.Frame(self, style='Dark.TFrame')
        button_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(
            button_frame,
            text="自动修改",
            command=self.auto_fix
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="导出文档",
            command=self.export_document
        ).pack(side='right', padx=5)
        
        # 工具栏
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(toolbar, text="添加批注", 
                  command=self._add_comment).pack(side='left', padx=5)
        ttk.Button(toolbar, text="刷新列表", 
                  command=self._refresh_comments).pack(side='left', padx=5)
        
        # 右键菜单
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="编辑", command=self._edit_comment)
        self.context_menu.add_command(label="标记完成", command=self._resolve_comment)
        self.context_menu.add_command(label="删除", command=self._delete_comment)
        
        self.comments_list.bind('<Button-3>', self._show_context_menu)
        
    def upload_file(self):
        file = filedialog.askopenfilename(
            title="选择文档",
            filetypes=[("Word文件", "*.docx;*.doc")]
        )
        if file:
            self.edit_text.insert('end', f"已上传文件：{file}\n")
            # 这里应该解析文档中的批注并显示在列表中
            
    def auto_fix(self):
        self.edit_text.insert('end', "正在自动处理批注...\n")
        
    def export_document(self):
        file = filedialog.asksaveasfilename(
            title="保存文档",
            filetypes=[("Word文件", "*.docx")]
        )
        if file:
            self.edit_text.insert('end', f"文档已导出：{file}\n")
            
    def set_document(self, document_id: str):
        """设置当前文档"""
        self.current_document_id = document_id
        self._refresh_comments()
        
    def _add_comment(self):
        """添加批注"""
        if not self.current_document_id:
            messagebox.showerror("错误", "请先选择文档")
            return
            
        dialog = CommentDialog(self)
        if dialog.result:
            try:
                comment = self.processor.process_comment(
                    self.current_document_id,
                    dialog.result
                )
                self._refresh_comments()
            except Exception as e:
                logger.error(f"添加批注失败: {str(e)}")
                messagebox.showerror("错误", str(e))
                
    def _refresh_comments(self):
        """刷新批注列表"""
        if not self.current_document_id:
            return
            
        # 清空列表
        for item in self.comments_list.get_children():
            self.comments_list.delete(item)
            
        try:
            # 获取并显示批注
            comments = self.processor.manager.get_comments(self.current_document_id)
            for comment in comments:
                self.comments_list.insert('', 'end', values=(
                    comment['id'],
                    comment['author'],
                    comment['content'][:50] + '...' if len(comment['content']) > 50 else comment['content'],
                    comment['created_at'].split('T')[0],
                    '已解决' if comment['resolved'] else '未解决'
                ))
        except Exception as e:
            logger.error(f"刷新批注失败: {str(e)}")
            messagebox.showerror("错误", str(e))
            
    def _show_context_menu(self, event):
        """显示右键菜单"""
        item = self.comments_list.identify_row(event.y)
        if item:
            self.comments_list.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def _edit_comment(self):
        """编辑批注"""
        selected = self.comments_list.selection()
        if not selected:
            return
            
        item = selected[0]
        comment_id = self.comments_list.item(item)['values'][0]
        
        dialog = CommentDialog(
            self, 
            initial_content=self.comments_list.item(item)['values'][2]
        )
        
        if dialog.result:
            try:
                self.processor.manager.update_comment(
                    self.current_document_id,
                    comment_id,
                    dialog.result['content']
                )
                self._refresh_comments()
            except Exception as e:
                logger.error(f"编辑批注失败: {str(e)}")
                messagebox.showerror("错误", str(e))

class CommentDialog(tk.Toplevel):
    def __init__(self, parent, initial_content=None):
        super().__init__(parent)
        self.title("批注")
        self.result = None
        self.initial_content = initial_content
        self.setup_ui()
        
    def setup_ui(self):
        # 内容输入
        ttk.Label(self, text="批注内容:").pack(padx=5, pady=5)
        
        self.content = tk.Text(self, height=5, width=40)
        self.content.pack(padx=5, pady=5)
        
        if self.initial_content:
            self.content.insert('1.0', self.initial_content)
            
        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="确定", 
                  command=self._confirm).pack(side='right', padx=5)
        ttk.Button(button_frame, text="取消", 
                  command=self.destroy).pack(side='right')
        
    def _confirm(self):
        """确认添加/编辑批注"""
        content = self.content.get('1.0', 'end-1c')
        if not content.strip():
            messagebox.showerror("错误", "批注内容不能为空")
            return
            
        self.result = {
            'content': content,
            'position': {'line': 0, 'column': 0},  # 这里需要根据实际情况设置
            'author': 'current_user'  # 这里需要根据实际情况设置
        }
        self.destroy()
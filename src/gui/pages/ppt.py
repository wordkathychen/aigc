import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import threading
import webbrowser
from typing import Dict, List, Optional, Any
import hashlib
import hmac
import base64
import time
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from src.utils.file_handler import FileHandler
from src.utils.logger import setup_logger
from src.gui.components.scrolled_text import ScrolledText
from src.gui.components.progress_bar import ProgressBar
from src.config.settings import PPT_APP_ID, PPT_API_SECRET

logger = setup_logger(__name__)

class AIPPT:
    """讯飞星火PPT生成类"""

    def __init__(self, APPId, APISecret, Text, templateId):
        self.APPid = APPId
        self.APISecret = APISecret
        self.text = Text
        self.header = {}
        self.templateId = templateId

    # 获取签名
    def get_signature(self, ts):
        try:
            # 对app_id和时间戳进行MD5加密
            auth = self.md5(self.APPid + str(ts))
            # 使用HMAC-SHA1算法对加密后的字符串进行加密
            return self.hmac_sha1_encrypt(auth, self.APISecret)
        except Exception as e:
            logger.error(f"获取签名失败: {str(e)}")
            return None

    def hmac_sha1_encrypt(self, encrypt_text, encrypt_key):
        # 使用HMAC-SHA1算法对文本进行加密，并将结果转换为Base64编码
        return base64.b64encode(hmac.new(encrypt_key.encode('utf-8'), encrypt_text.encode('utf-8'), hashlib.sha1).digest()).decode('utf-8')

    def md5(self, text):
        # 对文本进行MD5加密，并返回加密后的十六进制字符串
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    # 创建PPT生成任务
    def create_task(self, file_path=None):
        url = 'https://zwapi.xfyun.cn/api/ppt/v2/create'
        timestamp = int(time.time())
        signature = self.get_signature(timestamp)

        fields = {
            "query": self.text,
            "templateId": self.templateId,  # 模板的ID,从PPT主题列表查询中获取
            "author": "AI文本生成助手",    # PPT作者名：用户自行选择是否设置作者名
            "isCardNote": str(True),   # 是否生成PPT演讲备注, True or False
            "search": str(False),      # 是否联网搜索,True or False
            "isFigure": str(True),   # 是否自动配图, True or False
            "aiImage": "normal"   # ai配图类型： normal、advanced （isFigure为true的话生效）； normal-普通配图，20%正文配图；advanced-高级配图，50%正文配图
        }
        
        # 如果提供了文件路径，添加文件参数
        if file_path:
            fields["file"] = (os.path.basename(file_path), open(file_path, 'rb'), 'text/plain')
            fields["fileName"] = os.path.basename(file_path)

        formData = MultipartEncoder(fields=fields)

        headers = {
            "appId": self.APPid,
            "timestamp": str(timestamp),
            "signature": signature,
            "Content-Type": formData.content_type
        }
        self.header = headers
        
        try:
            response = requests.request(method="POST", url=url, data=formData, headers=headers).text
            logger.info(f"生成PPT返回结果：{response}")
            resp = json.loads(response)
            if 0 == resp['code']:
                return resp['data']['sid']
            else:
                logger.error(f'创建PPT任务失败: {resp.get("message", "")}')
                return None
        except Exception as e:
            logger.error(f"PPT API请求失败: {str(e)}")
            return None

    # 轮询任务进度，返回完整响应信息
    def get_process(self, sid):
        if None != sid:
            try:
                response = requests.request("GET", url=f"https://zwapi.xfyun.cn/api/ppt/v2/progress?sid={sid}", headers=self.header).text
                return response
            except Exception as e:
                logger.error(f"获取进度失败: {str(e)}")
                return None
        else:
            return None

    # 获取PPT，以下载连接形式返回
    def get_result(self, task_id):
        PPTurl = ''
        try:
            # 轮询任务进度
            while True:
                response = self.get_process(task_id)
                if not response:
                    time.sleep(3)
                    continue
                    
                resp = json.loads(response)
                pptStatus = resp['data']['pptStatus']
                aiImageStatus = resp['data']['aiImageStatus']
                cardNoteStatus = resp['data']['cardNoteStatus']

                if 'done' == pptStatus and 'done' == aiImageStatus and 'done' == cardNoteStatus:
                    PPTurl = resp['data']['pptUrl']
                    break
                else:
                    time.sleep(3)
            return PPTurl
        except Exception as e:
            logger.error(f"获取PPT结果失败: {str(e)}")
            return None

    def getHeaders(self):
        timestamp = int(time.time())
        signature = self.get_signature(timestamp)

        headers = {
            "appId": self.APPid,
            "timestamp": str(timestamp),
            "signature": signature,
            "Content-Type": "application/json; charset=utf-8"
        }
        return headers

    def getTheme(self):
        url = "https://zwapi.xfyun.cn/api/ppt/v2/template/list"
        self.header = self.getHeaders()
        body = {
            "payType": "not_free",
            "pageNum": 1,
            "pageSize": 20
        }

        try:
            response = requests.request("GET", url=url, headers=self.header).text
            return response
        except Exception as e:
            logger.error(f"获取主题列表失败: {str(e)}")
            return None

    def createOutline(self):
        url = "https://zwapi.xfyun.cn/api/ppt/v2/createOutline"
        body = {
            "query": self.text,
            "language": "cn",
            "search": str(False),  # 是否联网搜索,True or False
        }

        try:
            response = requests.post(url=url, json=body, headers=self.getHeaders()).text
            return response
        except Exception as e:
            logger.error(f"创建大纲失败: {str(e)}")
            return None

    def createOutlineByDoc(self, fileName, filePath=None, fileUrl=None):
        url = "https://zwapi.xfyun.cn/api/ppt/v2/createOutlineByDoc"
        
        fields = {
            "fileName": fileName,   # 文件名(带文件名后缀；如果传file或者fileUrl，fileName必填)
            "query": self.text,
            "language": "cn",
            "search": str(False),  # 是否联网搜索,True or False
        }
        
        if filePath:
            fields["file"] = (filePath, open(filePath, 'rb'), 'text/plain')
        if fileUrl:
            fields["fileUrl"] = fileUrl
            
        formData = MultipartEncoder(fields=fields)
        
        timestamp = int(time.time())
        signature = self.get_signature(timestamp)
        headers = {
            "appId": self.APPid,
            "timestamp": str(timestamp),
            "signature": signature,
            "Content-Type": formData.content_type
        }
        self.header = headers
        
        try:
            response = requests.post(url=url, data=formData, headers=headers).text
            return response
        except Exception as e:
            logger.error(f"通过文档创建大纲失败: {str(e)}")
            return None

    def createPptByOutline(self, outline):
        url = "https://zwapi.xfyun.cn/api/ppt/v2/createPptByOutline"
        body = {
            "query": self.text,
            "outline": outline,
            "templateId": self.templateId,  # 模板的ID,从PPT主题列表查询中获取
            "author": "AI文本生成助手",    # PPT作者名：用户自行选择是否设置作者名
            "isCardNote": True,   # 是否生成PPT演讲备注, True or False
            "search": False,      # 是否联网搜索,True or False
            "isFigure": True,   # 是否自动配图, True or False
            "aiImage": "normal",   # ai配图类型： normal、advanced （isFigure为true的话生效）； normal-普通配图，20%正文配图；advanced-高级配图，50%正文配图
        }

        try:
            response = requests.post(url, json=body, headers=self.getHeaders()).text
            resp = json.loads(response)
            if 0 == resp['code']:
                return resp['data']['sid']
            else:
                logger.error(f'通过大纲创建PPT失败: {resp.get("message", "")}')
                return None
        except Exception as e:
            logger.error(f"通过大纲创建PPT失败: {str(e)}")
            return None


class PPTMaker(ttk.Frame):
    """PPT生成页面"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.file_handler = FileHandler()
        self.template_id = "20240718489569D"  # 默认模板ID
        self.available_templates = {}  # 存储可用模板
        
        # 创建界面
        self.create_widgets()
        logger.info("初始化PPT生成页面")
        
        # 加载模板列表
        self.load_template_list()
        
    def create_widgets(self):
        """创建页面组件"""
        # 主页面分为上中下三部分
        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(fill='x', padx=10, pady=5)
        
        self.middle_frame = ttk.Frame(self)
        self.middle_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(fill='x', padx=10, pady=5)
        
        # 顶部控制区
        self.create_top_controls()
        
        # 中间文本区
        self.create_text_area()
        
        # 底部按钮区
        self.create_bottom_controls()
        
    def create_top_controls(self):
        """创建顶部控制区"""
        # 第一行 - 标题和模式选择
        row1 = ttk.Frame(self.top_frame)
        row1.pack(fill='x', pady=5)
        
        ttk.Label(row1, text="PPT生成", style="Title.TLabel").pack(side='left')
        
        # 模式选择区
        mode_frame = ttk.Frame(row1)
        mode_frame.pack(side='right')
        
        ttk.Label(mode_frame, text="生成模式:").pack(side='left')
        self.mode_var = tk.StringVar(value="文本生成")
        modes = ["文本生成", "文档转换", "大纲生成"]
        mode_cb = ttk.Combobox(mode_frame, textvariable=self.mode_var, 
                              values=modes, width=15, state="readonly")
        mode_cb.pack(side='left', padx=5)
        mode_cb.bind("<<ComboboxSelected>>", self.on_mode_change)
        
        # 第二行 - 模板选择
        row2 = ttk.Frame(self.top_frame)
        row2.pack(fill='x', pady=5)
        
        ttk.Label(row2, text="PPT模板:").pack(side='left')
        self.template_var = tk.StringVar(value="默认模板")
        self.template_cb = ttk.Combobox(row2, textvariable=self.template_var, 
                                      width=30, state="readonly")
        self.template_cb.pack(side='left', padx=5)
        
        # 文件上传区域（默认隐藏）
        self.file_frame = ttk.LabelFrame(self.top_frame, text="文件上传")
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(self.file_frame, textvariable=self.file_path_var, 
                 width=50, state='readonly').pack(side='left', padx=5, pady=5, fill='x', expand=True)
        ttk.Button(self.file_frame, text="选择文件", 
                  command=self.select_file).pack(side='right', padx=5, pady=5)
        
    def create_text_area(self):
        """创建文本区域"""
        # 创建输入区
        input_frame = ttk.LabelFrame(self.middle_frame, text="PPT主题描述")
        input_frame.pack(fill='both', expand=True)
        
        self.topic_input = ScrolledText(input_frame)
        self.topic_input.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 初始提示
        self.topic_input.insert('1.0', "请输入PPT主题或描述，例如：'企业年度总结报告'或'人工智能技术发展现状'")
        
    def create_bottom_controls(self):
        """创建底部控制区"""
        # 状态信息
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(self.bottom_frame, textvariable=self.status_var)
        status_label.pack(side='left', padx=5)
        
        # 进度条
        self.progress = ProgressBar(self.bottom_frame, width=200)
        self.progress.pack(side='left', padx=10)
        
        # 操作按钮
        buttons_frame = ttk.Frame(self.bottom_frame)
        buttons_frame.pack(side='right')
        
        self.generate_btn = ttk.Button(buttons_frame, text="生成PPT", 
                                     command=self.generate_ppt)
        self.generate_btn.pack(side='left', padx=5)
        
        self.download_btn = ttk.Button(buttons_frame, text="下载PPT", 
                                     command=self.download_ppt, state='disabled')
        self.download_btn.pack(side='left', padx=5)
        
    def on_mode_change(self, event=None):
        """模式变更处理"""
        mode = self.mode_var.get()
        
        # 根据模式显示或隐藏文件上传区域
        if mode in ["文档转换", "大纲生成"]:
            self.file_frame.pack(fill='x', pady=5, after=self.template_cb.master)
        else:
            self.file_frame.pack_forget()
            
        # 更新状态
        self.status_var.set(f"已选择{mode}模式")
        
    def select_file(self):
        """选择上传文件"""
        filetypes = [
            ("Word文档", "*.docx"),
            ("Word文档旧版", "*.doc"),
            ("PDF文档", "*.pdf"),
            ("文本文件", "*.txt"),
            ("Markdown文件", "*.md"),
            ("所有文件", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="选择文件",
            filetypes=filetypes
        )
        
        if filepath:
            self.file_path_var.set(filepath)
            self.status_var.set(f"已选择文件: {os.path.basename(filepath)}")
            
    def load_template_list(self):
        """加载PPT模板列表"""
        self.status_var.set("正在加载模板列表...")
        self.update_idletasks()
        
        def _load_templates():
            try:
                # 创建AIPPT实例
                ppt = AIPPT(PPT_APP_ID, PPT_API_SECRET, "", self.template_id)
                
                # 获取模板列表
                response = ppt.getTheme()
                if response:
                    data = json.loads(response)
                    if data['code'] == 0:
                        templates = data['data']['templates']
                        # 更新模板下拉框
                        template_names = []
                        for template in templates:
                            name = f"{template['templateName']} ({template['style']})"
                            template_names.append(name)
                            self.available_templates[name] = template['templateId']
                        
                        # 更新UI
                        self.template_cb['values'] = template_names
                        if template_names:
                            self.template_cb.current(0)
                            self.template_id = self.available_templates[template_names[0]]
                            
                        self.status_var.set(f"已加载 {len(template_names)} 个模板")
                    else:
                        self.status_var.set(f"加载模板失败: {data.get('message', '未知错误')}")
                else:
                    self.status_var.set("加载模板列表失败")
            except Exception as e:
                logger.error(f"加载模板列表失败: {str(e)}")
                self.status_var.set("加载模板列表失败")
        
        # 在后台线程中加载模板
        threading.Thread(target=_load_templates).start()
        
    def generate_ppt(self):
        """生成PPT"""
        # 获取模式和输入
        mode = self.mode_var.get()
        topic = self.topic_input.get('1.0', tk.END).strip()
        
        if not topic:
            messagebox.showwarning("提示", "请输入PPT主题或描述")
            return
            
        # 获取模板ID
        selected_template = self.template_var.get()
        if selected_template in self.available_templates:
            self.template_id = self.available_templates[selected_template]
            
        # 文件模式需要检查文件
        if mode in ["文档转换", "大纲生成"]:
            filepath = self.file_path_var.get()
            if not filepath or not os.path.exists(filepath):
                messagebox.showwarning("提示", "请选择要处理的文件")
                return
                
        # 禁用生成按钮，开始进度条
        self.generate_btn.config(state='disabled')
        self.download_btn.config(state='disabled')
        self.progress.start()
        self.status_var.set("正在生成PPT...")
        self.update_idletasks()
        
        # 在后台线程中生成
        threading.Thread(target=self._generate_ppt_thread).start()
        
    def _generate_ppt_thread(self):
        """在后台线程中生成PPT"""
        try:
            mode = self.mode_var.get()
            topic = self.topic_input.get('1.0', tk.END).strip()
            
            # 创建AIPPT实例
            ppt = AIPPT(PPT_APP_ID, PPT_API_SECRET, topic, self.template_id)
            
            # 根据模式调用不同的API
            if mode == "文本生成":
                # 直接生成PPT
                self.status_var.set("正在创建PPT任务...")
                self.update_idletasks()
                
                task_id = ppt.create_task()
                
                if not task_id:
                    raise Exception("创建PPT任务失败")
                    
                # 获取PPT结果
                self.status_var.set("正在生成PPT，请耐心等待...")
                self.update_idletasks()
                
                ppt_url = ppt.get_result(task_id)
                
                if not ppt_url:
                    raise Exception("获取PPT结果失败")
                    
                # 保存URL并启用下载按钮
                self.ppt_url = ppt_url
                self.status_var.set("PPT生成完成，可以下载")
                self.download_btn.config(state='normal')
                
            elif mode == "文档转换":
                # 通过文档生成PPT
                filepath = self.file_path_var.get()
                filename = os.path.basename(filepath)
                
                self.status_var.set("正在上传文档并创建PPT任务...")
                self.update_idletasks()
                
                task_id = ppt.create_task(filepath)
                
                if not task_id:
                    raise Exception("创建PPT任务失败")
                    
                # 获取PPT结果
                self.status_var.set("正在生成PPT，请耐心等待...")
                self.update_idletasks()
                
                ppt_url = ppt.get_result(task_id)
                
                if not ppt_url:
                    raise Exception("获取PPT结果失败")
                    
                # 保存URL并启用下载按钮
                self.ppt_url = ppt_url
                self.status_var.set("PPT生成完成，可以下载")
                self.download_btn.config(state='normal')
                
            elif mode == "大纲生成":
                # 先生成大纲，再生成PPT
                filepath = self.file_path_var.get()
                filename = os.path.basename(filepath)
                
                self.status_var.set("正在生成文档大纲...")
                self.update_idletasks()
                
                # 生成大纲
                outline_response = ppt.createOutlineByDoc(filename, filepath)
                
                if not outline_response:
                    raise Exception("生成大纲失败")
                    
                data = json.loads(outline_response)
                if data['code'] != 0:
                    raise Exception(f"生成大纲失败: {data.get('message', '未知错误')}")
                    
                outline = data["data"]["outline"]
                
                # 通过大纲生成PPT
                self.status_var.set("正在通过大纲创建PPT任务...")
                self.update_idletasks()
                
                task_id = ppt.createPptByOutline(outline)
                
                if not task_id:
                    raise Exception("创建PPT任务失败")
                    
                # 获取PPT结果
                self.status_var.set("正在生成PPT，请耐心等待...")
                self.update_idletasks()
                
                ppt_url = ppt.get_result(task_id)
                
                if not ppt_url:
                    raise Exception("获取PPT结果失败")
                    
                # 保存URL并启用下载按钮
                self.ppt_url = ppt_url
                self.status_var.set("PPT生成完成，可以下载")
                self.download_btn.config(state='normal')
            
            # 显示成功消息
            messagebox.showinfo("成功", "PPT生成成功，可以点击'下载PPT'按钮下载")
            
        except Exception as e:
            logger.error(f"生成PPT失败: {str(e)}")
            self.status_var.set(f"生成失败: {str(e)}")
            messagebox.showerror("错误", f"生成PPT失败: {str(e)}")
            
        finally:
            # 恢复UI状态
            self.progress.stop()
            self.generate_btn.config(state='normal')
            
    def download_ppt(self):
        """下载生成的PPT"""
        if not hasattr(self, 'ppt_url') or not self.ppt_url:
            messagebox.showinfo("提示", "没有可下载的PPT")
            return
            
        # 打开下载链接
        webbrowser.open(self.ppt_url)
        self.status_var.set("已打开PPT下载链接")
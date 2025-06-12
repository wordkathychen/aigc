from typing import Dict, Any, Optional, List, Tuple
import aiohttp
import asyncio
import time
import requests
import os
import json
import sqlite3
import logging
import sys
import socket
from src.config.settings import API_CONFIGS
from src.utils.exceptions import APIError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class APIManager:
    """API管理器类，负责从Web后台或本地数据库获取API密钥和配置"""
    
    def __init__(self, web_url: Optional[str] = None, token: Optional[str] = None, db_path: Optional[str] = None):
        """初始化API管理器
        
        Args:
            web_url: Web后台API地址，例如 http://localhost:5000/api
            token: 认证令牌，从Web后台登录API获取
            db_path: 本地数据库路径，如果无法连接Web后台，则使用本地数据库
        """
        self.web_url = web_url or os.environ.get('AI_TEXT_WEB_URL', 'http://localhost:5000/api')
        self.token = token or os.environ.get('AI_TEXT_AUTH_TOKEN')
        self.db_path = db_path or os.path.join(self._get_data_dir(), 'api_cache.db')
        
        # 初始化缓存
        self.cached_api_keys = {}
        self.cached_prompt_templates = {}
        self.cached_sensitive_words = []
        self.cached_model_configs = []
        self.last_update = 0
        self.cache_ttl = 600  # 缓存有效期10分钟
        
        # 网络连接检查设置
        self.require_network = os.environ.get('REQUIRE_NETWORK', 'false').lower() == 'true'
        self.check_api_endpoints = os.environ.get('CHECK_API_ENDPOINTS', 'false').lower() == 'true'
        self.api_check_timeout = int(os.environ.get('API_CHECK_TIMEOUT', '10'))
        
        # 初始化本地数据库
        self._init_local_db()
        
        # 检查网络连接
        if self.require_network:
            self.check_network_connectivity()
    
    def _get_data_dir(self) -> str:
        """获取数据目录"""
        # 获取应用数据目录
        if getattr(sys, 'frozen', False):
            # 如果是PyInstaller打包的应用
            base_dir = os.path.dirname(sys.executable)
        else:
            # 如果是直接运行的脚本
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    def _init_local_db(self):
        """初始化本地数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建API密钥表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY,
                api_type TEXT NOT NULL,
                key_name TEXT NOT NULL,
                api_key TEXT NOT NULL,
                api_endpoint TEXT,
                model_name TEXT,
                is_active INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建提示词模板表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_templates (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建敏感词表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensitive_words (
                id INTEGER PRIMARY KEY,
                word TEXT UNIQUE NOT NULL,
                is_active INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建模型配置表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_configs (
                id INTEGER PRIMARY KEY,
                task_type TEXT NOT NULL,
                education_level TEXT NOT NULL,
                api_type TEXT NOT NULL,
                model_name TEXT NOT NULL,
                temperature REAL DEFAULT 0.7,
                max_tokens INTEGER DEFAULT 2000,
                top_p REAL DEFAULT 1.0,
                frequency_penalty REAL DEFAULT 0.0,
                presence_penalty REAL DEFAULT 0.0,
                is_active INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("本地数据库初始化成功")
        except Exception as e:
            logger.error(f"本地数据库初始化失败: {str(e)}")
    
    def _check_web_connection(self) -> bool:
        """检查Web后台连接状态"""
        if not self.web_url or not self.token:
            return False
        
        try:
            response = requests.get(
                f"{self.web_url}/check_environment",
                timeout=5
            )
            
            if response.status_code == 200:
                return True
            return False
        except Exception as e:
            logger.warning(f"Web后台连接失败: {str(e)}")
            return False
    
    def _fetch_from_web(self, endpoint: str) -> Tuple[bool, Any]:
        """从Web后台获取数据
        
        Args:
            endpoint: API端点路径
            
        Returns:
            (成功标志, 数据)
        """
        if not self.web_url or not self.token:
            return False, None
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(
                f"{self.web_url}/{endpoint}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                logger.warning(f"从Web后台获取数据失败: {response.status_code} - {response.text}")
                return False, None
        except Exception as e:
            logger.warning(f"从Web后台获取数据出错: {str(e)}")
            return False, None
    
    def _save_to_local_db(self, table: str, data_list: List[Dict[str, Any]]):
        """保存数据到本地数据库
        
        Args:
            table: 表名
            data_list: 数据列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 根据表名构建插入语句
            if table == 'api_keys':
                for item in data_list:
                    cursor.execute(
                        "INSERT OR REPLACE INTO api_keys (api_type, key_name, api_key, api_endpoint, model_name, is_active, updated_at) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                        (item['api_type'], item['key_name'], item['api_key'], item.get('api_endpoint'), item.get('model_name'), 1)
                    )
            elif table == 'prompt_templates':
                for item in data_list:
                    cursor.execute(
                        "INSERT OR REPLACE INTO prompt_templates (name, category, content, is_active, updated_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                        (item['name'], item['category'], item['content'], 1)
                    )
            elif table == 'sensitive_words':
                for word in data_list:
                    cursor.execute(
                        "INSERT OR REPLACE INTO sensitive_words (word, is_active, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                        (word, 1)
                    )
            elif table == 'model_configs':
                for item in data_list:
                    cursor.execute(
                        "INSERT OR REPLACE INTO model_configs (task_type, education_level, api_type, model_name, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, is_active, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                        (item['task_type'], item['education_level'], item['api_type'], item['model_name'], 
                         item.get('temperature', 0.7), item.get('max_tokens', 2000), item.get('top_p', 1.0),
                         item.get('frequency_penalty', 0.0), item.get('presence_penalty', 0.0), item.get('is_active', 1))
                    )
            
            conn.commit()
            conn.close()
            logger.info(f"数据已保存到本地数据库: {table}")
        except Exception as e:
            logger.error(f"保存数据到本地数据库失败: {str(e)}")
    
    def _load_from_local_db(self, table: str) -> List[Dict[str, Any]]:
        """从本地数据库加载数据
        
        Args:
            table: 表名
            
        Returns:
            数据列表
        """
        result = []
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 根据表名查询数据
            if table == 'api_keys':
                cursor.execute("SELECT * FROM api_keys WHERE is_active = 1")
                rows = cursor.fetchall()
                for row in rows:
                    result.append({
                        'api_type': row['api_type'],
                        'key_name': row['key_name'],
                        'api_key': row['api_key'],
                        'api_endpoint': row['api_endpoint'],
                        'model_name': row['model_name']
                    })
            elif table == 'prompt_templates':
                cursor.execute("SELECT * FROM prompt_templates WHERE is_active = 1")
                rows = cursor.fetchall()
                for row in rows:
                    result.append({
                        'name': row['name'],
                        'category': row['category'],
                        'content': row['content']
                    })
            elif table == 'sensitive_words':
                cursor.execute("SELECT word FROM sensitive_words WHERE is_active = 1")
                rows = cursor.fetchall()
                result = [row['word'] for row in rows]
            elif table == 'model_configs':
                cursor.execute("SELECT * FROM model_configs WHERE is_active = 1")
                rows = cursor.fetchall()
                for row in rows:
                    result.append({
                        'task_type': row['task_type'],
                        'education_level': row['education_level'],
                        'api_type': row['api_type'],
                        'model_name': row['model_name'],
                        'temperature': row['temperature'],
                        'max_tokens': row['max_tokens'],
                        'top_p': row['top_p'],
                        'frequency_penalty': row['frequency_penalty'],
                        'presence_penalty': row['presence_penalty']
                    })
            
            conn.close()
            logger.info(f"从本地数据库加载数据成功: {table}")
            return result
        except Exception as e:
            logger.error(f"从本地数据库加载数据失败: {str(e)}")
            return []
    
    def get_api_keys(self, api_type: Optional[str] = None) -> Dict[str, Any]:
        """获取API密钥
        
        Args:
            api_type: API类型，如 'deepseek', 'openai' 等，如果为None则返回所有类型
            
        Returns:
            API密钥信息
        """
        # 检查缓存是否有效
        current_time = time.time()
        if current_time - self.last_update > self.cache_ttl:
            # 缓存过期，尝试从Web后台获取
            if self._check_web_connection():
                success, data = self._fetch_from_web('api_keys')
                if success and 'api_keys' in data:
                    # 更新缓存
                    self.cached_api_keys = data['api_keys']
                    self.last_update = current_time
                    
                    # 同时保存到本地数据库
                    all_keys = []
                    for key_type, keys in data['api_keys'].items():
                        for key in keys:
                            key['api_type'] = key_type
                            all_keys.append(key)
                    
                    self._save_to_local_db('api_keys', all_keys)
            else:
                # 从本地数据库加载
                keys = self._load_from_local_db('api_keys')
                self.cached_api_keys = {}
                
                for key in keys:
                    key_type = key['api_type']
                    if key_type not in self.cached_api_keys:
                        self.cached_api_keys[key_type] = []
                    
                    self.cached_api_keys[key_type].append({
                        'key_name': key['key_name'],
                        'api_key': key['api_key'],
                        'api_endpoint': key['api_endpoint'],
                        'model_name': key['model_name']
                    })
                
                self.last_update = current_time
        
        # 返回指定类型的API密钥
        if api_type:
            return self.cached_api_keys.get(api_type, [])
        else:
            return self.cached_api_keys
    
    def get_prompt_templates(self, category: Optional[str] = None) -> Dict[str, Any]:
        """获取提示词模板
        
        Args:
            category: 模板类别，如 'title', 'abstract_zh' 等，如果为None则返回所有类别
            
        Returns:
            提示词模板信息
        """
        # 检查缓存是否有效
        current_time = time.time()
        if current_time - self.last_update > self.cache_ttl:
            # 缓存过期，尝试从Web后台获取
            if self._check_web_connection():
                success, data = self._fetch_from_web('prompt_templates')
                if success and 'templates' in data:
                    # 更新缓存
                    self.cached_prompt_templates = data['templates']
                    self.last_update = current_time
                    
                    # 同时保存到本地数据库
                    all_templates = []
                    for template_category, templates in data['templates'].items():
                        for template in templates:
                            template['category'] = template_category
                            all_templates.append(template)
                    
                    self._save_to_local_db('prompt_templates', all_templates)
            else:
                # 从本地数据库加载
                templates = self._load_from_local_db('prompt_templates')
                self.cached_prompt_templates = {}
                
                for template in templates:
                    template_category = template['category']
                    if template_category not in self.cached_prompt_templates:
                        self.cached_prompt_templates[template_category] = []
                    
                    self.cached_prompt_templates[template_category].append({
                        'id': template.get('id'),
                        'name': template['name'],
                        'content': template['content']
                    })
                
                self.last_update = current_time
        
        # 返回指定类别的提示词模板
        if category:
            return self.cached_prompt_templates.get(category, [])
        else:
            return self.cached_prompt_templates
    
    def get_sensitive_words(self) -> List[str]:
        """获取敏感词列表
        
        Returns:
            敏感词列表
        """
        # 检查缓存是否有效
        current_time = time.time()
        if current_time - self.last_update > self.cache_ttl:
            # 缓存过期，尝试从Web后台获取
            if self._check_web_connection():
                success, data = self._fetch_from_web('sensitive_words')
                if success and 'sensitive_words' in data:
                    # 更新缓存
                    self.cached_sensitive_words = data['sensitive_words']
                    self.last_update = current_time
                    
                    # 同时保存到本地数据库
                    self._save_to_local_db('sensitive_words', data['sensitive_words'])
            else:
                # 从本地数据库加载
                self.cached_sensitive_words = self._load_from_local_db('sensitive_words')
                self.last_update = current_time
        
        return self.cached_sensitive_words
    
    def login(self, username: str, password: str) -> bool:
        """登录Web后台获取认证令牌
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            是否登录成功
        """
        if not self.web_url:
            logger.error("未配置Web后台URL")
            return False
        
        try:
            response = requests.post(
                f"{self.web_url}/login",
                json={'username': username, 'password': password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.token = data['token']
                    # 保存token到环境变量
                    os.environ['AI_TEXT_AUTH_TOKEN'] = self.token
                    logger.info("登录成功")
                    return True
            
            logger.warning(f"登录失败: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            logger.error(f"登录请求出错: {str(e)}")
            return False
    
    def get_model_configs(self, task_type: Optional[str] = None, education_level: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取模型配置
        
        Args:
            task_type: 任务类型，例如 title, abstract_zh, content 等
            education_level: 教育级别，例如 college, undergraduate, master, doctor 等
            
        Returns:
            模型配置列表
        """
        # 检查缓存是否过期
        current_time = time.time()
        if 'model_configs' not in self.cached_api_keys or (current_time - self.last_update) > self.cache_ttl:
            # 尝试从Web后台获取
            if self._check_web_connection():
                success, response = self._fetch_from_web('model_configs')
                if success and response and 'configs' in response:
                    self.cached_api_keys['model_configs'] = response['configs']
                    self._save_to_local_db('model_configs', response['configs'])
                    self.last_update = current_time
                else:
                    # 如果从Web获取失败，从本地数据库加载
                    self.cached_api_keys['model_configs'] = self._load_from_local_db('model_configs')
                    self.last_update = current_time
            else:
                # 直接从本地数据库加载
                self.cached_api_keys['model_configs'] = self._load_from_local_db('model_configs')
                self.last_update = current_time
        
        # 获取所有配置
        configs = self.cached_api_keys.get('model_configs', [])
        
        # 根据条件筛选
        if task_type and education_level:
            return [cfg for cfg in configs if cfg['task_type'] == task_type and cfg['education_level'] == education_level and cfg['is_active']]
        elif task_type:
            return [cfg for cfg in configs if cfg['task_type'] == task_type and cfg['is_active']]
        elif education_level:
            return [cfg for cfg in configs if cfg['education_level'] == education_level and cfg['is_active']]
        else:
            return [cfg for cfg in configs if cfg['is_active']]
    
    def get_best_model_config(self, task_type: str, education_level: str) -> Optional[Dict[str, Any]]:
        """获取最佳模型配置
        
        根据任务类型和教育级别获取最合适的模型配置。
        如果找不到完全匹配的配置，会尝试降级匹配。
        
        Args:
            task_type: 任务类型，例如 title, abstract_zh, content 等
            education_level: 教育级别，例如 college, undergraduate, master, doctor 等
            
        Returns:
            模型配置或None
        """
        # 教育级别降级顺序
        education_levels = {
            'doctor': ['doctor', 'master', 'undergraduate', 'college'],
            'master': ['master', 'undergraduate', 'college'],
            'undergraduate': ['undergraduate', 'college'],
            'college': ['college']
        }
        
        # 任务类型降级顺序
        task_types = {
            'title': ['title', 'content'],
            'abstract_zh': ['abstract_zh', 'content'],
            'abstract_en': ['abstract_en', 'abstract_zh', 'content'],
            'keywords_zh': ['keywords_zh', 'content'],
            'keywords_en': ['keywords_en', 'keywords_zh', 'content'],
            'content': ['content'],
            'references': ['references', 'content'],
            'acknowledgement': ['acknowledgement', 'content']
        }
        
        # 1. 尝试精确匹配
        configs = self.get_model_configs(task_type, education_level)
        if configs:
            return configs[0]
        
        # 2. 尝试降级匹配教育级别
        for level in education_levels.get(education_level, []):
            if level == education_level:
                continue
            configs = self.get_model_configs(task_type, level)
            if configs:
                return configs[0]
        
        # 3. 尝试降级匹配任务类型
        for task in task_types.get(task_type, []):
            if task == task_type:
                continue
            configs = self.get_model_configs(task, education_level)
            if configs:
                return configs[0]
        
        # 4. 尝试通用配置
        configs = self.get_model_configs('content', 'undergraduate')
        if configs:
            return configs[0]
        
        # 5. 尝试任何可用配置
        configs = self.get_model_configs()
        if configs:
            return configs[0]
        
        # 返回默认值
        return {
            'api_type': 'deepseek',
            'model_name': 'deepseek-chat',
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 1.0,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0
        }
    
    def check_network_connectivity(self) -> bool:
        """检查网络连接状态
        
        检查Internet连接以及API端点可用性
        
        Returns:
            连接状态: True表示连接正常，False表示连接失败
        """
        logger.info("正在检查网络连接状态...")
        
        # 检查Internet连接
        internet_connected = False
        test_hosts = [
            "www.baidu.com",
            "www.google.com",
            "www.microsoft.com",
            "www.qq.com"
        ]
        
        for host in test_hosts:
            try:
                # 尝试解析域名
                socket.gethostbyname(host)
                internet_connected = True
                logger.info(f"Internet连接正常，已连接到 {host}")
                break
            except Exception:
                continue
        
        if not internet_connected:
            logger.error("无法连接到Internet，请检查网络连接")
            if self.require_network:
                logger.error("系统需要网络连接才能正常运行，请确保网络连通")
            return False
        
        # 检查API端点可用性
        if self.check_api_endpoints:
            api_endpoints_available = False
            # 获取所有API密钥
            api_keys = self.get_api_keys()
            
            if not api_keys:
                logger.warning("没有可用的API密钥，无法检查API端点")
                return internet_connected
            
            # 测试每个API端点
            for api_key in api_keys:
                try:
                    api_type = api_key.get('api_type')
                    api_endpoint = api_key.get('api_endpoint')
                    
                    if not api_endpoint:
                        # 使用默认端点
                        if api_type == 'openai':
                            api_endpoint = "https://api.openai.com/v1"
                        elif api_type == 'deepseek':
                            api_endpoint = "https://api.deepseek.com/v1"
                    
                    if api_endpoint:
                        # 去除可能的路径，只保留主机部分
                        if '://' in api_endpoint:
                            api_host = api_endpoint.split('://')[1].split('/')[0]
                        else:
                            api_host = api_endpoint.split('/')[0]
                        
                        # 尝试解析域名
                        socket.gethostbyname(api_host)
                        logger.info(f"API端点 {api_host} 可访问")
                        api_endpoints_available = True
                        break
                except Exception as e:
                    logger.warning(f"API端点 {api_endpoint} 不可访问: {str(e)}")
            
            if not api_endpoints_available:
                logger.error("所有API端点均不可访问，请检查网络连接或API配置")
                return False
        
        logger.info("网络连接检查完成，连接正常")
        return True
    
    async def generate_content(self, prompt, max_tokens=None, temperature=None, model=None, task_type=None, education_level=None, **kwargs):
        """异步生成内容
        
        Args:
            prompt: 提示词
            max_tokens: 生成的最大token数
            temperature: 温度参数，越高越随机
            model: 模型名称
            task_type: 任务类型
            education_level: 教育级别
            **kwargs: 其他参数
            
        Returns:
            生成的内容
        """
        # 检查网络连接
        if self.require_network and not self.check_network_connectivity():
            raise APIError("网络连接不可用，无法生成内容")
        
        # 如果提供了任务类型和教育级别，根据任务类型和教育级别获取最佳模型配置
        if task_type and education_level:
            config = self.get_best_model_config(task_type, education_level)
            model = model or config.get('model_name')
            max_tokens = max_tokens or config.get('max_tokens')
            temperature = temperature or config.get('temperature')
            kwargs['top_p'] = kwargs.get('top_p', config.get('top_p'))
            kwargs['frequency_penalty'] = kwargs.get('frequency_penalty', config.get('frequency_penalty'))
            kwargs['presence_penalty'] = kwargs.get('presence_penalty', config.get('presence_penalty'))
            api_type = config.get('api_type')
            
            # 根据API类型获取对应的API密钥
            api_keys = self.get_api_keys(api_type)
            if not api_keys:
                raise APIError(f"未找到可用的{api_type}类型API密钥")
            
            api_key = api_keys[0]  # 使用第一个可用的API密钥
        else:
            # 获取默认API密钥
            api_keys = self.get_api_keys()
            if not api_keys:
                raise APIError("未找到可用的API密钥")
            
            api_key = api_keys[0]  # 使用第一个可用的API密钥
        
        # 根据API类型选择不同的生成方法
        try:
            # 同步转异步
            loop = asyncio.get_event_loop()
            if api_key['api_type'] == 'openai':
                return await loop.run_in_executor(
                    None, 
                    lambda: self._generate_with_openai(
                        api_key, prompt, max_tokens, temperature, model, **kwargs
                    )
                )
            elif api_key['api_type'] == 'azure':
                return await loop.run_in_executor(
                    None, 
                    lambda: self._generate_with_azure(
                        api_key, prompt, max_tokens, temperature, model, **kwargs
                    )
                )
            else:
                return await loop.run_in_executor(
                    None, 
                    lambda: self._generate_with_generic_api(
                        api_key, prompt, max_tokens, temperature, model, **kwargs
                    )
                )
        except Exception as e:
            logger.error(f"生成内容失败: {str(e)}")
            raise APIError(f"生成内容失败: {str(e)}")

    def generate_content_sync(self, prompt, max_tokens=None, temperature=None, model=None, task_type=None, education_level=None, **kwargs):
        """同步生成内容
        
        Args:
            prompt: 提示词
            max_tokens: 生成的最大token数
            temperature: 温度参数，越高越随机
            model: 模型名称
            task_type: 任务类型
            education_level: 教育级别
            **kwargs: 其他参数
            
        Returns:
            生成的内容
        """
        # 检查网络连接
        if self.require_network and not self.check_network_connectivity():
            raise APIError("网络连接不可用，无法生成内容")
        
        # 如果提供了任务类型和教育级别，根据任务类型和教育级别获取最佳模型配置
        if task_type and education_level:
            config = self.get_best_model_config(task_type, education_level)
            model = model or config.get('model_name')
            max_tokens = max_tokens or config.get('max_tokens')
            temperature = temperature or config.get('temperature')
            kwargs['top_p'] = kwargs.get('top_p', config.get('top_p'))
            kwargs['frequency_penalty'] = kwargs.get('frequency_penalty', config.get('frequency_penalty'))
            kwargs['presence_penalty'] = kwargs.get('presence_penalty', config.get('presence_penalty'))
            api_type = config.get('api_type')
            
            # 根据API类型获取对应的API密钥
            api_keys = self.get_api_keys(api_type)
            if not api_keys:
                raise APIError(f"未找到可用的{api_type}类型API密钥")
            
            api_key = api_keys[0]  # 使用第一个可用的API密钥
        else:
            # 获取默认API密钥
            api_keys = self.get_api_keys()
            if not api_keys:
                raise APIError("未找到可用的API密钥")
            
            api_key = api_keys[0]  # 使用第一个可用的API密钥
        
        # 根据API类型选择不同的生成方法
        try:
            if api_key['api_type'] == 'openai':
                return self._generate_with_openai(api_key, prompt, max_tokens, temperature, model, **kwargs)
            elif api_key['api_type'] == 'azure':
                return self._generate_with_azure(api_key, prompt, max_tokens, temperature, model, **kwargs)
            else:
                return self._generate_with_generic_api(api_key, prompt, max_tokens, temperature, model, **kwargs)
        except Exception as e:
            logger.error(f"生成内容失败: {str(e)}")
            raise APIError(f"生成内容失败: {str(e)}")
    
    def _generate_with_openai(self, api_key, prompt, max_tokens, temperature, model):
        """使用OpenAI API生成内容"""
        import openai
        
        openai.api_key = api_key.get("key")
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个帮助用户修改文本的助手。请根据批注要求修改文本。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    def _generate_with_azure(self, api_key, prompt, max_tokens, temperature, model):
        """使用Azure OpenAI API生成内容"""
        import openai
        
        openai.api_type = "azure"
        openai.api_key = api_key.get("key")
        openai.api_base = api_key.get("endpoint")
        openai.api_version = "2023-03-15-preview"
        
        response = openai.ChatCompletion.create(
            deployment_id=model,
            messages=[
                {"role": "system", "content": "你是一个帮助用户修改文本的助手。请根据批注要求修改文本。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    def _generate_with_generic_api(self, api_key, prompt, max_tokens, temperature, model):
        """使用通用API接口生成内容"""
        import requests
        
        url = api_key.get("endpoint")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key.get('key')}"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "你是一个帮助用户修改文本的助手。请根据批注要求修改文本。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            logger.error(f"API请求失败，状态码: {response.status_code}, 响应: {response.text}")
            return f"API请求失败: {response.status_code}"

# 单例模式
api_manager = APIManager()
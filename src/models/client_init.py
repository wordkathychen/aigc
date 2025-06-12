"""
客户端初始化模块
用于初始化客户端配置和连接Web后台
"""

import os
import json
import time
import requests
import logging
from typing import Dict, Any, Optional, List, Tuple
from src.config.client_config import WEB_API_URL, WEB_ENABLED, load_user_config

logger = logging.getLogger(__name__)

class ClientInitializer:
    """客户端初始化器"""
    
    def __init__(self):
        """初始化客户端"""
        self.api_url = WEB_API_URL
        self.web_enabled = WEB_ENABLED
        self.token = None
        self.user_info = None
        self.config = {}
        self.cache_dir = os.path.join(os.getcwd(), "data", "cache")
        
        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 尝试从配置文件加载token
        self._load_token()
    
    def _load_token(self):
        """从配置文件加载token"""
        token_file = os.path.join(os.path.expanduser("~"), ".ai_text_generator", "token.json")
        if os.path.exists(token_file):
            try:
                with open(token_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.token = data.get("token")
                    self.user_info = data.get("user_info")
            except Exception as e:
                print(f"加载token失败: {str(e)}")
    
    def _save_token(self, token, user_info):
        """保存token到配置文件"""
        token_file = os.path.join(os.path.expanduser("~"), ".ai_text_generator", "token.json")
        
        # 确保目录存在
        token_dir = os.path.dirname(token_file)
        os.makedirs(token_dir, exist_ok=True)
        
        try:
            with open(token_file, "w", encoding="utf-8") as f:
                json.dump({
                    "token": token,
                    "user_info": user_info
                }, f, indent=4)
            return True
        except Exception as e:
            print(f"保存token失败: {str(e)}")
            return False
    
    def check_connection(self) -> bool:
        """检查与Web后台的连接
        
        Returns:
            连接是否可用
        """
        if not self.web_enabled:
            logger.info("Web后台功能已禁用")
            return False
        
        try:
            # 尝试连接Web后台
            response = requests.get(f"{self.api_url}/check_environment", timeout=5)
            
            if response.status_code == 200:
                logger.info("Web后台连接成功")
                return True
            else:
                logger.warning(f"Web后台连接失败: HTTP {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Web后台连接错误: {str(e)}")
            return False
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """登录Web后台
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            (成功状态, 消息)
        """
        if not self.web_enabled:
            return False, "Web后台功能已禁用"
        
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data.get("token")
                    self.user_info = data.get("user_info")
                    
                    # 保存token
                    self._save_token(self.token, self.user_info)
                    
                    return True, "登录成功"
                else:
                    return False, data.get("message", "登录失败")
            else:
                return False, f"HTTP错误: {response.status_code}"
        
        except requests.exceptions.ConnectionError:
            return False, "连接服务器失败，请检查网络或服务器地址"
        except requests.exceptions.Timeout:
            return False, "连接服务器超时"
        except Exception as e:
            return False, f"登录失败: {str(e)}"
    
    def logout(self):
        """登出"""
        self.token = None
        self.user_info = None
        
        # 删除token文件
        token_file = os.path.join(os.path.expanduser("~"), ".ai_text_generator", "token.json")
        if os.path.exists(token_file):
            try:
                os.remove(token_file)
            except Exception as e:
                print(f"删除token文件失败: {str(e)}")
        
        return True, "登出成功"
    
    def check_login(self):
        """检查登录状态"""
        if not self.web_enabled:
            return False, "Web后台功能未启用"
        
        if not self.token:
            return False, "未登录"
        
        try:
            response = requests.get(
                f"{self.api_url}/auth/verify_token",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return True, "token有效"
                else:
                    # token无效，清除token
                    self.logout()
                    return False, "token已过期，请重新登录"
            else:
                return False, f"HTTP错误: {response.status_code}"
        
        except requests.exceptions.ConnectionError:
            return False, "连接服务器失败，请检查网络或服务器地址"
        except requests.exceptions.Timeout:
            return False, "连接服务器超时"
        except Exception as e:
            return False, f"验证token失败: {str(e)}"
    
    def get_user_info(self):
        """获取用户信息"""
        return self.user_info
    
    def is_logged_in(self):
        """是否已登录"""
        return self.token is not None
    
    def get_headers(self):
        """获取请求头"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def update_config(self, api_url=None, web_enabled=None):
        """更新配置"""
        if api_url is not None:
            self.api_url = api_url
        
        if web_enabled is not None:
            self.web_enabled = web_enabled
        
        # 更新配置文件
        from src.config.client_config import save_user_config
        save_user_config(web_api_url=self.api_url, web_enabled=self.web_enabled)
    
    def get_api_keys(self) -> List[Dict[str, Any]]:
        """获取API密钥列表
        
        Returns:
            API密钥列表
        """
        if not self.web_enabled or not self.token:
            return self._load_cached_api_keys()
        
        try:
            # 发送请求
            response = requests.get(
                f"{self.api_url}/api_keys",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            # 解析响应
            data = response.json()
            
            if response.status_code == 200 and data.get("code") == 200:
                api_keys = data.get("api_keys", {})
                
                # 保存到缓存
                self._save_api_keys_to_cache(api_keys)
                
                # 转换为列表格式
                result = []
                for api_type, keys in api_keys.items():
                    for key in keys:
                        key["api_type"] = api_type
                        result.append(key)
                
                return result
            else:
                logger.warning(f"获取API密钥失败: {data.get('error', '未知错误')}")
                return self._load_cached_api_keys()
        
        except Exception as e:
            logger.error(f"获取API密钥失败: {str(e)}")
            return self._load_cached_api_keys()
    
    def _save_api_keys_to_cache(self, api_keys: Dict[str, List[Dict[str, Any]]]) -> None:
        """保存API密钥到缓存
        
        Args:
            api_keys: API密钥数据
        """
        cache_file = os.path.join(self.cache_dir, "api_keys.json")
        
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump({
                    "api_keys": api_keys,
                    "updated_at": time.time()
                }, f)
        
        except Exception as e:
            logger.error(f"保存API密钥到缓存失败: {str(e)}")
    
    def _load_cached_api_keys(self) -> List[Dict[str, Any]]:
        """从缓存加载API密钥
        
        Returns:
            API密钥列表
        """
        cache_file = os.path.join(self.cache_dir, "api_keys.json")
        
        if not os.path.exists(cache_file):
            return []
        
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                api_keys = data.get("api_keys", {})
                
                # 转换为列表格式
                result = []
                for api_type, keys in api_keys.items():
                    for key in keys:
                        key["api_type"] = api_type
                        result.append(key)
                
                return result
        
        except Exception as e:
            logger.error(f"加载缓存的API密钥失败: {str(e)}")
            return []

# 单例模式
client_initializer = ClientInitializer() 
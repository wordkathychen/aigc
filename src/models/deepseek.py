"""
DeepSeek API 交互模块
提供与DeepSeek API通信的功能
"""

import os
import json
import time
import requests
from typing import Dict, List, Any, Optional, Union
from src.utils.logger import setup_logger
from src.config.settings import (
    DEEPSEEK_API_KEY, 
    DEEPSEEK_API_URL,
    DEEPSEEK_MODEL,
    MAX_TOKENS,
    MAX_RETRY_COUNT,
    REQUEST_TIMEOUT
)

logger = setup_logger(__name__)

class DeepseekAPI:
    """DeepSeek API 交互类"""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None, model: Optional[str] = None):
        """初始化API客户端
        
        Args:
            api_key: API密钥，默认使用配置文件中的密钥
            api_url: API端点URL，默认使用配置文件中的URL
            model: 模型名称，默认使用配置文件中的模型
        """
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.api_url = api_url or DEEPSEEK_API_URL
        self.model = model or DEEPSEEK_MODEL
        
        # 验证API密钥
        if self.api_key == "YOUR_DEEPSEEK_API_KEY":
            logger.warning("使用默认API密钥，请在配置文件中设置真实的API密钥")
        
        # 设置请求头
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        logger.info(f"初始化DeepSeek API客户端，模型: {self.model}")
    
    def generate_content(self, prompt: str, task: str, max_tokens: Optional[int] = None) -> str:
        """生成文本内容
        
        Args:
            prompt: 提示词
            task: 任务描述（用于日志）
            max_tokens: 最大生成令牌数
            
        Returns:
            str: 生成的文本内容
            
        Raises:
            Exception: API调用失败
        """
        if not prompt:
            raise ValueError("提示词不能为空")
            
        max_tokens = max_tokens or MAX_TOKENS
        
        # 准备请求数据
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的文本生成助手，擅长各类文档写作。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.95
        }
        
        # 尝试调用API
        retry_count = 0
        while retry_count < MAX_RETRY_COUNT:
            try:
                logger.info(f"发送API请求：{task}")
                response = requests.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=data,
                    timeout=REQUEST_TIMEOUT
                )
                
                # 检查响应状态
                response.raise_for_status()
                
                # 解析响应
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                logger.info(f"API请求成功: {task}")
                return content
                
            except requests.exceptions.RequestException as e:
                retry_count += 1
                logger.warning(f"API请求失败 ({retry_count}/{MAX_RETRY_COUNT}): {str(e)}")
                
                if retry_count < MAX_RETRY_COUNT:
                    # 等待一段时间后重试
                    time.sleep(2 ** retry_count)  # 指数退避
                else:
                    logger.error(f"API请求失败，已达到最大重试次数: {str(e)}")
                    raise Exception(f"API请求失败: {str(e)}")
    
    def generate_chat_completion(self, messages: List[Dict[str, str]], task: str, max_tokens: Optional[int] = None) -> str:
        """生成聊天完成
        
        Args:
            messages: 聊天消息列表，每个消息包含role和content
            task: 任务描述（用于日志）
            max_tokens: 最大生成令牌数
            
        Returns:
            str: 生成的文本内容
            
        Raises:
            Exception: API调用失败
        """
        if not messages:
            raise ValueError("消息列表不能为空")
            
        max_tokens = max_tokens or MAX_TOKENS
        
        # 准备请求数据
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.95
        }
        
        # 尝试调用API
        retry_count = 0
        while retry_count < MAX_RETRY_COUNT:
            try:
                logger.info(f"发送聊天API请求：{task}")
                response = requests.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=data,
                    timeout=REQUEST_TIMEOUT
                )
                
                # 检查响应状态
                response.raise_for_status()
                
                # 解析响应
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                logger.info(f"聊天API请求成功: {task}")
                return content
                
            except requests.exceptions.RequestException as e:
                retry_count += 1
                logger.warning(f"聊天API请求失败 ({retry_count}/{MAX_RETRY_COUNT}): {str(e)}")
                
                if retry_count < MAX_RETRY_COUNT:
                    # 等待一段时间后重试
                    time.sleep(2 ** retry_count)  # 指数退避
                else:
                    logger.error(f"聊天API请求失败，已达到最大重试次数: {str(e)}")
                    raise Exception(f"聊天API请求失败: {str(e)}")


class DeepseekGenerator:
    """基于DeepSeek的内容生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.api = DeepseekAPI()
        
    def generate_text(self, prompt: str, task_description: str, max_length: Optional[int] = None) -> str:
        """生成文本
        
        Args:
            prompt: 提示词
            task_description: 任务描述
            max_length: 最大生成长度
            
        Returns:
            str: 生成的文本
        """
        return self.api.generate_content(prompt, task_description, max_length)
    
    def generate_with_context(self, context: str, query: str, task_description: str, max_length: Optional[int] = None) -> str:
        """基于上下文生成内容
        
        Args:
            context: 上下文信息
            query: 查询/提问
            task_description: 任务描述
            max_length: 最大生成长度
            
        Returns:
            str: 生成的文本
        """
        prompt = f"""
        上下文信息：
        {context}
        
        请根据上述上下文，回答以下问题：
        {query}
        """
        
        return self.api.generate_content(prompt, task_description, max_length)
    
    def analyze_text(self, text: str, analysis_type: str, task_description: str) -> Dict:
        """分析文本
        
        Args:
            text: 待分析文本
            analysis_type: 分析类型（如"情感分析"、"关键词提取"等）
            task_description: 任务描述
            
        Returns:
            Dict: 分析结果
        """
        prompt = f"""
        请对以下文本进行{analysis_type}分析，并以JSON格式返回结果：
        
        {text}
        
        请确保返回的是有效的JSON格式，包含分析结果的各个方面。
        """
        
        result_text = self.api.generate_content(prompt, task_description)
        
        # 提取JSON部分
        try:
            # 查找JSON的开始和结束位置
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = result_text[start:end]
                return json.loads(json_str)
            else:
                # 尝试解析整个文本
                return json.loads(result_text)
        except json.JSONDecodeError:
            logger.warning(f"无法解析API返回的JSON: {result_text}")
            # 返回文本形式的结果
            return {"text": result_text}

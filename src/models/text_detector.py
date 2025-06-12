import os
import re
import difflib
import random
from typing import Dict, List, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from utils.api_manager import APIManager
from utils.logger import setup_logger
from src.models.deepseek import DeepseekAPI
from src.config.settings import DETECTION_THRESHOLD, MAX_RETRY_COUNT

logger = setup_logger(__name__)

class TextDetector:
    """文本检测与降重功能"""
    
    def __init__(self):
        self.api = DeepseekAPI()
        self.detection_threshold = DETECTION_THRESHOLD
        self.original_text = ""
        self.optimized_text = ""
        self.similarity_score = 0.0
        
    def load_text(self, text: str) -> None:
        """加载原始文本"""
        self.original_text = text
        logger.info(f"加载原始文本，长度：{len(text)}字符")
        
    def detect_similarity(self, text1: str, text2: str) -> float:
        """计算两段文本的相似度"""
        seq_matcher = difflib.SequenceMatcher(None, text1, text2)
        similarity = seq_matcher.ratio()
        logger.info(f"文本相似度: {similarity:.2f}")
        return similarity
        
    def optimize_text(self, text: str, intensity: str = "moderate") -> str:
        """使用AI优化文本，降低重复率"""
        intensity_map = {
            "light": "轻度优化，保持原文语义和结构，仅替换少量词语",
            "moderate": "中度优化，保持原文主要语义，但可以调整句式和表达方式",
            "heavy": "深度优化，保留核心意思，但可以重构整个段落和表达方式"
        }
        
        intensity_desc = intensity_map.get(intensity, intensity_map["moderate"])
        
        prompt = f"""
        请帮我优化以下文本，降低文本的重复率和可被检测率。
        优化要求：{intensity_desc}
        优化后的文本需要：
        1. 保持原文的核心意思和专业性
        2. 替换可能的同义词和近义词
        3. 调整句式结构，避免直接复制
        4. 重新组织表达顺序
        5. 适当补充或简化内容，但不改变原意
        
        原文：
        {text}
        """
        
        try:
            optimized = self.api.generate_content(prompt, "文本降重优化", len(text))
            return optimized
        except Exception as e:
            logger.error(f"文本优化失败: {str(e)}")
            return text
    
    def highlight_differences(self, original: str, optimized: str) -> Tuple[str, List[Tuple[int, int, float]]]:
        """标记优化后文本与原文的差异，并计算局部相似度"""
        differ = difflib.Differ()
        diff = list(differ.compare(original.split(), optimized.split()))
        
        highlighted_text = optimized
        similarity_regions = []
        
        # 将文本分成多个区块进行对比
        block_size = 50  # 每个区块的单词数
        for i in range(0, len(optimized.split()), block_size):
            block_end = min(i + block_size, len(optimized.split()))
            original_block = ' '.join(original.split()[i:block_end])
            optimized_block = ' '.join(optimized.split()[i:block_end])
            
            # 计算该区块的相似度
            block_similarity = self.detect_similarity(original_block, optimized_block)
            
            # 记录区块位置和相似度
            start_pos = len(' '.join(optimized.split()[:i]))
            end_pos = len(' '.join(optimized.split()[:block_end]))
            similarity_regions.append((start_pos, end_pos, block_similarity))
        
        return highlighted_text, similarity_regions
    
    def process(self, text: str, intensity: str = "moderate") -> Dict:
        """处理文本：检测并优化"""
        self.load_text(text)
        
        # 优化文本
        logger.info(f"开始优化文本，优化强度: {intensity}")
        self.optimized_text = self.optimize_text(text, intensity)
        
        # 计算整体相似度
        self.similarity_score = self.detect_similarity(self.original_text, self.optimized_text)
        
        # 标记差异并计算局部相似度
        highlighted_text, similarity_regions = self.highlight_differences(
            self.original_text, self.optimized_text
        )
        
        return {
            "original_text": self.original_text,
            "optimized_text": self.optimized_text,
            "similarity_score": self.similarity_score,
            "highlighted_text": highlighted_text,
            "similarity_regions": similarity_regions
        }
    
    def save_result(self, filepath: str) -> bool:
        """保存优化后的文本到文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.optimized_text)
            logger.info(f"优化后的文本已保存到: {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存文件失败: {str(e)}")
            return False


class AIDetector(TextDetector):
    """专门针对AI检测的文本优化器"""
    
    def __init__(self):
        super().__init__()
        self.detection_platforms = ["达郡AI检测", "论文狗", "PaperPass", "写作猫"]
        
    def optimize_for_ai_detection(self, text: str, platform: str = None) -> str:
        """特别针对AI检测平台优化文本"""
        platform_str = f"，特别针对{platform}平台" if platform else ""
        
        prompt = f"""
        请帮我优化以下文本，使其能够通过AI检测工具的检查{platform_str}。
        优化要求：
        1. 保持原文的核心意思和专业性
        2. 增加人类写作的特征，如适当的口语化表达、转折和过渡词的使用
        3. 引入更多专业术语和行业词汇
        4. 调整句式结构，避免AI常见的句式模式
        5. 减少模板化、规则化的表达
        6. 增加一些人类可能出现的小瑕疵，如适当的重复、转折等
        7. 保持文本的连贯性和专业性
        
        原文：
        {text}
        """
        
        try:
            optimized = self.api.generate_content(prompt, "AI检测优化", len(text))
            return optimized
        except Exception as e:
            logger.error(f"AI检测优化失败: {str(e)}")
            return text
    
    def estimate_ai_score(self, text: str, platform: str = None) -> float:
        """估算文本在AI检测平台上的得分（模拟）"""
        # 这里模拟AI检测得分，实际应用中可以接入真实API
        base_score = random.uniform(0.6, 0.9)  # 基础分数
        length_factor = min(1.0, len(text) / 5000)  # 文本长度因素
        random_factor = random.uniform(-0.1, 0.1)  # 随机波动
        
        score = base_score * length_factor + random_factor
        return max(0.0, min(1.0, score))  # 确保分数在0-1之间
    
    def process_for_ai_detection(self, text: str, platform: str = None) -> Dict:
        """处理文本：针对AI检测进行优化"""
        self.load_text(text)
        
        # 优化前估算AI检测得分
        before_score = self.estimate_ai_score(text, platform)
        
        # 针对AI检测优化文本
        logger.info(f"开始针对AI检测优化文本，目标平台: {platform or '通用'}")
        self.optimized_text = self.optimize_for_ai_detection(text, platform)
        
        # 优化后估算AI检测得分
        after_score = self.estimate_ai_score(self.optimized_text, platform)
        
        # 计算相似度
        self.similarity_score = self.detect_similarity(self.original_text, self.optimized_text)
        
        # 标记差异并计算局部相似度
        highlighted_text, similarity_regions = self.highlight_differences(
            self.original_text, self.optimized_text
        )
        
        return {
            "original_text": self.original_text,
            "optimized_text": self.optimized_text,
            "similarity_score": self.similarity_score,
            "highlighted_text": highlighted_text,
            "similarity_regions": similarity_regions,
            "before_ai_score": before_score,
            "after_ai_score": after_score,
            "platform": platform or "通用"
        }
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
import jieba
import numpy as np
from utils.logger import setup_logger
from utils.api_manager import APIManager

logger = setup_logger(__name__)

class TextOptimizer:
    def __init__(self, api_manager: APIManager):
        self.api = api_manager
        self.vectorizer = TfidfVectorizer(tokenizer=lambda x: list(jieba.cut(x)))
        
    def analyze_similarity(self, original_text: str, reference_texts: List[str]) -> Dict:
        """分析文本相似度"""
        try:
            # 计算TF-IDF向量
            texts = [original_text] + reference_texts
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # 计算相似度矩阵
            similarity_matrix = (tfidf_matrix * tfidf_matrix.T).toarray()
            
            # 获取与原文的相似度
            similarities = similarity_matrix[0][1:]
            
            # 找出高相似度段落
            similar_segments = self._find_similar_segments(
                original_text, 
                reference_texts,
                similarities
            )
            
            return {
                'overall_similarity': float(np.mean(similarities)),
                'max_similarity': float(np.max(similarities)),
                'similar_segments': similar_segments
            }
        except Exception as e:
            logger.error(f"相似度分析失败: {str(e)}")
            raise

    def optimize_text(self, text: str, similar_segments: List[Dict]) -> str:
        """优化文本内容"""
        try:
            # 根据相似段落生成优化提示
            prompt = self._create_optimization_prompt(text, similar_segments)
            
            # 调用API进行优化
            optimized_text = self.api.generate_text(prompt)
            
            return optimized_text
            
        except Exception as e:
            logger.error(f"文本优化失败: {str(e)}")
            raise

    def _find_similar_segments(self, text: str, references: List[str], 
                             similarities: np.ndarray) -> List[Dict]:
        """查找相似文本段落"""
        similar_segments = []
        sentences = text.split('。')
        
        for ref_idx, ref_text in enumerate(references):
            if similarities[ref_idx] > 0.6:  # 相似度阈值
                ref_sentences = ref_text.split('。')
                
                # 计算句子级别相似度
                sentence_vectorizer = TfidfVectorizer(
                    tokenizer=lambda x: list(jieba.cut(x))
                )
                sentence_matrix = sentence_vectorizer.fit_transform(
                    sentences + ref_sentences
                )
                sentence_similarity = (
                    sentence_matrix * sentence_matrix.T
                ).toarray()
                
                # 找出相似句子对
                n_sentences = len(sentences)
                for i, sent in enumerate(sentences):
                    for j, ref_sent in enumerate(ref_sentences):
                        sim_score = sentence_similarity[i][n_sentences + j]
                        if sim_score > 0.7:  # 句子相似度阈值
                            similar_segments.append({
                                'original': sent,
                                'reference': ref_sent,
                                'similarity': float(sim_score)
                            })
                            
        return similar_segments

    def _create_optimization_prompt(self, text: str, 
                                  similar_segments: List[Dict]) -> str:
        """创建优化提示词"""
        prompt = f"""
        请对以下文本进行改写和优化，重点关注以下相似片段，保持原意的同时使用不同的表达方式：
        
        原文：
        {text}
        
        需要重点优化的片段：
        {self._format_similar_segments(similar_segments)}
        
        优化要求：
        1. 保持学术性和专业性
        2. 改变句式结构
        3. 使用同义词替换
        4. 重组段落逻辑
        5. 避免改变原意
        6. 保持行文流畅
        
        请生成优化后的完整文本。
        """
        return prompt

    def _format_similar_segments(self, segments: List[Dict]) -> str:
        """格式化相似片段信息"""
        result = []
        for idx, seg in enumerate(segments, 1):
            result.append(
                f"{idx}. 原文片段：{seg['original']}\n"
                f"   相似内容：{seg['reference']}\n"
                f"   相似度：{seg['similarity']:.2%}\n"
            )
        return '\n'.join(result)

    def analyze_style(self, text: str) -> Dict:
        """分析文本风格特征"""
        try:
            # 分析文本风格
            words = list(jieba.cut(text))
            sentences = text.split('。')
            
            return {
                'avg_sentence_length': len(words) / len(sentences),
                'unique_words_ratio': len(set(words)) / len(words),
                'punctuation_ratio': len([c for c in text if c in '，。；：！？']) / len(text)
            }
        except Exception as e:
            logger.error(f"风格分析失败: {str(e)}")
            raise
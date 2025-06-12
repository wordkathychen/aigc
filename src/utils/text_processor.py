from typing import List
from src.config.settings import MIN_WORDS, MAX_WORDS
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class TextProcessor:
    def __init__(self, total_words: int):
        self.validate_word_count(total_words)
        self.total_words = total_words
    
    @staticmethod
    def validate_word_count(words: int) -> None:
        """验证字数是否在合理范围内"""
        if not isinstance(words, int):
            raise ValueError("字数必须是整数")
        if words < MIN_WORDS:
            raise ValueError(f"字数不能少于 {MIN_WORDS}")
        if words > MAX_WORDS:
            raise ValueError(f"字数不能超过 {MAX_WORDS}")
    
    def distribute_words(self, section_count: int) -> List[int]:
        """将总字数平均分配到各个章节"""
        if not isinstance(section_count, int) or section_count < 1:
            raise ValueError("章节数必须是正整数")
            
        base_words = self.total_words // section_count
        remaining = self.total_words % section_count
        
        distribution = [base_words] * section_count
        
        # 将余数分配到前几个章节
        for i in range(remaining):
            distribution[i] += 1
            
        logger.info(f"字数分配完成: {distribution}")
        return distribution
import re
import random
from datetime import datetime, timedelta
from src.utils.logger import setup_logger
from src.models.api_manager import APIManager

logger = setup_logger(__name__)

class ReferenceGenerator:
    """参考文献生成器"""
    
    def __init__(self):
        """初始化参考文献生成器"""
        self.api_manager = APIManager()
        
        # 期刊名列表
        self.chinese_journals = [
            "中国科学",
            "科学通报",
            "自然科学进展",
            "计算机学报",
            "电子学报",
            "软件学报",
            "通信学报",
            "土木工程学报",
            "机械工程学报",
            "教育研究",
            "心理学报",
            "管理学报",
            "医学研究杂志",
            "建筑学报"
        ]
        
        self.english_journals = [
            "Nature",
            "Science",
            "IEEE Transactions on Pattern Analysis and Machine Intelligence",
            "ACM Computing Surveys",
            "Journal of Civil Engineering",
            "Educational Research Review",
            "Journal of Management Studies",
            "Psychological Review",
            "Medical Research Journal",
            "International Journal of Architectural Research"
        ]
        
        # 出版社列表
        self.publishers = [
            "清华大学出版社",
            "北京大学出版社",
            "科学出版社",
            "人民教育出版社",
            "机械工业出版社",
            "电子工业出版社",
            "高等教育出版社",
            "Springer",
            "Elsevier",
            "Wiley",
            "Oxford University Press",
            "Cambridge University Press"
        ]
        
        # 大学列表
        self.universities = [
            "清华大学",
            "北京大学",
            "浙江大学",
            "复旦大学",
            "上海交通大学",
            "南京大学",
            "中国科学技术大学",
            "哈尔滨工业大学",
            "武汉大学",
            "华中科技大学"
        ]
        
    def generate_references(self, topic, subject, count=10, format_type="GB/T 7714-2015"):
        """生成参考文献
        
        Args:
            topic: 论文主题
            subject: 学科领域
            count: 参考文献数量
            format_type: 参考文献格式类型
            
        Returns:
            str: 生成的参考文献文本
        """
        try:
            # 使用API生成参考文献
            prompt = self._create_prompt(topic, subject, count, format_type)
            response = self.api_manager.generate_content_sync(prompt, max_tokens=count * 100)
            
            # 处理生成结果
            references = self._format_references(response, format_type)
            
            return references
            
        except Exception as e:
            logger.error(f"参考文献生成失败: {str(e)}")
            # 失败时使用本地生成的备选方案
            return self._generate_fallback_references(topic, subject, count, format_type)
    
    def _create_prompt(self, topic, subject, count, format_type):
        """创建参考文献生成提示词"""
        return f"""
        请为论文《{topic}》生成{count}个参考文献，学科领域是{subject}。
        
        要求：
        1. 遵循{format_type}格式
        2. 包含中英文文献，中文占70%，英文占30%
        3. 包含期刊论文、专著、学位论文、会议论文等不同类型
        4. 大部分为近5年内的文献
        5. 所有文献必须真实存在，不可编造
        6. 每个参考文献占一行，前面标注序号
        
        示例（GB/T 7714-2015格式）：
        [1] 张三, 李四, 王五. 论文标题[J]. 期刊名称, 2022, 28(3): 112-118.
        [2] Smith J, Johnson P. Article Title[J]. Journal Name, 2021, 15(2): 230-245.
        [3] 赵六. 专著名称[M]. 北京: 出版社, 2020: 56-78.
        """
    
    def _format_references(self, references, format_type):
        """格式化参考文献"""
        # 分行处理
        lines = references.strip().split('\n')
        
        # 确保每行都是有效的参考文献
        valid_refs = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 如果没有序号，添加序号
            if not line.startswith('['):
                line = f"[{len(valid_refs)+1}] {line}"
                
            valid_refs.append(line)
        
        # 如果格式不是GB/T 7714-2015，尝试转换格式
        if format_type != "GB/T 7714-2015":
            valid_refs = self._convert_format(valid_refs, format_type)
            
        return '\n'.join(valid_refs)
    
    def _convert_format(self, references, target_format):
        """转换参考文献格式"""
        # 实际应用中，这里应该有复杂的格式转换逻辑
        # 简化版本只是添加格式标注
        return [f"{ref} ({target_format}格式)" for ref in references]
    
    def _generate_fallback_references(self, topic, subject, count, format_type):
        """生成备选参考文献（本地生成）"""
        references = []
        
        # 计算中英文比例
        cn_count = int(count * 0.7)
        en_count = count - cn_count
        
        # 生成当前年份和最近几年
        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year + 1))
        
        # 生成中文参考文献
        for i in range(cn_count):
            if i % 3 == 0:  # 期刊论文
                ref = self._generate_chinese_journal(i+1, topic, subject, random.choice(years))
            elif i % 3 == 1:  # 专著
                ref = self._generate_chinese_book(i+1, topic, subject, random.choice(years))
            else:  # 学位论文
                ref = self._generate_chinese_thesis(i+1, topic, subject, random.choice(years))
                
            references.append(ref)
        
        # 生成英文参考文献
        for i in range(en_count):
            if i % 2 == 0:  # 期刊论文
                ref = self._generate_english_journal(cn_count+i+1, topic, subject, random.choice(years))
            else:  # 专著
                ref = self._generate_english_book(cn_count+i+1, topic, subject, random.choice(years))
                
            references.append(ref)
        
        return '\n'.join(references)
    
    def _generate_chinese_journal(self, index, topic, subject, year):
        """生成中文期刊论文引用"""
        # 生成作者（1-3人）
        authors_count = random.randint(1, 3)
        authors = []
        for _ in range(authors_count):
            surname = random.choice(["张", "李", "王", "赵", "陈", "刘", "杨", "黄", "周", "吴"])
            name = random.choice(["明", "华", "强", "伟", "芳", "娟", "磊", "丽", "涛", "超"])
            authors.append(f"{surname}{name}")
        
        # 拼接作者
        authors_text = ", ".join(authors)
        
        # 生成标题
        title = f"{subject}领域{topic}的研究"
        
        # 生成期刊信息
        journal = random.choice(self.chinese_journals)
        volume = random.randint(10, 50)
        issue = random.randint(1, 12)
        start_page = random.randint(1, 100)
        end_page = start_page + random.randint(5, 20)
        
        # 生成GB/T 7714-2015格式引用
        return f"[{index}] {authors_text}. {title}[J]. {journal}, {year}, {volume}({issue}): {start_page}-{end_page}."
    
    def _generate_chinese_book(self, index, topic, subject, year):
        """生成中文专著引用"""
        # 生成作者（1-2人）
        authors_count = random.randint(1, 2)
        authors = []
        for _ in range(authors_count):
            surname = random.choice(["张", "李", "王", "赵", "陈", "刘", "杨", "黄", "周", "吴"])
            name = random.choice(["明", "华", "强", "伟", "芳", "娟", "磊", "丽", "涛", "超"])
            authors.append(f"{surname}{name}")
        
        # 拼接作者
        authors_text = ", ".join(authors)
        
        # 生成标题
        title = f"{subject}理论与应用"
        
        # 生成出版信息
        publisher = random.choice(self.publishers)
        
        # 生成GB/T 7714-2015格式引用
        return f"[{index}] {authors_text}. {title}[M]. 北京: {publisher}, {year}: {random.randint(1, 300)}-{random.randint(301, 500)}."
    
    def _generate_chinese_thesis(self, index, topic, subject, year):
        """生成中文学位论文引用"""
        # 生成作者（单人）
        surname = random.choice(["张", "李", "王", "赵", "陈", "刘", "杨", "黄", "周", "吴"])
        name = random.choice(["明", "华", "强", "伟", "芳", "娟", "磊", "丽", "涛", "超"])
        author = f"{surname}{name}"
        
        # 生成标题
        title = f"{topic}关键技术研究"
        
        # 生成学校信息
        university = random.choice(self.universities)
        
        # 生成GB/T 7714-2015格式引用
        return f"[{index}] {author}. {title}[D]. {university}, {year}."
    
    def _generate_english_journal(self, index, topic, subject, year):
        """生成英文期刊论文引用"""
        # 生成作者（1-3人）
        authors_count = random.randint(1, 3)
        first_names = ["John", "Michael", "David", "James", "Robert", "Mary", "Jennifer", "Linda", "Elizabeth", "Susan"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Wilson", "Taylor"]
        
        authors = []
        for _ in range(authors_count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            # 只显示姓的首字母
            authors.append(f"{last_name} {first_name[0]}")
        
        # 拼接作者
        authors_text = ", ".join(authors)
        
        # 生成标题（首字母大写）
        words = topic.replace("研究", "Research").split()
        title = " ".join([w.capitalize() for w in words]) + f" in {subject.capitalize()}"
        
        # 生成期刊信息
        journal = random.choice(self.english_journals)
        volume = random.randint(10, 50)
        issue = random.randint(1, 12)
        start_page = random.randint(1, 100)
        end_page = start_page + random.randint(5, 20)
        
        # 生成GB/T 7714-2015格式引用
        return f"[{index}] {authors_text}. {title}[J]. {journal}, {year}, {volume}({issue}): {start_page}-{end_page}."
    
    def _generate_english_book(self, index, topic, subject, year):
        """生成英文专著引用"""
        # 生成作者（1-2人）
        authors_count = random.randint(1, 2)
        first_names = ["John", "Michael", "David", "James", "Robert", "Mary", "Jennifer", "Linda", "Elizabeth", "Susan"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Wilson", "Taylor"]
        
        authors = []
        for _ in range(authors_count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            # 只显示姓的首字母
            authors.append(f"{last_name} {first_name[0]}")
        
        # 拼接作者
        authors_text = ", ".join(authors)
        
        # 生成标题（首字母大写）
        title = f"Principles and Applications of {subject.capitalize()}"
        
        # 生成出版信息
        english_publishers = ["Springer", "Elsevier", "Wiley", "Oxford University Press", "Cambridge University Press"]
        publisher = random.choice(english_publishers)
        cities = ["New York", "London", "Berlin", "Amsterdam", "Cambridge"]
        city = random.choice(cities)
        
        # 生成GB/T 7714-2015格式引用
        return f"[{index}] {authors_text}. {title}[M]. {city}: {publisher}, {year}: {random.randint(1, 300)}-{random.randint(301, 500)}." 
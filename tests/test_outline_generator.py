import unittest
import sys
import os
from unittest.mock import patch

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.utils.outline_generator import OutlineGenerator

class TestOutlineGenerator(unittest.TestCase):
    def setUp(self):
        """测试前的设置"""
        self.generator = OutlineGenerator()

    def test_generate_outline_valid_title(self):
        """测试有效标题的大纲生成"""
        title = "Python编程入门指南"
        outline = self.generator.generate_outline(title)
        
        # 验证返回的大纲
        self.assertIsInstance(outline, list)
        self.assertTrue(len(outline) > 0)
        self.assertTrue(all(isinstance(section, str) for section in outline))

    def test_generate_outline_empty_title(self):
        """测试空标题"""
        with self.assertRaises(ValueError):
            self.generator.generate_outline("")

    def test_generate_outline_long_title(self):
        """测试过长标题"""
        long_title = "x" * 101
        with self.assertRaises(ValueError):
            self.generator.generate_outline(long_title)

    @patch('src.utils.outline_generator.DeepseekAPI')
    def test_generate_outline_api_integration(self, mock_deepseek):
        """测试与DeepseekAPI的集成"""
        # 模拟API返回值
        mock_outline = ["第一章：基础概念", "第二章：进阶技巧", "第三章：实战应用"]
        mock_deepseek.return_value.generate_outline.return_value = mock_outline
        
        title = "Python入门教程"
        outline = self.generator.generate_outline(title)
        
        self.assertEqual(outline, mock_outline)
        mock_deepseek.return_value.generate_outline.assert_called_once_with(title)

    def test_generate_outline_special_characters(self):
        """测试包含特殊字符的标题"""
        title = "Python！@#￥%……&*（）特殊字符测试"
        outline = self.generator.generate_outline(title)
        
        self.assertIsInstance(outline, list)
        self.assertTrue(len(outline) > 0)

if __name__ == '__main__':
    unittest.main()
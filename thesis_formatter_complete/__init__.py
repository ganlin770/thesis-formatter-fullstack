#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
毕业论文格式化工具完整版
包含所有格式化模块的集成包
"""

# 版本信息
__version__ = "1.0.0"
__author__ = "Thesis Formatter Team"
__description__ = "江西财经大学现代经济管理学院毕业论文格式化工具"

# 导入所有模块
from .cover_generator import CoverGenerator, CommitmentGenerator
from .page_number_handler import PageNumberHandler, PageNumberStyle
from .keyword_formatter import KeywordFormatter
from .figure_table_handler import FigureTableHandler
from .footnote_formatter import FootnoteFormatter
from .math_formatter import MathFormatter
from .toc_generator import TOCGenerator
from .acknowledgment_formatter import AcknowledgmentFormatter
from .main_formatter import CompleteThesisFormatter

# 导出的类和函数
__all__ = [
    # 主格式化器
    'CompleteThesisFormatter',
    
    # 各个功能模块
    'CoverGenerator',
    'CommitmentGenerator',
    'PageNumberHandler',
    'PageNumberStyle',
    'KeywordFormatter',
    'FigureTableHandler',
    'FootnoteFormatter',
    'MathFormatter',
    'TOCGenerator',
    'AcknowledgmentFormatter',
]

# 快速格式化函数
def format_thesis(document_path, thesis_info=None, config=None):
    """
    快速格式化论文
    
    Args:
        document_path: Word文档路径
        thesis_info: 论文信息字典
        config: 配置字典
    
    Returns:
        str: 格式化后的文档路径
    """
    formatter = CompleteThesisFormatter(document_path, config)
    success = formatter.format_document(thesis_info)
    
    if success:
        return formatter.document_path
    else:
        raise Exception("格式化失败")

# 配置模板
def get_default_config():
    """获取默认配置"""
    return {
        'generate_cover': True,           # 生成封面
        'generate_commitment': True,      # 生成诚信承诺书
        'format_keywords': True,          # 格式化关键词
        'format_figures_tables': True,    # 格式化图表编号
        'format_footnotes': True,         # 格式化脚注
        'format_math': True,              # 格式化数学公式
        'update_toc': True,               # 更新目录
        'format_acknowledgment': True,    # 格式化致谢
        'setup_page_numbers': True,       # 设置页码
        'reorder_document': True          # 重组文档结构
    }

def get_thesis_info_template():
    """获取论文信息模板"""
    return {
        'title': '论文题目',
        'major': '专业名称',
        'class': '班级',
        'student_id': '学号',
        'name': '姓名',
        'advisor': '指导教师',
        'date': '2024年5月'
    }
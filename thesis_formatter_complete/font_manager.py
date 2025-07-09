#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体管理器模块
提供精确的字体字号控制，支持特殊字号和复杂字体规则
"""

from docx import Document
from docx.shared import Pt, Cm
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
import logging
from typing import Dict, Optional, Tuple, Union

class FontManager:
    """字体管理器：统一管理所有字体字号设置"""
    
    # 特殊字号映射表
    SPECIAL_FONT_SIZES = {
        '初号': 42,
        '小初': 36,
        '一号': 26,
        '小一': 24,
        '二号': 22,
        '二号六': 21,  # 特殊字号
        '小二': 18,
        '三号': 16,
        '小三': 15,
        '四号': 14,
        '小四': 12,
        '五号': 10.5,
        '小五': 9
    }
    
    # 字体规则配置
    FONT_RULES = {
        'cover_title': {
            'cn_font': '宋体',
            'en_font': 'Times New Roman',
            'size': '三号',
            'bold': True,
            'alignment': 'center'
        },
        'abstract_title_cn': {
            'cn_font': '黑体',  # 修正：原来错误使用宋体
            'en_font': 'Arial',
            'size': '二号',
            'bold': True,
            'alignment': 'center'
        },
        'abstract_title_en': {
            'cn_font': 'Arial Black',
            'en_font': 'Arial Black',  # 修正：原来错误使用Times New Roman
            'size': '二号',
            'bold': True,
            'alignment': 'center'
        },
        'thesis_title': {
            'cn_font': '宋体',
            'en_font': 'Times New Roman',
            'size': '二号六',  # 特殊字号
            'bold': True,
            'alignment': 'center'
        },
        'heading_1': {
            'cn_font': '宋体',
            'en_font': 'Times New Roman',
            'size': '小三',
            'bold': True,
            'alignment': 'left'
        },
        'heading_2': {
            'cn_font': '宋体',
            'en_font': 'Times New Roman',
            'size': '四号',
            'bold': True,
            'alignment': 'left'
        },
        'heading_3': {
            'cn_font': '宋体',
            'en_font': 'Times New Roman',
            'size': '小四',
            'bold': True,
            'alignment': 'left'
        },
        'main_text': {
            'cn_font': '宋体',
            'en_font': 'Times New Roman',
            'size': '小四',
            'bold': False,
            'alignment': 'justify'
        },
        'table_header': {
            'cn_font': '宋体',
            'en_font': 'Times New Roman',
            'size': '小四',
            'bold': True,  # 确保表头加粗
            'alignment': 'center'
        },
        'table_content': {
            'cn_font': '宋体',
            'en_font': 'Times New Roman',
            'size': '小四',
            'bold': False,
            'alignment': 'center'
        },
        'formula_variable': {
            'cn_font': 'Times New Roman',
            'en_font': 'Times New Roman',
            'size': '小四',
            'bold': False,
            'italic': True  # 变量使用斜体
        },
        'formula_constant': {
            'cn_font': 'Times New Roman',
            'en_font': 'Times New Roman',
            'size': '小四',
            'bold': False,
            'italic': False  # 常量使用正体
        },
        'footnote': {
            'cn_font': '宋体',
            'en_font': 'Times New Roman',
            'size': '小五',
            'bold': False,
            'alignment': 'justify'
        },
        'reference': {
            'cn_font': '宋体',
            'en_font': 'Times New Roman',
            'size': '五号',
            'bold': False,
            'alignment': 'justify'
        },
        'keyword_label': {
            'cn_font': '楷体',
            'en_font': 'Times New Roman',
            'size': '小四',
            'bold': True,
            'alignment': 'left'
        },
        'keyword_content': {
            'cn_font': '楷体',
            'en_font': 'Times New Roman',
            'size': '小四',
            'bold': False,
            'alignment': 'left'
        },
        'page_header': {
            'cn_font': '宋体',
            'en_font': 'Times New Roman',
            'size': '五号',
            'bold': False,
            'alignment': 'center'
        },
        'figure_caption': {
            'cn_font': '宋体',
            'en_font': 'Times New Roman',
            'size': '五号',
            'bold': False,
            'alignment': 'center'
        },
        'source_note': {
            'cn_font': '宋体',
            'en_font': 'Times New Roman',
            'size': '小五',
            'bold': False,
            'alignment': 'left'
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def apply_font_style(self, run, style_name: str, 
                        text_type: str = 'cn') -> None:
        """
        应用字体样式到run对象
        
        Args:
            run: docx run对象
            style_name: 样式名称（从FONT_RULES中选择）
            text_type: 文本类型 'cn'中文 或 'en'英文
        """
        if style_name not in self.FONT_RULES:
            self.logger.warning(f"未知的样式名称: {style_name}")
            return
            
        rule = self.FONT_RULES[style_name]
        
        # 设置字体
        font_key = f'{text_type}_font'
        if font_key in rule:
            run.font.name = rule[font_key]
            if text_type == 'cn':
                run._element.rPr.rFonts.set(qn('w:eastAsia'), rule[font_key])
        
        # 设置字号
        if 'size' in rule:
            size_value = rule['size']
            if isinstance(size_value, str) and size_value in self.SPECIAL_FONT_SIZES:
                run.font.size = Pt(self.SPECIAL_FONT_SIZES[size_value])
            elif isinstance(size_value, (int, float)):
                run.font.size = Pt(size_value)
        
        # 设置加粗
        if 'bold' in rule:
            run.font.bold = rule['bold']
        
        # 设置斜体
        if 'italic' in rule:
            run.font.italic = rule['italic']
    
    def apply_paragraph_style(self, paragraph, style_name: str) -> None:
        """
        应用段落样式
        
        Args:
            paragraph: docx paragraph对象
            style_name: 样式名称
        """
        if style_name not in self.FONT_RULES:
            return
            
        rule = self.FONT_RULES[style_name]
        
        # 设置对齐方式
        if 'alignment' in rule:
            alignment_map = {
                'left': WD_ALIGN_PARAGRAPH.LEFT,
                'center': WD_ALIGN_PARAGRAPH.CENTER,
                'right': WD_ALIGN_PARAGRAPH.RIGHT,
                'justify': WD_ALIGN_PARAGRAPH.JUSTIFY
            }
            if rule['alignment'] in alignment_map:
                paragraph.alignment = alignment_map[rule['alignment']]
    
    def detect_text_type(self, text: str) -> str:
        """
        检测文本类型（中文或英文）
        
        Args:
            text: 待检测文本
            
        Returns:
            'cn' 或 'en'
        """
        # 简单判断：如果包含中文字符则认为是中文
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return 'cn'
        return 'en'
    
    def format_mixed_text(self, paragraph, style_name: str) -> None:
        """
        格式化中英文混合文本
        
        Args:
            paragraph: 段落对象
            style_name: 样式名称
        """
        # 首先应用段落样式
        self.apply_paragraph_style(paragraph, style_name)
        
        # 对每个run分别处理
        for run in paragraph.runs:
            text_type = self.detect_text_type(run.text)
            self.apply_font_style(run, style_name, text_type)
    
    def get_font_size_pt(self, size_name: str) -> float:
        """
        获取字号对应的磅值
        
        Args:
            size_name: 字号名称
            
        Returns:
            磅值
        """
        return self.SPECIAL_FONT_SIZES.get(size_name, 12)
    
    def validate_font_settings(self, document: Document) -> Dict[str, list]:
        """
        验证文档字体设置
        
        Args:
            document: Word文档对象
            
        Returns:
            包含错误和警告的字典
        """
        errors = []
        warnings = []
        
        # 检查摘要标题
        for i, para in enumerate(document.paragraphs):
            text = para.text.strip()
            
            # 检查中文摘要标题
            if text == '摘要' and para.runs:
                run = para.runs[0]
                if run.font.name != '黑体':
                    errors.append(f"第{i+1}段：中文摘要标题应使用黑体，当前为{run.font.name}")
            
            # 检查英文摘要标题
            elif text == 'Abstract' and para.runs:
                run = para.runs[0]
                if run.font.name != 'Arial Black':
                    errors.append(f"第{i+1}段：英文摘要标题应使用Arial Black，当前为{run.font.name}")
        
        return {'errors': errors, 'warnings': warnings}
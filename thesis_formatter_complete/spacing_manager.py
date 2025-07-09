#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行间距管理器模块
提供精确的行间距控制，支持不同文档区域的差异化设置
"""

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_LINE_SPACING
import logging
from typing import Dict, List, Optional

class SpacingManager:
    """行间距管理器：统一管理所有行间距设置"""
    
    # 行间距配置表
    SPACING_RULES = {
        'cover_info': {
            'line_spacing': 28,  # 封面学生信息
            'space_before': 0,
            'space_after': 0,
            'spacing_rule': WD_LINE_SPACING.EXACTLY
        },
        'main_text': {
            'line_spacing': 22,  # 正文
            'space_before': 0,
            'space_after': 0,
            'spacing_rule': WD_LINE_SPACING.EXACTLY
        },
        'footnote': {
            'line_spacing': 12,  # 脚注
            'space_before': 0,
            'space_after': 0,
            'spacing_rule': WD_LINE_SPACING.EXACTLY
        },
        'reference': {
            'line_spacing': 18,  # 参考文献
            'space_before': 0,
            'space_after': 0,
            'spacing_rule': WD_LINE_SPACING.EXACTLY
        },
        'abstract': {
            'line_spacing': 22,  # 摘要内容
            'space_before': 0,
            'space_after': 0,
            'spacing_rule': WD_LINE_SPACING.EXACTLY
        },
        'toc': {
            'line_spacing': 20,  # 目录
            'space_before': 0,
            'space_after': 0,
            'spacing_rule': WD_LINE_SPACING.EXACTLY
        },
        'heading_1': {
            'line_spacing': 22,
            'space_before': 12,  # 标题前空12磅
            'space_after': 6,    # 标题后空6磅
            'spacing_rule': WD_LINE_SPACING.EXACTLY
        },
        'heading_2': {
            'line_spacing': 22,
            'space_before': 6,
            'space_after': 6,
            'spacing_rule': WD_LINE_SPACING.EXACTLY
        },
        'heading_3': {
            'line_spacing': 22,
            'space_before': 6,
            'space_after': 3,
            'spacing_rule': WD_LINE_SPACING.EXACTLY
        },
        'figure_caption': {
            'line_spacing': 18,
            'space_before': 6,   # 图题上方6磅
            'space_after': 6,    # 图题下方6磅
            'spacing_rule': WD_LINE_SPACING.EXACTLY
        },
        'table_caption': {
            'line_spacing': 18,
            'space_before': 6,
            'space_after': 3,
            'spacing_rule': WD_LINE_SPACING.EXACTLY
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def apply_spacing(self, paragraph, spacing_type: str) -> None:
        """
        应用行间距设置到段落
        
        Args:
            paragraph: docx paragraph对象
            spacing_type: 间距类型（从SPACING_RULES中选择）
        """
        if spacing_type not in self.SPACING_RULES:
            self.logger.warning(f"未知的间距类型: {spacing_type}")
            return
        
        rule = self.SPACING_RULES[spacing_type]
        pf = paragraph.paragraph_format
        
        # 设置行间距
        pf.line_spacing_rule = rule['spacing_rule']
        pf.line_spacing = Pt(rule['line_spacing'])
        
        # 设置段前段后间距
        pf.space_before = Pt(rule['space_before'])
        pf.space_after = Pt(rule['space_after'])
    
    def detect_paragraph_type(self, paragraph, structure: Dict) -> str:
        """
        检测段落类型以确定应用哪种间距规则
        
        Args:
            paragraph: 段落对象
            structure: 文档结构信息
            
        Returns:
            间距类型名称
        """
        text = paragraph.text.strip()
        para_idx = self._get_paragraph_index(paragraph)
        
        # 检查是否在封面区域
        if para_idx < structure.get('abstract_cn', 999):
            if any(keyword in text for keyword in ['专业', '班级', '学号', '姓名', '指导教师']):
                return 'cover_info'
        
        # 检查是否是标题
        if self._is_heading(paragraph):
            level = self._get_heading_level(text)
            if level == 1:
                return 'heading_1'
            elif level == 2:
                return 'heading_2'
            elif level == 3:
                return 'heading_3'
        
        # 检查是否在参考文献区域
        ref_start = structure.get('references', -1)
        if ref_start > 0 and para_idx > ref_start:
            return 'reference'
        
        # 检查是否是图表标题
        if text.startswith('图') and '.' in text[:5]:
            return 'figure_caption'
        elif text.startswith('表') and '.' in text[:5]:
            return 'table_caption'
        
        # 检查是否在摘要区域
        abstract_cn = structure.get('abstract_cn', -1)
        abstract_en = structure.get('abstract_en', -1)
        if abstract_cn > 0 and abstract_en > 0:
            if abstract_cn < para_idx < abstract_en + 10:
                return 'abstract'
        
        # 默认为正文
        return 'main_text'
    
    def _get_paragraph_index(self, paragraph) -> int:
        """获取段落在文档中的索引"""
        doc = paragraph._element.getparent().getparent().getparent()
        paragraphs = doc.xpath('.//w:p', namespaces=doc.nsmap)
        for i, p in enumerate(paragraphs):
            if p == paragraph._element:
                return i
        return -1
    
    def _is_heading(self, paragraph) -> bool:
        """判断是否为标题"""
        if paragraph.runs and paragraph.runs[0].font.bold:
            text = paragraph.text.strip()
            # 检查标题模式
            import re
            if re.match(r'^第[一二三四五六七八九十\d]+[章节]', text):
                return True
            if re.match(r'^\d+\.\d*\s+', text):
                return True
        return False
    
    def _get_heading_level(self, text: str) -> int:
        """获取标题级别"""
        import re
        if re.match(r'^第[一二三四五六七八九十\d]+[章节]', text):
            return 1
        elif re.match(r'^\d+\.\d+\s+', text):
            return 2
        elif re.match(r'^\d+\.\d+\.\d+\s+', text):
            return 3
        return 0
    
    def process_document_spacing(self, document: Document, structure: Dict) -> None:
        """
        处理整个文档的行间距
        
        Args:
            document: Word文档对象
            structure: 文档结构信息
        """
        for paragraph in document.paragraphs:
            # 跳过空段落
            if not paragraph.text.strip():
                continue
            
            # 检测段落类型
            para_type = self.detect_paragraph_type(paragraph, structure)
            
            # 应用相应的间距设置
            self.apply_spacing(paragraph, para_type)
            
            self.logger.debug(f"段落类型: {para_type}, 内容: {paragraph.text[:20]}...")
    
    def validate_spacing(self, document: Document) -> Dict[str, List[str]]:
        """
        验证文档行间距设置
        
        Args:
            document: Word文档对象
            
        Returns:
            包含错误和警告的字典
        """
        errors = []
        warnings = []
        
        for i, para in enumerate(document.paragraphs):
            pf = para.paragraph_format
            
            # 检查行间距是否为固定值
            if pf.line_spacing_rule != WD_LINE_SPACING.EXACTLY:
                warnings.append(f"第{i+1}段：行间距不是固定值")
            
            # 检查特殊区域的行间距
            text = para.text.strip()
            if '参考文献' in text and pf.line_spacing != Pt(18):
                errors.append(f"第{i+1}段：参考文献区域行间距应为18磅")
            
        return {'errors': errors, 'warnings': warnings}
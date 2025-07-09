# 毕业论文格式化工具 - 完整版

## 📋 功能概述

本工具专为江西财经大学现代经济管理学院毕业论文格式化设计，实现一键式自动格式化，确保论文格式完全符合学院要求。

### ✅ 已实现功能

1. **封面生成** - 自动生成标准格式封面
2. **诚信承诺书** - 生成诚信承诺书页面
3. **页码系统** - 前置部分罗马数字，正文阿拉伯数字
4. **关键词格式** - [关键词]黑体方括号格式
5. **图表编号** - 按章节编号（图1.1、表1.1）
6. **脚注格式** - 小五号宋体，每页重新编号
7. **数学公式** - 居中显示，编号右对齐
8. **目录生成** - 自动生成和更新目录
9. **致谢格式** - 标准致谢格式处理

## 🚀 快速开始

### 安装依赖

```bash
pip install python-docx
```

### 使用方法

#### 方法1：命令行使用

```python
from thesis_formatter_complete import CompleteThesisFormatter

# 创建格式化器
formatter = CompleteThesisFormatter("我的论文.docx")

# 设置论文信息
thesis_info = {
    'title': '基于深度学习的图像识别研究',
    'major': '计算机科学与技术',
    'class': '计科1901',
    'student_id': '20190001',
    'name': '张三',
    'advisor': '李教授',
    'date': '2024年5月'
}

# 执行格式化
formatter.format_document(thesis_info)
```

#### 方法2：GUI界面使用

```bash
python thesis_formatter_complete/main_formatter.py
```

## 📁 项目结构

```
thesis_formatter_complete/
├── __init__.py              # 包初始化文件
├── main_formatter.py        # 主格式化器（含GUI）
├── cover_generator.py       # 封面和承诺书生成
├── page_number_handler.py   # 页码处理
├── keyword_formatter.py     # 关键词格式化
├── figure_table_handler.py  # 图表编号处理
├── footnote_formatter.py    # 脚注格式化
├── math_formatter.py        # 数学公式格式化
├── toc_generator.py         # 目录生成
├── acknowledgment_formatter.py  # 致谢格式化
└── README.md               # 本文档
```

## 🔧 配置选项

```python
config = {
    'generate_cover': True,          # 生成封面
    'generate_commitment': True,     # 生成诚信承诺书
    'format_keywords': True,         # 格式化关键词
    'format_figures_tables': True,   # 格式化图表编号
    'format_footnotes': True,        # 格式化脚注
    'format_math': True,             # 格式化数学公式
    'update_toc': True,              # 更新目录
    'format_acknowledgment': True,   # 格式化致谢
    'setup_page_numbers': True,      # 设置页码
    'reorder_document': True         # 重组文档结构
}
```

## 📝 格式规范

### 1. 标题格式
- 一级标题：二号宋体加粗
- 二级标题：三号宋体加粗
- 三级标题：四号宋体加粗

### 2. 正文格式
- 字体：宋体小四号
- 行距：22磅
- 段前段后：0磅
- 首行缩进：2字符

### 3. 页码格式
- 封面到目录：罗马数字（I, II, III...）
- 正文开始：阿拉伯数字（1, 2, 3...）
- 位置：页面底端居中

### 4. 特殊格式
- 摘要：楷体小四号
- 关键词：[关键词]黑体 + 楷体内容
- 参考文献：宋体五号，行距18磅
- 图表标题：宋体小四号，居中

## 🧪 测试

运行测试脚本：

```bash
python test_complete_formatter.py
```

## ⚠️ 注意事项

1. **备份原文档** - 格式化前请备份原始文档
2. **检查结果** - 格式化后请仔细检查文档
3. **手动调整** - 某些特殊情况可能需要手动微调
4. **兼容性** - 建议使用 Microsoft Word 2016 及以上版本

## 📞 技术支持

如遇到问题，请检查：
1. Python 版本是否为 3.6+
2. python-docx 是否正确安装
3. 原始文档是否为 .docx 格式
4. 文档是否包含特殊元素（如嵌入对象）

## 🔄 更新日志

### v1.0.0 (2024-01-13)
- 实现所有核心格式化功能
- 添加GUI界面
- 支持并行处理
- 完整的错误处理

## 📄 许可证

本项目仅供学习和个人使用。
# 毕业论文格式化工具 - 快速开始指南

## 🚀 5分钟快速上手

### 1. 安装依赖

```bash
pip install python-docx
```

### 2. 最简单的使用方式 - GUI界面

```bash
cd thesis_formatter_complete
python gui_enhanced.py
```

然后：
1. 点击"浏览"选择你的Word文档
2. 切换到"论文信息"标签，填写你的信息
3. 点击"开始格式化"

### 3. 命令行快速使用

```python
from thesis_formatter_complete.main_formatter import CompleteThesisFormatter

# 最简单的使用
formatter = CompleteThesisFormatter('my_thesis.docx')
formatter.format_document()  # 自动保存为 my_thesis_formatted_时间戳.docx
```

### 4. 自定义论文信息

```python
formatter = CompleteThesisFormatter()

thesis_info = {
    'title': '基于深度学习的图像识别研究',
    'major': '计算机科学与技术',
    'class': '计科1901',
    'student_id': '20190001',
    'name': '张三',
    'advisor': '李教授',
    'date': '2024年6月'
}

formatter.format_document(
    input_file='thesis.docx',
    output_file='thesis_final.docx',
    thesis_info=thesis_info
)
```

### 5. 选择性格式化

如果只想使用部分功能：

```python
formatter = CompleteThesisFormatter()

# 设置格式化选项
formatter.format_options = {
    'cover': True,        # 生成封面
    'commitment': True,   # 生成承诺书
    'page_number': True,  # 设置页码
    'keywords': True,     # 格式化关键词
    'figures_tables': False,  # 不处理图表编号
    'toc': True,         # 生成目录
    'reorganize': False  # 不重组文档结构
}

formatter.format_document('thesis.docx')
```

### 6. 单独使用某个功能

```python
from thesis_formatter_complete.keyword_formatter import KeywordFormatter
from docx import Document

# 只格式化关键词
doc = Document('thesis.docx')
formatter = KeywordFormatter()
structure = {'abstract_cn': 5}  # 中文摘要在第5段
formatter.format_keywords(doc, structure)
doc.save('thesis_keywords_formatted.docx')
```

## 📋 常见问题

### Q: 文档格式被打乱了怎么办？
A: 确保使用前备份原文档。如果格式异常，可以关闭`reorganize`选项。

### Q: 如何跳过封面生成？
A: 在format_options中设置`'cover': False`

### Q: 支持哪些Word版本？
A: 支持Word 2007及以上版本的.docx格式

### Q: 处理大文档很慢？
A: 正常情况下50页文档需要10秒左右。如果更慢，检查是否有大量图片。

## 💡 专业提示

1. **备份原文档** - 始终在格式化前备份
2. **检查结构** - 确保文档有清晰的章节标题
3. **使用模板** - 基于已有的规范文档效果更好
4. **逐步调试** - 如果效果不理想，可以单独运行各模块

## 🆘 需要帮助？

- 查看完整文档：`README.md`
- 查看实现细节：`SUMMARY.md`
- 查看最终报告：`FINAL_REPORT.md`

---

祝你论文格式化顺利！🎓
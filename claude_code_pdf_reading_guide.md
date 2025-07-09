# Claude Code 读取 PDF 文件完整指南

## 研究总结

经过深入测试和研究，以下是Claude Code处理PDF文件的所有可行方法及其优缺点。

## 1. Read工具直接读取（不支持）

**测试结果**：❌ 不支持

尽管Claude Code的Read工具说明中提到它是多模态的，可以读取图像文件，但实测发现：
- Read工具**无法直接读取PDF文件**
- 尝试读取PDF时会报错："This tool cannot read binary files"
- PDF被识别为二进制文件而非可视化内容

## 2. 命令行工具

### 2.1 可用工具检查

**macOS内置工具**：
- `strings` - 可以提取PDF中的可读字符串，但格式混乱
- `mdls` - 可以读取PDF元数据，但无法提取文本内容
- `textutil` - 不支持PDF格式

**需要安装的工具**：
- `pdftotext` (poppler-utils) - 最专业的PDF文本提取工具
- `ps2ascii` (ghostscript) - 可以处理PostScript格式的PDF
- `pandoc` - 可以从PDF转换为其他格式，但需要LaTeX支持

### 2.2 安装建议

```bash
# macOS 使用 Homebrew
brew install poppler  # 包含 pdftotext
brew install ghostscript  # 包含 ps2ascii
```

## 3. Python库（推荐方法）

### 3.1 已安装的库测试结果

| 库名 | 成功率 | 优点 | 缺点 |
|------|--------|------|------|
| **PyMuPDF (fitz)** | ✅ 100% | 速度快，功能强大，支持中文 | 文件较大 |
| **pypdf** | ✅ 100% | PyPDF2的继任者，更稳定 | 某些PDF格式支持不完善 |
| **PyPDF2** | ✅ 100% | 使用广泛，文档丰富 | 已不再维护，建议用pypdf |
| **pdfminer.six** | ✅ 100% | 文本提取准确 | 速度较慢，API复杂 |
| **pdf2zh** | ❌ 失败 | 专门处理中文PDF | 依赖问题，主要用于翻译 |

### 3.2 推荐使用顺序

1. **PyMuPDF (fitz)** - 首选，最可靠
2. **pypdf** - 备选方案
3. **pdfminer.six** - 当需要更精确的文本提取时

## 4. MCP工具支持

**测试结果**：❌ 目前没有专门的MCP工具支持PDF处理

- Exa工具可以爬取网页，但不能处理本地PDF文件
- WebFetch工具只能处理在线内容

## 5. 最佳实践和代码示例

### 5.1 简单读取PDF（使用PyMuPDF）

```python
import fitz  # PyMuPDF

def read_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

# 使用示例
content = read_pdf("document.pdf")
print(content)
```

### 5.2 综合PDF读取工具（自动选择最佳方法）

参见 `pdf_reader_tool.py` - 这是一个完整的工具，支持：
- 自动检测可用的库
- 按优先级尝试不同方法
- 命令行界面
- 错误处理

使用方法：
```bash
python3 pdf_reader_tool.py <pdf_file> [method]
# method可选: auto, pymupdf, pypdf, pdfminer, command
```

### 5.3 在Claude Code中的推荐工作流程

1. **检查Python库**：
   ```bash
   pip3 list | grep -i pdf
   ```

2. **如果没有安装，安装PyMuPDF**：
   ```bash
   pip3 install PyMuPDF
   ```

3. **使用Python脚本读取PDF**：
   ```python
   import fitz
   doc = fitz.open("your_file.pdf")
   for page in doc:
       print(page.get_text())
   ```

## 6. 性能和准确性比较

| 方法 | 速度 | 准确性 | 中文支持 | 格式保持 |
|------|------|--------|----------|----------|
| PyMuPDF | 快 | 高 | 优秀 | 好 |
| pypdf | 中 | 中 | 良好 | 一般 |
| pdfminer | 慢 | 高 | 良好 | 优秀 |
| strings命令 | 快 | 低 | 差 | 无 |

## 7. 常见问题和解决方案

### Q1: Read工具为什么不能读取PDF？
A: Read工具只支持文本文件和图像文件，PDF被视为二进制文件。

### Q2: 哪种方法最适合提取表格数据？
A: 使用专门的库如`tabula-py`或`camelot`，它们基于Java和需要额外配置。

### Q3: 如何处理扫描版PDF（图片PDF）？
A: 需要OCR功能，可以使用：
- `pytesseract` + `pdf2image`
- `ocrmypdf`命令行工具

### Q4: 如何处理加密的PDF？
A: PyMuPDF和pypdf都支持处理加密PDF，需要提供密码：
```python
doc = fitz.open("encrypted.pdf")
doc.authenticate("password")
```

## 8. 总结

**最佳实践建议**：

1. **首选方案**：使用Python的PyMuPDF库
   - 安装简单：`pip3 install PyMuPDF`
   - 功能强大，速度快
   - 支持中文和各种PDF格式

2. **备选方案**：使用pypdf或pdfminer.six

3. **紧急方案**：使用strings命令提取可读文本

4. **不推荐**：
   - 不要期望Read工具能直接读取PDF
   - 避免使用过时的PyPDF2（使用pypdf代替）

记住：在Claude Code中处理PDF，Python库是最可靠和方便的选择！
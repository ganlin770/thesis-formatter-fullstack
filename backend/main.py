#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI后端服务 - 毕业论文格式化工具
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import sys
import os
import json
import tempfile
from datetime import datetime
from pathlib import Path

# 添加thesis_formatter_complete模块路径
sys.path.append(str(Path(__file__).parent.parent / "thesis_formatter_complete"))

try:
    from main_formatter import CompleteThesisFormatter
except ImportError as e:
    print(f"无法导入格式化模块: {e}")

app = FastAPI(
    title="毕业论文格式化API",
    description="江西财经大学现代经济管理学院毕业论文格式化工具API",
    version="2.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "毕业论文格式化API服务", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/format")
async def format_document(
    file: UploadFile = File(...),
    thesis_info: str = Form(...),
    format_options: str = Form(...)
):
    """
    格式化论文文档
    """
    try:
        # 验证文件类型
        if not file.filename.endswith('.docx'):
            raise HTTPException(status_code=400, detail="只支持.docx格式文件")
        
        # 解析JSON参数
        try:
            thesis_data = json.loads(thesis_info)
            options_data = json.loads(format_options)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="JSON参数格式错误")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_input:
            content = await file.read()
            temp_input.write(content)
            temp_input_path = temp_input.name
        
        # 生成输出文件路径
        output_filename = f"{thesis_data.get('title', 'formatted_thesis')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        temp_output_path = os.path.join(tempfile.gettempdir(), output_filename)
        
        # 执行格式化
        formatter = CompleteThesisFormatter(temp_input_path)
        
        # 设置格式化选项
        formatter.config.update({
            'generate_cover': options_data.get('cover', True),
            'generate_commitment': options_data.get('commitment', True),
            'format_keywords': options_data.get('keywords', True),
            'format_figures_tables': options_data.get('figures_tables', True),
            'format_footnotes': options_data.get('footnotes', True),
            'format_math': options_data.get('math', True),
            'update_toc': options_data.get('toc', True),
            'format_acknowledgment': options_data.get('acknowledgment', True),
            'format_appendix': options_data.get('appendix', True),
            'setup_page_numbers': options_data.get('page_number', True),
            'reorder_document': options_data.get('reorganize', True),
            'basic_formatting': options_data.get('basic', True)
        })
        
        # 执行格式化
        success = formatter.format_document(
            input_file=temp_input_path,
            output_file=temp_output_path,
            thesis_info=thesis_data
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="格式化处理失败")
        
        # 清理临时输入文件
        os.unlink(temp_input_path)
        
        # 返回格式化后的文件
        return FileResponse(
            path=temp_output_path,
            filename=output_filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.post("/api/validate")
async def validate_document(file: UploadFile = File(...)):
    """
    验证文档格式
    """
    try:
        if not file.filename.endswith('.docx'):
            raise HTTPException(status_code=400, detail="只支持.docx格式文件")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # 执行验证
        formatter = CompleteThesisFormatter(temp_file_path)
        report = formatter.get_format_report()
        
        # 清理临时文件
        os.unlink(temp_file_path)
        
        return {"validation_report": report}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
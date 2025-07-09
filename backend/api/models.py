"""
API数据模型定义
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """任务类型枚举"""
    SINGLE_FORMAT = "single_format"
    BATCH_FORMAT = "batch_format"


class ThesisInfo(BaseModel):
    """论文信息模型"""
    title: str = Field(..., description="论文题目", max_length=200)
    major: str = Field(..., description="专业", max_length=100)
    class_name: str = Field(..., description="班级", max_length=50, alias="class")
    student_id: str = Field(..., description="学号", max_length=20)
    name: str = Field(..., description="学生姓名", max_length=50)
    advisor: str = Field(..., description="指导教师", max_length=50)
    date: str = Field(..., description="日期", max_length=20)
    
    @validator('date')
    def validate_date(cls, v):
        """验证日期格式"""
        if not v:
            return datetime.now().strftime('%Y年%m月')
        return v
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "title": "基于深度学习的图像识别研究",
                "major": "计算机科学与技术",
                "class": "计科1901",
                "student_id": "20190001",
                "name": "张三",
                "advisor": "李教授",
                "date": "2024年6月"
            }
        }


class FormatOptions(BaseModel):
    """格式化选项模型"""
    generate_cover: bool = Field(True, description="生成封面")
    generate_commitment: bool = Field(True, description="生成承诺书")
    format_keywords: bool = Field(True, description="格式化关键词")
    format_figures_tables: bool = Field(True, description="格式化图表")
    format_footnotes: bool = Field(True, description="格式化脚注")
    format_math: bool = Field(True, description="格式化数学公式")
    update_toc: bool = Field(True, description="更新目录")
    format_acknowledgment: bool = Field(True, description="格式化致谢")
    format_appendix: bool = Field(True, description="格式化附录")
    setup_page_numbers: bool = Field(True, description="设置页码")
    reorder_document: bool = Field(True, description="重新排序文档")
    basic_formatting: bool = Field(True, description="基础格式化")
    
    class Config:
        schema_extra = {
            "example": {
                "generate_cover": True,
                "generate_commitment": True,
                "format_keywords": True,
                "format_figures_tables": True,
                "format_footnotes": True,
                "format_math": True,
                "update_toc": True,
                "format_acknowledgment": True,
                "format_appendix": True,
                "setup_page_numbers": True,
                "reorder_document": True,
                "basic_formatting": True
            }
        }


class FormatRequest(BaseModel):
    """格式化请求模型"""
    thesis_info: ThesisInfo = Field(..., description="论文信息")
    format_options: FormatOptions = Field(FormatOptions(), description="格式化选项")
    
    class Config:
        schema_extra = {
            "example": {
                "thesis_info": {
                    "title": "基于深度学习的图像识别研究",
                    "major": "计算机科学与技术",
                    "class": "计科1901",
                    "student_id": "20190001",
                    "name": "张三",
                    "advisor": "李教授",
                    "date": "2024年6月"
                },
                "format_options": {
                    "generate_cover": True,
                    "format_keywords": True,
                    "update_toc": True
                }
            }
        }


class BatchFormatRequest(BaseModel):
    """批量格式化请求模型"""
    thesis_infos: List[ThesisInfo] = Field(..., description="论文信息列表")
    format_options: FormatOptions = Field(FormatOptions(), description="格式化选项")
    
    @validator('thesis_infos')
    def validate_thesis_infos(cls, v):
        if len(v) == 0:
            raise ValueError("至少需要一个论文信息")
        if len(v) > 10:  # 限制批量处理数量
            raise ValueError("批量处理最多支持10个文件")
        return v


class ProgressUpdate(BaseModel):
    """进度更新模型"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    progress: int = Field(..., description="进度百分比", ge=0, le=100)
    message: str = Field(..., description="进度消息")
    current_step: Optional[str] = Field(None, description="当前步骤")
    total_steps: Optional[int] = Field(None, description="总步骤数")
    completed_steps: Optional[int] = Field(None, description="已完成步骤数")
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "task_123456",
                "status": "processing",
                "progress": 45,
                "message": "正在格式化图表...",
                "current_step": "format_figures_tables",
                "total_steps": 12,
                "completed_steps": 5
            }
        }


class TaskInfo(BaseModel):
    """任务信息模型"""
    task_id: str = Field(..., description="任务ID")
    task_type: TaskType = Field(..., description="任务类型")
    status: TaskStatus = Field(..., description="任务状态")
    progress: int = Field(0, description="进度百分比", ge=0, le=100)
    message: str = Field("", description="状态消息")
    created_at: datetime = Field(..., description="创建时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    file_count: int = Field(1, description="文件数量")
    processed_files: int = Field(0, description="已处理文件数")
    error_message: Optional[str] = Field(None, description="错误消息")
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "task_123456",
                "task_type": "single_format",
                "status": "processing",
                "progress": 45,
                "message": "正在格式化图表...",
                "created_at": "2024-01-01T10:00:00Z",
                "started_at": "2024-01-01T10:00:01Z",
                "completed_at": None,
                "file_count": 1,
                "processed_files": 0,
                "error_message": None
            }
        }


class FormatResponse(BaseModel):
    """格式化响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    message: str = Field(..., description="响应消息")
    download_url: Optional[str] = Field(None, description="下载链接")
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "task_123456",
                "status": "pending",
                "message": "任务已创建，正在排队处理",
                "download_url": None
            }
        }


class BatchFormatResponse(BaseModel):
    """批量格式化响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    message: str = Field(..., description="响应消息")
    total_files: int = Field(..., description="总文件数")
    processed_files: int = Field(0, description="已处理文件数")
    download_urls: List[str] = Field([], description="下载链接列表")
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "batch_task_123456",
                "status": "pending",
                "message": "批量任务已创建，正在排队处理",
                "total_files": 3,
                "processed_files": 0,
                "download_urls": []
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(..., description="检查时间")
    version: str = Field(..., description="版本信息")
    uptime: float = Field(..., description="运行时间(秒)")
    active_tasks: int = Field(..., description="活跃任务数")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T10:00:00Z",
                "version": "1.0.0",
                "uptime": 3600.0,
                "active_tasks": 2
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "FILE_VALIDATION_ERROR",
                "message": "不支持的文件格式",
                "details": {
                    "allowed_formats": ["docx", "doc"],
                    "received_format": "pdf"
                }
            }
        }


class FileInfo(BaseModel):
    """文件信息模型"""
    filename: str = Field(..., description="文件名")
    size: int = Field(..., description="文件大小(字节)")
    content_type: str = Field(..., description="文件类型")
    upload_time: datetime = Field(..., description="上传时间")
    
    class Config:
        schema_extra = {
            "example": {
                "filename": "thesis.docx",
                "size": 1024000,
                "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "upload_time": "2024-01-01T10:00:00Z"
            }
        }
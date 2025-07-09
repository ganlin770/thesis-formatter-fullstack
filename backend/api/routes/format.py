"""
格式化API路由
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
import json
from pathlib import Path

from ..models import (
    FormatRequest, FormatResponse, BatchFormatRequest, BatchFormatResponse,
    TaskInfo, ThesisInfo, FormatOptions, TaskStatus
)
from ...services.formatter_service import get_formatter_service, FormatterService
from ...services.file_service import get_file_service, FileService
from ...utils.logger import get_logger
from ...utils.exceptions import HTTPExceptionHandler

router = APIRouter(prefix="/api/format", tags=["格式化"])
logger = get_logger("format_routes")


@router.post("/", response_model=FormatResponse, summary="单文件格式化")
async def format_document(
    file: UploadFile = File(..., description="要格式化的Word文档"),
    thesis_info: str = Form(..., description="论文信息JSON字符串"),
    format_options: Optional[str] = Form(None, description="格式化选项JSON字符串"),
    formatter_service: FormatterService = Depends(get_formatter_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    格式化单个Word文档
    
    - **file**: 上传的Word文档文件(.docx或.doc)
    - **thesis_info**: 论文信息，包含标题、作者、专业等
    - **format_options**: 格式化选项，可选
    
    返回任务ID，可用于查询格式化状态和下载结果
    """
    try:
        # 解析论文信息
        try:
            thesis_data = json.loads(thesis_info)
            thesis_info_obj = ThesisInfo(**thesis_data)
        except json.JSONDecodeError:
            raise HTTPExceptionHandler.file_validation_error("论文信息JSON格式错误")
        except Exception as e:
            raise HTTPExceptionHandler.file_validation_error(f"论文信息格式错误: {str(e)}")
        
        # 解析格式化选项
        format_options_obj = FormatOptions()
        if format_options:
            try:
                options_data = json.loads(format_options)
                format_options_obj = FormatOptions(**options_data)
            except json.JSONDecodeError:
                raise HTTPExceptionHandler.file_validation_error("格式化选项JSON格式错误")
            except Exception as e:
                raise HTTPExceptionHandler.file_validation_error(f"格式化选项格式错误: {str(e)}")
        
        # 保存上传的文件
        file_path = await file_service.save_uploaded_file(file)
        
        # 创建格式化任务
        task_id = await formatter_service.format_document(
            file_path, thesis_info_obj, format_options_obj
        )
        
        logger.info(f"Created format task {task_id} for file {file.filename}")
        
        return FormatResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="格式化任务已创建，正在排队处理"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to create format task: {e}")
        raise HTTPExceptionHandler.internal_server_error(f"创建格式化任务失败: {str(e)}")


@router.post("/batch", response_model=BatchFormatResponse, summary="批量格式化")
async def format_documents_batch(
    files: List[UploadFile] = File(..., description="要格式化的Word文档列表"),
    thesis_infos: str = Form(..., description="论文信息列表JSON字符串"),
    format_options: Optional[str] = Form(None, description="格式化选项JSON字符串"),
    formatter_service: FormatterService = Depends(get_formatter_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    批量格式化多个Word文档
    
    - **files**: 上传的Word文档文件列表
    - **thesis_infos**: 论文信息列表，每个文件对应一个论文信息
    - **format_options**: 格式化选项，应用于所有文件
    
    返回批量任务ID，可用于查询格式化状态和下载结果
    """
    try:
        # 验证文件数量
        if len(files) == 0:
            raise HTTPExceptionHandler.file_validation_error("没有上传文件")
        if len(files) > 10:
            raise HTTPExceptionHandler.file_validation_error("批量处理最多支持10个文件")
        
        # 解析论文信息列表
        try:
            thesis_data_list = json.loads(thesis_infos)
            if not isinstance(thesis_data_list, list):
                raise ValueError("论文信息必须是数组格式")
            if len(thesis_data_list) != len(files):
                raise ValueError(f"论文信息数量({len(thesis_data_list)})与文件数量({len(files)})不匹配")
            
            thesis_info_objs = [ThesisInfo(**data) for data in thesis_data_list]
        except json.JSONDecodeError:
            raise HTTPExceptionHandler.file_validation_error("论文信息JSON格式错误")
        except Exception as e:
            raise HTTPExceptionHandler.file_validation_error(f"论文信息格式错误: {str(e)}")
        
        # 解析格式化选项
        format_options_obj = FormatOptions()
        if format_options:
            try:
                options_data = json.loads(format_options)
                format_options_obj = FormatOptions(**options_data)
            except json.JSONDecodeError:
                raise HTTPExceptionHandler.file_validation_error("格式化选项JSON格式错误")
            except Exception as e:
                raise HTTPExceptionHandler.file_validation_error(f"格式化选项格式错误: {str(e)}")
        
        # 保存上传的文件
        file_paths = await file_service.save_uploaded_files(files)
        
        # 创建批量格式化任务
        task_id = await formatter_service.format_documents_batch(
            file_paths, thesis_info_objs, format_options_obj
        )
        
        logger.info(f"Created batch format task {task_id} for {len(files)} files")
        
        return BatchFormatResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="批量格式化任务已创建，正在排队处理",
            total_files=len(files)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to create batch format task: {e}")
        raise HTTPExceptionHandler.internal_server_error(f"创建批量格式化任务失败: {str(e)}")


@router.get("/status/{task_id}", response_model=TaskInfo, summary="查询任务状态")
async def get_task_status(
    task_id: str,
    formatter_service: FormatterService = Depends(get_formatter_service)
):
    """
    查询格式化任务状态
    
    - **task_id**: 任务ID
    
    返回任务的详细状态信息，包括进度、状态、错误信息等
    """
    try:
        task_info = await formatter_service.get_task_status(task_id)
        return task_info
        
    except Exception as e:
        logger.error(f"Failed to get task status for {task_id}: {e}")
        raise HTTPExceptionHandler.task_not_found_error(task_id)


@router.get("/download/{task_id}", summary="下载格式化结果")
async def download_formatted_document(
    task_id: str,
    file_index: int = 0,
    formatter_service: FormatterService = Depends(get_formatter_service)
):
    """
    下载格式化后的文档
    
    - **task_id**: 任务ID
    - **file_index**: 文件索引，批量任务时指定下载第几个文件（从0开始）
    
    返回格式化后的Word文档文件
    """
    try:
        # 检查任务状态
        task_info = await formatter_service.get_task_status(task_id)
        if task_info.status != TaskStatus.COMPLETED:
            raise HTTPExceptionHandler.file_processing_error(
                f"任务状态为 {task_info.status.value}，无法下载"
            )
        
        # 获取输出文件路径
        try:
            output_file_path = formatter_service.get_output_file_path(task_id, file_index)
        except FileNotFoundError:
            raise HTTPExceptionHandler.file_processing_error("输出文件不存在")
        
        # 检查文件是否存在
        if not output_file_path.exists():
            raise HTTPExceptionHandler.file_processing_error("输出文件不存在")
        
        # 返回文件
        return FileResponse(
            path=str(output_file_path),
            filename=f"formatted_{task_id}_{file_index}.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to download file for task {task_id}: {e}")
        raise HTTPExceptionHandler.internal_server_error(f"下载文件失败: {str(e)}")


@router.get("/download/{task_id}/all", summary="下载所有格式化结果")
async def download_all_formatted_documents(
    task_id: str,
    formatter_service: FormatterService = Depends(get_formatter_service)
):
    """
    下载任务的所有格式化结果（批量任务）
    
    - **task_id**: 任务ID
    
    返回包含所有格式化文档的ZIP文件
    """
    try:
        # 检查任务状态
        task_info = await formatter_service.get_task_status(task_id)
        if task_info.status != TaskStatus.COMPLETED:
            raise HTTPExceptionHandler.file_processing_error(
                f"任务状态为 {task_info.status.value}，无法下载"
            )
        
        # 获取所有输出文件
        output_files = formatter_service.get_all_output_files(task_id)
        if not output_files:
            raise HTTPExceptionHandler.file_processing_error("没有找到输出文件")
        
        # 如果只有一个文件，直接返回
        if len(output_files) == 1:
            return FileResponse(
                path=str(output_files[0]),
                filename=f"formatted_{task_id}.docx",
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        
        # 多个文件时，创建ZIP包
        import zipfile
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            with zipfile.ZipFile(tmp_file, 'w') as zip_file:
                for i, file_path in enumerate(output_files):
                    zip_file.write(file_path, f"formatted_{i+1}.docx")
            
            zip_path = tmp_file.name
        
        return FileResponse(
            path=zip_path,
            filename=f"formatted_batch_{task_id}.zip",
            media_type="application/zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to download all files for task {task_id}: {e}")
        raise HTTPExceptionHandler.internal_server_error(f"下载文件失败: {str(e)}")


@router.delete("/{task_id}", summary="取消任务")
async def cancel_task(
    task_id: str,
    formatter_service: FormatterService = Depends(get_formatter_service)
):
    """
    取消格式化任务
    
    - **task_id**: 任务ID
    
    取消正在进行或排队中的任务
    """
    try:
        await formatter_service.cancel_task(task_id)
        
        logger.info(f"Cancelled task {task_id}")
        
        return {"message": f"任务 {task_id} 已取消"}
        
    except Exception as e:
        logger.error(f"Failed to cancel task {task_id}: {e}")
        raise HTTPExceptionHandler.task_not_found_error(task_id)


@router.get("/", summary="获取所有任务状态")
async def get_all_tasks(
    formatter_service: FormatterService = Depends(get_formatter_service)
):
    """
    获取所有任务的状态信息
    
    返回系统中所有任务的状态列表
    """
    try:
        task_manager = formatter_service.task_manager
        
        # 获取所有任务
        all_tasks = []
        async with task_manager.task_lock:
            for task_id, task_info in task_manager.tasks.items():
                all_tasks.append(task_info)
        
        return {
            "total_tasks": len(all_tasks),
            "active_tasks": task_manager.get_active_tasks_count(),
            "tasks": all_tasks
        }
        
    except Exception as e:
        logger.exception(f"Failed to get all tasks: {e}")
        raise HTTPExceptionHandler.internal_server_error(f"获取任务列表失败: {str(e)}")


@router.post("/test", summary="测试格式化接口")
async def test_format():
    """
    测试格式化接口
    
    返回测试信息，用于验证服务是否正常工作
    """
    return {
        "message": "格式化服务正常运行",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }
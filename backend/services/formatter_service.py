"""
格式化服务模块
集成CompleteThesisFormatter，提供异步格式化功能
"""

import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor

from ..api.models import (
    TaskStatus, TaskType, TaskInfo, ThesisInfo, 
    FormatOptions, ProgressUpdate
)
from ..utils.logger import get_logger
from ..utils.exceptions import (
    FormattingError, TaskNotFoundError, TaskTimeoutError,
    FileProcessingError
)
from ..thesis_formatter_complete.main_formatter import CompleteThesisFormatter


logger = get_logger("formatter_service")


class TaskManager:
    """任务管理器"""
    
    def __init__(self, max_concurrent_tasks: int = 5):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.tasks: Dict[str, TaskInfo] = {}
        self.progress_callbacks: Dict[str, Callable] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        self.running_tasks = 0
        self.task_lock = asyncio.Lock()
    
    async def create_task(self, task_type: TaskType, file_count: int = 1) -> str:
        """创建新任务"""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        task_info = TaskInfo(
            task_id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            file_count=file_count
        )
        
        async with self.task_lock:
            self.tasks[task_id] = task_info
        
        logger.log_task_start(task_id, task_type.value)
        return task_id
    
    async def get_task(self, task_id: str) -> TaskInfo:
        """获取任务信息"""
        async with self.task_lock:
            if task_id not in self.tasks:
                raise TaskNotFoundError(f"Task {task_id} not found")
            return self.tasks[task_id]
    
    async def update_task_status(self, task_id: str, status: TaskStatus, 
                               message: str = "", progress: int = 0, 
                               error_message: str = None):
        """更新任务状态"""
        async with self.task_lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            task.status = status
            task.message = message
            task.progress = progress
            
            if error_message:
                task.error_message = error_message
            
            if status == TaskStatus.PROCESSING and not task.started_at:
                task.started_at = datetime.now()
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                task.completed_at = datetime.now()
                if status == TaskStatus.COMPLETED:
                    task.progress = 100
                    
                # 减少运行中的任务计数
                self.running_tasks = max(0, self.running_tasks - 1)
    
    async def cancel_task(self, task_id: str):
        """取消任务"""
        await self.update_task_status(task_id, TaskStatus.CANCELLED, "任务已取消")
    
    def register_progress_callback(self, task_id: str, callback: Callable):
        """注册进度回调"""
        self.progress_callbacks[task_id] = callback
    
    def get_active_tasks_count(self) -> int:
        """获取活跃任务数"""
        return self.running_tasks
    
    async def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        async with self.task_lock:
            to_remove = []
            for task_id, task in self.tasks.items():
                if task.created_at.timestamp() < cutoff_time:
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self.tasks[task_id]
                if task_id in self.progress_callbacks:
                    del self.progress_callbacks[task_id]
        
        logger.info(f"Cleaned up {len(to_remove)} old tasks")


class FormatterService:
    """格式化服务"""
    
    def __init__(self, task_manager: TaskManager, 
                 upload_dir: str = "static/uploads",
                 output_dir: str = "static/outputs",
                 task_timeout: int = 300):
        self.task_manager = task_manager
        self.upload_dir = Path(upload_dir)
        self.output_dir = Path(output_dir)
        self.task_timeout = task_timeout
        
        # 确保目录存在
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def format_document(self, file_path: Path, thesis_info: ThesisInfo,
                            format_options: FormatOptions) -> str:
        """格式化单个文档"""
        task_id = await self.task_manager.create_task(TaskType.SINGLE_FORMAT)
        
        # 注册进度回调
        def progress_callback(message: str, progress: int):
            asyncio.create_task(
                self.task_manager.update_task_status(
                    task_id, TaskStatus.PROCESSING, message, progress
                )
            )
        
        self.task_manager.register_progress_callback(task_id, progress_callback)
        
        # 异步执行格式化
        asyncio.create_task(self._format_document_async(
            task_id, file_path, thesis_info, format_options
        ))
        
        return task_id
    
    async def format_documents_batch(self, file_paths: list[Path], 
                                   thesis_infos: list[ThesisInfo],
                                   format_options: FormatOptions) -> str:
        """批量格式化文档"""
        task_id = await self.task_manager.create_task(
            TaskType.BATCH_FORMAT, len(file_paths)
        )
        
        # 异步执行批量格式化
        asyncio.create_task(self._format_documents_batch_async(
            task_id, file_paths, thesis_infos, format_options
        ))
        
        return task_id
    
    async def _format_document_async(self, task_id: str, file_path: Path,
                                   thesis_info: ThesisInfo, format_options: FormatOptions):
        """异步格式化单个文档"""
        try:
            await self.task_manager.update_task_status(
                task_id, TaskStatus.PROCESSING, "开始格式化...", 0
            )
            
            # 准备输出文件路径
            output_path = self.output_dir / f"{task_id}_{file_path.stem}_formatted.docx"
            
            # 创建进度回调
            def progress_callback(message: str, progress: int):
                asyncio.create_task(
                    self.task_manager.update_task_status(
                        task_id, TaskStatus.PROCESSING, message, progress
                    )
                )
            
            # 在线程池中执行格式化
            loop = asyncio.get_event_loop()
            
            def format_in_thread():
                try:
                    # 创建格式化器
                    formatter = CompleteThesisFormatter(str(file_path))
                    
                    # 设置格式化选项
                    formatter.format_options = format_options.dict()
                    
                    # 执行格式化
                    success = formatter.format_document(
                        thesis_info=thesis_info.dict(),
                        progress_callback=progress_callback,
                        output_file=str(output_path)
                    )
                    
                    return success, str(output_path)
                except Exception as e:
                    logger.exception(f"Formatting error in thread: {e}")
                    raise FormattingError(f"格式化失败: {str(e)}")
            
            # 执行格式化任务
            success, output_file = await asyncio.wait_for(
                loop.run_in_executor(self.task_manager.executor, format_in_thread),
                timeout=self.task_timeout
            )
            
            if success:
                await self.task_manager.update_task_status(
                    task_id, TaskStatus.COMPLETED, "格式化完成", 100
                )
                logger.log_task_complete(task_id, "single_format", 
                                       (datetime.now() - (await self.task_manager.get_task(task_id)).started_at).total_seconds())
            else:
                await self.task_manager.update_task_status(
                    task_id, TaskStatus.FAILED, "格式化失败", error_message="格式化器返回失败"
                )
                
        except asyncio.TimeoutError:
            await self.task_manager.update_task_status(
                task_id, TaskStatus.FAILED, "任务超时", error_message="格式化超时"
            )
            logger.log_task_error(task_id, "single_format", "Task timeout")
            
        except Exception as e:
            await self.task_manager.update_task_status(
                task_id, TaskStatus.FAILED, f"格式化失败: {str(e)}", error_message=str(e)
            )
            logger.log_task_error(task_id, "single_format", str(e))
    
    async def _format_documents_batch_async(self, task_id: str, file_paths: list[Path],
                                          thesis_infos: list[ThesisInfo], 
                                          format_options: FormatOptions):
        """异步批量格式化文档"""
        try:
            await self.task_manager.update_task_status(
                task_id, TaskStatus.PROCESSING, "开始批量格式化...", 0
            )
            
            total_files = len(file_paths)
            completed_files = 0
            
            for i, (file_path, thesis_info) in enumerate(zip(file_paths, thesis_infos)):
                # 检查任务是否被取消
                task = await self.task_manager.get_task(task_id)
                if task.status == TaskStatus.CANCELLED:
                    return
                
                # 更新进度
                progress = int((i / total_files) * 100)
                await self.task_manager.update_task_status(
                    task_id, TaskStatus.PROCESSING, 
                    f"正在处理第 {i+1}/{total_files} 个文件: {file_path.name}", 
                    progress
                )
                
                # 准备输出文件路径
                output_path = self.output_dir / f"{task_id}_{i}_{file_path.stem}_formatted.docx"
                
                # 在线程池中执行格式化
                loop = asyncio.get_event_loop()
                
                def format_single_in_thread():
                    try:
                        formatter = CompleteThesisFormatter(str(file_path))
                        formatter.format_options = format_options.dict()
                        
                        success = formatter.format_document(
                            thesis_info=thesis_info.dict(),
                            output_file=str(output_path)
                        )
                        
                        return success, str(output_path)
                    except Exception as e:
                        logger.exception(f"Batch formatting error: {e}")
                        return False, str(e)
                
                # 执行单个文件格式化
                success, result = await asyncio.wait_for(
                    loop.run_in_executor(self.task_manager.executor, format_single_in_thread),
                    timeout=self.task_timeout
                )
                
                if success:
                    completed_files += 1
                    # 更新任务中的已处理文件数
                    async with self.task_manager.task_lock:
                        self.task_manager.tasks[task_id].processed_files = completed_files
                else:
                    logger.error(f"Failed to format file {file_path}: {result}")
            
            # 完成批量任务
            final_message = f"批量格式化完成: {completed_files}/{total_files} 个文件处理成功"
            await self.task_manager.update_task_status(
                task_id, TaskStatus.COMPLETED, final_message, 100
            )
            
            logger.log_task_complete(task_id, "batch_format", 
                                   (datetime.now() - (await self.task_manager.get_task(task_id)).started_at).total_seconds())
            
        except asyncio.TimeoutError:
            await self.task_manager.update_task_status(
                task_id, TaskStatus.FAILED, "批量任务超时", error_message="批量格式化超时"
            )
            logger.log_task_error(task_id, "batch_format", "Batch task timeout")
            
        except Exception as e:
            await self.task_manager.update_task_status(
                task_id, TaskStatus.FAILED, f"批量格式化失败: {str(e)}", error_message=str(e)
            )
            logger.log_task_error(task_id, "batch_format", str(e))
    
    async def get_task_status(self, task_id: str) -> TaskInfo:
        """获取任务状态"""
        return await self.task_manager.get_task(task_id)
    
    async def cancel_task(self, task_id: str):
        """取消任务"""
        await self.task_manager.cancel_task(task_id)
    
    def get_output_file_path(self, task_id: str, file_index: int = 0) -> Path:
        """获取输出文件路径"""
        if file_index == 0:
            # 单文件格式化
            pattern = f"{task_id}_*_formatted.docx"
        else:
            # 批量格式化
            pattern = f"{task_id}_{file_index}_*_formatted.docx"
        
        # 查找匹配的文件
        matching_files = list(self.output_dir.glob(pattern))
        if matching_files:
            return matching_files[0]
        
        raise FileNotFoundError(f"Output file not found for task {task_id}")
    
    def get_all_output_files(self, task_id: str) -> list[Path]:
        """获取任务的所有输出文件"""
        pattern = f"{task_id}_*_formatted.docx"
        return list(self.output_dir.glob(pattern))
    
    async def cleanup_task_files(self, task_id: str):
        """清理任务相关文件"""
        try:
            # 清理输出文件
            output_files = self.get_all_output_files(task_id)
            for file_path in output_files:
                file_path.unlink(missing_ok=True)
            
            logger.info(f"Cleaned up {len(output_files)} files for task {task_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup files for task {task_id}: {e}")


# 全局服务实例
_task_manager = None
_formatter_service = None


def get_task_manager() -> TaskManager:
    """获取任务管理器实例"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager


def get_formatter_service() -> FormatterService:
    """获取格式化服务实例"""
    global _formatter_service
    if _formatter_service is None:
        _formatter_service = FormatterService(get_task_manager())
    return _formatter_service
"""
健康检查API路由
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import psutil
import time
import os
from pathlib import Path

from ..models import HealthResponse
from ...services.formatter_service import get_formatter_service, FormatterService
from ...services.file_service import get_file_service, FileService
from ...utils.logger import get_logger
from ... import __version__

router = APIRouter(tags=["健康检查"])
logger = get_logger("health_routes")

# 启动时间
START_TIME = time.time()


@router.get("/health", response_model=HealthResponse, summary="服务健康状态")
async def health_check(
    formatter_service: FormatterService = Depends(get_formatter_service)
):
    """
    检查服务健康状态
    
    返回服务的基本健康信息，包括：
    - 服务状态
    - 版本信息
    - 运行时间
    - 活跃任务数
    """
    try:
        uptime = time.time() - START_TIME
        active_tasks = formatter_service.task_manager.get_active_tasks_count()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            version=__version__,
            uptime=uptime,
            active_tasks=active_tasks
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            version=__version__,
            uptime=time.time() - START_TIME,
            active_tasks=0
        )


@router.get("/health/detailed", summary="详细健康状态")
async def detailed_health_check(
    formatter_service: FormatterService = Depends(get_formatter_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    获取详细的健康状态信息
    
    返回详细的系统健康信息，包括：
    - 基本服务状态
    - 系统资源使用情况
    - 磁盘空间
    - 任务统计
    - 文件系统状态
    """
    try:
        uptime = time.time() - START_TIME
        
        # 获取系统资源信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        
        # 获取任务统计
        task_manager = formatter_service.task_manager
        task_stats = {
            "total_tasks": len(task_manager.tasks),
            "active_tasks": task_manager.get_active_tasks_count(),
            "pending_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0
        }
        
        # 统计任务状态
        async with task_manager.task_lock:
            for task in task_manager.tasks.values():
                if task.status.value == "pending":
                    task_stats["pending_tasks"] += 1
                elif task.status.value == "completed":
                    task_stats["completed_tasks"] += 1
                elif task.status.value == "failed":
                    task_stats["failed_tasks"] += 1
        
        # 获取文件系统信息
        upload_dir = file_service.get_upload_dir()
        output_dir = file_service.get_output_dir()
        
        def get_dir_size(path: Path) -> int:
            """计算目录大小"""
            if not path.exists():
                return 0
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        
        file_stats = {
            "upload_dir": str(upload_dir),
            "output_dir": str(output_dir),
            "upload_dir_size": get_dir_size(upload_dir),
            "output_dir_size": get_dir_size(output_dir),
            "upload_file_count": len(list(upload_dir.glob('*'))),
            "output_file_count": len(list(output_dir.glob('*')))
        }
        
        # 检查依赖服务状态
        dependencies = {
            "python_docx": True,  # 假设已安装
            "thread_pool": task_manager.executor is not None,
            "file_system": upload_dir.exists() and output_dir.exists()
        }
        
        # 确定整体健康状态
        is_healthy = all([
            cpu_percent < 90,  # CPU使用率小于90%
            memory.percent < 90,  # 内存使用率小于90%
            disk_usage.percent < 90,  # 磁盘使用率小于90%
            all(dependencies.values())  # 所有依赖都正常
        ])
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "timestamp": datetime.now(),
            "version": __version__,
            "uptime": uptime,
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "disk_percent": disk_usage.percent,
                "disk_free": disk_usage.free
            },
            "tasks": task_stats,
            "files": file_stats,
            "dependencies": dependencies
        }
        
    except Exception as e:
        logger.exception(f"Detailed health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(),
            "version": __version__,
            "uptime": time.time() - START_TIME,
            "error": str(e)
        }


@router.get("/health/ready", summary="服务就绪状态")
async def readiness_check(
    formatter_service: FormatterService = Depends(get_formatter_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    检查服务就绪状态
    
    用于Kubernetes等容器编排系统的就绪探测
    返回服务是否准备好接收请求
    """
    try:
        # 检查关键组件是否就绪
        checks = {
            "task_manager": formatter_service.task_manager is not None,
            "file_service": file_service is not None,
            "upload_dir": file_service.get_upload_dir().exists(),
            "output_dir": file_service.get_output_dir().exists(),
            "thread_pool": formatter_service.task_manager.executor is not None
        }
        
        is_ready = all(checks.values())
        
        return {
            "ready": is_ready,
            "timestamp": datetime.now(),
            "checks": checks
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "ready": False,
            "timestamp": datetime.now(),
            "error": str(e)
        }


@router.get("/health/live", summary="服务存活状态")
async def liveness_check():
    """
    检查服务存活状态
    
    用于Kubernetes等容器编排系统的存活探测
    返回服务是否仍在运行
    """
    try:
        # 简单的存活检查
        return {
            "alive": True,
            "timestamp": datetime.now(),
            "uptime": time.time() - START_TIME
        }
        
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        return {
            "alive": False,
            "timestamp": datetime.now(),
            "error": str(e)
        }


@router.get("/metrics", summary="服务指标")
async def get_metrics(
    formatter_service: FormatterService = Depends(get_formatter_service)
):
    """
    获取服务指标
    
    返回用于监控的指标数据
    """
    try:
        task_manager = formatter_service.task_manager
        
        # 基本指标
        metrics = {
            "uptime_seconds": time.time() - START_TIME,
            "active_tasks": task_manager.get_active_tasks_count(),
            "total_tasks": len(task_manager.tasks),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
        
        # 任务状态统计
        task_status_counts = {
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }
        
        async with task_manager.task_lock:
            for task in task_manager.tasks.values():
                status = task.status.value
                if status in task_status_counts:
                    task_status_counts[status] += 1
        
        metrics.update({f"tasks_{status}": count for status, count in task_status_counts.items()})
        
        return metrics
        
    except Exception as e:
        logger.exception(f"Failed to get metrics: {e}")
        return {"error": str(e)}


@router.post("/health/cleanup", summary="清理系统")
async def cleanup_system(
    formatter_service: FormatterService = Depends(get_formatter_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    清理系统临时文件和旧任务
    
    清理包括：
    - 清理旧的上传文件
    - 清理旧的输出文件
    - 清理旧的任务记录
    """
    try:
        # 清理旧文件
        await file_service.cleanup_old_files(max_age_hours=24)
        
        # 清理旧任务
        await formatter_service.task_manager.cleanup_old_tasks(max_age_hours=24)
        
        return {
            "message": "系统清理完成",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.exception(f"System cleanup failed: {e}")
        return {
            "message": "系统清理失败",
            "error": str(e),
            "timestamp": datetime.now()
        }
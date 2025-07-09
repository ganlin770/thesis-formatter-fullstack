"""
日志配置模块
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import structlog
from typing import Dict, Any

# 创建日志目录
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class LoggerConfig:
    """日志配置类"""
    
    def __init__(self, 
                 log_level: str = "INFO",
                 log_format: str = "json",
                 log_file: str = None):
        self.log_level = log_level.upper()
        self.log_format = log_format
        self.log_file = log_file or f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
        
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志配置"""
        # 配置structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer() if self.log_format == "json" 
                else structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # 配置Python标准日志
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(self.log_file, encoding='utf-8')
            ]
        )
        
        # 设置第三方库日志级别
        logging.getLogger("uvicorn").setLevel(logging.INFO)
        logging.getLogger("fastapi").setLevel(logging.INFO)


class AppLogger:
    """应用日志器"""
    
    def __init__(self, name: str = "thesis_formatter"):
        self.logger = structlog.get_logger(name)
    
    def info(self, message: str, **kwargs):
        """记录信息日志"""
        self.logger.info(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """记录错误日志"""
        self.logger.error(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录警告日志"""
        self.logger.warning(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        self.logger.debug(message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """记录异常日志"""
        self.logger.exception(message, **kwargs)
    
    def log_request(self, method: str, url: str, status_code: int, 
                   processing_time: float, **kwargs):
        """记录请求日志"""
        self.logger.info(
            "HTTP Request",
            method=method,
            url=url,
            status_code=status_code,
            processing_time=processing_time,
            **kwargs
        )
    
    def log_task_start(self, task_id: str, task_type: str, **kwargs):
        """记录任务开始日志"""
        self.logger.info(
            "Task Started",
            task_id=task_id,
            task_type=task_type,
            **kwargs
        )
    
    def log_task_complete(self, task_id: str, task_type: str, 
                         processing_time: float, **kwargs):
        """记录任务完成日志"""
        self.logger.info(
            "Task Completed",
            task_id=task_id,
            task_type=task_type,
            processing_time=processing_time,
            **kwargs
        )
    
    def log_task_error(self, task_id: str, task_type: str, 
                      error: str, **kwargs):
        """记录任务错误日志"""
        self.logger.error(
            "Task Error",
            task_id=task_id,
            task_type=task_type,
            error=error,
            **kwargs
        )
    
    def log_file_upload(self, filename: str, file_size: int, 
                       content_type: str, **kwargs):
        """记录文件上传日志"""
        self.logger.info(
            "File Upload",
            filename=filename,
            file_size=file_size,
            content_type=content_type,
            **kwargs
        )
    
    def log_file_download(self, filename: str, **kwargs):
        """记录文件下载日志"""
        self.logger.info(
            "File Download",
            filename=filename,
            **kwargs
        )


# 创建全局日志器实例
logger = AppLogger()


# 日志中间件
class LoggingMiddleware:
    """日志中间件"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = datetime.now()
            
            # 记录请求开始
            logger.info(
                "Request Started",
                method=scope["method"],
                path=scope["path"],
                client=scope.get("client", ["unknown", 0])[0]
            )
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    processing_time = (datetime.now() - start_time).total_seconds()
                    logger.log_request(
                        method=scope["method"],
                        url=scope["path"],
                        status_code=message["status"],
                        processing_time=processing_time,
                        client=scope.get("client", ["unknown", 0])[0]
                    )
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


# 导出函数
def setup_logging(log_level: str = "INFO", log_format: str = "json", 
                 log_file: str = None):
    """设置日志配置"""
    return LoggerConfig(log_level, log_format, log_file)


def get_logger(name: str = "thesis_formatter") -> AppLogger:
    """获取日志器实例"""
    return AppLogger(name)
"""
自定义异常类
"""

from fastapi import HTTPException


class ThesisFormatterException(Exception):
    """基础异常类"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class FileValidationError(ThesisFormatterException):
    """文件验证错误"""
    pass


class FileProcessingError(ThesisFormatterException):
    """文件处理错误"""
    pass


class FormattingError(ThesisFormatterException):
    """格式化错误"""
    pass


class TaskNotFoundError(ThesisFormatterException):
    """任务未找到错误"""
    pass


class TaskTimeoutError(ThesisFormatterException):
    """任务超时错误"""
    pass


class ConfigurationError(ThesisFormatterException):
    """配置错误"""
    pass


# HTTP异常映射
class HTTPExceptionHandler:
    """HTTP异常处理器"""
    
    @staticmethod
    def file_validation_error(detail: str):
        return HTTPException(
            status_code=400,
            detail={
                "error": "FILE_VALIDATION_ERROR",
                "message": detail
            }
        )
    
    @staticmethod
    def file_processing_error(detail: str):
        return HTTPException(
            status_code=422,
            detail={
                "error": "FILE_PROCESSING_ERROR",
                "message": detail
            }
        )
    
    @staticmethod
    def formatting_error(detail: str):
        return HTTPException(
            status_code=500,
            detail={
                "error": "FORMATTING_ERROR",
                "message": detail
            }
        )
    
    @staticmethod
    def task_not_found_error(task_id: str):
        return HTTPException(
            status_code=404,
            detail={
                "error": "TASK_NOT_FOUND",
                "message": f"任务 {task_id} 不存在"
            }
        )
    
    @staticmethod
    def task_timeout_error(task_id: str):
        return HTTPException(
            status_code=408,
            detail={
                "error": "TASK_TIMEOUT",
                "message": f"任务 {task_id} 执行超时"
            }
        )
    
    @staticmethod
    def internal_server_error(detail: str = "内部服务器错误"):
        return HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": detail
            }
        )
    
    @staticmethod
    def file_too_large_error(max_size: int):
        return HTTPException(
            status_code=413,
            detail={
                "error": "FILE_TOO_LARGE",
                "message": f"文件大小超过限制 ({max_size} bytes)"
            }
        )
    
    @staticmethod
    def unsupported_file_type_error(allowed_types: list):
        return HTTPException(
            status_code=415,
            detail={
                "error": "UNSUPPORTED_FILE_TYPE",
                "message": f"不支持的文件类型，允许的类型: {', '.join(allowed_types)}"
            }
        )
    
    @staticmethod
    def too_many_requests_error():
        return HTTPException(
            status_code=429,
            detail={
                "error": "TOO_MANY_REQUESTS",
                "message": "请求过于频繁，请稍后再试"
            }
        )
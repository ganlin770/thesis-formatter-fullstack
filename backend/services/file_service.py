"""
文件处理服务模块
处理文件上传、下载、验证等功能
"""

import aiofiles
import aiofiles.os
from pathlib import Path
from typing import List, Optional, BinaryIO
from datetime import datetime
import uuid
import mimetypes
import os

from fastapi import UploadFile, HTTPException
from ..api.models import FileInfo
from ..utils.logger import get_logger
from ..utils.exceptions import (
    FileValidationError, FileProcessingError, 
    HTTPExceptionHandler
)


logger = get_logger("file_service")


class FileValidator:
    """文件验证器"""
    
    def __init__(self, max_file_size: int = 50 * 1024 * 1024,  # 50MB
                 allowed_extensions: List[str] = None):
        self.max_file_size = max_file_size
        self.allowed_extensions = allowed_extensions or ['docx', 'doc']
        
        # MIME类型映射
        self.mime_type_mapping = {
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword'
        }
    
    async def validate_file(self, file: UploadFile) -> bool:
        """验证上传的文件"""
        # 检查文件名
        if not file.filename:
            raise FileValidationError("文件名不能为空")
        
        # 检查文件扩展名
        file_extension = Path(file.filename).suffix.lower()
        if file_extension.lstrip('.') not in self.allowed_extensions:
            raise FileValidationError(
                f"不支持的文件格式: {file_extension}，"
                f"支持的格式: {', '.join(self.allowed_extensions)}"
            )
        
        # 检查MIME类型
        if file.content_type:
            expected_mime = self.mime_type_mapping.get(file_extension)
            if expected_mime and file.content_type != expected_mime:
                logger.warning(
                    f"MIME type mismatch for {file.filename}: "
                    f"expected {expected_mime}, got {file.content_type}"
                )
        
        # 检查文件大小
        if hasattr(file, 'size') and file.size:
            if file.size > self.max_file_size:
                raise FileValidationError(
                    f"文件大小超过限制: {file.size} bytes > {self.max_file_size} bytes"
                )
        
        # 检查文件内容（读取前几个字节）
        try:
            content = await file.read(1024)  # 读取前1KB
            await file.seek(0)  # 重置文件指针
            
            # 检查文件是否为空
            if not content:
                raise FileValidationError("文件内容为空")
            
            # 检查文件头（魔数）
            if file_extension == '.docx':
                # DOCX文件应该是ZIP格式，以PK开头
                if not content.startswith(b'PK'):
                    raise FileValidationError("文件格式不正确，可能已损坏")
            elif file_extension == '.doc':
                # DOC文件的魔数
                if not (content.startswith(b'\xd0\xcf\x11\xe0') or 
                       content.startswith(b'\x0f\x00\xe8\x03')):
                    raise FileValidationError("文件格式不正确，可能已损坏")
            
        except Exception as e:
            if isinstance(e, FileValidationError):
                raise
            raise FileValidationError(f"文件验证失败: {str(e)}")
        
        return True
    
    def validate_filename(self, filename: str) -> str:
        """验证并清理文件名"""
        if not filename:
            raise FileValidationError("文件名不能为空")
        
        # 移除危险字符
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
        clean_filename = filename
        for char in dangerous_chars:
            clean_filename = clean_filename.replace(char, '_')
        
        # 限制文件名长度
        if len(clean_filename) > 255:
            name, ext = os.path.splitext(clean_filename)
            clean_filename = name[:255-len(ext)] + ext
        
        return clean_filename


class FileService:
    """文件处理服务"""
    
    def __init__(self, 
                 upload_dir: str = "static/uploads",
                 output_dir: str = "static/outputs",
                 max_file_size: int = 50 * 1024 * 1024,
                 allowed_extensions: List[str] = None):
        self.upload_dir = Path(upload_dir)
        self.output_dir = Path(output_dir)
        self.validator = FileValidator(max_file_size, allowed_extensions)
        
        # 确保目录存在
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"FileService initialized with upload_dir: {self.upload_dir}, "
                   f"output_dir: {self.output_dir}")
    
    async def save_uploaded_file(self, file: UploadFile) -> Path:
        """保存上传的文件"""
        try:
            # 验证文件
            await self.validator.validate_file(file)
            
            # 生成唯一文件名
            clean_filename = self.validator.validate_filename(file.filename)
            file_id = uuid.uuid4().hex[:8]
            file_extension = Path(clean_filename).suffix
            unique_filename = f"{file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
            
            file_path = self.upload_dir / unique_filename
            
            # 保存文件
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # 记录文件信息
            file_info = FileInfo(
                filename=clean_filename,
                size=len(content),
                content_type=file.content_type or 'application/octet-stream',
                upload_time=datetime.now()
            )
            
            logger.log_file_upload(
                filename=clean_filename,
                file_size=len(content),
                content_type=file.content_type or 'unknown',
                saved_path=str(file_path)
            )
            
            return file_path
            
        except FileValidationError as e:
            logger.error(f"File validation failed: {e}")
            raise HTTPExceptionHandler.file_validation_error(str(e))
        except Exception as e:
            logger.exception(f"Failed to save uploaded file: {e}")
            raise HTTPExceptionHandler.file_processing_error(f"文件保存失败: {str(e)}")
    
    async def save_uploaded_files(self, files: List[UploadFile]) -> List[Path]:
        """保存多个上传的文件"""
        if not files:
            raise HTTPExceptionHandler.file_validation_error("没有上传文件")
        
        if len(files) > 10:  # 限制批量上传数量
            raise HTTPExceptionHandler.file_validation_error("批量上传最多支持10个文件")
        
        file_paths = []
        try:
            for file in files:
                file_path = await self.save_uploaded_file(file)
                file_paths.append(file_path)
            
            return file_paths
            
        except Exception as e:
            # 如果有任何文件保存失败，清理已保存的文件
            for file_path in file_paths:
                try:
                    await aiofiles.os.remove(file_path)
                except:
                    pass
            raise
    
    async def get_file_info(self, file_path: Path) -> FileInfo:
        """获取文件信息"""
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            stat = await aiofiles.os.stat(file_path)
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            return FileInfo(
                filename=file_path.name,
                size=stat.st_size,
                content_type=mime_type or 'application/octet-stream',
                upload_time=datetime.fromtimestamp(stat.st_mtime)
            )
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            raise FileProcessingError(f"获取文件信息失败: {str(e)}")
    
    async def read_file(self, file_path: Path) -> bytes:
        """读取文件内容"""
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
            
            logger.log_file_download(filename=file_path.name)
            return content
            
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise FileProcessingError(f"读取文件失败: {str(e)}")
    
    async def delete_file(self, file_path: Path):
        """删除文件"""
        try:
            if file_path.exists():
                await aiofiles.os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
    
    async def cleanup_old_files(self, max_age_hours: int = 24):
        """清理旧文件"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        cleanup_count = 0
        for directory in [self.upload_dir, self.output_dir]:
            for file_path in directory.glob("*"):
                if file_path.is_file():
                    try:
                        stat = await aiofiles.os.stat(file_path)
                        if stat.st_mtime < cutoff_time:
                            await aiofiles.os.remove(file_path)
                            cleanup_count += 1
                    except Exception as e:
                        logger.error(f"Failed to cleanup file {file_path}: {e}")
        
        logger.info(f"Cleaned up {cleanup_count} old files")
    
    def get_upload_dir(self) -> Path:
        """获取上传目录"""
        return self.upload_dir
    
    def get_output_dir(self) -> Path:
        """获取输出目录"""
        return self.output_dir
    
    def get_file_url(self, file_path: Path, base_url: str = "http://localhost:8000") -> str:
        """生成文件访问URL"""
        try:
            # 确定文件相对路径
            if file_path.is_relative_to(self.upload_dir):
                relative_path = file_path.relative_to(self.upload_dir)
                return f"{base_url}/static/uploads/{relative_path}"
            elif file_path.is_relative_to(self.output_dir):
                relative_path = file_path.relative_to(self.output_dir)
                return f"{base_url}/static/outputs/{relative_path}"
            else:
                raise ValueError(f"File path {file_path} is not in upload or output directory")
        except Exception as e:
            logger.error(f"Failed to generate file URL for {file_path}: {e}")
            return ""
    
    async def create_temp_file(self, content: bytes, suffix: str = ".tmp") -> Path:
        """创建临时文件"""
        try:
            temp_name = f"temp_{uuid.uuid4().hex[:8]}{suffix}"
            temp_path = self.upload_dir / temp_name
            
            async with aiofiles.open(temp_path, 'wb') as f:
                await f.write(content)
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to create temp file: {e}")
            raise FileProcessingError(f"创建临时文件失败: {str(e)}")
    
    async def move_file(self, src: Path, dst: Path):
        """移动文件"""
        try:
            await aiofiles.os.rename(src, dst)
            logger.info(f"Moved file from {src} to {dst}")
        except Exception as e:
            logger.error(f"Failed to move file from {src} to {dst}: {e}")
            raise FileProcessingError(f"移动文件失败: {str(e)}")
    
    async def copy_file(self, src: Path, dst: Path):
        """复制文件"""
        try:
            async with aiofiles.open(src, 'rb') as src_file:
                content = await src_file.read()
            
            async with aiofiles.open(dst, 'wb') as dst_file:
                await dst_file.write(content)
            
            logger.info(f"Copied file from {src} to {dst}")
            
        except Exception as e:
            logger.error(f"Failed to copy file from {src} to {dst}: {e}")
            raise FileProcessingError(f"复制文件失败: {str(e)}")


# 全局服务实例
_file_service = None


def get_file_service() -> FileService:
    """获取文件服务实例"""
    global _file_service
    if _file_service is None:
        _file_service = FileService()
    return _file_service
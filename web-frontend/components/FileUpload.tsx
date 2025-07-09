'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, AlertCircle, CheckCircle2 } from 'lucide-react';
import { FileUploadProps, UploadedFile, SUPPORTED_FILE_TYPES, MAX_FILE_SIZE } from '../types';

export default function FileUpload({
  onFileUpload,
  onError,
  acceptedFileTypes = SUPPORTED_FILE_TYPES,
  maxFileSize = MAX_FILE_SIZE,
  disabled = false,
}: FileUploadProps) {
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      
      // 验证文件类型
      if (!acceptedFileTypes.includes(file.type) && !acceptedFileTypes.some(type => file.name.endsWith(type))) {
        onError({
          code: 'INVALID_FILE_TYPE',
          message: '请上传.docx格式的Word文档',
          details: `当前文件类型：${file.type}`,
          timestamp: new Date(),
        });
        return;
      }

      // 验证文件大小
      if (file.size > maxFileSize) {
        onError({
          code: 'FILE_TOO_LARGE',
          message: `文件大小超过限制（${Math.round(maxFileSize / 1024 / 1024)}MB）`,
          details: `当前文件大小：${Math.round(file.size / 1024 / 1024)}MB`,
          timestamp: new Date(),
        });
        return;
      }

      setIsUploading(true);
      setUploadProgress(0);

      try {
        // 模拟上传进度
        const progressInterval = setInterval(() => {
          setUploadProgress(prev => {
            if (prev >= 90) {
              clearInterval(progressInterval);
              return prev;
            }
            return prev + Math.random() * 10;
          });
        }, 100);

        // 模拟文件处理时间
        await new Promise(resolve => setTimeout(resolve, 1000));

        const uploadedFileData: UploadedFile = {
          file,
          id: Date.now().toString(),
          name: file.name,
          size: file.size,
          type: file.type,
          uploadTime: new Date(),
        };

        setUploadProgress(100);
        setUploadedFile(uploadedFileData);
        onFileUpload(uploadedFileData);

        clearInterval(progressInterval);
      } catch (error) {
        onError({
          code: 'UPLOAD_FAILED',
          message: '文件上传失败',
          details: error instanceof Error ? error.message : '未知错误',
          timestamp: new Date(),
        });
      } finally {
        setIsUploading(false);
        setTimeout(() => setUploadProgress(0), 1000);
      }
    },
    [acceptedFileTypes, maxFileSize, onError, onFileUpload]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
    disabled: disabled || isUploading,
  });

  const removeFile = () => {
    setUploadedFile(null);
    setUploadProgress(0);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full">
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">上传论文文档</h2>
          <p className="text-sm text-gray-600 mt-1">
            请上传需要格式化的Word文档（.docx格式）
          </p>
        </div>

        {!uploadedFile ? (
          <div
            {...getRootProps()}
            className={`upload-zone ${
              isDragActive ? 'upload-zone-active' : ''
            } ${isDragReject ? 'upload-zone-error' : ''} ${
              disabled ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <input {...getInputProps()} />
            <div className="flex flex-col items-center space-y-4">
              <Upload className="h-12 w-12 text-gray-400" />
              <div className="text-center">
                <p className="text-lg font-medium text-gray-900">
                  {isDragActive ? '松开鼠标上传文件' : '拖拽文件到此处'}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  或者 <span className="text-primary-600 font-medium cursor-pointer">点击选择文件</span>
                </p>
              </div>
              <div className="text-xs text-gray-500 text-center">
                <p>支持格式：.docx</p>
                <p>最大文件大小：{Math.round(maxFileSize / 1024 / 1024)}MB</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <File className="h-8 w-8 text-blue-500" />
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {uploadedFile.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(uploadedFile.size)} • 上传于 {uploadedFile.uploadTime.toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="h-5 w-5 text-success-500" />
                <button
                  onClick={removeFile}
                  className="p-1 hover:bg-gray-200 rounded"
                  disabled={disabled}
                >
                  <X className="h-4 w-4 text-gray-500" />
                </button>
              </div>
            </div>
          </div>
        )}

        {isUploading && (
          <div className="mt-4 space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">上传进度</span>
              <span className="text-gray-900">{Math.round(uploadProgress)}%</span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {isDragReject && (
          <div className="mt-4 p-3 bg-error-50 border border-error-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 text-error-500" />
              <p className="text-sm text-error-800">
                不支持的文件类型，请上传.docx格式的Word文档
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
'use client';

import React, { useState } from 'react';
import { 
  Download, 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Clock, 
  Eye, 
  RefreshCw,
  FileCheck,
  Info
} from 'lucide-react';
import { FormatReportProps } from '../types';

export default function FormatReport({
  result,
  onDownload,
  onReset,
  onShowDetails,
}: FormatReportProps) {
  const [showChanges, setShowChanges] = useState(false);
  const [showWarnings, setShowWarnings] = useState(false);
  const [showErrors, setShowErrors] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTime = (milliseconds: number) => {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
      return `${minutes}分${remainingSeconds}秒`;
    }
    return `${remainingSeconds}秒`;
  };

  const handleDownload = async () => {
    if (!result.downloadUrl) return;
    
    setDownloading(true);
    try {
      await onDownload(result.downloadUrl);
    } finally {
      setDownloading(false);
    }
  };

  const getChangeTypeIcon = (type: string) => {
    switch (type) {
      case 'font':
        return <FileText className="h-4 w-4 text-blue-500" />;
      case 'spacing':
        return <FileCheck className="h-4 w-4 text-green-500" />;
      case 'margin':
        return <FileText className="h-4 w-4 text-purple-500" />;
      case 'header':
      case 'footer':
        return <FileText className="h-4 w-4 text-orange-500" />;
      case 'page':
        return <FileText className="h-4 w-4 text-indigo-500" />;
      default:
        return <FileText className="h-4 w-4 text-gray-500" />;
    }
  };

  const getChangeTypeColor = (type: string) => {
    switch (type) {
      case 'font':
        return 'bg-blue-50 text-blue-800';
      case 'spacing':
        return 'bg-green-50 text-green-800';
      case 'margin':
        return 'bg-purple-50 text-purple-800';
      case 'header':
      case 'footer':
        return 'bg-orange-50 text-orange-800';
      case 'page':
        return 'bg-indigo-50 text-indigo-800';
      default:
        return 'bg-gray-50 text-gray-800';
    }
  };

  return (
    <div className="w-full">
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">格式化报告</h2>
            <div className="flex items-center space-x-2">
              {result.success ? (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800">
                  <CheckCircle2 className="h-3 w-3 mr-1" />
                  成功
                </span>
              ) : (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-error-100 text-error-800">
                  <XCircle className="h-3 w-3 mr-1" />
                  失败
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {/* 处理结果摘要 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">
                {result.changes.length}
              </div>
              <div className="text-sm text-gray-600">格式更改</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-warning-600">
                {result.warnings.length}
              </div>
              <div className="text-sm text-gray-600">警告</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-error-600">
                {result.errors.length}
              </div>
              <div className="text-sm text-gray-600">错误</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">
                {formatTime(result.processingTime)}
              </div>
              <div className="text-sm text-gray-600">处理时间</div>
            </div>
          </div>

          {/* 结果消息 */}
          <div className={`p-4 rounded-lg ${
            result.success 
              ? 'bg-success-50 border border-success-200' 
              : 'bg-error-50 border border-error-200'
          }`}>
            <div className="flex items-center space-x-2">
              {result.success ? (
                <CheckCircle2 className="h-5 w-5 text-success-500" />
              ) : (
                <XCircle className="h-5 w-5 text-error-500" />
              )}
              <p className={`text-sm font-medium ${
                result.success ? 'text-success-800' : 'text-error-800'
              }`}>
                {result.message}
              </p>
            </div>
          </div>

          {/* 文件信息 */}
          {result.success && result.downloadUrl && (
            <div className="p-4 bg-primary-50 border border-primary-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileText className="h-8 w-8 text-primary-500" />
                  <div>
                    <p className="text-sm font-medium text-primary-900">
                      {result.fileName || '格式化后的文档.docx'}
                    </p>
                    <p className="text-xs text-primary-700">
                      {result.fileSize ? formatFileSize(result.fileSize) : '文件大小未知'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleDownload}
                  disabled={downloading}
                  className="btn-primary"
                >
                  {downloading ? (
                    <>
                      <Clock className="h-4 w-4 mr-2 animate-spin" />
                      下载中...
                    </>
                  ) : (
                    <>
                      <Download className="h-4 w-4 mr-2" />
                      下载文件
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* 格式更改详情 */}
          {result.changes.length > 0 && (
            <div>
              <button
                onClick={() => setShowChanges(!showChanges)}
                className="flex items-center justify-between w-full p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
              >
                <div className="flex items-center space-x-2">
                  <FileCheck className="h-4 w-4 text-gray-600" />
                  <span className="font-medium text-gray-900">
                    格式更改详情 ({result.changes.length})
                  </span>
                </div>
                <span className="text-gray-500">
                  {showChanges ? '−' : '+'}
                </span>
              </button>
              
              {showChanges && (
                <div className="mt-3 space-y-2">
                  {result.changes.map((change, index) => (
                    <div
                      key={index}
                      className="flex items-start space-x-3 p-3 bg-white border border-gray-200 rounded-lg"
                    >
                      <div className="flex-shrink-0 mt-0.5">
                        {getChangeTypeIcon(change.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getChangeTypeColor(change.type)}`}>
                            {change.type}
                          </span>
                          <span className="text-xs text-gray-500">{change.location}</span>
                        </div>
                        <p className="text-sm text-gray-900 mt-1">
                          {change.description}
                        </p>
                        {change.oldValue && change.newValue && (
                          <div className="text-xs text-gray-600 mt-1">
                            <span className="text-error-600">旧值：{change.oldValue}</span>
                            <span className="mx-2">→</span>
                            <span className="text-success-600">新值：{change.newValue}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* 警告信息 */}
          {result.warnings.length > 0 && (
            <div>
              <button
                onClick={() => setShowWarnings(!showWarnings)}
                className="flex items-center justify-between w-full p-3 bg-warning-50 rounded-lg hover:bg-warning-100 transition-colors duration-200"
              >
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4 text-warning-600" />
                  <span className="font-medium text-warning-900">
                    警告信息 ({result.warnings.length})
                  </span>
                </div>
                <span className="text-warning-700">
                  {showWarnings ? '−' : '+'}
                </span>
              </button>
              
              {showWarnings && (
                <div className="mt-3 space-y-2">
                  {result.warnings.map((warning, index) => (
                    <div
                      key={index}
                      className="flex items-start space-x-3 p-3 bg-warning-50 border border-warning-200 rounded-lg"
                    >
                      <AlertTriangle className="h-4 w-4 text-warning-500 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-warning-800">{warning}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* 错误信息 */}
          {result.errors.length > 0 && (
            <div>
              <button
                onClick={() => setShowErrors(!showErrors)}
                className="flex items-center justify-between w-full p-3 bg-error-50 rounded-lg hover:bg-error-100 transition-colors duration-200"
              >
                <div className="flex items-center space-x-2">
                  <XCircle className="h-4 w-4 text-error-600" />
                  <span className="font-medium text-error-900">
                    错误信息 ({result.errors.length})
                  </span>
                </div>
                <span className="text-error-700">
                  {showErrors ? '−' : '+'}
                </span>
              </button>
              
              {showErrors && (
                <div className="mt-3 space-y-2">
                  {result.errors.map((error, index) => (
                    <div
                      key={index}
                      className="flex items-start space-x-3 p-3 bg-error-50 border border-error-200 rounded-lg"
                    >
                      <XCircle className="h-4 w-4 text-error-500 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-error-800">{error}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* 操作按钮 */}
          <div className="flex justify-between items-center pt-4">
            <button
              onClick={onReset}
              className="btn-secondary"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              重新开始
            </button>
            
            <div className="flex space-x-3">
              {onShowDetails && (
                <button
                  onClick={() => onShowDetails(result.changes)}
                  className="btn-secondary"
                >
                  <Eye className="h-4 w-4 mr-2" />
                  查看详情
                </button>
              )}
              
              {result.success && result.downloadUrl && (
                <button
                  onClick={handleDownload}
                  disabled={downloading}
                  className="btn-primary"
                >
                  {downloading ? (
                    <>
                      <Clock className="h-4 w-4 mr-2 animate-spin" />
                      下载中...
                    </>
                  ) : (
                    <>
                      <Download className="h-4 w-4 mr-2" />
                      下载文件
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
'use client';

import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle2, XCircle, AlertCircle, Loader2, Play, Pause } from 'lucide-react';
import { FormatProgressProps } from '../types';

export default function FormatProgress({
  progress,
  onCancel,
  showDetails = true,
}: FormatProgressProps) {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      if (progress.status === 'processing') {
        setElapsedTime(Date.now() - progress.startTime.getTime());
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [progress.status, progress.startTime]);

  const formatTime = (milliseconds: number) => {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getEstimatedTimeRemaining = () => {
    if (progress.estimatedTime && progress.progress > 0) {
      const totalTime = progress.estimatedTime;
      const elapsedRatio = progress.progress / 100;
      const remainingTime = totalTime * (1 - elapsedRatio);
      return remainingTime;
    }
    return null;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-success-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-error-500" />;
      case 'processing':
        return <Loader2 className="h-4 w-4 text-primary-500 animate-spin" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-success-600';
      case 'error':
        return 'text-error-600';
      case 'processing':
        return 'text-primary-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return '等待开始';
      case 'processing':
        return '正在处理';
      case 'completed':
        return '已完成';
      case 'error':
        return '处理失败';
      default:
        return '未知状态';
    }
  };

  const estimatedTimeRemaining = getEstimatedTimeRemaining();

  return (
    <div className="w-full">
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">格式化进度</h2>
            <div className="flex items-center space-x-2">
              <div className={`text-sm font-medium ${getStatusColor(progress.status)}`}>
                {getStatusText(progress.status)}
              </div>
              {getStatusIcon(progress.status)}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {/* 总进度 */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">总进度</span>
              <span className="text-sm text-gray-600">{progress.progress}%</span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${progress.progress}%` }}
              />
            </div>
          </div>

          {/* 当前步骤 */}
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="flex-shrink-0">
              {progress.status === 'processing' ? (
                <Play className="h-5 w-5 text-primary-500" />
              ) : (
                <Pause className="h-5 w-5 text-gray-400" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900">
                {progress.currentStep}
              </p>
              <p className="text-xs text-gray-600 mt-1">
                {progress.status === 'processing' ? '正在执行...' : '等待中...'}
              </p>
            </div>
          </div>

          {/* 时间信息 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-600">已用时间</div>
              <div className="text-lg font-semibold text-gray-900">
                {formatTime(elapsedTime)}
              </div>
            </div>
            {estimatedTimeRemaining && (
              <div className="text-center">
                <div className="text-sm text-gray-600">预计剩余</div>
                <div className="text-lg font-semibold text-gray-900">
                  {formatTime(estimatedTimeRemaining)}
                </div>
              </div>
            )}
            <div className="text-center">
              <div className="text-sm text-gray-600">开始时间</div>
              <div className="text-lg font-semibold text-gray-900">
                {progress.startTime.toLocaleTimeString()}
              </div>
            </div>
          </div>

          {/* 详细步骤 */}
          {showDetails && (
            <div>
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="flex items-center justify-between w-full p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
              >
                <div className="flex items-center space-x-2">
                  <AlertCircle className="h-4 w-4 text-gray-600" />
                  <span className="font-medium text-gray-900">详细步骤</span>
                </div>
                <span className="text-gray-500">
                  {isExpanded ? '−' : '+'}
                </span>
              </button>
              
              {isExpanded && (
                <div className="mt-3 space-y-2">
                  {progress.steps.map((step, index) => (
                    <div
                      key={step.id}
                      className="flex items-center space-x-3 p-3 bg-white border border-gray-200 rounded-lg"
                    >
                      <div className="flex-shrink-0">
                        {getStatusIcon(step.status)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900">
                            {step.name}
                          </p>
                          <span className="text-xs text-gray-500">
                            {step.progress}%
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 mt-1">
                          {step.description}
                        </p>
                        {step.message && (
                          <p className="text-xs text-gray-500 mt-1">
                            {step.message}
                          </p>
                        )}
                        {step.status === 'processing' && (
                          <div className="mt-2">
                            <div className="w-full bg-gray-200 rounded-full h-1">
                              <div
                                className="bg-primary-600 h-1 rounded-full transition-all duration-300"
                                style={{ width: `${step.progress}%` }}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* 操作按钮 */}
          {progress.status === 'processing' && onCancel && (
            <div className="flex justify-center">
              <button
                onClick={onCancel}
                className="btn-danger"
              >
                取消处理
              </button>
            </div>
          )}

          {/* 错误状态 */}
          {progress.status === 'error' && (
            <div className="p-4 bg-error-50 border border-error-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <XCircle className="h-5 w-5 text-error-500" />
                <p className="text-sm font-medium text-error-800">
                  格式化过程中发生错误
                </p>
              </div>
              <p className="text-sm text-error-700 mt-2">
                请检查文档格式是否正确，或联系技术支持获取帮助。
              </p>
            </div>
          )}

          {/* 完成状态 */}
          {progress.status === 'completed' && (
            <div className="p-4 bg-success-50 border border-success-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="h-5 w-5 text-success-500" />
                <p className="text-sm font-medium text-success-800">
                  格式化完成！
                </p>
              </div>
              <p className="text-sm text-success-700 mt-2">
                您的论文已成功格式化，可以下载结果文件。
              </p>
              {progress.endTime && (
                <p className="text-xs text-success-600 mt-1">
                  完成时间：{progress.endTime.toLocaleString()}
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
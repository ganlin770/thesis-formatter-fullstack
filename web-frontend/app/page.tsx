'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { ChevronRight, ChevronLeft, CheckCircle2, Circle, AlertCircle } from 'lucide-react';
import FileUpload from '../components/FileUpload';
import ThesisInfoForm from '../components/ThesisInfoForm';
import FormatOptions from '../components/FormatOptions';
import FormatProgress from '../components/FormatProgress';
import FormatReport from '../components/FormatReport';
import { 
  AppState, 
  UploadedFile, 
  ThesisInfo, 
  FormatOptions as FormatOptionsType, 
  FormatProgress as FormatProgressType, 
  FormatResult, 
  ErrorInfo, 
  Notification, 
  STEPS, 
  StepId,
  DEFAULT_FORMAT_OPTIONS 
} from '../types';
import { 
  startFormatting, 
  pollForProgress, 
  getFormatResult, 
  downloadFileFromUrl, 
  handleApiError 
} from '../lib/api';

export default function HomePage() {
  const [state, setState] = useState<AppState>({
    currentStep: 1,
    uploadedFile: null,
    thesisInfo: null,
    formatOptions: DEFAULT_FORMAT_OPTIONS,
    formatProgress: null,
    formatResult: null,
    isLoading: false,
    errors: [],
    notifications: [],
  });

  // 添加通知
  const addNotification = useCallback((notification: Omit<Notification, 'id'>) => {
    const id = Date.now().toString();
    const newNotification = { ...notification, id };
    
    setState(prev => ({
      ...prev,
      notifications: [...prev.notifications, newNotification],
    }));

    // 自动移除通知
    setTimeout(() => {
      setState(prev => ({
        ...prev,
        notifications: prev.notifications.filter(n => n.id !== id),
      }));
    }, notification.duration || 5000);
  }, []);

  // 添加错误
  const addError = useCallback((error: ErrorInfo) => {
    setState(prev => ({
      ...prev,
      errors: [...prev.errors, error],
    }));

    addNotification({
      type: 'error',
      title: '错误',
      message: error.message,
      duration: 5000,
    });
  }, [addNotification]);

  // 清除错误
  const clearErrors = useCallback(() => {
    setState(prev => ({
      ...prev,
      errors: [],
    }));
  }, []);

  // 移除通知
  const removeNotification = useCallback((id: string) => {
    setState(prev => ({
      ...prev,
      notifications: prev.notifications.filter(n => n.id !== id),
    }));
  }, []);

  // 文件上传处理
  const handleFileUpload = useCallback((file: UploadedFile) => {
    setState(prev => ({
      ...prev,
      uploadedFile: file,
    }));
    
    addNotification({
      type: 'success',
      title: '上传成功',
      message: '文件上传成功，请继续填写论文信息',
      duration: 3000,
    });
  }, [addNotification]);

  // 论文信息提交处理
  const handleThesisInfoSubmit = useCallback((info: ThesisInfo) => {
    setState(prev => ({
      ...prev,
      thesisInfo: info,
    }));
    
    addNotification({
      type: 'success',
      title: '信息保存成功',
      message: '论文信息已保存，请设置格式化选项',
      duration: 3000,
    });
  }, [addNotification]);

  // 格式化选项变更处理
  const handleFormatOptionsChange = useCallback((options: FormatOptionsType) => {
    setState(prev => ({
      ...prev,
      formatOptions: options,
    }));
  }, []);

  // 开始格式化
  const handleStartFormatting = useCallback(async () => {
    if (!state.uploadedFile || !state.thesisInfo) {
      addError({
        code: 'MISSING_DATA',
        message: '请先上传文件并填写论文信息',
        timestamp: new Date(),
      });
      return;
    }

    setState(prev => ({ ...prev, isLoading: true }));
    clearErrors();

    try {
      // 开始格式化
      const { processId } = await startFormatting(
        state.uploadedFile.id,
        state.thesisInfo,
        state.formatOptions
      );

      // 设置初始进度
      const initialProgress: FormatProgressType = {
        id: processId,
        status: 'processing',
        progress: 0,
        currentStep: '正在初始化...',
        steps: [
          {
            id: '1',
            name: '文档解析',
            description: '解析Word文档结构',
            status: 'processing',
            progress: 0,
          },
          {
            id: '2',
            name: '格式分析',
            description: '分析当前文档格式',
            status: 'pending',
            progress: 0,
          },
          {
            id: '3',
            name: '应用格式',
            description: '应用新的格式设置',
            status: 'pending',
            progress: 0,
          },
          {
            id: '4',
            name: '生成文档',
            description: '生成格式化后的文档',
            status: 'pending',
            progress: 0,
          },
        ],
        estimatedTime: 30000,
        startTime: new Date(),
      };

      setState(prev => ({
        ...prev,
        formatProgress: initialProgress,
        currentStep: 4,
        isLoading: false,
      }));

      // 开始轮询进度
      const finalProgress = await pollForProgress(
        processId,
        (progress) => {
          setState(prev => ({
            ...prev,
            formatProgress: progress,
          }));
        }
      );

      // 获取格式化结果
      if (finalProgress.status === 'completed') {
        const result = await getFormatResult(processId);
        setState(prev => ({
          ...prev,
          formatResult: result,
          currentStep: 5,
        }));

        addNotification({
          type: 'success',
          title: '格式化完成',
          message: '论文格式化已完成，可以下载结果文件',
          duration: 5000,
        });
      } else if (finalProgress.status === 'error') {
        addError({
          code: 'FORMAT_ERROR',
          message: '格式化过程中发生错误',
          details: '请检查文档格式是否正确',
          timestamp: new Date(),
        });
      }
    } catch (error) {
      addError({
        code: 'API_ERROR',
        message: handleApiError(error),
        timestamp: new Date(),
      });
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, [state.uploadedFile, state.thesisInfo, state.formatOptions, addError, addNotification, clearErrors]);

  // 下载文件处理
  const handleDownload = useCallback(async (downloadUrl: string) => {
    try {
      const filename = state.formatResult?.fileName || '格式化后的文档.docx';
      await downloadFileFromUrl(downloadUrl, filename);
      
      addNotification({
        type: 'success',
        title: '下载成功',
        message: '文件已保存到下载目录',
        duration: 3000,
      });
    } catch (error) {
      addError({
        code: 'DOWNLOAD_ERROR',
        message: '文件下载失败',
        details: error instanceof Error ? error.message : '未知错误',
        timestamp: new Date(),
      });
    }
  }, [state.formatResult, addNotification, addError]);

  // 重置应用状态
  const handleReset = useCallback(() => {
    setState({
      currentStep: 1,
      uploadedFile: null,
      thesisInfo: null,
      formatOptions: DEFAULT_FORMAT_OPTIONS,
      formatProgress: null,
      formatResult: null,
      isLoading: false,
      errors: [],
      notifications: [],
    });

    addNotification({
      type: 'info',
      title: '已重置',
      message: '应用状态已重置，可以重新开始',
      duration: 3000,
    });
  }, [addNotification]);

  // 取消格式化
  const handleCancelFormatting = useCallback(async () => {
    if (state.formatProgress) {
      setState(prev => ({
        ...prev,
        formatProgress: null,
        currentStep: 3,
      }));

      addNotification({
        type: 'warning',
        title: '已取消',
        message: '格式化过程已取消',
        duration: 3000,
      });
    }
  }, [state.formatProgress, addNotification]);

  // 步骤导航
  const goToStep = useCallback((step: StepId) => {
    if (step === 1) {
      setState(prev => ({ ...prev, currentStep: step }));
    } else if (step === 2 && state.uploadedFile) {
      setState(prev => ({ ...prev, currentStep: step }));
    } else if (step === 3 && state.uploadedFile && state.thesisInfo) {
      setState(prev => ({ ...prev, currentStep: step }));
    }
  }, [state.uploadedFile, state.thesisInfo]);

  // 下一步
  const nextStep = useCallback(() => {
    if (state.currentStep < 5) {
      if (state.currentStep === 1 && state.uploadedFile) {
        setState(prev => ({ ...prev, currentStep: 2 }));
      } else if (state.currentStep === 2 && state.thesisInfo) {
        setState(prev => ({ ...prev, currentStep: 3 }));
      } else if (state.currentStep === 3) {
        handleStartFormatting();
      }
    }
  }, [state.currentStep, state.uploadedFile, state.thesisInfo, handleStartFormatting]);

  // 上一步
  const prevStep = useCallback(() => {
    if (state.currentStep > 1) {
      setState(prev => ({ ...prev, currentStep: prev.currentStep - 1 }));
    }
  }, [state.currentStep]);

  const canProceed = useCallback(() => {
    switch (state.currentStep) {
      case 1:
        return !!state.uploadedFile;
      case 2:
        return !!state.thesisInfo;
      case 3:
        return true;
      default:
        return false;
    }
  }, [state.currentStep, state.uploadedFile, state.thesisInfo]);

  const getStepStatus = useCallback((stepId: StepId) => {
    if (stepId < state.currentStep) return 'completed';
    if (stepId === state.currentStep) return 'active';
    return 'pending';
  }, [state.currentStep]);

  return (
    <div className="max-w-4xl mx-auto">
      {/* 步骤指示器 */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {STEPS.map((step, index) => (
            <React.Fragment key={step.id}>
              <div 
                className="flex flex-col items-center cursor-pointer group"
                onClick={() => goToStep(step.id)}
              >
                <div className={`
                  step-indicator transition-all duration-200
                  ${getStepStatus(step.id) === 'completed' ? 'step-completed' : ''}
                  ${getStepStatus(step.id) === 'active' ? 'step-active' : ''}
                  ${getStepStatus(step.id) === 'pending' ? 'step-pending' : ''}
                  group-hover:scale-110
                `}>
                  {getStepStatus(step.id) === 'completed' ? (
                    <CheckCircle2 className="h-4 w-4" />
                  ) : (
                    <span>{step.id}</span>
                  )}
                </div>
                <div className="text-xs text-gray-600 mt-2 text-center max-w-20">
                  {step.name}
                </div>
                <div className="text-xs text-gray-500 mt-1 text-center max-w-24 hidden sm:block">
                  {step.description}
                </div>
              </div>
              {index < STEPS.length - 1 && (
                <div className="flex-1 mx-2">
                  <div className="h-1 bg-gray-200 rounded-full">
                    <div 
                      className={`h-1 rounded-full transition-all duration-500 ${
                        step.id < state.currentStep ? 'bg-success-500' : 'bg-gray-200'
                      }`}
                      style={{ width: step.id < state.currentStep ? '100%' : '0%' }}
                    />
                  </div>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* 主要内容 */}
      <div className="animate-fade-in">
        {state.currentStep === 1 && (
          <FileUpload
            onFileUpload={handleFileUpload}
            onError={addError}
            disabled={state.isLoading}
          />
        )}

        {state.currentStep === 2 && (
          <ThesisInfoForm
            initialData={state.thesisInfo || undefined}
            onSubmit={handleThesisInfoSubmit}
            onError={addError}
            disabled={state.isLoading}
          />
        )}

        {state.currentStep === 3 && (
          <FormatOptions
            initialOptions={state.formatOptions}
            onOptionsChange={handleFormatOptionsChange}
            disabled={state.isLoading}
          />
        )}

        {state.currentStep === 4 && state.formatProgress && (
          <FormatProgress
            progress={state.formatProgress}
            onCancel={handleCancelFormatting}
            showDetails={true}
          />
        )}

        {state.currentStep === 5 && state.formatResult && (
          <FormatReport
            result={state.formatResult}
            onDownload={handleDownload}
            onReset={handleReset}
          />
        )}
      </div>

      {/* 导航按钮 */}
      {state.currentStep < 4 && (
        <div className="flex justify-between items-center mt-8">
          <button
            onClick={prevStep}
            disabled={state.currentStep === 1 || state.isLoading}
            className="btn-secondary disabled:opacity-50"
          >
            <ChevronLeft className="h-4 w-4 mr-2" />
            上一步
          </button>
          
          <button
            onClick={nextStep}
            disabled={!canProceed() || state.isLoading}
            className="btn-primary disabled:opacity-50"
          >
            {state.isLoading ? (
              <>
                <div className="loader mr-2" />
                处理中...
              </>
            ) : (
              <>
                {state.currentStep === 3 ? '开始格式化' : '下一步'}
                <ChevronRight className="h-4 w-4 ml-2" />
              </>
            )}
          </button>
        </div>
      )}

      {/* 通知列表 */}
      <div className="fixed top-4 right-4 space-y-2 z-50">
        {state.notifications.map((notification) => (
          <div
            key={notification.id}
            className={`notification ${
              notification.type === 'success' ? 'notification-success' : ''
            } ${
              notification.type === 'error' ? 'notification-error' : ''
            } ${
              notification.type === 'warning' ? 'notification-warning' : ''
            }`}
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                {notification.type === 'success' && <CheckCircle2 className="h-5 w-5" />}
                {notification.type === 'error' && <AlertCircle className="h-5 w-5" />}
                {notification.type === 'warning' && <AlertCircle className="h-5 w-5" />}
                {notification.type === 'info' && <Circle className="h-5 w-5" />}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">{notification.title}</p>
                <p className="text-sm mt-1">{notification.message}</p>
              </div>
              <button
                onClick={() => removeNotification(notification.id)}
                className="flex-shrink-0 text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
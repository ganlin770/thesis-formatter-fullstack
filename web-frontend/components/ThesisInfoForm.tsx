'use client';

import React, { useState, useEffect } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { Calendar, User, BookOpen, GraduationCap, Hash, UserCheck } from 'lucide-react';
import { ThesisInfoFormProps, ThesisInfo, FormErrors } from '../types';

export default function ThesisInfoForm({
  initialData,
  onSubmit,
  onError,
  disabled = false,
}: ThesisInfoFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
    reset,
  } = useForm<ThesisInfo>({
    defaultValues: {
      title: initialData?.title || '',
      major: initialData?.major || '',
      className: initialData?.className || '',
      studentId: initialData?.studentId || '',
      studentName: initialData?.studentName || '',
      instructor: initialData?.instructor || '',
      date: initialData?.date || new Date().toISOString().split('T')[0],
    },
  });

  // 监听表单变化，实时保存到本地存储
  const formData = watch();
  useEffect(() => {
    localStorage.setItem('thesis-info', JSON.stringify(formData));
  }, [formData]);

  // 从本地存储恢复数据
  useEffect(() => {
    const savedData = localStorage.getItem('thesis-info');
    if (savedData && !initialData) {
      try {
        const parsedData = JSON.parse(savedData);
        Object.keys(parsedData).forEach((key) => {
          setValue(key as keyof ThesisInfo, parsedData[key]);
        });
      } catch (error) {
        console.error('Failed to parse saved thesis info:', error);
      }
    }
  }, [initialData, setValue]);

  const onSubmitForm: SubmitHandler<ThesisInfo> = async (data) => {
    setIsSubmitting(true);
    
    try {
      // 验证数据
      const validationErrors: FormErrors = {};
      
      if (!data.title.trim()) {
        validationErrors.title = '论文标题不能为空';
      } else if (data.title.length > 100) {
        validationErrors.title = '论文标题不能超过100个字符';
      }
      
      if (!data.major.trim()) {
        validationErrors.major = '专业名称不能为空';
      }
      
      if (!data.className.trim()) {
        validationErrors.className = '班级信息不能为空';
      }
      
      if (!data.studentId.trim()) {
        validationErrors.studentId = '学号不能为空';
      } else if (!/^\d{8,12}$/.test(data.studentId)) {
        validationErrors.studentId = '学号格式不正确（8-12位数字）';
      }
      
      if (!data.studentName.trim()) {
        validationErrors.studentName = '学生姓名不能为空';
      } else if (data.studentName.length > 20) {
        validationErrors.studentName = '学生姓名不能超过20个字符';
      }
      
      if (!data.instructor.trim()) {
        validationErrors.instructor = '指导教师不能为空';
      } else if (data.instructor.length > 20) {
        validationErrors.instructor = '指导教师姓名不能超过20个字符';
      }
      
      if (!data.date) {
        validationErrors.date = '日期不能为空';
      } else {
        const selectedDate = new Date(data.date);
        const today = new Date();
        if (selectedDate > today) {
          validationErrors.date = '日期不能是未来日期';
        }
      }
      
      if (Object.keys(validationErrors).length > 0) {
        onError({
          code: 'VALIDATION_ERROR',
          message: '表单验证失败，请检查输入信息',
          details: Object.values(validationErrors).join('; '),
          timestamp: new Date(),
        });
        return;
      }
      
      // 提交数据
      await onSubmit(data);
      
      // 清除本地存储
      localStorage.removeItem('thesis-info');
      
    } catch (error) {
      onError({
        code: 'SUBMIT_ERROR',
        message: '提交表单失败',
        details: error instanceof Error ? error.message : '未知错误',
        timestamp: new Date(),
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const clearForm = () => {
    reset();
    localStorage.removeItem('thesis-info');
  };

  return (
    <div className="w-full">
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">论文基本信息</h2>
          <p className="text-sm text-gray-600 mt-1">
            请填写论文的基本信息，这些信息将用于生成封面和格式化文档
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmitForm)} className="space-y-6">
          {/* 论文标题 */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
              <BookOpen className="inline h-4 w-4 mr-1" />
              论文标题 *
            </label>
            <input
              {...register('title', { 
                required: '论文标题不能为空',
                maxLength: { value: 100, message: '论文标题不能超过100个字符' }
              })}
              type="text"
              id="title"
              className={`input-field ${errors.title ? 'input-error' : ''}`}
              placeholder="请输入论文标题"
              disabled={disabled || isSubmitting}
            />
            {errors.title && (
              <p className="mt-1 text-sm text-error-600">{errors.title.message}</p>
            )}
          </div>

          {/* 专业和班级 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="major" className="block text-sm font-medium text-gray-700 mb-2">
                <GraduationCap className="inline h-4 w-4 mr-1" />
                专业 *
              </label>
              <input
                {...register('major', { required: '专业名称不能为空' })}
                type="text"
                id="major"
                className={`input-field ${errors.major ? 'input-error' : ''}`}
                placeholder="请输入专业名称"
                disabled={disabled || isSubmitting}
              />
              {errors.major && (
                <p className="mt-1 text-sm text-error-600">{errors.major.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="className" className="block text-sm font-medium text-gray-700 mb-2">
                <User className="inline h-4 w-4 mr-1" />
                班级 *
              </label>
              <input
                {...register('className', { required: '班级信息不能为空' })}
                type="text"
                id="className"
                className={`input-field ${errors.className ? 'input-error' : ''}`}
                placeholder="请输入班级信息"
                disabled={disabled || isSubmitting}
              />
              {errors.className && (
                <p className="mt-1 text-sm text-error-600">{errors.className.message}</p>
              )}
            </div>
          </div>

          {/* 学号和姓名 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="studentId" className="block text-sm font-medium text-gray-700 mb-2">
                <Hash className="inline h-4 w-4 mr-1" />
                学号 *
              </label>
              <input
                {...register('studentId', { 
                  required: '学号不能为空',
                  pattern: { value: /^\d{8,12}$/, message: '学号格式不正确（8-12位数字）' }
                })}
                type="text"
                id="studentId"
                className={`input-field ${errors.studentId ? 'input-error' : ''}`}
                placeholder="请输入学号"
                disabled={disabled || isSubmitting}
              />
              {errors.studentId && (
                <p className="mt-1 text-sm text-error-600">{errors.studentId.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="studentName" className="block text-sm font-medium text-gray-700 mb-2">
                <User className="inline h-4 w-4 mr-1" />
                学生姓名 *
              </label>
              <input
                {...register('studentName', { 
                  required: '学生姓名不能为空',
                  maxLength: { value: 20, message: '学生姓名不能超过20个字符' }
                })}
                type="text"
                id="studentName"
                className={`input-field ${errors.studentName ? 'input-error' : ''}`}
                placeholder="请输入学生姓名"
                disabled={disabled || isSubmitting}
              />
              {errors.studentName && (
                <p className="mt-1 text-sm text-error-600">{errors.studentName.message}</p>
              )}
            </div>
          </div>

          {/* 指导教师和日期 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="instructor" className="block text-sm font-medium text-gray-700 mb-2">
                <UserCheck className="inline h-4 w-4 mr-1" />
                指导教师 *
              </label>
              <input
                {...register('instructor', { 
                  required: '指导教师不能为空',
                  maxLength: { value: 20, message: '指导教师姓名不能超过20个字符' }
                })}
                type="text"
                id="instructor"
                className={`input-field ${errors.instructor ? 'input-error' : ''}`}
                placeholder="请输入指导教师姓名"
                disabled={disabled || isSubmitting}
              />
              {errors.instructor && (
                <p className="mt-1 text-sm text-error-600">{errors.instructor.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="inline h-4 w-4 mr-1" />
                日期 *
              </label>
              <input
                {...register('date', { required: '日期不能为空' })}
                type="date"
                id="date"
                className={`input-field ${errors.date ? 'input-error' : ''}`}
                disabled={disabled || isSubmitting}
              />
              {errors.date && (
                <p className="mt-1 text-sm text-error-600">{errors.date.message}</p>
              )}
            </div>
          </div>

          {/* 按钮组 */}
          <div className="flex justify-between items-center pt-4">
            <button
              type="button"
              onClick={clearForm}
              className="btn-secondary"
              disabled={disabled || isSubmitting}
            >
              清空表单
            </button>
            
            <button
              type="submit"
              className="btn-primary"
              disabled={disabled || isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <div className="loader mr-2" />
                  提交中...
                </>
              ) : (
                '下一步'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
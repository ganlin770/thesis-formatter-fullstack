'use client';

import React, { useState, useEffect } from 'react';
import { Settings, Type, AlignJustify, FileText, Header, List, BookOpen, FileImage } from 'lucide-react';
import { FormatOptionsProps, FormatOptions, DEFAULT_FORMAT_OPTIONS } from '../types';

export default function FormatOptionsComponent({
  initialOptions = DEFAULT_FORMAT_OPTIONS,
  onOptionsChange,
  disabled = false,
}: FormatOptionsProps) {
  const [options, setOptions] = useState<FormatOptions>(initialOptions);
  const [expandedSections, setExpandedSections] = useState<string[]>(['basic']);

  useEffect(() => {
    onOptionsChange(options);
  }, [options, onOptionsChange]);

  const updateOption = <K extends keyof FormatOptions>(
    key: K,
    value: FormatOptions[K]
  ) => {
    setOptions(prev => ({ ...prev, [key]: value }));
  };

  const updateMargin = (side: keyof FormatOptions['margins'], value: number) => {
    setOptions(prev => ({
      ...prev,
      margins: { ...prev.margins, [side]: value }
    }));
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev =>
      prev.includes(section)
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  const resetToDefault = () => {
    setOptions(DEFAULT_FORMAT_OPTIONS);
  };

  const presetOptions = [
    {
      name: '本科毕业论文',
      description: '适用于本科毕业论文格式要求',
      options: {
        ...DEFAULT_FORMAT_OPTIONS,
        fontSize: 12,
        fontFamily: 'Times New Roman',
        lineSpacing: 1.5,
        margins: { top: 25, bottom: 25, left: 30, right: 20 },
      },
    },
    {
      name: '硕士学位论文',
      description: '适用于硕士学位论文格式要求',
      options: {
        ...DEFAULT_FORMAT_OPTIONS,
        fontSize: 12,
        fontFamily: 'Times New Roman',
        lineSpacing: 1.5,
        margins: { top: 30, bottom: 25, left: 30, right: 20 },
      },
    },
    {
      name: '博士学位论文',
      description: '适用于博士学位论文格式要求',
      options: {
        ...DEFAULT_FORMAT_OPTIONS,
        fontSize: 12,
        fontFamily: 'Times New Roman',
        lineSpacing: 1.5,
        margins: { top: 35, bottom: 30, left: 35, right: 25 },
      },
    },
  ];

  return (
    <div className="w-full">
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-gray-900">格式化选项</h2>
          <p className="text-sm text-gray-600 mt-1">
            选择论文格式化选项，或使用预设方案
          </p>
        </div>

        <div className="space-y-6">
          {/* 预设方案 */}
          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-3">预设方案</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {presetOptions.map((preset) => (
                <button
                  key={preset.name}
                  onClick={() => setOptions(preset.options)}
                  disabled={disabled}
                  className="p-3 text-left border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors duration-200 disabled:opacity-50"
                >
                  <div className="font-medium text-sm text-gray-900">{preset.name}</div>
                  <div className="text-xs text-gray-600 mt-1">{preset.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* 基本格式设置 */}
          <div>
            <button
              onClick={() => toggleSection('basic')}
              className="flex items-center justify-between w-full p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
            >
              <div className="flex items-center space-x-2">
                <Type className="h-4 w-4 text-gray-600" />
                <span className="font-medium text-gray-900">基本格式</span>
              </div>
              <span className="text-gray-500">
                {expandedSections.includes('basic') ? '−' : '+'}
              </span>
            </button>
            
            {expandedSections.includes('basic') && (
              <div className="mt-3 p-4 border border-gray-200 rounded-lg space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      字体
                    </label>
                    <select
                      value={options.fontFamily}
                      onChange={(e) => updateOption('fontFamily', e.target.value)}
                      disabled={disabled}
                      className="input-field"
                    >
                      <option value="Times New Roman">Times New Roman</option>
                      <option value="Arial">Arial</option>
                      <option value="Calibri">Calibri</option>
                      <option value="宋体">宋体</option>
                      <option value="黑体">黑体</option>
                      <option value="微软雅黑">微软雅黑</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      字号
                    </label>
                    <select
                      value={options.fontSize}
                      onChange={(e) => updateOption('fontSize', parseInt(e.target.value))}
                      disabled={disabled}
                      className="input-field"
                    >
                      <option value={10}>10</option>
                      <option value={11}>11</option>
                      <option value={12}>12</option>
                      <option value={14}>14</option>
                      <option value={16}>16</option>
                      <option value={18}>18</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    行间距
                  </label>
                  <select
                    value={options.lineSpacing}
                    onChange={(e) => updateOption('lineSpacing', parseFloat(e.target.value))}
                    disabled={disabled}
                    className="input-field"
                  >
                    <option value={1}>单倍行距</option>
                    <option value={1.15}>1.15倍行距</option>
                    <option value={1.5}>1.5倍行距</option>
                    <option value={2}>2倍行距</option>
                    <option value={2.5}>2.5倍行距</option>
                    <option value={3}>3倍行距</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          {/* 页面设置 */}
          <div>
            <button
              onClick={() => toggleSection('page')}
              className="flex items-center justify-between w-full p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
            >
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4 text-gray-600" />
                <span className="font-medium text-gray-900">页面设置</span>
              </div>
              <span className="text-gray-500">
                {expandedSections.includes('page') ? '−' : '+'}
              </span>
            </button>
            
            {expandedSections.includes('page') && (
              <div className="mt-3 p-4 border border-gray-200 rounded-lg space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    页边距 (毫米)
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">上边距</label>
                      <input
                        type="number"
                        value={options.margins.top}
                        onChange={(e) => updateMargin('top', parseInt(e.target.value))}
                        disabled={disabled}
                        className="input-field text-sm"
                        min="10"
                        max="50"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">下边距</label>
                      <input
                        type="number"
                        value={options.margins.bottom}
                        onChange={(e) => updateMargin('bottom', parseInt(e.target.value))}
                        disabled={disabled}
                        className="input-field text-sm"
                        min="10"
                        max="50"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">左边距</label>
                      <input
                        type="number"
                        value={options.margins.left}
                        onChange={(e) => updateMargin('left', parseInt(e.target.value))}
                        disabled={disabled}
                        className="input-field text-sm"
                        min="10"
                        max="50"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">右边距</label>
                      <input
                        type="number"
                        value={options.margins.right}
                        onChange={(e) => updateMargin('right', parseInt(e.target.value))}
                        disabled={disabled}
                        className="input-field text-sm"
                        min="10"
                        max="50"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="pageNumbering"
                    checked={options.pageNumbering}
                    onChange={(e) => updateOption('pageNumbering', e.target.checked)}
                    disabled={disabled}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label htmlFor="pageNumbering" className="text-sm text-gray-700">
                    添加页码
                  </label>
                </div>
              </div>
            )}
          </div>

          {/* 文档结构 */}
          <div>
            <button
              onClick={() => toggleSection('structure')}
              className="flex items-center justify-between w-full p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
            >
              <div className="flex items-center space-x-2">
                <List className="h-4 w-4 text-gray-600" />
                <span className="font-medium text-gray-900">文档结构</span>
              </div>
              <span className="text-gray-500">
                {expandedSections.includes('structure') ? '−' : '+'}
              </span>
            </button>
            
            {expandedSections.includes('structure') && (
              <div className="mt-3 p-4 border border-gray-200 rounded-lg space-y-3">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="coverPage"
                    checked={options.coverPage}
                    onChange={(e) => updateOption('coverPage', e.target.checked)}
                    disabled={disabled}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label htmlFor="coverPage" className="text-sm text-gray-700">
                    生成封面页
                  </label>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="tableOfContents"
                    checked={options.tableOfContents}
                    onChange={(e) => updateOption('tableOfContents', e.target.checked)}
                    disabled={disabled}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label htmlFor="tableOfContents" className="text-sm text-gray-700">
                    生成目录
                  </label>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="headerFooter"
                    checked={options.headerFooter}
                    onChange={(e) => updateOption('headerFooter', e.target.checked)}
                    disabled={disabled}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label htmlFor="headerFooter" className="text-sm text-gray-700">
                    添加页眉页脚
                  </label>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="bibliography"
                    checked={options.bibliography}
                    onChange={(e) => updateOption('bibliography', e.target.checked)}
                    disabled={disabled}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label htmlFor="bibliography" className="text-sm text-gray-700">
                    格式化参考文献
                  </label>
                </div>
              </div>
            )}
          </div>

          {/* 操作按钮 */}
          <div className="flex justify-between items-center pt-4">
            <button
              onClick={resetToDefault}
              className="btn-secondary"
              disabled={disabled}
            >
              重置为默认
            </button>
            
            <div className="text-sm text-gray-600">
              当前配置：{options.fontFamily} {options.fontSize}pt, {options.lineSpacing}倍行距
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
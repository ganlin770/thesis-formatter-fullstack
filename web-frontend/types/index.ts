// 论文信息接口
export interface ThesisInfo {
  title: string;
  major: string;
  className: string;
  studentId: string;
  studentName: string;
  instructor: string;
  date: string;
}

// 文件上传接口
export interface UploadedFile {
  file: File;
  id: string;
  name: string;
  size: number;
  type: string;
  uploadTime: Date;
}

// 格式化选项接口
export interface FormatOptions {
  fontSize: number;
  fontFamily: string;
  lineSpacing: number;
  margins: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
  pageNumbering: boolean;
  headerFooter: boolean;
  tableOfContents: boolean;
  bibliography: boolean;
  coverPage: boolean;
  customRules: string[];
}

// 格式化进度接口
export interface FormatProgress {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number; // 0-100
  currentStep: string;
  steps: FormatStep[];
  estimatedTime?: number;
  startTime: Date;
  endTime?: Date;
}

// 格式化步骤接口
export interface FormatStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  message?: string;
}

// 格式化结果接口
export interface FormatResult {
  id: string;
  success: boolean;
  message: string;
  downloadUrl?: string;
  fileName?: string;
  fileSize?: number;
  changes: FormatChange[];
  warnings: string[];
  errors: string[];
  processingTime: number;
}

// 格式化更改记录接口
export interface FormatChange {
  type: 'font' | 'spacing' | 'margin' | 'header' | 'footer' | 'page' | 'other';
  description: string;
  location: string;
  oldValue?: string;
  newValue?: string;
}

// API响应接口
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  code?: number;
}

// 错误信息接口
export interface ErrorInfo {
  code: string;
  message: string;
  details?: string;
  timestamp: Date;
}

// 通知接口
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  actions?: NotificationAction[];
}

// 通知操作接口
export interface NotificationAction {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

// 应用状态接口
export interface AppState {
  currentStep: number;
  uploadedFile: UploadedFile | null;
  thesisInfo: ThesisInfo | null;
  formatOptions: FormatOptions;
  formatProgress: FormatProgress | null;
  formatResult: FormatResult | null;
  isLoading: boolean;
  errors: ErrorInfo[];
  notifications: Notification[];
}

// 组件属性接口
export interface FileUploadProps {
  onFileUpload: (file: UploadedFile) => void;
  onError: (error: ErrorInfo) => void;
  acceptedFileTypes?: string[];
  maxFileSize?: number;
  disabled?: boolean;
}

export interface ThesisInfoFormProps {
  initialData?: Partial<ThesisInfo>;
  onSubmit: (data: ThesisInfo) => void;
  onError: (error: ErrorInfo) => void;
  disabled?: boolean;
}

export interface FormatOptionsProps {
  initialOptions?: Partial<FormatOptions>;
  onOptionsChange: (options: FormatOptions) => void;
  disabled?: boolean;
}

export interface FormatProgressProps {
  progress: FormatProgress;
  onCancel?: () => void;
  showDetails?: boolean;
}

export interface FormatReportProps {
  result: FormatResult;
  onDownload: (url: string) => void;
  onReset: () => void;
  onShowDetails?: (changes: FormatChange[]) => void;
}

// 表单验证接口
export interface FormErrors {
  [key: string]: string | undefined;
}

// 默认格式化选项
export const DEFAULT_FORMAT_OPTIONS: FormatOptions = {
  fontSize: 12,
  fontFamily: 'Times New Roman',
  lineSpacing: 1.5,
  margins: {
    top: 25,
    bottom: 25,
    left: 30,
    right: 20,
  },
  pageNumbering: true,
  headerFooter: true,
  tableOfContents: true,
  bibliography: true,
  coverPage: true,
  customRules: [],
};

// 支持的文件类型
export const SUPPORTED_FILE_TYPES = [
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  '.docx',
];

// 最大文件大小 (50MB)
export const MAX_FILE_SIZE = 50 * 1024 * 1024;

// 步骤定义
export const STEPS = [
  { id: 1, name: '上传文档', description: '上传需要格式化的Word文档' },
  { id: 2, name: '填写信息', description: '填写论文基本信息' },
  { id: 3, name: '格式设置', description: '选择格式化选项' },
  { id: 4, name: '处理进度', description: '等待格式化完成' },
  { id: 5, name: '下载结果', description: '查看结果并下载文档' },
] as const;

export type StepId = typeof STEPS[number]['id'];
# 毕业论文格式化工具 - 前端

一个现代化的毕业论文格式化工具前端应用，基于 Next.js 14 和 TypeScript 构建。

## 功能特性

- 📁 **文件上传** - 支持拖拽上传 .docx 格式的 Word 文档
- 📝 **论文信息** - 完整的论文基本信息表单
- ⚙️ **格式化选项** - 丰富的格式化选项和预设方案
- 📊 **实时进度** - 实时显示格式化进度和状态
- 📄 **结果报告** - 详细的格式化结果和下载功能
- 🎨 **响应式设计** - 适配各种设备和屏幕尺寸
- 🔄 **状态管理** - 完整的应用状态管理和错误处理

## 技术栈

- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **HTTP客户端**: Axios
- **表单管理**: React Hook Form
- **文件上传**: React Dropzone
- **图标**: Lucide React

## 项目结构

```
web-frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # 根布局组件
│   ├── page.tsx           # 主页面
│   └── globals.css        # 全局样式
├── components/             # React 组件
│   ├── FileUpload.tsx     # 文件上传组件
│   ├── ThesisInfoForm.tsx # 论文信息表单
│   ├── FormatOptions.tsx  # 格式化选项
│   ├── FormatProgress.tsx # 进度显示
│   └── FormatReport.tsx   # 结果报告
├── lib/                   # 工具库
│   └── api.ts            # API 客户端
├── types/                 # TypeScript 类型定义
│   └── index.ts          # 项目类型
├── tasks/                 # 开发任务
│   └── todo.md           # 任务清单
└── 配置文件...
```

## 开发指南

### 环境要求

- Node.js 18.0+
- npm 或 yarn

### 安装依赖

```bash
npm install
# 或
yarn install
```

### 环境配置

复制环境变量模板：

```bash
cp .env.local.example .env.local
```

编辑 `.env.local` 文件，配置 API 地址：

```env
NEXT_PUBLIC_API_URL=http://localhost:3001/api
```

### 启动开发服务器

```bash
npm run dev
# 或
yarn dev
```

应用将在 http://localhost:3000 启动。

### 构建生产版本

```bash
npm run build
npm run start
# 或
yarn build
yarn start
```

## 组件说明

### FileUpload 组件

- 支持拖拽和点击上传
- 文件类型和大小验证
- 上传进度显示
- 错误处理和提示

### ThesisInfoForm 组件

- 响应式表单设计
- 实时验证和错误提示
- 本地存储自动保存
- 数据格式验证

### FormatOptions 组件

- 丰富的格式化选项
- 预设方案快速选择
- 实时预览配置
- 折叠式界面设计

### FormatProgress 组件

- 实时进度显示
- 详细步骤跟踪
- 时间估算和统计
- 可取消操作

### FormatReport 组件

- 详细的格式化结果
- 更改记录和统计
- 警告和错误信息
- 文件下载功能

## API 集成

应用通过 Axios 与后端 API 交互：

- `POST /api/upload` - 文件上传
- `POST /api/format/start` - 开始格式化
- `GET /api/format/progress/:id` - 获取进度
- `GET /api/format/result/:id` - 获取结果
- `GET /api/download/:url` - 下载文件

## 状态管理

应用使用 React State 和 Context 管理状态：

- 文件上传状态
- 论文信息数据
- 格式化选项
- 进度和结果状态
- 错误和通知

## 样式系统

使用 Tailwind CSS 构建响应式界面：

- 原子化 CSS 类
- 自定义组件样式
- 响应式设计
- 主题色彩系统
- 动画和过渡效果

## 错误处理

完整的错误处理机制：

- API 错误拦截
- 表单验证错误
- 用户友好的错误提示
- 错误状态管理
- 重试和恢复机制

## 性能优化

- 组件懒加载
- 图片优化
- 代码分割
- 缓存策略
- 响应式图片

## 浏览器兼容性

- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+

## 部署

### Vercel 部署

```bash
npm run build
vercel --prod
```

### 其他平台

构建静态文件：

```bash
npm run build
npm run export
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 支持

如有问题或建议，请创建 Issue 或联系开发团队。
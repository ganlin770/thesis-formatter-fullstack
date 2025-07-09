# 江西财经大学毕业论文格式化工具 - 全栈版

[![Deploy to Railway](https://railway.app/button.svg)](https://railway.app/template/deploy)

一个专为江西财经大学现代经济管理学院设计的完整论文格式化工具，支持Web界面操作和一键部署。

## 🌟 项目特色

- **🎯 精确格式化**: 完全符合江财学院论文格式要求
- **🚀 现代化技术栈**: Next.js 14 + FastAPI + Python
- **☁️ 一键部署**: 完整的Railway部署配置
- **🔧 并行处理**: 12个并行任务，高效处理大文档
- **📱 响应式设计**: 支持桌面和移动设备

## 🏗️ 技术架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js 14    │───▶│   FastAPI       │───▶│ Format Engine   │
│   TypeScript     │    │   Python 3.11   │    │   Python        │
│   Tailwind CSS  │    │   Uvicorn       │    │   python-docx   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File Upload   │    │   RESTful API   │    │ Font Manager    │
│   Progress UI   │    │   CORS Support  │    │ Spacing Manager │
│   Result Display│    │   Health Check  │    │ Header Handler  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 项目结构

```
thesis-formatter-fullstack/
├── 📁 backend/                    # FastAPI后端服务
│   ├── 🐳 Dockerfile
│   ├── 🐍 main.py
│   ├── 📋 requirements.txt
│   ├── 📁 api/
│   ├── 📁 services/
│   └── 📁 utils/
├── 📁 web-frontend/               # Next.js前端应用
│   ├── 🐳 Dockerfile
│   ├── 📦 package.json
│   ├── 📁 app/
│   ├── 📁 components/
│   └── 📁 lib/
├── 📁 thesis_formatter_complete/  # 核心格式化引擎
│   ├── 🎨 font_manager.py        # 字体管理器
│   ├── 📏 spacing_manager.py     # 行间距管理器
│   ├── 📄 header_handler.py      # 页眉处理器
│   ├── 🔧 main_formatter.py      # 主格式化器
│   └── 📁 [其他格式化模块]
├── 🚀 railway.json               # Railway部署配置
├── 🐳 docker-compose.yml        # 本地开发环境
├── 📜 deploy.sh                 # 一键部署脚本
└── 📖 DEPLOYMENT_GUIDE.md       # 详细部署文档
```

## 🚀 快速开始

### 本地开发

```bash
# 克隆项目
git clone https://github.com/ganlin770/thesis-formatter-fullstack.git
cd thesis-formatter-fullstack

# 使用Docker Compose启动
docker-compose up -d

# 访问应用
open http://localhost:3000
```

### 一键部署到Railway

```bash
# 方法1: 使用Railway CLI
railway login
railway init --name thesis-formatter-fullstack
railway up

# 方法2: 使用部署脚本
./deploy.sh deploy
```

## 📋 功能特性

### 🎯 核心格式化功能

- ✅ **封面生成**: 自动生成标准封面和诚信承诺书
- ✅ **字体管理**: 支持特殊字号"二号六"(21pt)、摘要标题字体修正
- ✅ **行间距控制**: 精确控制各区域行间距(正文22pt、脚注12pt、参考文献18pt)
- ✅ **页眉设置**: 仅正文区域显示页眉，符合江财学院要求
- ✅ **页码系统**: 智能页码分区管理
- ✅ **图表处理**: 自动编号和格式化
- ✅ **参考文献**: 标准化引用格式
- ✅ **目录生成**: 自动更新目录结构

### 🌐 Web界面功能

- ✅ **文件上传**: 支持拖拽上传、进度显示
- ✅ **论文信息**: 完整的学生信息收集表单
- ✅ **格式选项**: 可选择启用的功能模块
- ✅ **实时反馈**: 处理状态和错误提示
- ✅ **结果下载**: 一键下载格式化后的文档

### 🔧 技术特性

- ✅ **并行处理**: 12个并行任务同时执行
- ✅ **容器化部署**: 完整的Docker支持
- ✅ **健康检查**: 完善的监控和错误处理
- ✅ **CORS配置**: 安全的跨域资源共享
- ✅ **文件安全**: 安全的文件上传和处理

## 📊 格式化规则

### 字体设置
- **中文摘要标题**: 黑体 二号
- **英文摘要标题**: Arial Black 二号
- **论文标题**: 宋体 二号六 (21pt)
- **一级标题**: 宋体 小三 加粗
- **二级标题**: 宋体 四号 加粗
- **正文**: 宋体 小四

### 行间距设置
- **正文**: 22磅固定行距
- **脚注**: 12磅固定行距
- **参考文献**: 18磅固定行距
- **封面信息**: 28磅固定行距

### 页面设置
- **页眉**: 仅正文部分显示"江西财经大学现代经济管理学院普通本科毕业论文"
- **页码**: 智能分区管理，正文使用阿拉伯数字
- **页边距**: 上2.5cm，下2.5cm，左3cm，右2cm

## 🛠 环境要求

### 后端环境
- Python 3.11+
- FastAPI
- python-docx
- uvicorn

### 前端环境
- Node.js 18+
- Next.js 14
- TypeScript
- Tailwind CSS

### 部署环境
- Docker
- Railway CLI (可选)

## 🚀 部署指南

### Railway部署 (推荐)

1. **使用Railway模板部署**
   ```bash
   # 点击上方的"Deploy to Railway"按钮
   # 或者使用CLI
   railway login
   railway up
   ```

2. **手动部署**
   ```bash
   # 创建Railway项目
   railway init --name thesis-formatter-fullstack
   
   # 部署服务
   railway up
   ```

### 本地Docker部署

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📖 使用说明

1. **访问Web界面**: 打开部署后的前端地址
2. **上传文档**: 选择或拖拽.docx文件到上传区域
3. **填写信息**: 完成论文基本信息表单
4. **选择功能**: 选择需要的格式化功能
5. **开始处理**: 点击"开始格式化"按钮
6. **下载结果**: 处理完成后下载格式化文档

## 🔍 监控和维护

### 健康检查
```bash
# 后端健康检查
curl https://your-backend-domain.railway.app/health

# API端点检查
curl https://your-backend-domain.railway.app/api/health
```

### 日志查看
```bash
# 查看后端日志
railway logs --service backend

# 查看前端日志
railway logs --service frontend
```

## 📝 更新日志

### v1.0.0 (2025-07-09)
- ✅ 完整的Web界面实现
- ✅ FastAPI后端集成
- ✅ 核心格式化功能完善
- ✅ Railway部署配置
- ✅ 字体管理器优化
- ✅ 行间距管理器实现
- ✅ 页眉处理器完善

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- 江西财经大学现代经济管理学院
- FastAPI 框架
- Next.js 框架
- Railway 部署平台
- python-docx 库

## 📞 联系我们

- 项目地址: [https://github.com/ganlin770/thesis-formatter-fullstack](https://github.com/ganlin770/thesis-formatter-fullstack)
- 问题反馈: [Issues](https://github.com/ganlin770/thesis-formatter-fullstack/issues)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！

🔗 **快速链接**: [部署指南](DEPLOYMENT_GUIDE.md) | [API文档](backend/README.md) | [前端文档](web-frontend/README.md)
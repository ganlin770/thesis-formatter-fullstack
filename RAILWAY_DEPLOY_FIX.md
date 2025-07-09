# Railway部署问题修复指南

## 问题分析

您遇到的"Nixpacks build failed"错误是因为Railway无法正确识别多服务项目结构。

## 解决方案

### 方法1: 分别部署前后端服务（推荐）

#### 1. 部署后端服务
```bash
# 进入项目根目录
cd /path/to/thesis-formatter-fullstack

# 登录Railway
railway login

# 创建项目
railway init --name thesis-formatter-backend

# 使用后端Dockerfile部署
railway up --dockerfile backend/Dockerfile

# 设置环境变量
railway variables set ENVIRONMENT=production
railway variables set PORT=8000
railway variables set CORS_ORIGINS=https://your-frontend-domain.railway.app
railway variables set MAX_FILE_SIZE=10485760
railway variables set UPLOAD_DIR=/app/static/uploads
railway variables set OUTPUT_DIR=/app/static/outputs
```

#### 2. 部署前端服务
```bash
# 创建新的Railway项目
railway init --name thesis-formatter-frontend

# 进入前端目录
cd web-frontend

# 部署前端
railway up

# 设置环境变量
railway variables set NODE_ENV=production
railway variables set PORT=3000
railway variables set NEXT_PUBLIC_API_URL=https://your-backend-domain.railway.app
```

### 方法2: 使用GitHub连接部署

#### 1. 连接GitHub仓库
1. 访问 [Railway Dashboard](https://railway.app/dashboard)
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 选择 `thesis-formatter-fullstack` 仓库

#### 2. 配置后端服务
- **Service Name**: `backend`
- **Build Command**: 使用 `backend/Dockerfile`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  ```
  ENVIRONMENT=production
  PORT=8000
  CORS_ORIGINS=https://your-frontend-domain.railway.app
  MAX_FILE_SIZE=10485760
  UPLOAD_DIR=/app/static/uploads
  OUTPUT_DIR=/app/static/outputs
  ```

#### 3. 配置前端服务
- **Service Name**: `frontend`
- **Build Command**: 使用 `web-frontend/Dockerfile`
- **Start Command**: `node server.js`
- **Environment Variables**:
  ```
  NODE_ENV=production
  PORT=3000
  NEXT_PUBLIC_API_URL=https://your-backend-domain.railway.app
  ```

## 文件修复说明

我已经为您修复了以下文件：

1. **`web-frontend/next.config.js`**: 添加了 `output: 'standalone'` 配置
2. **`railway.toml`**: 创建了Railway配置文件
3. **`nixpacks.toml`**: 添加了构建指导
4. **`package.json`**: 创建了根目录package.json

## 验证部署

部署完成后，检查以下端点：

```bash
# 后端健康检查
curl https://your-backend-domain.railway.app/health

# API端点检查
curl https://your-backend-domain.railway.app/api/health

# 前端可访问性
curl https://your-frontend-domain.railway.app
```

## 故障排除

### 如果前端构建失败：
1. 确保使用 `web-frontend/Dockerfile`
2. 检查 `NEXT_PUBLIC_API_URL` 环境变量设置
3. 确认Next.js配置中有 `output: 'standalone'`

### 如果后端构建失败：
1. 确保使用 `backend/Dockerfile`
2. 检查Python依赖是否正确安装
3. 验证 `thesis_formatter_complete` 目录是否正确复制

### 如果服务无法通信：
1. 检查CORS设置是否正确
2. 确认环境变量中的域名设置
3. 验证健康检查端点是否响应

## 部署成功标志

- ✅ 后端服务返回 200 状态码在 `/health` 端点
- ✅ 前端服务可以正常访问
- ✅ 文件上传功能正常工作
- ✅ 格式化处理无错误

## 快速部署脚本

```bash
#!/bin/bash
# 快速部署脚本

echo "开始部署论文格式化工具..."

# 部署后端
echo "部署后端服务..."
railway login
railway init --name thesis-formatter-backend
railway up --dockerfile backend/Dockerfile

# 获取后端域名
BACKEND_DOMAIN=$(railway domain)
echo "后端域名: $BACKEND_DOMAIN"

# 部署前端
echo "部署前端服务..."
railway init --name thesis-formatter-frontend
cd web-frontend
railway up
railway variables set NEXT_PUBLIC_API_URL="https://$BACKEND_DOMAIN"

echo "部署完成！"
```

使用这个修复方案应该能够解决您遇到的部署问题。
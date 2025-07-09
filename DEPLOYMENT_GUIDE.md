# 论文格式化工具 Railway 部署指南

## 项目概述

这是一个全栈论文格式化工具，包含：
- **前端**: Next.js TypeScript 应用
- **后端**: FastAPI Python API
- **核心**: 完整的Python论文格式化引擎
- **部署**: Railway 云平台

## 部署架构

```
Internet → Railway Load Balancer → Frontend Service (Next.js)
                                 ↓
                                 Backend Service (FastAPI)
                                 ↓
                                 Thesis Formatter Engine (Python)
```

## 预备工作

### 1. 安装依赖

```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 安装 Docker 和 Docker Compose
# 参考: https://docs.docker.com/get-docker/
```

### 2. 获取 Railway API Token

1. 访问 [Railway Dashboard](https://railway.app/dashboard)
2. 点击 "Account Settings" → "Tokens"
3. 创建新的 API Token
4. 设置环境变量：
   ```bash
   export RAILWAY_API_TOKEN="your-token-here"
   ```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置必要的变量
vim .env
```

## 部署步骤

### 方式一：使用 Railway.json 一键部署（推荐）

```bash
# 1. 登录 Railway
railway login

# 2. 初始化项目
railway init --name thesis-formatter-fullstack

# 3. 使用 railway.json 配置部署
railway up

# 4. 查看部署状态
railway status
```

### 方式二：手动部署

#### 1. 创建 Railway 项目

```bash
railway login
railway init --name thesis-formatter
```

#### 2. 部署后端服务

```bash
# 创建后端服务
railway service create backend

# 设置环境变量
railway variables set \
  ENVIRONMENT=production \
  PORT=8000 \
  CORS_ORIGINS=https://your-frontend-domain.railway.app \
  MAX_FILE_SIZE=10485760 \
  UPLOAD_DIR=/app/static/uploads \
  OUTPUT_DIR=/app/static/outputs

# 部署
railway up --service backend
```

#### 3. 部署前端服务

```bash
# 创建前端服务
railway service create frontend

# 获取后端域名
BACKEND_URL=$(railway domain --service backend)

# 设置环境变量
railway variables set \
  NODE_ENV=production \
  NEXT_PUBLIC_API_URL="https://$BACKEND_URL" \
  PORT=3000

# 部署
railway up --service frontend
```

#### 4. 配置域名

```bash
# 查看生成的域名
railway domain --service frontend
railway domain --service backend

# 配置自定义域名（可选）
railway domain add yourdomain.com --service frontend
```

## 本地开发

### 使用 Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 直接运行

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd web-frontend
npm install
npm run dev
```

## 环境变量说明

### 必需变量

- `RAILWAY_API_TOKEN`: Railway API 令牌
- `ENVIRONMENT`: 应用环境 (development/production)
- `NODE_ENV`: Node.js 环境 (development/production)
- `NEXT_PUBLIC_API_URL`: 前端访问后端的 URL
- `PORT`: 服务端口 (frontend: 3000, backend: 8000)

### 可选变量

- `CORS_ORIGINS`: 允许的跨域源 (后端)
- `MAX_FILE_SIZE`: 最大文件大小限制 (默认 10MB)
- `UPLOAD_DIR`: 文件上传目录 (默认 /app/static/uploads)
- `OUTPUT_DIR`: 输出文件目录 (默认 /app/static/outputs)

## 监控和维护

### 查看日志

```bash
# 查看前端日志
railway logs --service frontend

# 查看后端日志
railway logs --service backend

```

### 健康检查

```bash
# 检查后端健康状态
curl https://your-backend-domain.railway.app/health

# 检查前端可访问性
curl https://your-frontend-domain.railway.app

# 检查API端点
curl https://your-backend-domain.railway.app/api/health
```

### 扩容和性能

```bash
# 查看服务资源使用情况
railway status

# 增加服务副本数
railway service update --replicas 2 --service backend
```

## 故障排除

### 常见问题

1. **构建失败**
   - 检查 Dockerfile 语法
   - 确保所有依赖都在 requirements.txt 中

2. **环境变量问题**
   - 确保所有必需的环境变量都已设置
   - 检查变量名拼写

3. **API连接问题**
   - 检查 CORS_ORIGINS 环境变量
   - 确保后端服务正在运行
   - 验证 NEXT_PUBLIC_API_URL 设置

4. **文件上传失败**
   - 检查文件大小限制 (MAX_FILE_SIZE)
   - 确保上传目录有写权限
   - 检查文件格式是否支持 (.docx)

### 日志分析

```bash
# 实时查看日志
railway logs --service backend --follow

# 查看特定时间段的日志
railway logs --service backend --since 1h
```

## 备份和恢复

### 文件备份

```bash
# 备份上传的文件
railway run --service backend 'tar -czf backup.tar.gz /app/static/uploads /app/static/outputs'

# 下载备份文件
railway run --service backend 'cat backup.tar.gz' > local_backup.tar.gz

# 恢复文件
railway run --service backend 'tar -xzf backup.tar.gz'
```

## 安全最佳实践

1. **API 密钥管理**
   - 使用环境变量存储敏感信息
   - 定期轮换 API 密钥

2. **文件上传安全**
   - 限制文件类型和大小
   - 病毒扫描（如果需要）
   - 使用安全的文件名

3. **HTTPS 配置**
   - Railway 自动提供 HTTPS
   - 强制 HTTPS 重定向

4. **CORS 配置**
   - 仅允许必要的域名
   - 设置适当的 CORS 策略

## 成本优化

1. **服务休眠**
   - 在低使用期间启用服务休眠
   - 使用 `sleepApplication: true` 配置

2. **资源限制**
   - 设置适当的 CPU 和内存限制
   - 监控资源使用情况

3. **优化策略**
   - 使用文件缓存优化重复处理
   - 设置适当的文件清理策略

## 更新和发布

### 更新应用

```bash
# 更新后端
railway up --service backend

# 更新前端
railway up --service frontend

# 同时更新所有服务
railway up
```

### 版本管理

```bash
# 标记版本
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 部署特定版本
railway up --service backend --commit abc123
```

## 联系支持

- Railway 文档: https://docs.railway.app/
- Railway 社区: https://discord.gg/railway
- 项目 Issues: https://github.com/your-repo/issues

---

## 快速开始

如果你是第一次部署，直接运行：

```bash
# 克隆项目
git clone your-repo-url
cd thesis-formatter

# 配置环境
cp .env.example .env
# 编辑 .env 文件

# 一键部署
./deploy.sh deploy
```

部署完成后，你将看到前端和后端的访问地址。
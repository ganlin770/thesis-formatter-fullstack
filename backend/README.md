# 论文格式化FastAPI后端服务

## 项目概述

基于现有的`thesis_formatter_complete`模块创建的FastAPI后端服务，提供论文格式化的Web API接口。

## 项目结构

```
backend/
├── main.py                    # FastAPI应用入口
├── requirements.txt           # 依赖列表
├── Dockerfile                 # Docker配置
├── .env                       # 环境变量配置
├── README.md                  # 项目文档
├── api/
│   ├── __init__.py
│   ├── models.py             # Pydantic数据模型
│   └── routes/
│       ├── __init__.py
│       ├── format.py         # 格式化API路由
│       └── health.py         # 健康检查路由
├── services/
│   ├── __init__.py
│   ├── formatter_service.py  # 格式化服务
│   └── file_service.py       # 文件处理服务
├── utils/
│   ├── __init__.py
│   ├── exceptions.py         # 自定义异常
│   └── logger.py            # 日志配置
├── static/                   # 静态文件目录
│   ├── uploads/             # 上传文件存储
│   └── outputs/             # 格式化输出文件
└── thesis_formatter_complete/ # 现有格式化模块(软链接)
```

## 核心功能

### 1. 文件格式化API

#### 单文件格式化
- **端点**: `POST /api/format`
- **功能**: 上传单个Word文档并进行格式化
- **支持**: 异步处理，进度追踪

#### 批量格式化
- **端点**: `POST /api/format/batch`
- **功能**: 批量处理多个Word文档
- **限制**: 最多10个文件并行处理

#### 任务状态查询
- **端点**: `GET /api/format/status/{task_id}`
- **功能**: 实时查询格式化任务状态和进度

#### 文件下载
- **端点**: `GET /api/format/download/{task_id}`
- **功能**: 下载格式化完成的文档

### 2. 健康检查

#### 基础健康检查
- **端点**: `GET /health`
- **功能**: 服务基本健康状态

#### 详细健康检查
- **端点**: `GET /health/detailed`
- **功能**: 详细系统状态，包括CPU、内存、磁盘使用率

#### 服务就绪检查
- **端点**: `GET /health/ready`
- **功能**: Kubernetes就绪探测

#### 服务存活检查
- **端点**: `GET /health/live`
- **功能**: Kubernetes存活探测

### 3. 服务监控

#### 系统指标
- **端点**: `GET /metrics`
- **功能**: 获取服务监控指标

#### 系统清理
- **端点**: `POST /health/cleanup`
- **功能**: 清理临时文件和过期任务

## 技术特性

### 1. 异步处理
- 使用asyncio实现异步文件处理
- 线程池执行CPU密集型格式化任务
- 支持并发任务处理

### 2. 进度追踪
- 实时任务状态更新
- 详细的进度信息反馈
- 任务取消支持

### 3. 文件安全
- 严格的文件类型验证
- 文件大小限制(50MB)
- 恶意文件检测

### 4. 错误处理
- 全面的异常处理机制
- 详细的错误日志记录
- 友好的错误信息返回

### 5. 日志系统
- 结构化日志记录
- 可配置的日志级别
- 请求追踪和性能监控

## 部署说明

### 1. 环境要求
- Python 3.11+
- FastAPI 0.104.1+
- 依赖库（见requirements.txt）

### 2. 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 运行服务
python main.py
```

### 3. Docker部署
```bash
# 构建镜像
docker build -t thesis-formatter-api .

# 运行容器
docker run -p 8000:8000 thesis-formatter-api
```

### 4. 配置说明
环境变量配置（.env文件）：
- `APP_NAME`: 应用名称
- `DEBUG`: 调试模式
- `LOG_LEVEL`: 日志级别
- `MAX_FILE_SIZE`: 最大文件大小限制
- `MAX_CONCURRENT_TASKS`: 最大并发任务数

## API文档

启动服务后，可通过以下地址访问API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 示例用法

### 1. 单文件格式化
```bash
curl -X POST "http://localhost:8000/api/format" \
  -F "file=@thesis.docx" \
  -F "thesis_info={\"title\":\"论文标题\",\"name\":\"作者姓名\",...}" \
  -F "format_options={\"generate_cover\":true,\"update_toc\":true}"
```

### 2. 查询任务状态
```bash
curl "http://localhost:8000/api/format/status/task_12345678"
```

### 3. 下载格式化文件
```bash
curl "http://localhost:8000/api/format/download/task_12345678" -o formatted.docx
```

## 性能特性

- **并发处理**: 支持5个并发格式化任务
- **异步I/O**: 文件操作使用异步I/O
- **内存优化**: 流式文件处理，避免大文件内存占用
- **任务队列**: 内置任务队列管理
- **自动清理**: 定期清理临时文件和过期任务

## 监控和日志

- **结构化日志**: 使用structlog记录结构化日志
- **性能监控**: 记录API响应时间和系统资源使用
- **错误追踪**: 详细的错误堆栈和上下文信息
- **健康检查**: 多层次的健康检查机制

## 扩展性

- **插件化架构**: 易于扩展新的格式化功能
- **微服务就绪**: 支持容器化部署和服务发现
- **水平扩展**: 支持负载均衡和多实例部署
- **数据库集成**: 预留数据库集成接口

## 安全性

- **文件验证**: 严格的文件类型和内容验证
- **大小限制**: 防止大文件攻击
- **CORS配置**: 可配置的跨域访问控制
- **安全头**: 自动添加安全HTTP头

## 开发状态

- ✅ 基础架构完成
- ✅ API接口实现
- ✅ 文件处理服务
- ✅ 格式化服务集成
- ✅ 健康检查和监控
- ⚠️ 测试覆盖率待提升
- ⚠️ 生产环境优化待完善

## 未来规划

- [ ] 添加数据库支持
- [ ] 实现用户认证
- [ ] 添加任务队列中间件
- [ ] 支持WebSocket实时更新
- [ ] 添加性能分析工具
- [ ] 实现分布式任务处理
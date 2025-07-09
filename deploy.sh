#!/bin/bash

# 论文格式化工具 Railway 部署脚本
# 使用 Railway CLI 进行自动化部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

# 检查依赖
check_dependencies() {
    log "检查依赖..."
    
    # 检查 Railway CLI
    if ! command -v railway &> /dev/null; then
        error "Railway CLI 未安装。请运行: npm install -g @railway/cli"
    fi
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        error "Docker 未安装。请先安装 Docker"
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose 未安装。请先安装 Docker Compose"
    fi
    
    log "依赖检查完成"
}

# 环境配置
setup_environment() {
    log "设置环境配置..."
    
    # 检查 .env 文件
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            log "从 .env.example 复制环境变量"
            cp .env.example .env
            warn "请编辑 .env 文件并设置必要的环境变量"
        else
            warn ".env 文件不存在，将使用默认配置"
        fi
    fi
    
    # 加载环境变量
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
}

# 本地构建测试
local_build() {
    log "执行本地构建测试..."
    
    # 构建前端
    log "构建前端..."
    cd web-frontend
    npm install
    npm run build
    cd ..
    
    # 测试后端
    log "测试后端..."
    cd backend
    pip install -r requirements.txt
    python -m pytest tests/ || warn "后端测试失败，但继续部署"
    cd ..
    
    log "本地构建测试完成"
}

# Docker 构建测试
docker_build() {
    log "执行 Docker 构建测试..."
    
    # 构建前端镜像
    log "构建前端Docker镜像..."
    docker build -t thesis-formatter-frontend ./web-frontend
    
    # 构建后端镜像
    log "构建后端Docker镜像..."
    docker build -t thesis-formatter-backend -f backend/Dockerfile .
    
    log "Docker 构建测试完成"
}

# Railway 登录
railway_login() {
    log "检查 Railway 登录状态..."
    
    if ! railway whoami &> /dev/null; then
        log "需要登录 Railway..."
        railway login
    else
        log "已登录 Railway"
    fi
}

# 创建 Railway 项目
create_railway_project() {
    log "创建 Railway 项目..."
    
    PROJECT_NAME=${1:-"thesis-formatter"}
    
    # 检查项目是否存在
    if railway status &> /dev/null; then
        log "项目已存在，跳过创建"
        return
    fi
    
    # 创建新项目
    railway init --name "$PROJECT_NAME"
    
    log "Railway 项目创建完成"
}

# 使用 railway.json 配置部署
deploy_with_config() {
    log "使用 railway.json 配置部署..."
    
    # 检查 railway.json 是否存在
    if [ ! -f railway.json ]; then
        error "railway.json 配置文件不存在"
    fi
    
    # 使用配置文件部署
    railway up
    
    log "配置部署完成"
}

# 部署后端服务
deploy_backend() {
    log "部署后端服务..."
    
    # 创建后端服务
    railway service create backend
    
    # 设置后端环境变量
    railway variables set \
        ENVIRONMENT=production \
        PORT=8000 \
        CORS_ORIGINS=https://thesis-formatter-frontend.up.railway.app \
        MAX_FILE_SIZE=10485760 \
        UPLOAD_DIR=/app/static/uploads \
        OUTPUT_DIR=/app/static/outputs
    
    # 部署后端
    railway up --service backend
    
    log "后端服务部署完成"
}

# 部署前端服务
deploy_frontend() {
    log "部署前端服务..."
    
    # 获取后端 URL
    BACKEND_URL=$(railway domain --service backend)
    
    # 创建前端服务
    railway service create frontend
    
    # 设置前端环境变量
    railway variables set \
        NODE_ENV=production \
        NEXT_PUBLIC_API_URL="https://$BACKEND_URL" \
        PORT=3000
    
    # 部署前端
    railway up --service frontend
    
    log "前端服务部署完成"
}

# 配置域名
setup_domain() {
    log "配置域名..."
    
    # 获取生成的域名
    FRONTEND_DOMAIN=$(railway domain --service frontend)
    BACKEND_DOMAIN=$(railway domain --service backend)
    
    log "前端域名: https://$FRONTEND_DOMAIN"
    log "后端域名: https://$BACKEND_DOMAIN"
    
    # 如果有自定义域名，在这里配置
    if [ ! -z "$CUSTOM_DOMAIN" ]; then
        log "配置自定义域名: $CUSTOM_DOMAIN"
        railway domain add "$CUSTOM_DOMAIN" --service frontend
    fi
}

# 健康检查
health_check() {
    log "执行健康检查..."
    
    # 检查后端健康状态
    BACKEND_URL=$(railway domain --service backend)
    if curl -f "https://$BACKEND_URL/health" &> /dev/null; then
        log "后端健康检查通过"
    else
        warn "后端健康检查失败"
    fi
    
    # 检查API端点
    if curl -f "https://$BACKEND_URL/api/health" &> /dev/null; then
        log "API端点健康检查通过"
    else
        warn "API端点健康检查失败"
    fi
    
    # 检查前端可访问性
    FRONTEND_URL=$(railway domain --service frontend)
    if curl -f "https://$FRONTEND_URL" &> /dev/null; then
        log "前端健康检查通过"
    else
        warn "前端健康检查失败"
    fi
}

# 显示部署信息
show_deployment_info() {
    log "部署完成！"
    
    FRONTEND_URL=$(railway domain --service frontend)
    BACKEND_URL=$(railway domain --service backend)
    
    echo "=================================="
    echo "部署信息："
    echo "前端地址: https://$FRONTEND_URL"
    echo "后端地址: https://$BACKEND_URL"
    echo "项目名称: $(railway status --json | jq -r '.project.name')"
    echo "环境: $(railway status --json | jq -r '.environment.name')"
    echo "=================================="
}

# 主函数
main() {
    log "开始部署论文格式化工具到 Railway..."
    
    case "${1:-deploy}" in
        "check")
            check_dependencies
            ;;
        "build")
            check_dependencies
            setup_environment
            local_build
            docker_build
            ;;
        "deploy")
            check_dependencies
            setup_environment
            local_build
            docker_build
            railway_login
            create_railway_project
            deploy_with_config
            setup_domain
            health_check
            show_deployment_info
            ;;
        "update")
            railway_login
            deploy_with_config
            health_check
            show_deployment_info
            ;;
        "status")
            railway_login
            railway status
            ;;
        *)
            echo "用法: $0 {check|build|deploy|update|status}"
            echo "  check  - 检查依赖"
            echo "  build  - 本地构建测试"
            echo "  deploy - 完整部署"
            echo "  update - 更新部署"
            echo "  status - 查看状态"
            exit 1
            ;;
    esac
}

# 捕获错误
trap 'error "部署失败，请检查错误信息"' ERR

# 运行主函数
main "$@"
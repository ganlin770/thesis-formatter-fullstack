#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文格式化工具 API 服务器
为前端提供RESTful API接口
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import tempfile
import zipfile
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor

# 导入格式化模块
from main_formatter import MainFormatter

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = '/tmp/uploads'
PROCESSED_FOLDER = '/tmp/processed'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'docx', 'doc'}

# 确保文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """检查文件是否允许上传"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'thesis-formatter-api'
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """上传文件端点"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有找到文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型'}), 400
        
        # 安全的文件名
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        logger.info(f"文件上传成功: {unique_filename}")
        
        return jsonify({
            'message': '文件上传成功',
            'filename': unique_filename,
            'original_name': file.filename,
            'size': os.path.getsize(filepath)
        })
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@app.route('/format', methods=['POST'])
def format_document():
    """格式化文档端点"""
    try:
        data = request.json
        filename = data.get('filename')
        options = data.get('options', {})
        
        if not filename:
            return jsonify({'error': '缺少文件名'}), 400
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(input_path):
            return jsonify({'error': '文件不存在'}), 404
        
        # 创建输出文件路径
        output_filename = f"formatted_{filename}"
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
        
        # 执行格式化
        formatter = MainFormatter()
        
        # 异步处理以提高性能
        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(formatter.format_document, input_path, output_path, options)
            result = future.result(timeout=300)  # 5分钟超时
        
        if result.get('success'):
            logger.info(f"文档格式化成功: {output_filename}")
            return jsonify({
                'message': '格式化成功',
                'output_filename': output_filename,
                'processed_at': datetime.now().isoformat(),
                'details': result.get('details', {})
            })
        else:
            return jsonify({'error': f'格式化失败: {result.get("error", "未知错误")}'}), 500
            
    except Exception as e:
        logger.error(f"文档格式化失败: {str(e)}")
        return jsonify({'error': f'格式化失败: {str(e)}'}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """下载处理后的文件"""
    try:
        safe_filename = secure_filename(filename)
        file_path = os.path.join(app.config['PROCESSED_FOLDER'], safe_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        logger.error(f"文件下载失败: {str(e)}")
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.route('/status/<filename>', methods=['GET'])
def get_file_status(filename):
    """获取文件处理状态"""
    try:
        safe_filename = secure_filename(filename)
        
        # 检查原始文件
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], f"formatted_{safe_filename}")
        
        status = {
            'uploaded': os.path.exists(input_path),
            'processed': os.path.exists(output_path),
            'filename': safe_filename
        }
        
        if status['uploaded']:
            status['upload_time'] = datetime.fromtimestamp(os.path.getctime(input_path)).isoformat()
        
        if status['processed']:
            status['process_time'] = datetime.fromtimestamp(os.path.getctime(output_path)).isoformat()
            status['download_url'] = f"/download/formatted_{safe_filename}"
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"获取文件状态失败: {str(e)}")
        return jsonify({'error': f'获取状态失败: {str(e)}'}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """清理临时文件"""
    try:
        # 清理超过24小时的文件
        cutoff_time = datetime.now().timestamp() - 24 * 3600
        
        cleaned_files = []
        for folder in [app.config['UPLOAD_FOLDER'], app.config['PROCESSED_FOLDER']]:
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.getctime(filepath) < cutoff_time:
                    os.remove(filepath)
                    cleaned_files.append(filename)
        
        return jsonify({
            'message': f'清理了 {len(cleaned_files)} 个文件',
            'cleaned_files': cleaned_files
        })
        
    except Exception as e:
        logger.error(f"清理文件失败: {str(e)}")
        return jsonify({'error': f'清理失败: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"启动论文格式化API服务器，端口: {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
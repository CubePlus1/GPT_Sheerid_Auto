"""
本地邮件接收服务器
用于接收 Cloudflare Worker 转发的邮件，自动提取验证链接
"""

from flask import Flask, request, jsonify
import re
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from collections import deque

app = Flask(__name__)

# 存储最近接收的邮件
recent_emails = deque(maxlen=50)
verification_links = {}
email_lock = threading.Lock()

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / 'email_receiver.log'


def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')


def extract_verification_link(content):
    """从邮件内容提取验证链接"""
    import html
    
    # 匹配 SheerID 验证链接
    patterns = [
        r'href="(https://services\.sheerid\.com/verify/[^"]+emailToken=[^"]+)"',
        r'(https://services\.sheerid\.com/verify/[^\s<>"]+emailToken=\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            link = match.group(1)
            # 解码所有 HTML 实体 (&amp; -> &, &quot; -> ", etc.)
            link = html.unescape(link)
            return link
    
    return None


def extract_email_token(url):
    """从验证链接提取 emailToken"""
    match = re.search(r'emailToken=(\d+)', url)
    return match.group(1) if match else None


@app.route('/', methods=['GET'])
def index():
    """首页 - 显示状态"""
    return jsonify({
        'status': 'running',
        'service': 'SheerID Email Receiver',
        'recent_emails': len(recent_emails),
        'verification_links': len(verification_links),
        'endpoints': {
            'POST /email': 'Receive email from Worker',
            'GET /status': 'Get service status',
            'GET /links': 'Get verification links',
            'GET /emails': 'Get recent emails'
        }
    })


@app.route('/email', methods=['POST'])
def receive_email():
    """接收来自 Worker 的邮件"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # 提取邮件信息
        to_email = data.get('to', '')
        from_email = data.get('from', '')
        subject = data.get('subject', '')
        text = data.get('text', '')
        html = data.get('html', '')
        
        log(f"收到邮件: {from_email} -> {to_email}")
        log(f"主题: {subject}")
        
        # 存储邮件
        email_data = {
            'timestamp': datetime.now().isoformat(),
            'to': to_email,
            'from': from_email,
            'subject': subject,
            'text': text,
            'html': html
        }
        
        with email_lock:
            recent_emails.append(email_data)
        
        # 检查是否是 SheerID 验证邮件
        content = html or text
        
        log(f"检查邮件内容: 长度={len(content)}, 包含sheerid={'sheerid' in content.lower()}")
        
        if 'sheerid' in content.lower() or 'verification' in subject.lower():
            log(f"检测到 SheerID 验证邮件，尝试提取链接...")
            # 提取验证链接
            verification_link = extract_verification_link(content)
            
            if verification_link:
                email_token = extract_email_token(verification_link)
                
                with email_lock:
                    verification_links[to_email] = {
                        'link': verification_link,
                        'token': email_token,
                        'timestamp': datetime.now().isoformat(),
                        'subject': subject
                    }
                
                log(f"✓ 提取到验证链接: emailToken={email_token}")
                log(f"✓ 存储到 verification_links[{to_email}]")
                log(f"✓ 当前存储的邮箱: {list(verification_links.keys())}")
                
                return jsonify({
                    'success': True,
                    'message': 'Verification email received',
                    'has_link': True,
                    'email_token': email_token
                }), 200
        
        return jsonify({
            'success': True,
            'message': 'Email received',
            'has_link': False
        }), 200
        
    except Exception as e:
        log(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    """获取服务状态"""
    return jsonify({
        'status': 'running',
        'recent_emails': len(recent_emails),
        'verification_links': len(verification_links),
        'uptime': 'active'
    })


@app.route('/links', methods=['GET'])
def get_links():
    """获取所有验证链接"""
    email = request.args.get('email')
    
    with email_lock:
        log(f"查询链接: email={email}, 当前存储的邮箱={list(verification_links.keys())}")
        
        if email:
            link_data = verification_links.get(email)
            if link_data:
                log(f"✓ 找到链接: {email} -> token={link_data.get('token')}")
                return jsonify({
                    'email': email,
                    'link': link_data['link'],
                    'token': link_data['token'],
                    'timestamp': link_data['timestamp']
                })
            else:
                log(f"✗ 未找到链接: {email}")
                return jsonify({'error': 'No link found for this email'}), 404
        else:
            log(f"返回所有链接: {len(verification_links)} 个")
            return jsonify(verification_links)


@app.route('/emails', methods=['GET'])
def get_emails():
    """获取最近的邮件"""
    limit = request.args.get('limit', 10, type=int)
    
    with email_lock:
        emails = list(recent_emails)[-limit:]
    
    return jsonify({
        'total': len(emails),
        'emails': emails
    })


@app.route('/clear', methods=['POST'])
def clear_data():
    """清空数据"""
    with email_lock:
        recent_emails.clear()
        verification_links.clear()
    
    log("数据已清空")
    return jsonify({'success': True, 'message': 'Data cleared'})


@app.route('/clear_link', methods=['POST'])
def clear_link():
    """清除指定邮箱的链接（避免重复使用）"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        with email_lock:
            if email in verification_links:
                del verification_links[email]
                log(f"清除链接: {email}")
                return jsonify({'success': True, 'message': f'Link cleared for {email}'})
            else:
                return jsonify({'error': 'No link found for this email'}), 404
    
    except Exception as e:
        log(f"清除链接错误: {str(e)}")
        return jsonify({'error': str(e)}), 500


def run_server(host='0.0.0.0', port=5000):
    """启动服务器"""
    log(f"启动邮件接收服务器: http://{host}:{port}")
    log("等待接收来自 Worker 的邮件...")
    log("-" * 50)
    
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    import sys
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    
    print()
    print("=" * 60)
    print("  SheerID 邮件接收服务器")
    print("=" * 60)
    print()
    print(f"  监听端口: {port}")
    print(f"  接收端点: http://localhost:{port}/email")
    print(f"  状态查询: http://localhost:{port}/status")
    print(f"  查看链接: http://localhost:{port}/links")
    print()
    print("  配置 Cloudflare Worker 发送邮件到此地址")
    print()
    print("=" * 60)
    print()
    
    run_server(port=port)

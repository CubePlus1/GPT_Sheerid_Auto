#!/usr/bin/env python3
"""
测试邮件接收服务器
发送一个模拟的 SheerID 验证邮件
"""

import requests
import json

# 模拟的 SheerID 验证邮件
test_email = {
    "to": "verify@test.com",
    "from": "noreply@sheerid.com",
    "subject": "SheerID: Finish Verifying Your Eligibility",
    "text": "Please verify your email",
    "html": """
    <html>
    <body>
        <h2>You're almost there!</h2>
        <p>Click the link below to verify your email:</p>
        <a href="https://services.sheerid.com/verify/690415d58971e73ca187d8c9/?verificationId=67935afd67d8ca2ef9c5fbff&emailToken=1234567890">
            Finish Verifying
        </a>
    </body>
    </html>
    """
}

def test_email_receiver():
    """测试邮件接收服务"""
    print("=" * 60)
    print("测试邮件接收服务器")
    print("=" * 60)
    print()
    
    # 测试状态接口
    print("1. 测试状态接口...")
    try:
        resp = requests.get('http://localhost:5000/status', timeout=5)
        if resp.status_code == 200:
            print(f"   ✓ 状态接口正常")
            print(f"   响应: {resp.json()}")
        else:
            print(f"   ✗ 状态码: {resp.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
        print()
        print("请先启动邮件接收服务器:")
        print("python email_receiver.py 5000")
        return False
    
    print()
    
    # 发送测试邮件
    print("2. 发送测试验证邮件...")
    try:
        resp = requests.post(
            'http://localhost:5000/email',
            json=test_email,
            timeout=5
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✓ 邮件发送成功")
            print(f"   响应: {data}")
            
            if data.get('has_link'):
                print(f"   ✓ 验证链接已提取")
                print(f"   emailToken: {data.get('email_token')}")
        else:
            print(f"   ✗ 状态码: {resp.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ 发送失败: {e}")
        return False
    
    print()
    
    # 查询验证链接
    print("3. 查询验证链接...")
    try:
        resp = requests.get(
            'http://localhost:5000/links',
            params={'email': test_email['to']},
            timeout=5
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✓ 查询成功")
            print(f"   验证链接: {data.get('link', '')[:80]}...")
            print(f"   Token: {data.get('token')}")
        else:
            print(f"   ✗ 状态码: {resp.status_code}")
    except Exception as e:
        print(f"   ✗ 查询失败: {e}")
    
    print()
    
    # 查看所有邮件
    print("4. 查看最近邮件...")
    try:
        resp = requests.get('http://localhost:5000/emails?limit=5', timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✓ 邮件总数: {data.get('total')}")
            for email in data.get('emails', []):
                print(f"   - {email['from']} -> {email['to']}")
                print(f"     主题: {email['subject']}")
        else:
            print(f"   ✗ 状态码: {resp.status_code}")
    except Exception as e:
        print(f"   ✗ 查询失败: {e}")
    
    print()
    print("=" * 60)
    print("✓ 测试完成！")
    print()
    print("现在可以:")
    print("1. 访问 http://localhost:5000 查看服务状态")
    print("2. 配置 Cloudflare Worker 发送邮件到此服务")
    print("3. 运行 python main.py 开始验证")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    test_email_receiver()

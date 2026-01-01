#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试本地代理连接

用法: python test_local_proxy.py
"""

import requests

# 🔧 根据你的截图，基础端口是 38491
PROXY_PORT = 38491

# 配置代理
proxies = {
    'http': f'http://127.0.0.1:{PROXY_PORT}',
    'https': f'http://127.0.0.1:{PROXY_PORT}'
}

# 如果是 SOCKS5 代理，使用：
# proxies = {
#     'http': f'socks5://127.0.0.1:{PROXY_PORT}',
#     'https': f'socks5://127.0.0.1:{PROXY_PORT}'
# }

print("=" * 60)
print("本地代理测试工具")
print("=" * 60)
print(f"\n代理配置:")
print(f"  HTTP:  {proxies['http']}")
print(f"  HTTPS: {proxies['https']}")

# 测试 1: 获取 IP 地址
print("\n" + "=" * 60)
print("测试 1: 检查代理 IP")
print("=" * 60)

try:
    # 不使用代理获取本地 IP
    print("\n[直连] 获取本地 IP...")
    response = requests.get('https://api.ipify.org?format=json', timeout=10)
    local_ip = response.json()['ip']
    print(f"✅ 本地 IP: {local_ip}")
except Exception as e:
    print(f"❌ 获取本地 IP 失败: {e}")
    local_ip = None

try:
    # 使用代理获取 IP
    print("\n[代理] 通过代理获取 IP...")
    response = requests.get('https://api.ipify.org?format=json', 
                          proxies=proxies, 
                          timeout=10)
    proxy_ip = response.json()['ip']
    print(f"✅ 代理 IP: {proxy_ip}")
    
    if local_ip and proxy_ip != local_ip:
        print(f"✅ IP 已切换（代理工作正常）")
    else:
        print(f"⚠️  IP 未切换（可能使用直连）")
        
except requests.exceptions.ProxyError:
    print(f"❌ 代理连接失败")
    print(f"\n可能原因:")
    print(f"  1. 代理软件未运行")
    print(f"  2. 端口号不正确（检查是否为 {PROXY_PORT}）")
    print(f"  3. 代理协议不匹配（HTTP vs SOCKS5）")
except requests.exceptions.Timeout:
    print(f"❌ 连接超时")
except Exception as e:
    print(f"❌ 错误: {e}")

# 测试 2: 访问 Google（测试国际连接）
print("\n" + "=" * 60)
print("测试 2: 访问国际网站")
print("=" * 60)

test_urls = [
    ('Google', 'https://www.google.com'),
    ('GitHub', 'https://github.com'),
]

for name, url in test_urls:
    try:
        print(f"\n[{name}] 访问 {url}")
        response = requests.get(url, proxies=proxies, timeout=10, allow_redirects=True)
        print(f"✅ 成功（状态码: {response.status_code}）")
    except Exception as e:
        print(f"❌ 失败: {type(e).__name__}")

# 测试 3: SheerID API（实际使用场景）
print("\n" + "=" * 60)
print("测试 3: SheerID API 连接")
print("=" * 60)

try:
    print("\n访问 https://services.sheerid.com")
    response = requests.get('https://services.sheerid.com', 
                          proxies=proxies, 
                          timeout=10,
                          allow_redirects=True)
    print(f"✅ SheerID 连接成功（状态码: {response.status_code}）")
except Exception as e:
    print(f"❌ SheerID 连接失败: {e}")

# 总结
print("\n" + "=" * 60)
print("测试总结")
print("=" * 60)
print(f"\n如果所有测试通过，可以在 proxy.txt 中添加:")
print(f"  127.0.0.1:{PROXY_PORT}")
print(f"\n然后运行: python main.py")
print("=" * 60)

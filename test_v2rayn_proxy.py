#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v2rayN 代理测试工具

测试 v2rayN 的多个端口配置
"""

import requests
import time

# v2rayN 常用端口配置
V2RAYN_PORTS = {
    'HTTP': 10809,
    'SOCKS5': 10808,
}

def test_proxy_port(port, protocol='http'):
    """测试单个代理端口"""
    if protocol.lower() == 'socks5':
        proxy_url = f'socks5://127.0.0.1:{port}'
    else:
        proxy_url = f'http://127.0.0.1:{port}'
    
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    print(f"\n{'='*60}")
    print(f"测试端口: {port} ({protocol.upper()})")
    print(f"{'='*60}")
    print(f"代理配置: {proxy_url}")
    
    try:
        # 测试连接
        print("\n[1/3] 测试连接...")
        start = time.time()
        response = requests.get('https://www.google.com', 
                              proxies=proxies, 
                              timeout=10,
                              allow_redirects=False)
        latency = int((time.time() - start) * 1000)
        print(f"✅ 连接成功 (延迟: {latency}ms, 状态: {response.status_code})")
        
        # 获取 IP
        print("\n[2/3] 获取代理 IP...")
        response = requests.get('https://api.ipify.org?format=json', 
                              proxies=proxies, 
                              timeout=10)
        proxy_ip = response.json()['ip']
        print(f"✅ 代理 IP: {proxy_ip}")
        
        # 测试 SheerID
        print("\n[3/3] 测试 SheerID API...")
        response = requests.get('https://services.sheerid.com', 
                              proxies=proxies, 
                              timeout=10,
                              allow_redirects=True)
        print(f"✅ SheerID 连接成功 (状态: {response.status_code})")
        
        print(f"\n✅ 端口 {port} 工作正常")
        return True
        
    except requests.exceptions.ProxyError:
        print(f"❌ 代理连接失败")
        print(f"   可能原因:")
        print(f"   - v2rayN 未运行")
        print(f"   - 端口号错误")
        print(f"   - 协议类型错误 (HTTP vs SOCKS5)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ 连接超时")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    """主测试流程"""
    print("=" * 60)
    print("v2rayN 代理测试工具")
    print("=" * 60)
    
    # 先测试直连
    print("\n[直连] 测试本地 IP...")
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        local_ip = response.json()['ip']
        print(f"✅ 本地 IP: {local_ip}")
    except:
        print(f"⚠️  无法获取本地 IP")
        local_ip = None
    
    # 测试 v2rayN 端口
    results = {}
    
    for name, port in V2RAYN_PORTS.items():
        protocol = 'socks5' if name == 'SOCKS5' else 'http'
        results[f"{name} ({port})"] = test_proxy_port(port, protocol)
    
    # 测试自定义端口（如果有）
    custom_ports = [10810, 10811, 7890, 38491]
    print(f"\n{'='*60}")
    print("测试其他可能的端口...")
    print(f"{'='*60}")
    
    for port in custom_ports:
        print(f"\n尝试端口 {port}...")
        try:
            proxy_url = f'http://127.0.0.1:{port}'
            proxies = {'http': proxy_url, 'https': proxy_url}
            response = requests.get('https://www.google.com', 
                                  proxies=proxies, 
                                  timeout=5,
                                  allow_redirects=False)
            print(f"✅ 端口 {port} 可用")
            results[f"Port {port}"] = True
        except:
            pass
    
    # 总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    
    working_ports = [k for k, v in results.items() if v]
    
    if working_ports:
        print(f"\n✅ 可用的代理端口:")
        for port in working_ports:
            print(f"   - {port}")
        
        print(f"\n📝 推荐配置到 proxy.txt:")
        print(f"   # v2rayN HTTP 代理（推荐）")
        print(f"   127.0.0.1:{V2RAYN_PORTS['HTTP']}")
        print(f"")
        print(f"   # 或 SOCKS5 代理")
        print(f"   # socks5://127.0.0.1:{V2RAYN_PORTS['SOCKS5']}")
    else:
        print(f"\n❌ 未检测到可用代理")
        print(f"\n排查建议:")
        print(f"1. 确认 v2rayN 正在运行")
        print(f"2. 检查 v2rayN 设置 → 参数设置 → 本地监听端口")
        print(f"3. 确认已选择一个服务器并启用代理")
        print(f"4. 尝试重启 v2rayN")
    
    print(f"{'='*60}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试已取消")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

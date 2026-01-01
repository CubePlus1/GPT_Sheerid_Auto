#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理测试脚本 - 验证代理配置是否正确工作

用法:
    python test_proxy.py

功能:
    1. 测试 proxy.txt 文件是否存在
    2. 验证代理格式是否正确
    3. 测试代理连通性
    4. 显示代理 IP 地址
"""

import sys
from pathlib import Path

# 添加父目录到路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# 导入主程序中的代理函数
from main import load_random_proxy, get_proxy_dict, PROXY_FILE

try:
    import requests
except ImportError:
    print("❌ 错误: 需要安装 requests 库")
    print("   运行: pip install requests")
    sys.exit(1)


def test_proxy_file():
    """测试代理文件是否存在"""
    print("=" * 60)
    print("测试 1: 检查代理文件")
    print("=" * 60)
    
    if not PROXY_FILE.exists():
        print(f"❌ 代理文件不存在: {PROXY_FILE}")
        print(f"   创建文件: copy proxy.example.txt proxy.txt")
        return False
    
    print(f"✅ 代理文件存在: {PROXY_FILE}")
    
    try:
        content = PROXY_FILE.read_text(encoding='utf-8')
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
        
        if not lines:
            print(f"⚠️  代理文件为空，需要添加代理配置")
            return False
        
        print(f"✅ 找到 {len(lines)} 个代理配置")
        print(f"\n代理列表:")
        for i, line in enumerate(lines, 1):
            # 隐藏密码部分
            if ':' in line:
                parts = line.split(':')
                if len(parts) >= 3:
                    display = f"{parts[0]}:{parts[1]}:***:***"
                else:
                    display = line
            else:
                display = line
            print(f"  {i}. {display}")
        
        return True
    except Exception as e:
        print(f"❌ 读取代理文件失败: {e}")
        return False


def test_proxy_parsing():
    """测试代理解析"""
    print("\n" + "=" * 60)
    print("测试 2: 代理格式解析")
    print("=" * 60)
    
    proxy = load_random_proxy(PROXY_FILE)
    if not proxy:
        print("❌ 无法加载代理")
        return None
    
    print("✅ 代理解析成功")
    print(f"   格式: {proxy}")
    
    proxy_dict = get_proxy_dict(proxy)
    if not proxy_dict:
        print("❌ 无法生成代理字典")
        return None
    
    print("✅ 代理字典生成成功")
    
    # 隐藏密码
    display_dict = {}
    for key, value in proxy_dict.items():
        if '@' in value:
            # socks5://user:pass@ip:port -> socks5://***:***@ip:port
            protocol, rest = value.split('://', 1)
            if '@' in rest:
                auth, server = rest.split('@', 1)
                display_dict[key] = f"{protocol}://***:***@{server}"
            else:
                display_dict[key] = value
        else:
            display_dict[key] = value
    
    print(f"   http:  {display_dict.get('http', 'N/A')}")
    print(f"   https: {display_dict.get('https', 'N/A')}")
    
    return proxy_dict


def test_proxy_connection(proxy_dict):
    """测试代理连通性"""
    print("\n" + "=" * 60)
    print("测试 3: 代理连通性")
    print("=" * 60)
    
    test_url = 'https://httpbin.org/ip'
    print(f"测试 URL: {test_url}")
    print("等待响应...")
    
    try:
        # 测试直连
        print("\n[直连测试]")
        response = requests.get(test_url, timeout=10)
        direct_ip = response.json()['origin']
        print(f"✅ 直连成功")
        print(f"   本地 IP: {direct_ip}")
    except Exception as e:
        print(f"❌ 直连失败: {e}")
        direct_ip = None
    
    # 测试代理
    print("\n[代理测试]")
    try:
        response = requests.get(test_url, proxies=proxy_dict, timeout=15)
        proxy_ip = response.json()['origin']
        print(f"✅ 代理连接成功")
        print(f"   代理 IP: {proxy_ip}")
        
        if direct_ip and proxy_ip != direct_ip:
            print(f"✅ IP 已切换（代理工作正常）")
        elif direct_ip and proxy_ip == direct_ip:
            print(f"⚠️  警告: 代理 IP 与本地 IP 相同")
        
        return True
    except requests.exceptions.ProxyError as e:
        print(f"❌ 代理连接失败: 代理错误")
        print(f"   可能原因:")
        print(f"   - 代理服务器无响应")
        print(f"   - 代理地址或端口错误")
        print(f"   - 用户名密码错误")
        return False
    except requests.exceptions.ConnectTimeout:
        print(f"❌ 代理连接超时")
        print(f"   可能原因:")
        print(f"   - 代理服务器太慢")
        print(f"   - 网络连接问题")
        return False
    except Exception as e:
        print(f"❌ 代理连接失败: {type(e).__name__}")
        print(f"   错误: {e}")
        return False


def test_https_connection(proxy_dict):
    """测试 HTTPS 连接"""
    print("\n" + "=" * 60)
    print("测试 4: HTTPS 连接")
    print("=" * 60)
    
    test_url = 'https://services.sheerid.com'
    print(f"测试 URL: {test_url}")
    
    try:
        response = requests.get(test_url, proxies=proxy_dict, timeout=15, allow_redirects=True)
        print(f"✅ HTTPS 连接成功")
        print(f"   状态码: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ HTTPS 连接失败: {e}")
        return False


def main():
    """主测试流程"""
    print("\n" + "🔍 代理配置测试工具" + "\n")
    
    # 测试 1: 文件检查
    if not test_proxy_file():
        print("\n" + "=" * 60)
        print("测试中止: 代理文件不存在或为空")
        print("=" * 60)
        print("\n请按照以下步骤配置代理:")
        print("1. 创建 proxy.txt 文件")
        print("2. 添加代理配置（每行一个）")
        print("3. 格式示例: 192.168.1.100:1080:user:pass")
        print("\n详细说明: 查看 PROXY_SETUP.md")
        return
    
    # 测试 2: 解析代理
    proxy_dict = test_proxy_parsing()
    if not proxy_dict:
        print("\n" + "=" * 60)
        print("测试中止: 代理解析失败")
        print("=" * 60)
        return
    
    # 测试 3: 连通性
    connection_ok = test_proxy_connection(proxy_dict)
    
    # 测试 4: HTTPS
    if connection_ok:
        https_ok = test_https_connection(proxy_dict)
    else:
        https_ok = False
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if connection_ok and https_ok:
        print("✅ 所有测试通过！代理配置正确")
        print("\n可以运行主程序:")
        print("   python main.py")
    else:
        print("❌ 部分测试失败")
        print("\n排查建议:")
        print("1. 检查代理格式是否正确")
        print("2. 验证代理服务器是否可用")
        print("3. 确认用户名密码正确")
        print("4. 尝试其他代理")
        print("\n详细帮助: 查看 PROXY_SETUP.md")
    
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试已取消")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

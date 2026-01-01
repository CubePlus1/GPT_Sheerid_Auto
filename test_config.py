#!/usr/bin/env python3
"""
配置测试脚本
用于验证 Mailpit、config.json 和 Docker 配置是否正常
"""

import json
import requests
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / 'config.json'


def test_config_file():
    """测试配置文件"""
    print("=" * 60)
    print("1. 检查配置文件")
    print("=" * 60)
    
    if not CONFIG_FILE.exists():
        print("❌ config.json 不存在")
        print("   请复制 config.example.json 为 config.json")
        return False
    
    print("✅ config.json 存在")
    
    try:
        config = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"❌ 配置文件格式错误: {e}")
        return False
    
    print("✅ 配置文件格式正确")
    
    # 检查 accessToken
    if not config.get('accessToken') or '你的ChatGPT' in config.get('accessToken', ''):
        print("⚠️  accessToken 未配置")
        print("   请访问 https://chatgpt.com/api/auth/session 获取")
    else:
        print(f"✅ accessToken 已配置 (长度: {len(config['accessToken'])} 字符)")
    
    # 检查邮箱配置
    email = config.get('email', {})
    email_type = email.get('type', '').lower()
    
    print(f"\n邮箱类型: {email_type}")
    
    if email_type == 'mailpit':
        print("✅ 使用 Mailpit 本地邮箱")
        return test_mailpit(email)
    elif email_type == 'imap':
        print("✅ 使用 IMAP 邮箱")
        return True
    elif email_type == 'cloudmail':
        print("✅ 使用 CloudMail 邮箱")
        return True
    else:
        print(f"❌ 不支持的邮箱类型: {email_type}")
        return False


def test_mailpit(email_config):
    """测试 Mailpit 连接"""
    print("\n" + "=" * 60)
    print("2. 检查 Mailpit 服务")
    print("=" * 60)
    
    api_url = email_config.get('api_url', 'http://localhost:8025').rstrip('/')
    email_address = email_config.get('email_address', '')
    
    print(f"API URL: {api_url}")
    print(f"邮箱地址: {email_address}")
    
    # 测试 API 连接
    try:
        resp = requests.get(f'{api_url}/api/v1/info', timeout=5)
        if resp.status_code == 200:
            print("✅ Mailpit API 连接成功")
            
            # 获取版本信息
            info = resp.json()
            print(f"   版本: {info.get('version', 'unknown')}")
        else:
            print(f"❌ Mailpit API 返回错误: {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 Mailpit")
        print("   请确保 Docker 容器正在运行:")
        print("   docker-compose up -d")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False
    
    # 测试获取邮件列表
    try:
        resp = requests.get(f'{api_url}/api/v1/messages', timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            total = data.get('total', 0)
            print(f"✅ 邮件列表 API 正常 (当前邮件数: {total})")
        else:
            print(f"⚠️  邮件列表 API 返回: {resp.status_code}")
    except Exception as e:
        print(f"⚠️  邮件列表测试失败: {e}")
    
    # 测试 Web 界面
    try:
        web_url = api_url.replace('/api/v1', '')
        resp = requests.get(web_url, timeout=5)
        if resp.status_code == 200:
            print(f"✅ Web 界面可访问: {web_url}")
        else:
            print(f"⚠️  Web 界面返回: {resp.status_code}")
    except Exception as e:
        print(f"⚠️  Web 界面测试失败: {e}")
    
    return True


def test_docker():
    """测试 Docker 环境"""
    print("\n" + "=" * 60)
    print("3. 检查 Docker 环境")
    print("=" * 60)
    
    import subprocess
    
    # 检查 Docker 是否安装
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            print(f"✅ Docker 已安装: {result.stdout.strip()}")
        else:
            print("❌ Docker 未正确安装")
            return False
    except FileNotFoundError:
        print("❌ Docker 未安装")
        print("   请访问 https://www.docker.com/get-started 下载安装")
        return False
    except Exception as e:
        print(f"❌ Docker 检查失败: {e}")
        return False
    
    # 检查容器状态
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=mail-server', '--format', '{{.Status}}'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            status = result.stdout.strip()
            if 'Up' in status:
                print(f"✅ Mailpit 容器运行中: {status}")
            else:
                print(f"⚠️  容器状态: {status}")
        else:
            print("⚠️  Mailpit 容器未运行")
            print("   启动容器: docker-compose up -d")
            return False
    except Exception as e:
        print(f"⚠️  容器状态检查失败: {e}")
    
    return True


def test_dependencies():
    """测试 Python 依赖"""
    print("\n" + "=" * 60)
    print("4. 检查 Python 依赖")
    print("=" * 60)
    
    packages = ['requests']
    optional_packages = ['requests_go']
    
    all_ok = True
    
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"✅ {pkg} 已安装")
        except ImportError:
            print(f"❌ {pkg} 未安装")
            print(f"   安装: pip install {pkg}")
            all_ok = False
    
    for pkg in optional_packages:
        try:
            __import__(pkg)
            print(f"✅ {pkg} 已安装 (可选)")
        except ImportError:
            print(f"⚠️  {pkg} 未安装 (可选，用于 TLS 指纹模拟)")
    
    return all_ok


def main():
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "GPT SheerID Auto - 配置测试" + " " * 20 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    results = []
    
    # 测试配置文件和邮箱
    results.append(("配置文件", test_config_file()))
    
    # 如果使用 Mailpit，测试 Docker
    try:
        config = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        if config.get('email', {}).get('type', '').lower() == 'mailpit':
            results.append(("Docker 环境", test_docker()))
    except:
        pass
    
    # 测试 Python 依赖
    results.append(("Python 依赖", test_dependencies()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    all_pass = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if not result:
            all_pass = False
    
    print()
    if all_pass:
        print("🎉 所有测试通过！可以运行 python main.py")
    else:
        print("⚠️  部分测试未通过，请根据提示修复问题")
    
    print()
    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())

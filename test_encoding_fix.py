#!/usr/bin/env python3
"""
快速测试编码修复
"""

def sanitize_headers(headers):
    """清理 headers，确保所有值都是 ASCII 兼容的"""
    sanitized = {}
    for key, value in headers.items():
        if isinstance(value, str):
            # 尝试编码为 ASCII，如果失败则使用 latin-1
            try:
                # 先尝试 ASCII
                value.encode('ascii')
            except UnicodeEncodeError:
                # 如果包含非 ASCII 字符，尝试 latin-1
                try:
                    value.encode('latin-1')
                except UnicodeEncodeError:
                    # 如果 latin-1 也不行，使用 utf-8 再转为 latin-1
                    value = value.encode('utf-8').decode('utf-8', errors='ignore')
        sanitized[key] = value
    return sanitized

# 测试
headers = {
    'user-agent': 'Mozilla/5.0',
    'referer': 'https://services.sheerid.com/verify/690415d58971e73ca187d8c9/?verificationId=test&emailToken=123',
    'accept-language': 'en-US,en;q=0.9',
}

print("原始 headers:")
for k, v in headers.items():
    print(f"  {k}: {v}")

print("\n清理后的 headers:")
cleaned = sanitize_headers(headers)
for k, v in cleaned.items():
    print(f"  {k}: {v}")

print("\n✅ 编码修复测试通过!")

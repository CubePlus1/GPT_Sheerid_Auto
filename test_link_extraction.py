#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试验证链接提取和HTML实体解码

用于验证链接提取功能是否正确处理HTML实体编码
"""

import re
import html

def extract_verification_link(content):
    """从邮件内容提取验证链接"""
    # 尝试从 href 属性提取
    match = re.search(r'href="(https://services\.sheerid\.com/verify/[^"]+emailToken=[^"]+)"', content)
    if match:
        link = match.group(1)
        # 解码 HTML 实体 (&amp; -> &, &quot; -> ", etc.)
        link = html.unescape(link)
        return link

    # 尝试直接匹配 URL
    match = re.search(r'https://services\.sheerid\.com/verify/[^\s<>"]+emailToken=\d+', content)
    if match:
        link = match.group(0)
        # 解码 HTML 实体
        link = html.unescape(link)
        return link

    return None


def test_link_extraction():
    """测试链接提取"""
    
    # 测试用例 1: 用户提供的HTML（带有 &amp;）
    test_html_1 = '''<a style="display:inline-block; background:#011851; color:#ffffff; font-family:Helvetica,arial,sans-serif; font-size:1rem; font-weight:bold; line-height:1.25rem; margin:0; text-decoration:none; text-transform:none; padding:10px 25px; border-radius:40px" data-auth="NotApplicable" rel="noopener noreferrer" target="_blank" href="https://services.sheerid.com/verify/690415d58971e73ca187d8c9/?verificationId=6950a9fc12fb296cf476b4f0&amp;emailToken=160160" data-linkindex="0" title="https://services.sheerid.com/verify/690415d58971e73ca187d8c9/?verificationId=6950a9fc12fb296cf476b4f0&amp;emailToken=160160">Finish Verifying </a>'''
    
    # 测试用例 2: 正常的链接（没有 &amp;）
    test_html_2 = '''<a href="https://services.sheerid.com/verify/690415d58971e73ca187d8c9/?verificationId=6950a9fc12fb296cf476b4f0&emailToken=160160">Verify</a>'''
    
    # 测试用例 3: 纯文本链接
    test_html_3 = '''Please click: https://services.sheerid.com/verify/690415d58971e73ca187d8c9/?verificationId=6950a9fc12fb296cf476b4f0&emailToken=160160'''
    
    # 测试用例 4: 多个 HTML 实体
    test_html_4 = '''<a href="https://services.sheerid.com/verify/690415d58971e73ca187d8c9/?verificationId=6950a9fc12fb296cf476b4f0&amp;emailToken=160160&amp;foo=bar">Link</a>'''
    
    print("=" * 70)
    print("验证链接提取测试")
    print("=" * 70)
    
    test_cases = [
        ("HTML with &amp; (用户问题)", test_html_1),
        ("正常HTML链接", test_html_2),
        ("纯文本链接", test_html_3),
        ("多个HTML实体", test_html_4),
    ]
    
    expected_link = "https://services.sheerid.com/verify/690415d58971e73ca187d8c9/?verificationId=6950a9fc12fb296cf476b4f0&emailToken=160160"
    
    all_passed = True
    
    for i, (name, html_content) in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {name}")
        print("-" * 70)
        
        extracted = extract_verification_link(html_content)
        
        if extracted:
            print(f"✅ 提取成功")
            print(f"   提取的链接: {extracted[:80]}...")
            
            # 检查是否包含正确的参数分隔符
            if '&amp;' in extracted:
                print(f"❌ 错误: 链接包含未解码的 &amp;")
                all_passed = False
            elif '&' in extracted and 'emailToken=' in extracted:
                print(f"✅ 正确: HTML实体已解码")
                
                # 验证链接格式
                if 'verificationId=' in extracted and 'emailToken=' in extracted:
                    print(f"✅ 链接格式正确")
                else:
                    print(f"❌ 警告: 链接可能不完整")
                    all_passed = False
            else:
                print(f"⚠️  注意: 链接不包含 & 分隔符")
        else:
            print(f"❌ 提取失败")
            all_passed = False
    
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    if all_passed:
        print("✅ 所有测试通过！链接提取功能正常工作")
        print("\n可以放心运行主程序:")
        print("   cd src")
        print("   python main.py")
    else:
        print("❌ 部分测试失败，需要检查代码")
    
    print("=" * 70)
    
    # 显示实际提取的链接供手动验证
    print("\n手动验证:")
    print("-" * 70)
    link = extract_verification_link(test_html_1)
    if link:
        print(f"提取的完整链接:\n{link}")
        print(f"\n验证参数:")
        
        # 提取参数
        if '?' in link:
            params = link.split('?')[1]
            for param in params.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    print(f"   {key} = {value}")


if __name__ == '__main__':
    try:
        test_link_extraction()
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

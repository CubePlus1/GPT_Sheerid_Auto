# 浏览器自动化使用指南

## 📌 功能说明

使用 Selenium 模拟人类在 ChatGPT 页面上点击"验证资格"按钮，避免直接调用 API 导致的 429 限流问题。

## 🔧 安装依赖

```bash
pip install selenium
```

**下载 ChromeDriver：**
1. 访问：https://googlechromelabs.github.io/chrome-for-testing/
2. 下载与您的 Chrome 版本匹配的 ChromeDriver
3. 将 `chromedriver.exe` 放到 Python Scripts 目录或系统 PATH

或使用自动安装：
```bash
pip install webdriver-manager
```

## 📖 使用方法

### 1. 单独测试

```bash
python browser_automation.py
```

这将：
- ✓ 启动 Chrome 浏览器（显示窗口）
- ✓ 注入您的 accessToken
- ✓ 访问 https://chatgpt.com/veterans-claim
- ✓ 点击"验证资格"按钮
- ✓ 提取 verificationId

### 2. 集成到主程序

在 `main.py` 中替换 `create_verification()` 函数：

```python
from browser_automation import ChatGPTAutomation

def create_verification(record, headers):
    """使用浏览器自动化创建验证"""
    
    # 从 headers 中提取 accessToken
    auth = headers.get('Authorization', '')
    access_token = auth.replace('Bearer ', '').strip()
    
    if not access_token:
        return {'success': False, 'error': '未找到 accessToken'}
    
    print("  [浏览器] 启动自动化...")
    
    automation = ChatGPTAutomation(access_token, headless=True)
    
    try:
        result = automation.trigger_verification()
        
        if result.get('success'):
            verification_id = result.get('verification_id')
            print(f"  ✓ verificationId: {verification_id}")
            
            return {
                'verificationId': verification_id,
                'currentStep': 'pending'
            }
        else:
            print(f"  ✗ 失败: {result.get('message')}")
            return {'success': False, 'error': result.get('message')}
            
    finally:
        automation.close()
```

## ⚙️ 配置选项

### 显示/隐藏浏览器窗口

```python
# 显示窗口（调试时推荐）
automation = ChatGPTAutomation(access_token, headless=False)

# 无头模式（生产环境推荐）
automation = ChatGPTAutomation(access_token, headless=True)
```

### 自定义等待时间

修改 `browser_automation.py` 中的 `time.sleep()` 值：
- 注入 token 后：`time.sleep(2)` → 可改为 1-3 秒
- 页面加载：`time.sleep(3)` → 可改为 2-5 秒
- 点击按钮后：`time.sleep(3)` → 可改为 2-5 秒

## 🐛 常见问题

### 1. ChromeDriver 版本不匹配

**错误：** `session not created: This version of ChromeDriver only supports Chrome version XX`

**解决：**
```bash
# 方法 1：自动管理（推荐）
pip install webdriver-manager

# 然后修改 browser_automation.py
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

self.driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
```

### 2. 未找到验证按钮

**可能原因：**
- ChatGPT 页面改版，按钮选择器失效
- accessToken 无效或过期
- 页面加载不完整

**调试方法：**
1. 设置 `headless=False` 查看实际页面
2. 检查打印的页面源代码
3. 手动访问 https://chatgpt.com/veterans-claim 查看实际 HTML

### 3. 无法提取 verificationId

**可能原因：**
- 点击后未跳转到 SheerID 页面
- verificationId 在其他位置（如 POST 请求体）

**解决：**
1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 点击验证按钮
4. 查看网络请求中的 verificationId 位置
5. 更新 `extract_verification_id()` 函数

## 🎯 优势

✅ **避免 429 限流** - 模拟真实用户行为  
✅ **更真实** - 与人工点击无差别  
✅ **灵活** - 可适配页面改版  
✅ **可视化** - 可观察验证流程  

## ⚠️ 注意事项

1. **速度较慢**：启动浏览器需要 3-5 秒
2. **资源消耗**：Chrome 占用 200-500MB 内存
3. **稳定性**：依赖页面结构，改版可能失效
4. **并发限制**：不建议同时运行多个浏览器实例

## 📊 性能对比

| 方式 | 速度 | 资源 | 稳定性 | 限流风险 |
|-----|------|------|--------|---------|
| 直接 API | ⚡ 快 | 💾 低 | ✅ 高 | ⚠️ 高 |
| 浏览器自动化 | 🐌 慢 | 💾 高 | ⚠️ 中 | ✅ 低 |

## 🔄 回退方案

如果浏览器自动化失败，可以回退到原 API 方式：

```python
def create_verification(record, headers):
    # 先尝试浏览器自动化
    result = try_browser_automation(record, headers)
    
    if not result.get('success'):
        print("  → 浏览器方式失败，回退到 API")
        result = try_api_method(record, headers)
    
    return result
```

## 📝 下一步

1. 测试自动化脚本：`python browser_automation.py`
2. 检查是否成功提取 verificationId
3. 决定是否集成到主程序
4. 根据实际情况调整等待时间和选择器

# 🎯 Webhook 模式完整指南

## ✨ 概述

Webhook 模式是**最简单、最强大**的邮件接收方案！

- ✅ **无需 Docker** - 只需 Python
- ✅ **无需 Mailpit** - 直接 HTTP 接收
- ✅ **实时处理** - 立即提取验证链接
- ✅ **灵活扩展** - 可集成通知服务

---

## 📦 快速开始

### 1. 安装依赖

```bash
pip install flask
```

### 2. 启动邮件接收服务

**方式一：直接运行**

```bash
python email_receiver.py
```

**方式二：使用批处理（Windows）**

双击 `start_webhook.bat`

### 3. 配置 config.json

```json
{
    "accessToken": "你的ChatGPT accessToken",
    "programId": "690415d58971e73ca187d8c9",
    
    "email": {
        "type": "webhook",
        "api_url": "http://localhost:5000",
        "email_address": "verify@yourdomain.com"
    }
}
```

### 4. 配置 Cloudflare Email Worker

见下方完整示例 ⬇️

---

## 🔧 Cloudflare Worker 配置

### 方式一：转发到本地服务器

```javascript
export default {
  async email(message, env, ctx) {
    try {
      // 读取邮件内容
      const rawEmail = await streamToString(message.raw);
      
      // 构建邮件数据
      const emailData = {
        to: message.to,
        from: message.from,
        subject: message.headers.get('subject') || '',
        text: rawEmail,
        html: rawEmail
      };
      
      // 转发到本地服务器（使用 Cloudflare Tunnel）
      await fetch('https://your-tunnel.trycloudflare.com/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailData)
      });
      
    } catch (error) {
      console.error('Error:', error);
    }
  }
}

// 辅助函数：Stream 转字符串
async function streamToString(stream) {
  const reader = stream.getReader();
  const chunks = [];
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }
  
  return new TextDecoder().decode(
    new Uint8Array(chunks.flatMap(chunk => [...chunk]))
  );
}
```

### 方式二：同时发送到 Gotify

```javascript
export default {
  async email(message, env, ctx) {
    try {
      const rawEmail = await streamToString(message.raw);
      const subject = message.headers.get('subject') || '';
      
      // 提取验证链接
      const linkMatch = rawEmail.match(/https:\/\/services\.sheerid\.com\/verify\/[^\s<>"]+emailToken=\d+/);
      const verificationLink = linkMatch ? linkMatch[0] : '';
      
      // 发送到本地服务器
      await fetch('https://your-tunnel.trycloudflare.com/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to: message.to,
          from: message.from,
          subject: subject,
          text: rawEmail,
          html: rawEmail
        })
      });
      
      // 同时发送通知到 Gotify
      await fetch(`https://gotify.yourdomain.com/message?token=${env.GOTIFY_TOKEN}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: '📧 SheerID 验证邮件',
          message: `主题: ${subject}\n\n${verificationLink ? `验证链接: ${verificationLink}` : '无验证链接'}`,
          priority: 8,
          extras: {
            'client::display': {
              'contentType': 'text/markdown'
            }
          }
        })
      });
      
    } catch (error) {
      console.error('Error:', error);
    }
  }
}
```

---

## 🌐 使用 Cloudflare Tunnel

让 Worker 能访问您的本地服务器：

### 安装 cloudflared

**Windows:**
```bash
# 下载 cloudflared.exe
# https://github.com/cloudflare/cloudflared/releases
```

**macOS:**
```bash
brew install cloudflare/cloudflare/cloudflared
```

**Linux:**
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

### 启动隧道

```bash
cloudflared tunnel --url http://localhost:5000
```

输出示例：
```
Your quick Tunnel has been created! Visit it at:
https://abc-def-123.trycloudflare.com
```

将这个 URL 用在 Worker 中！

---

## 🚀 完整工作流程

### 终端 1：邮件接收服务

```bash
python email_receiver.py
```

输出：
```
============================================================
  SheerID 邮件接收服务器
============================================================

  监听端口: 5000
  接收端点: http://localhost:5000/email
  状态查询: http://localhost:5000/status
  查看链接: http://localhost:5000/links
============================================================
```

### 终端 2：Cloudflare Tunnel（可选）

```bash
cloudflared tunnel --url http://localhost:5000
```

### 终端 3：主程序

```bash
python main.py
```

---

## 🧪 测试服务器

运行测试脚本：

```bash
python test_email_receiver.py
```

或手动测试：

```bash
# 查看状态
curl http://localhost:5000/status

# 发送测试邮件
curl -X POST http://localhost:5000/email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "verify@test.com",
    "from": "test@example.com",
    "subject": "Test",
    "text": "https://services.sheerid.com/verify/123?emailToken=456",
    "html": "..."
  }'

# 查看验证链接
curl http://localhost:5000/links?email=verify@test.com

# 查看最近邮件
curl http://localhost:5000/emails?limit=5
```

---

## 📊 API 接口文档

### POST /email
接收邮件

**请求体:**
```json
{
  "to": "verify@yourdomain.com",
  "from": "noreply@sheerid.com",
  "subject": "Verify your email",
  "text": "邮件文本内容",
  "html": "邮件HTML内容"
}
```

**响应:**
```json
{
  "success": true,
  "message": "Verification email received",
  "has_link": true,
  "email_token": "1234567890"
}
```

### GET /status
获取服务状态

**响应:**
```json
{
  "status": "running",
  "recent_emails": 5,
  "verification_links": 2,
  "uptime": "active"
}
```

### GET /links
获取验证链接

**参数:**
- `email` (可选): 筛选特定邮箱

**响应:**
```json
{
  "email": "verify@test.com",
  "link": "https://services.sheerid.com/verify/...",
  "token": "1234567890",
  "timestamp": "2025-12-30T23:56:37"
}
```

### GET /emails
获取最近邮件

**参数:**
- `limit` (默认10): 返回邮件数量

**响应:**
```json
{
  "total": 5,
  "emails": [...]
}
```

### POST /clear
清空所有数据

**响应:**
```json
{
  "success": true,
  "message": "Data cleared"
}
```

---

## 🎨 与其他方案对比

| 特性 | Webhook | Mailpit | IMAP | CloudMail |
|------|---------|---------|------|-----------|
| 设置复杂度 | ⭐ 简单 | ⭐⭐ 中等 | ⭐⭐⭐ 复杂 | ⭐⭐⭐ 复杂 |
| 需要 Docker | ❌ 否 | ✅ 是 | ❌ 否 | ❌ 否 |
| 实时性 | ⭐⭐⭐ 最快 | ⭐⭐ 快 | ⭐ 慢 | ⭐⭐ 快 |
| 可扩展性 | ⭐⭐⭐ 最强 | ⭐ 弱 | ⭐⭐ 中 | ⭐⭐ 中 |
| 通知集成 | ✅ 简单 | ❌ 困难 | ❌ 困难 | ⭐ 中等 |
| 适用场景 | 生产+测试 | 仅测试 | 生产 | 生产 |

---

## 💡 高级功能

### 集成 Gotify 通知

修改 `email_receiver.py`，添加：

```python
import os

GOTIFY_URL = os.getenv('GOTIFY_URL', 'https://gotify.yourdomain.com')
GOTIFY_TOKEN = os.getenv('GOTIFY_TOKEN', '')

@app.route('/email', methods=['POST'])
def receive_email():
    # ...existing code...
    
    if verification_link and GOTIFY_TOKEN:
        # 发送通知
        requests.post(
            f'{GOTIFY_URL}/message?token={GOTIFY_TOKEN}',
            json={
                'title': '✅ 验证邮件已接收',
                'message': f'Token: {email_token}',
                'priority': 8
            }
        )
    
    # ...rest of code...
```

### 自定义端口

```bash
python email_receiver.py 8080
```

更新 config.json:
```json
"api_url": "http://localhost:8080"
```

### 日志查看

```bash
tail -f email_receiver.log
```

---

## 🐛 故障排除

### 服务无法启动

```bash
# 检查端口占用
netstat -ano | findstr :5000

# 使用其他端口
python email_receiver.py 8080
```

### Worker 无法连接

1. 确保 Cloudflare Tunnel 正在运行
2. 检查 Worker 中的 URL 是否正确
3. 查看 Worker 日志

### 未收到邮件

1. 访问 http://localhost:5000/emails 检查
2. 查看 email_receiver.log 日志
3. 测试 Worker 配置

### 验证链接未提取

检查邮件内容格式，确保包含 SheerID 链接。

---

## 📝 环境变量

可以使用环境变量配置：

```bash
# Windows
set GOTIFY_URL=https://gotify.yourdomain.com
set GOTIFY_TOKEN=your_token

# Linux/macOS
export GOTIFY_URL=https://gotify.yourdomain.com
export GOTIFY_TOKEN=your_token
```

---

## 🎉 总结

Webhook 模式提供了：

- ✅ **最简单的设置** - 只需运行一个 Python 脚本
- ✅ **实时接收** - 无需轮询，立即处理
- ✅ **灵活扩展** - 轻松集成通知服务
- ✅ **完全控制** - 自定义所有处理逻辑

**推荐用于：**
- 生产环境
- 需要通知的场景
- 自动化工作流

**现在开始使用吧！** 🚀

# Webhook 邮件接收配置指南

## 🚀 什么是 Webhook 模式？

Webhook 模式让您的本地 Python 脚本直接接收来自 Cloudflare Worker 的邮件，无需 Mailpit 或任何邮件服务器！

### 工作流程

```
SheerID 发送邮件
    ↓
Cloudflare Email Worker 接收
    ↓
Worker HTTP POST → 本地 Python 服务器
    ↓
自动提取验证链接
    ↓
main.py 直接使用链接完成验证 ✅
```

---

## 📦 安装依赖

```bash
pip install flask
```

---

## ⚙️ 配置步骤

### 1. 配置 config.json

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

### 2. 启动邮件接收服务器

打开**第一个终端**：

```bash
python email_receiver.py
```

或指定端口：

```bash
python email_receiver.py 5000
```

服务器将监听 `http://localhost:5000/email`

### 3. 配置 Cloudflare Worker

修改您的 Email Worker，添加转发到本地服务器：

```javascript
export default {
  async email(message, env, ctx) {
    // 读取邮件内容
    const reader = message.raw.getReader();
    const chunks = [];
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
    }
    const rawEmail = new TextDecoder().decode(
      new Uint8Array(chunks.flatMap(chunk => [...chunk]))
    );

    // 解析邮件（简化版）
    const emailData = {
      to: message.to,
      from: message.from,
      subject: message.headers.get('subject') || '',
      text: rawEmail,  // 或使用邮件解析库
      html: rawEmail
    };

    // 转发到本地服务器（需要公网访问或使用 Cloudflare Tunnel）
    await fetch('https://your-tunnel-url.com/email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(emailData)
    });

    // 也可以发送到 Gotify 等通知服务
    await fetch(`https://gotify.yourdomain.com/message?token=${env.GOTIFY_TOKEN}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: '验证邮件',
        message: `收到来自 ${message.from} 的邮件`,
        priority: 8
      })
    });
  }
}
```

### 4. 使用 Cloudflare Tunnel（推荐）

让 Worker 能访问您的本地服务器：

```bash
# 安装 cloudflared
# Windows: https://github.com/cloudflare/cloudflared/releases

# 启动隧道
cloudflared tunnel --url http://localhost:5000
```

会得到一个公网 URL，如：`https://xxx.trycloudflare.com`

在 Worker 中使用这个 URL。

---

## 🎯 运行程序

启动两个终端：

**终端 1 - 邮件接收服务**：
```bash
python email_receiver.py
```

**终端 2 - 主程序**：
```bash
python main.py
```

---

## 🔍 API 接口

邮件接收服务器提供以下接口：

### 接收邮件
```
POST /email
Body: {
  "to": "verify@yourdomain.com",
  "from": "noreply@sheerid.com",
  "subject": "Verify your email",
  "text": "...",
  "html": "..."
}
```

### 查看状态
```
GET /status
```

### 查看验证链接
```
GET /links
GET /links?email=verify@yourdomain.com
```

### 查看最近邮件
```
GET /emails?limit=10
```

### 清空数据
```
POST /clear
```

---

## 📊 Web 界面

访问 `http://localhost:5000` 查看服务状态。

---

## 🔧 高级配置

### 修改端口

```bash
python email_receiver.py 8080
```

然后更新 `config.json`:
```json
"api_url": "http://localhost:8080"
```

### 使用 ngrok 代替 Cloudflare Tunnel

```bash
ngrok http 5000
```

---

## ⚡ 优势

相比 Mailpit：

- ✅ **更简单** - 无需 Docker 容器
- ✅ **更快** - 直接 HTTP 接收，无需轮询
- ✅ **更灵活** - 可以添加自定义处理逻辑
- ✅ **更轻量** - 只是一个 Flask 应用
- ✅ **实时通知** - 可以集成 Gotify/Telegram 等

---

## 🐛 故障排除

### Worker 无法连接到本地服务器

1. 确保 `email_receiver.py` 正在运行
2. 检查防火墙设置
3. 使用 Cloudflare Tunnel 或 ngrok

### 未收到邮件

1. 检查 Worker 日志
2. 访问 `http://localhost:5000/emails` 查看
3. 确认邮件地址匹配

### 连接被拒绝

```bash
# 检查服务是否运行
curl http://localhost:5000/status
```

---

## 💡 示例 Worker 完整代码

```javascript
// Cloudflare Email Worker
export default {
  async email(message, env, ctx) {
    try {
      // 获取邮件内容
      const content = await streamToString(message.raw);
      
      // 提取关键信息
      const emailData = {
        to: message.to,
        from: message.from,
        subject: message.headers.get('subject') || '',
        text: content,
        html: content
      };
      
      // 发送到本地服务器
      const response = await fetch('https://your-tunnel.trycloudflare.com/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailData)
      });
      
      console.log('Email forwarded:', response.status);
      
    } catch (error) {
      console.error('Error processing email:', error);
    }
  }
}

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

---

**现在您有了最简单的邮件接收方案！** 🎉

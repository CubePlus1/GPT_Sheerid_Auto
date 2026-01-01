# Cloudflare Email Worker 配置指南

## ⚠️ 错误修复

如果看到错误 "Handler does not export a fetch() function"，说明 Worker 代码配置不正确。

---

## 📝 完整配置步骤

### 1. 创建 Email Routing

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 选择您的域名
3. 进入 **Email** → **Email Routing**
4. 启用 Email Routing
5. 添加目标邮箱地址（如 `verify@yourdomain.com`）

### 2. 创建 Worker

1. 进入 **Workers & Pages**
2. 点击 **Create application** → **Create Worker**
3. 命名为 `email-handler`
4. 复制以下代码到编辑器：

```javascript
export default {
  async email(message, env, ctx) {
    console.log('收到邮件:', message.from, '->', message.to);
    
    try {
      // 读取邮件内容
      const rawEmail = await streamToString(message.raw);
      const subject = message.headers.get('subject') || '';
      
      // 构建邮件数据
      const emailData = {
        to: message.to,
        from: message.from,
        subject: subject,
        text: rawEmail,
        html: rawEmail
      };
      
      // 转发到本地服务器（使用 Cloudflare Tunnel URL）
      await fetch(env.LOCAL_SERVER_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailData)
      });
      
      console.log('邮件已转发');
    } catch (error) {
      console.error('处理失败:', error);
    }
  }
};

async function streamToString(stream) {
  const reader = stream.getReader();
  const chunks = [];
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }
  
  const uint8Array = new Uint8Array(
    chunks.reduce((acc, chunk) => acc + chunk.length, 0)
  );
  
  let offset = 0;
  for (const chunk of chunks) {
    uint8Array.set(chunk, offset);
    offset += chunk.length;
  }
  
  return new TextDecoder('utf-8').decode(uint8Array);
}
```

### 3. 配置环境变量

在 Worker 设置中添加：

- **LOCAL_SERVER_URL**: `https://your-tunnel.trycloudflare.com/email`
- **GOTIFY_URL** (可选): `https://gotify.yourdomain.com`
- **GOTIFY_TOKEN** (可选): `your_gotify_token`

### 4. 绑定 Email Route

1. 返回 **Email Routing**
2. 点击 **Routing rules**
3. 添加规则：
   - **Matcher**: `verify@yourdomain.com`
   - **Action**: Send to Worker
   - **Worker**: 选择 `email-handler`

---

## 🌐 设置 Cloudflare Tunnel

### Windows

1. 下载 cloudflared: https://github.com/cloudflare/cloudflared/releases
2. 运行：
```bash
cloudflared.exe tunnel --url http://localhost:5000
```

3. 复制生成的 URL（如 `https://abc-123.trycloudflare.com`）
4. 在 Worker 环境变量中设置 `LOCAL_SERVER_URL` 为 `https://abc-123.trycloudflare.com/email`

### Linux/macOS

```bash
# 安装
brew install cloudflare/cloudflare/cloudflared

# 启动
cloudflared tunnel --url http://localhost:5000
```

---

## ✅ 测试流程

### 1. 启动本地服务器

```bash
python email_receiver.py
```

应该看到：
```
============================================================
  SheerID 邮件接收服务器
============================================================
  监听端口: 5000
```

### 2. 启动 Cloudflare Tunnel

```bash
cloudflared tunnel --url http://localhost:5000
```

记录生成的 URL。

### 3. 更新 Worker 环境变量

将 Tunnel URL 设置为 `LOCAL_SERVER_URL`。

### 4. 发送测试邮件

发送邮件到 `verify@yourdomain.com`，检查：

1. **Cloudflare Dashboard** → Workers → Logs
2. **本地终端** - email_receiver.py 的输出
3. **浏览器** - http://localhost:5000/emails

---

## 🐛 常见问题

### 问题 1: "Handler does not export a fetch() function"

**原因**: Worker 代码格式不正确

**解决**: 确保代码包含：
```javascript
export default {
  async email(message, env, ctx) {
    // 邮件处理逻辑
  }
}
```

### 问题 2: Worker 无法连接到本地服务器

**原因**: 
- Cloudflare Tunnel 未运行
- LOCAL_SERVER_URL 配置错误
- 本地防火墙阻止

**解决**:
1. 确认 `cloudflared` 正在运行
2. 检查 Tunnel URL 是否正确
3. 测试 Tunnel: `curl https://your-tunnel.trycloudflare.com/status`

### 问题 3: 本地服务器未收到邮件

**检查清单**:
- [ ] email_receiver.py 正在运行
- [ ] Cloudflare Tunnel 正在运行
- [ ] Worker 环境变量配置正确
- [ ] Email Route 已绑定到 Worker
- [ ] 查看 Worker 日志是否有错误

### 问题 4: 邮件转发失败

查看 Worker 日志：
1. Cloudflare Dashboard → Workers
2. 点击您的 Worker
3. 查看 **Logs** 标签

---

## 📊 完整架构

```
发件人
  ↓
Cloudflare Email Routing
  ↓
Email Worker (email-handler)
  ↓
Cloudflare Tunnel (公网 → 本地)
  ↓
email_receiver.py (localhost:5000)
  ↓
存储验证链接
  ↓
main.py 读取并验证
```

---

## 🎯 快速命令

```bash
# 1. 启动本地服务器
python email_receiver.py

# 2. 启动 Cloudflare Tunnel（新终端）
cloudflared tunnel --url http://localhost:5000

# 3. 测试本地服务器
curl http://localhost:5000/status

# 4. 测试 Tunnel（使用 Tunnel URL）
curl https://your-tunnel.trycloudflare.com/status

# 5. 运行主程序（新终端）
python main.py
```

---

## 💡 调试技巧

### 查看 Worker 日志

```bash
# 使用 wrangler CLI
npx wrangler tail
```

### 发送测试邮件

使用任何邮箱发送邮件到 `verify@yourdomain.com`

### 查看本地接收

```bash
# 查看最近邮件
curl http://localhost:5000/emails

# 查看验证链接
curl http://localhost:5000/links
```

---

## ✅ 验证成功标志

1. **Worker 日志**显示 "邮件已转发"
2. **本地终端**显示 "收到邮件: ..."
3. **http://localhost:5000/emails** 能看到邮件
4. **http://localhost:5000/links** 能看到验证链接

---

**需要帮助？** 请提供：
1. Worker 日志截图
2. email_receiver.py 输出
3. Tunnel 的 URL

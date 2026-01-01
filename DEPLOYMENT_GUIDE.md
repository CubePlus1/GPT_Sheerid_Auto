# 📖 分步部署指南

## 第一阶段：基础环境准备（10 分钟）

### ✅ 检查清单

- [ ] Windows/Mac/Linux 系统
- [ ] Python 3.8+ 已安装
- [ ] 拥有自己的域名
- [ ] 已有 Cloudflare 账户
- [ ] 域名 DNS 指向 Cloudflare

### 步骤 1.1：验证 Python

```bash
python --version
```

输出示例：`Python 3.11.7`

如未安装，访问 [python.org](https://www.python.org/downloads/) 下载安装。

### 步骤 1.2：安装项目依赖

```bash
cd D:\0code\py\test\GPT_Sheerid_Auto
pip install flask requests
```

### 步骤 1.3：下载 Cloudflare Tunnel

**选项 A：从官网下载**
1. 访问 [cloudflare.com/warp](https://www.cloudflare.com/warp/)
2. 下载适用于您操作系统的版本

**选项 B：从 GitHub 下载**
1. 访问 [github.com/cloudflare/cloudflared/releases](https://github.com/cloudflare/cloudflared/releases)
2. 下载最新版本

**验证安装：**
```bash
cloudflared --version
```

输出示例：`cloudflared version 2024.12.0`

---

## 第二阶段：本地服务配置（15 分钟）

### ✅ 本阶段目标

启动 Flask 邮件接收服务，可以通过 API 接收邮件

### 步骤 2.1：启动 Flask 服务

打开**第一个**终端窗口：

```bash
cd D:\0code\py\test\GPT_Sheerid_Auto
python email_receiver.py
```

**预期输出：**
```
 * Running on http://0.0.0.0:5000
 * Debug mode: off
 WARNING in werkzeug.serving: This is a development server. Do not use in a production deployment.
```

✅ **不要关闭此终端窗口！** Flask 服务需要持续运行

### 步骤 2.2：验证服务（新终端）

打开**第二个**终端窗口：

```bash
# 测试服务状态
curl http://localhost:5000/status
```

**预期输出：**
```json
{
  "recent_emails": 0,
  "status": "running",
  "uptime": "active",
  "verification_links": 0
}
```

如果看到此输出，✅ Flask 服务正常运行！

### 步骤 2.3：运行测试脚本

在**第二个**终端继续：

```bash
python test_email_receiver.py
```

**预期输出：**
```
============================================================
测试邮件接收服务器
============================================================

1. 测试状态接口...
   ✓ 状态接口正常
   响应: {...}

2. 发送测试验证邮件...
   ✓ 邮件发送成功
   响应: {...}
   ✓ 验证链接已提取
   emailToken: 1234567890

3. 查询验证链接...
   ✓ 查询成功
   验证链接: https://services.sheerid.com/verify/...

4. 查看最近邮件...
   ✓ 邮件总数: 2

============================================================
✓ 测试完成！
```

✅ **第二阶段完成！** Flask 服务正常运行。

---

## 第三阶段：Cloudflare Tunnel 配置（10 分钟）

### ✅ 本阶段目标

创建从互联网到本地服务的安全隧道

### 步骤 3.1：启动 Tunnel

打开**第三个**终端窗口：

```bash
cloudflared tunnel --url http://localhost:5000
```

**第一次运行：**

您会看到类似输出：
```
A session has been created. Please visit:

https://dash.cloudflare.com/argotunnel?aud=...&token=...

This aud cookie will expire in 15 minutes.
```

1. 点击链接或复制到浏览器打开
2. 登录 Cloudflare 账户
3. 选择您的域名
4. 授权 Tunnel 访问

**Tunnel 启动成功：**
```
2025-12-31 10:00:00 INF Your quick tunnel has been created! 
Visit it at (it'll be live for 24 hrs):

https://chicago-meat-switch-advert.trycloudflare.com
```

**⚠️ 重要：记录这个 URL！** 您在第 5 阶段会用到它。

格式：`https://xxx-yyy-zzz.trycloudflare.com`

✅ **不要关闭此终端窗口！** Tunnel 需要持续运行

### 步骤 3.2：验证 Tunnel 连接

打开**第四个**终端窗口：

```bash
# 测试 Tunnel URL 是否可访问
curl https://chicago-meat-switch-advert.trycloudflare.com/status
```

**预期输出：**
```json
{
  "recent_emails": 0,
  "status": "running",
  "uptime": "active",
  "verification_links": 0
}
```

✅ **Tunnel 连接成功！** 现在您可以通过互联网访问本地服务。

---

## 第四阶段：Cloudflare Email Routing 配置（10 分钟）

### ✅ 本阶段目标

配置 Cloudflare 接收发送到 `verify@yourdomain.com` 的邮件

### 步骤 4.1：登录 Cloudflare Dashboard

1. 访问 [dash.cloudflare.com](https://dash.cloudflare.com)
2. 使用您的 Cloudflare 账户登录
3. 选择您的域名

### 步骤 4.2：启用 Email Routing

1. 在左侧菜单选择 **Email**
2. 点击 **Email Routing**
3. 点击 **Enable Email Routing** 按钮
4. 选择您的域名（如 yourdomain.com）
5. 点击确认

### 步骤 4.3：添加目标邮箱

1. 在 Email Routing 页面，点击 **Add address**
2. 输入收件邮箱（如 `verify@yourdomain.com`）
3. 点击 **Create address**

⚠️ **重要：** 记住这个邮箱地址，后面会频繁用到。

**预期显示：**
```
Destination address: verify@yourdomain.com
Status: Active
```

### 步骤 4.4：暂停等待

**暂时不配置路由规则！** 我们需要先创建 Worker（第 5 阶段）。

---

## 第五阶段：Cloudflare Worker 配置（20 分钟）

### ✅ 本阶段目标

创建 Worker 处理邮件并转发到本地服务

### 步骤 5.1：创建 Worker

1. 在 Cloudflare Dashboard 左侧菜单选择 **Workers & Pages**
2. 点击 **Create application**
3. 点击 **Create Worker**
4. 输入名称：`email-handler`
5. 点击 **Deploy** 创建

### 步骤 5.2：编辑 Worker 代码

1. 进入刚创建的 `email-handler` Worker
2. 点击 **Edit code** 或 **Code editor**
3. 将所有代码替换为以下内容：

```javascript
export default {
  async email(message, env, ctx) {
    console.log('📧 收到邮件:', message.from, '->', message.to);
    
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
      
      // 转发到本地服务器
      const url = env.LOCAL_SERVER_URL;
      console.log('🔄 转发到:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailData)
      });
      
      console.log('✅ 转发成功:', response.status);
      
    } catch (error) {
      console.error('❌ 转发失败:', error);
    }
  },
  
  // 用于测试的 HTTP 处理器
  async fetch(request, env, ctx) {
    if (request.method === 'GET') {
      return new Response('Worker is running! ✅', { status: 200 });
    }
    return new Response('Method not allowed', { status: 405 });
  }
};

// 辅助函数
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

4. 点击 **Save and deploy**

✅ Worker 代码已部署！

### 步骤 5.3：配置环境变量

1. 在 Worker 页面右侧点击 **Settings**
2. 选择 **Environment variables**
3. 点击 **Add variable**
4. 填写：
   - **Variable name**: `LOCAL_SERVER_URL`
   - **Value**: `https://chicago-meat-switch-advert.trycloudflare.com/email`
   
   ⚠️ **重要：** 
   - 将 `chicago-meat-switch-advert.trycloudflare.com` 替换为**您的 Tunnel URL**（第 3 阶段记录的）
   - **必须加上 `/email` 后缀！**

5. 点击 **Save and deploy**

**验证环境变量：**
```
LOCAL_SERVER_URL: https://your-tunnel-url.trycloudflare.com/email
```

✅ Worker 配置完成！

---

## 第六阶段：完成 Email Routing 配置（5 分钟）

### ✅ 本阶段目标

将 Email Routing 规则与 Worker 连接

### 步骤 6.1：设置路由规则

1. 返回 Cloudflare Dashboard
2. 选择 **Email** → **Email Routing**
3. 点击 **Routing rules**

### 步骤 6.2：创建规则

1. 点击 **Add routing rule**
2. 填写规则：
   - **Match**: 选择 **Custom domain**
   - **输入**: `verify@yourdomain.com`（替换为您的实际地址）
   - **Action**: 选择 **Send to a Worker**
   - **Worker**: 在下拉菜单中选择 `email-handler`

3. 点击 **Save**

**预期显示：**
```
Rule: verify@yourdomain.com
Action: Send to Worker: email-handler
Status: Enabled
```

✅ **Email Routing 配置完成！**

---

## 第七阶段：配置本地应用（10 分钟）

### ✅ 本阶段目标

准备 ChatGPT 和验证数据配置

### 步骤 7.1：获取 ChatGPT Access Token

1. 登录 [ChatGPT](https://chatgpt.com)
2. 访问 [Session API](https://chatgpt.com/api/auth/session)
3. 您会看到 JSON 响应，找到 `accessToken` 字段
4. 复制整个 token 值（长字符串，以 `eyJ...` 开头）

### 步骤 7.2：编辑 config.json

在**项目目录**打开 `config.json`：

```json
{
    "accessToken": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0...",
    "programId": "690415d58971e73ca187d8c9",
    
    "email": {
        "type": "webhook",
        "api_url": "http://localhost:5000",
        "email_address": "verify@yourdomain.com"
    }
}
```

替换：
- `accessToken`: 粘贴您的真实 token
- `email_address`: 改为您实际设置的邮箱地址

### 步骤 7.3：准备 data.txt

创建或编辑 `data.txt`：

```
firstName|lastName|branch|birthDate|dischargeDate
JOHN|SMITH|Army|1990-05-15|2023-06-01
JANE|DOE|Navy|1985-03-20|2022-08-15
```

格式说明：
- **firstName**: 名
- **lastName**: 姓
- **branch**: 军种（见下表）
- **birthDate**: 出生日期（YYYY-MM-DD）
- **dischargeDate**: 退役日期（YYYY-MM-DD）

**支持的 branch 值：**
```
Army, Navy, Air Force, Marine Corps, Coast Guard, Space Force,
Army National Guard, Army Reserve, Navy Reserve,
Air National Guard, Air Force Reserve,
Marine Corps Forces Reserve, Coast Guard Reserve
```

✅ **配置完成！**

---

## 第八阶段：端到端测试（15 分钟）

### ✅ 当前运行状态检查

验证以下服务都在运行（应该有 3-4 个终端窗口）：

**终端 1：Flask 服务**
```bash
python email_receiver.py
# 输出：Running on http://0.0.0.0:5000
```

**终端 2：Cloudflare Tunnel**
```bash
cloudflared tunnel --url http://localhost:5000
# 输出：https://xxx-yyy-zzz.trycloudflare.com
```

**终端 3：发送测试邮件**

```bash
# 从任意邮箱发送邮件到 verify@yourdomain.com
# 或使用测试脚本：
python test_email_receiver.py
```

### 步骤 8.1：检查邮件接收

```bash
# 检查 Flask 服务是否收到邮件
curl http://localhost:5000/emails

# 预期输出：包含邮件列表
```

### 步骤 8.2：检查验证链接提取

```bash
curl http://localhost:5000/links

# 预期输出：包含验证链接和 token
```

### 步骤 8.3：检查 Worker 日志

1. 进入 Cloudflare Dashboard
2. **Workers & Pages** → **email-handler**
3. 点击 **Real-time logs**
4. 应该看到邮件处理日志

### 步骤 8.4：完整流程测试

```bash
python main.py
```

**预期行为：**
1. 连接到本地 Flask 服务
2. 等待 SheerID 验证邮件
3. 邮件到达后自动提取验证链接
4. 打开浏览器点击链接
5. 完成身份验证

✅ **全部测试完成！**

---

## 🎉 部署成功清单

- [ ] Python 环境已准备
- [ ] Flask 服务运行正常（端口 5000）
- [ ] Cloudflare Tunnel 已启动并获得 URL
- [ ] Email Routing 已启用
- [ ] Worker `email-handler` 已部署
- [ ] Worker 环境变量 `LOCAL_SERVER_URL` 已配置
- [ ] Email Routing 规则已关联 Worker
- [ ] config.json 已填写完整
- [ ] data.txt 已准备好
- [ ] 所有测试都通过了

---

## 🚀 运行验证脚本

一切准备就绪，现在可以运行完整的验证流程：

```bash
python main.py
```

程序将自动：
1. ✅ 连接到本地服务
2. ✅ 等待 SheerID 邮件
3. ✅ 提取验证链接
4. ✅ 完成身份验证

---

## 💡 常见问题

**Q: 某个服务停止了怎么办？**  
A: 各个服务是独立的，可以单独重启。重启后无需重新配置。

**Q: Tunnel URL 每次都不一样？**  
A: 是的，临时 Tunnel URL 是动态的。重启后会生成新 URL，需要更新 Worker 环境变量。

**Q: 邮件没有到达本地服务？**  
A: 检查 Worker 日志、Email Routing 规则、Tunnel 连接等。

**Q: 可以运行多个实例吗？**  
A: 可以，但需要使用不同的端口和 Tunnel URL。

---

**更新时间**：2025-12-31  
**版本**：1.0

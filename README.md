# 🎓 GPT SheerID Auto - ChatGPT Plus 军事身份自动验证

自动化验证 ChatGPT Plus 的军事身份优惠资格，实现一键点击验证链接的完整解决方案。

**作者**: dy安心大油条&cubeplus1+AI  
**当前版本**: 1.0 (Webhook + Cloudflare Integration)  
**最后更新**: 2025-12-31

> 📚 **新用户？** 建议先查看 [📖 文档索引](DOCS_INDEX.md) 了解完整的文档结构和推荐阅读路径

---

## 📋 快速导航

- [5分钟快速开始](#-快速开始5分钟)
- [完整部署步骤](#-完整部署步骤)
- [配置详解](#-配置详解)
- [测试方法](#-测试与验证)
- [问题排查](#-故障排除)
- [常见问题](#-faq)

---

## ✨ 核心特点

✅ **零外部邮箱** - 无需 Gmail、Outlook 等第三方邮箱  
✅ **完全本地化** - 邮件处理全部在本地进行  
✅ **Cloudflare 原生** - 利用 Email Routing 和 Workers  
✅ **实时处理** - 邮件到达即刻提取验证链接  
✅ **可靠稳定** - 支持多种邮件接收方式

---

## 🚀 快速开始（5分钟）

### 前置要求

- ✅ Python 3.8+ 已安装
- ✅ 拥有自己的域名（DNS 指向 Cloudflare）
- ✅ Cloudflare 免费账户
- ✅ ChatGPT 账户

### 步骤 1: 安装依赖

```bash
pip install flask requests
```

### 步骤 2: 配置 config.json

```json
{
    "accessToken": "your_chatgpt_token_here",
    "programId": "690415d58971e73ca187d8c9",
    
    "email": {
        "type": "webhook",
        "api_url": "http://localhost:5000",
        "email_address": "verify@yourdomain.com"
    }
}
```

### 步骤 3: 启动本地邮件服务

```bash
python email_receiver.py
```

输出应显示：`Running on http://0.0.0.0:5000`

### 步骤 4: 启动 Cloudflare Tunnel

```bash
cloudflared tunnel --url http://localhost:5000
```

记录输出的 Tunnel URL（格式：`https://xxx-yyy-zzz.trycloudflare.com`）

### 步骤 5: 配置 Cloudflare Worker

1. 进入 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 创建 Worker `email-handler`
3. 复制下面的代码（见详细步骤）
4. 配置环境变量 `LOCAL_SERVER_URL` = `https://your-tunnel-url.trycloudflare.com/email`

### 步骤 6: 运行验证

```bash
python main.py
```

✅ **完成！** 脚本会自动等待邮件并点击验证链接

---

## 📚 完整部署步骤

### 第 1 部分: 环境准备

#### 1.1 验证 Python 环境

```bash
python --version    # 应为 3.8 或更新
pip --version       # 应为 20.0 或更新

# 安装依赖
pip install flask requests
```

#### 1.2 下载 Cloudflare Tunnel

访问 [cloudflare.com/warp](https://www.cloudflare.com/warp/) 或 [GitHub](https://github.com/cloudflare/cloudflared/releases) 下载

**验证安装：**
```bash
cloudflared --version
```

### 第 2 部分: 本地 Flask 服务配置

#### 2.1 启动邮件接收服务

```bash
python email_receiver.py
```

**预期输出：**
```
 * Running on http://0.0.0.0:5000
 * Debug mode: off
```

#### 2.2 验证服务运行（新终端）

```bash
# 检查服务状态
curl http://localhost:5000/status

# 预期响应
{
  "recent_emails": 0,
  "status": "running",
  "uptime": "active",
  "verification_links": 0
}
```

#### 2.3 运行测试脚本

```bash
python test_email_receiver.py
```

**预期输出：**
```
✓ 状态接口正常
✓ 邮件发送成功
✓ 验证链接已提取
✓ 邮件总数: 2
✓ 测试完成！
```

### 第 3 部分: Cloudflare Tunnel 配置

#### 3.1 启动 Tunnel

```bash
cloudflared tunnel --url http://localhost:5000
```

**首次运行：**
- 点击提供的登录链接
- 选择您的域名
- 授权 Tunnel 访问

**记录输出的 Tunnel URL：**
```
https://xxx-yyy-zzz.trycloudflare.com
```

#### 3.2 验证 Tunnel 连接

```bash
# 新终端测试
curl https://xxx-yyy-zzz.trycloudflare.com/status

# 应返回与本地相同的 JSON
```

### 第 4 部分: Cloudflare Email Routing 配置

#### 4.1 启用 Email Routing

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 选择您的域名
3. **Email** → **Email Routing** → **Enable Email Routing**
4. 添加目标邮箱（如 `verify@yourdomain.com`）

#### 4.2 后续步骤

暂停，先创建 Worker（下一部分）

### 第 5 部分: Cloudflare Worker 配置

#### 5.1 创建 Worker

1. **Workers & Pages** → **Create application**
2. 命名为 `email-handler`
3. 复制以下代码到编辑器：

```javascript
export default {
  async email(message, env, ctx) {
    console.log('📧 收到邮件:', message.from, '->', message.to);
    
    try {
      const rawEmail = await streamToString(message.raw);
      const subject = message.headers.get('subject') || '';
      
      const emailData = {
        to: message.to,
        from: message.from,
        subject: subject,
        text: rawEmail,
        html: rawEmail
      };
      
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
  
  async fetch(request, env, ctx) {
    return new Response('Worker is running! ✅', { status: 200 });
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

4. 点击 **Deploy**

#### 5.2 配置环境变量

1. Worker 页面 → **Settings** → **Variables**
2. 添加：
   - **LOCAL_SERVER_URL** = `https://xxx-yyy-zzz.trycloudflare.com/email`
   
   ⚠️ **重要：** 必须加上 `/email` 后缀！

3. **Save and deploy**

### 第 6 部分: 完成 Email Routing 配置

1. **Email** → **Email Routing** → **Routing rules**
2. 创建规则：
   - **Match**: `verify@yourdomain.com`
   - **Action**: Send to a Worker
   - **Worker**: 选择 `email-handler`
3. 保存

✅ **配置完成！**

---

## ⚙️ 配置详解

### config.json 详细说明

```json
{
    // ChatGPT Access Token
    // 获取方式：
    // 1. 登录 https://chatgpt.com
    // 2. 访问 https://chatgpt.com/api/auth/session
    // 3. 复制 accessToken 字段值
    "accessToken": "eyJhbGci...",
    
    // SheerID Program ID（固定值）
    "programId": "690415d58971e73ca187d8c9",
    
    // 邮件配置
    "email": {
        // 类型：webhook 推荐！
        // 其他：imap, cloudmail, mailpit
        "type": "webhook",
        
        // Flask 服务 URL（webhook 类型）
        "api_url": "http://localhost:5000",
        
        // 目标邮箱地址
        // 必须与 Email Routing 配置一致
        "email_address": "verify@yourdomain.com"
    }
}
```

### data.txt 数据格式

```
firstName|lastName|branch|birthDate|dischargeDate
JOHN|SMITH|Army|1990-05-15|2023-06-01
JANE|DOE|Navy|1985-03-20|2022-08-15
```

**branch 支持值：**

| 值 | 含义 |
|----|------|
| Army | 陆军 |
| Navy | 海军 |
| Air Force | 空军 |
| Marine Corps | 海军陆战队 |
| Coast Guard | 海岸警卫队 |
| Space Force | 太空军 |
| Army National Guard | 陆军国民警卫队 |
| Army Reserve | 陆军预备役 |
| Navy Reserve | 海军预备役 |
| Air National Guard | 空军国民警卫队 |
| Air Force Reserve | 空军预备役 |
| Marine Corps Forces Reserve | 海军陆战队预备役 |
| Coast Guard Reserve | 海岸警卫队预备役 |

### 🔌 代理配置（可选）

使用代理可以提高成功率、避免 IP 限制。**代理是可选的**，不配置也能正常运行。

#### 快速配置

1. 创建 `proxy.txt` 文件：

```bash
# 复制示例文件
copy proxy.example.txt proxy.txt

# 或手动创建
echo 192.168.1.100:1080:user:pass > proxy.txt
```

2. 添加代理（每行一个，支持多个格式）：

```txt
# SOCKS5 认证代理（推荐）
192.168.1.100:1080:username:password

# HTTP 代理
192.168.1.101:8080

# 完整 URL 格式
socks5://user:pass@proxy.example.com:1080
http://proxy.example.com:8080
```

3. 运行程序，会显示：

```
[代理] 使用代理: 192.168.1.100:1080 (认证)
```

#### 支持的代理格式

| 格式 | 示例 | 说明 |
|------|------|------|
| SOCKS5 认证 | `ip:port:user:pass` | 推荐，性能最好 |
| HTTP 无认证 | `ip:port` | 简单代理 |
| SOCKS5 URL | `socks5://user:pass@ip:port` | 完整连接字符串 |
| HTTP URL | `http://ip:port` | HTTP 代理 URL |

#### 禁用代理

删除或重命名 `proxy.txt` 即可：

```bash
del proxy.txt
# 或
ren proxy.txt proxy.txt.bak
```

**📖 详细配置**: 查看 [PROXY_SETUP.md](PROXY_SETUP.md) 了解完整代理配置指南

---

## 🧪 测试与验证

### 测试 1: 本地服务

```bash
python test_email_receiver.py
```

### 测试 2: Tunnel 连接

```bash
curl https://your-tunnel-url.trycloudflare.com/status
```

### 测试 3: 邮件转发

发送邮件到 `verify@yourdomain.com`，检查本地服务：

```bash
curl http://localhost:5000/emails
```

### 测试 4: 完整流程

1. 确保以下服务运行中：
   - Flask: `python email_receiver.py`
   - Tunnel: `cloudflared tunnel --url http://localhost:5000`
   - Worker: 已部署并配置

2. 运行：
```bash
python main.py
```

---

## 🔧 故障排除

### ❌ "Cannot connect to localhost:5000"

**解决方案：**
```bash
# 检查端口占用
netstat -ano | findstr :5000

# 重启 Flask
python email_receiver.py
```

### ❌ "Tunnel URL returns 404"

**解决方案：**
```bash
# 重启 Tunnel（旧 URL 可能过期）
# 停止当前 (Ctrl+C)
cloudflared tunnel --url http://localhost:5000

# 记录新 URL，更新 Worker 环境变量
```

### ❌ "Email not received"

1. 检查 Email Routing 规则是否正确
2. 检查 Worker 日志（Real-time logs）
3. 验证发送地址是否匹配

---

## ❓ FAQ

**Q: 需要 Cloudflare DNS 吗？**  
A: 是的，域名 DNS 必须指向 Cloudflare

**Q: accessToken 会过期吗？**  
A: 是的，有效期通常为几小时，过期需重新获取

**Q: 支持批量验证吗？**  
A: 支持，编辑 data.txt 添加多行数据

**Q: 能否固定 Tunnel URL？**  
A: Cloudflare 高级套餐支持自定义域名

---

## 📖 其他邮件接收方式

### 方式 2: IMAP（使用现有邮箱）

```json
"email": {
    "type": "imap",
    "host": "imap.gmail.com",
    "port": 993,
    "email": "your-email@gmail.com",
    "password": "your-app-password"
}
```

### 方式 3: Mailpit（本地测试）

```json
"email": {
    "type": "mailpit",
    "api_url": "http://localhost:8025",
    "email_address": "verify@test.com"
}
```

启动：`docker-compose up -d`

---

## 📞 技术支持

遇到问题？检查：

1. ✅ 所有服务是否运行
2. ✅ 配置文件格式是否正确
3. ✅ accessToken 是否过期
4. ✅ Tunnel URL 是否有效
5. ✅ Worker 日志是否有错误

---

## 📄 许可证

MIT License - 仅供学习使用

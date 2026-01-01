# 🚀 快速参考表

## 服务启动命令汇总

### 开发环境快速启动（3 个终端）

**终端 1：Flask 邮件服务**
```bash
cd D:\0code\py\test\GPT_Sheerid_Auto
python email_receiver.py
```
- 端口：`5000`
- 状态检查：`curl http://localhost:5000/status`
- 日志文件：`email_receiver.log`

**终端 2：Cloudflare Tunnel**
```bash
cloudflared tunnel --url http://localhost:5000
```
- 输出：`https://xxx-yyy-zzz.trycloudflare.com`
- ⚠️ 记录此 URL，用于配置 Worker

**终端 3：运行验证程序**
```bash
python main.py
```
- 会自动调用 Flask 服务
- 等待 SheerID 验证邮件
- 自动点击验证链接

---

## API 端点速查

### Flask 服务（http://localhost:5000）

| 端点 | 方法 | 说明 | 示例 |
|------|------|------|------|
| `/` | GET | 服务首页 | `curl http://localhost:5000/` |
| `/status` | GET | 服务状态 | `curl http://localhost:5000/status` |
| `/email` | POST | 接收邮件 | `curl -X POST http://localhost:5000/email -d '...'` |
| `/emails` | GET | 查看邮件 | `curl http://localhost:5000/emails` |
| `/links` | GET | 查看链接 | `curl http://localhost:5000/links` |
| `/clear` | POST | 清空数据 | `curl -X POST http://localhost:5000/clear` |

---

## 配置文件模板

### config.json

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

### data.txt

```
firstName|lastName|branch|birthDate|dischargeDate
JOHN|SMITH|Army|1990-05-15|2023-06-01
JANE|DOE|Navy|1985-03-20|2022-08-15
```

### proxy.txt（可选）

```txt
# SOCKS5 认证代理（推荐）
192.168.1.100:1080:username:password

# HTTP 代理
192.168.1.101:8080

# 完整 URL 格式
socks5://user:pass@proxy.example.com:1080
http://proxy.example.com:8080
```

**测试代理：** `python test_proxy.py`

**格式支持：**
- `ip:port:user:pass` - SOCKS5 认证
- `ip:port` - HTTP 无认证
- `socks5://user:pass@ip:port` - 完整 URL
- `http://ip:port` - HTTP URL

---

## Cloudflare 配置清单

### Email Routing 步骤

1. ✅ 启用 Email Routing
2. ✅ 添加目标邮箱（如 `verify@yourdomain.com`）
3. ✅ 创建路由规则
   - Match: `verify@yourdomain.com`
   - Action: Send to Worker `email-handler`

### Worker 配置步骤

1. ✅ 创建 Worker `email-handler`
2. ✅ 复制邮件处理代码
3. ✅ 部署 Worker
4. ✅ 配置环境变量：
   - `LOCAL_SERVER_URL` = `https://your-tunnel-url.trycloudflare.com/email`

---

## 测试命令

### 本地服务测试

```bash
# 检查服务状态
curl http://localhost:5000/status

# 查看接收的邮件
curl http://localhost:5000/emails

# 查看提取的验证链接
curl http://localhost:5000/links

# 运行完整测试脚本
python test_email_receiver.py
```

### Tunnel 连接测试

```bash
# 测试 Tunnel URL 连接
curl https://your-tunnel-url.trycloudflare.com/status

# 替换 your-tunnel-url 为实际的 Tunnel URL
```

### Worker 日志检查

1. Cloudflare Dashboard
2. **Workers & Pages** → **email-handler**
3. **Real-time logs** 查看实时日志

---

## 环境变量参考

### Flask 应用

无额外环境变量需求

### Worker 应用

| 变量名 | 值示例 | 说明 |
|--------|--------|------|
| `LOCAL_SERVER_URL` | `https://xxx-yyy-zzz.trycloudflare.com/email` | 本地服务 Tunnel URL |
| `GOTIFY_URL` (可选) | `https://gotify.example.com` | Gotify 通知服务地址 |
| `GOTIFY_TOKEN` (可选) | `xxx-token-xxx` | Gotify 认证 token |

---

## 文件结构

```
GPT_Sheerid_Auto/
├── main.py                          # 主验证脚本
├── email_receiver.py                # Flask 邮件服务
├── webhook_email_client.py          # Webhook 邮件客户端
├── config.json                      # 配置文件（需填写）
├── config.example.json              # 配置示例
├── data.txt                         # 验证数据（需填写）
├── data.example.txt                 # 数据示例
│
├── cloudflare-email-worker.js       # Worker 代码
├── test_email_receiver.py           # Flask 服务测试脚本
├── test_config.py                   # 配置文件测试脚本
│
├── README.md                        # 完整使用指南
├── DEPLOYMENT_GUIDE.md              # 分步部署指南（本文件）
├── WEBHOOK_GUIDE.md                 # Webhook 模式详细指南
├── CLOUDFLARE_WORKER_FIX.md         # Worker 配置详细指南
│
├── requirements.txt                 # Python 依赖
├── docker-compose.yml               # Docker Mailpit 配置（可选）
├── .gitignore                       # Git 忽略配置
└── email_receiver.log               # Flask 服务日志（自动生成）
```

---

## 邮件类型对比

| 特点 | Webhook（推荐）| IMAP | Mailpit | CloudMail |
|------|---|---|---|---|
| 配置复杂度 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| 实时性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 依赖外部 | ❌ | ⚠️（需邮箱） | ❌（本地） | ⚠️（需服务） |
| 可靠性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 生产适用 | ✅ | ✅ | ❌（测试用）| ✅ |

---

## 故障排除速查

### Flask 服务问题

```bash
# 端口 5000 被占用
netstat -ano | findstr :5000

# 重启 Flask（停止当前进程后）
python email_receiver.py
```

### Tunnel 问题

```bash
# URL 过期或连接失败
# 停止当前 Tunnel (Ctrl+C)
cloudflared tunnel --url http://localhost:5000
# 记录新 URL，更新 Worker 环境变量
```

### 邮件未收到

检查清单：
- [ ] Flask 服务运行中
- [ ] Tunnel 连接正常
- [ ] Worker 已部署
- [ ] 环境变量 LOCAL_SERVER_URL 正确
- [ ] Email Routing 规则已启用
- [ ] 邮件地址与配置一致

---

## 获取 Token 指南

### ChatGPT Access Token

```
1. 访问 https://chatgpt.com/api/auth/session
2. 在返回的 JSON 中找到 "accessToken" 字段
3. 复制整个 token 值（以 eyJ 开头）
4. 粘贴到 config.json 的 accessToken 字段
```

### Cloudflare API Token

```
1. Cloudflare Dashboard → 右上角账户
2. My Profile → API Tokens
3. Create Token 或使用预设模板
4. 复制 API Token
```

---

## 日志查看

### Flask 服务日志

```bash
# 实时查看日志
tail -f email_receiver.log

# Windows 用户
type email_receiver.log

# 查看最后 50 行
tail -n 50 email_receiver.log
```

### Worker 日志

1. Cloudflare Dashboard
2. **Workers & Pages**
3. 选择 **email-handler**
4. 点击 **Real-time logs**

---

## 性能优化建议

### Flask 服务

```python
# 内存使用优化
# email_receiver.py 中的 emails 和 verification_links
# 使用 deque(maxlen=50) 限制内存

# 增加存储容量
from collections import deque
emails = deque(maxlen=100)  # 改为 100
```

### Worker

```javascript
// 添加速率限制
if (env.RATE_LIMIT_ENABLED) {
  const count = await ctx.storage.getCounter(message.from);
  if (count > 10) return; // 限制每个发件人 10 封/小时
}
```

---

## 安全建议

1. **不要提交敏感文件**
   - config.json（包含 accessToken）
   - proxy.txt（包含代理信息）
   - data.txt（包含个人信息）
   
   ✅ 这些已在 .gitignore 中

2. **定期更新 Token**
   - ChatGPT accessToken 会过期
   - 定期重新获取并更新

3. **使用环境变量**
   - Worker 敏感信息放在环境变量中
   - 不要硬编码 URL 或 Token

4. **限制 Tunnel 访问**
   - 考虑添加基础认证
   - 不要公开分享 Tunnel URL

---

## 常用命令速查

```bash
# 获取帮助
python main.py --help
python email_receiver.py --help

# 清空数据
curl -X POST http://localhost:5000/clear

# 批量导入数据
python -c "
with open('data.txt') as f:
    for line in f:
        print(line.strip())
"

# 检查依赖
pip show flask requests

# 更新依赖
pip install --upgrade flask requests
```

---

**快速参考表版本**：1.0  
**更新时间**：2025-12-31

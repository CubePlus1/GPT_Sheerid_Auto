# GPT SheerID Auto - 快速配置指南

## ✅ 已完成更新

本项目已添加 **Mailpit 本地测试邮箱支持**，现在支持三种邮箱方式：

1. **IMAP**（Gmail、QQ 等真实邮箱）
2. **CloudMail**（自建临时邮箱服务）
3. **Mailpit**（本地测试邮箱）⭐ 推荐本地测试

---

## 🚀 快速开始（使用 Mailpit）

### 步骤 1：启动 Mailpit

```bash
# 确保 Docker 已安装并运行
docker-compose up -d

# 验证 Mailpit 是否运行
docker ps
```

**访问 Mailpit Web 界面：** http://localhost:8025

### 步骤 2：配置 config.json

`config.json` 已经预配置好 Mailpit：

```json
{
    "accessToken": "你的ChatGPT accessToken",
    "programId": "690415d58971e73ca187d8c9",
    
    "email": {
        "type": "mailpit",
        "api_url": "http://localhost:8025",
        "email_address": "verify@test.com"
    }
}
```

**需要修改的内容：**

1. **accessToken**：
   - 登录 https://chatgpt.com
   - 访问 https://chatgpt.com/api/auth/session
   - 复制 `accessToken` 的值

2. **email_address**：可以是任意邮箱地址（如 `verify@test.com`），因为 Mailpit 会捕获所有邮件

### 步骤 3：准备数据文件

创建 `data.txt`，格式：

```
firstName|lastName|branch|birthDate|dischargeDate
JOHN|SMITH|Army|1990-05-15|2023-06-01
```

### 步骤 4：运行程序

```bash
python main.py
```

---

## 📋 完整配置选项

### Mailpit 配置（推荐本地测试）

```json
{
    "email": {
        "type": "mailpit",
        "api_url": "http://localhost:8025",
        "email_address": "verify@test.com"
    }
}
```

**参数说明：**
- `type`: 必须为 `"mailpit"`
- `api_url`: Mailpit API 地址，默认 `http://localhost:8025`
- `email_address`: 接收邮件的地址（任意值，Mailpit 会捕获所有邮件）

### IMAP 配置（使用真实邮箱）

```json
{
    "email": {
        "type": "imap",
        "imap_server": "imap.gmail.com",
        "imap_port": 993,
        "email_address": "your_email@gmail.com",
        "email_password": "your_app_password",
        "use_ssl": true
    }
}
```

### CloudMail 配置（自建服务）

```json
{
    "email": {
        "type": "cloudmail",
        "api_url": "https://your-cloudmail-api.com",
        "admin_email": "admin@example.com",
        "admin_password": "your_password",
        "email_address": "receive@yourdomain.com"
    }
}
```

---

## 🔧 Mailpit 功能说明

### 端口配置

- **Web 界面**: 8025 (http://localhost:8025)
- **SMTP 服务**: 1025

### 工作原理

1. SheerID 发送验证邮件到指定邮箱
2. 邮件通过 SMTP (1025) 发送到 Mailpit
3. Mailpit 捕获邮件并通过 API 提供访问
4. 程序自动从 Mailpit API 读取邮件
5. 提取验证链接并自动完成验证

### Web 界面功能

- 📧 查看所有接收的邮件
- 🔍 搜索和过滤邮件
- 📎 查看附件
- 🗑️ 删除邮件

---

## ⚠️ 注意事项

### 使用 Mailpit 时

1. **确保 Docker 正在运行**
   ```bash
   docker ps
   ```

2. **端口不冲突**
   - Web: 8025
   - SMTP: 1025

3. **网络访问**
   - 如果 SheerID 无法访问本地 1025 端口，需要：
     - 使用公网服务器
     - 或使用内网穿透（ngrok、cloudflared 等）

### 生产环境

- ❌ 不建议在生产环境使用 Mailpit
- ✅ 推荐使用 IMAP 或 CloudMail

---

## 🐛 故障排除

### Mailpit 连接失败

```bash
# 检查容器状态
docker ps

# 查看日志
docker logs mail-server

# 重启容器
docker-compose restart
```

### 未收到验证邮件

1. 检查 Mailpit Web 界面 (http://localhost:8025)
2. 确认邮件地址配置正确
3. 检查 SheerID 是否能访问您的 SMTP 服务器

### AccessToken 过期

重新获取：
1. 访问 https://chatgpt.com/api/auth/session
2. 复制新的 `accessToken`
3. 更新 `config.json`

---

## 📝 数据文件格式

### data.txt

```
firstName|lastName|branch|birthDate|dischargeDate
JOHN|SMITH|Army|1990-05-15|2023-06-01
JANE|DOE|Navy|1985-03-20|2022-08-15
```

### branch 可选值

- Army
- Navy
- Air Force
- Marine Corps
- Coast Guard
- Space Force
- Army National Guard
- Army Reserve
- Navy Reserve
- Air National Guard
- Air Force Reserve
- Marine Corps Forces Reserve
- Coast Guard Reserve

---

## 💡 使用技巧

### 1. 批量验证

在 `data.txt` 中添加多条数据，程序会自动逐条处理

### 2. 代理支持

创建 `proxy.txt`：

```
192.168.1.100:1080:username:password
socks5://user:pass@proxy.com:1080
```

### 3. TLS 指纹模拟

在 `tls_json/` 目录下放入 Chrome TLS 指纹 JSON 文件

---

## 📞 支持

如有问题，请：
1. 查看 `result.txt` 日志
2. 检查 Mailpit Web 界面
3. 查看 Docker 容器日志

---

**作者**: dy安心大油条  
**更新日期**: 2025-12-30  
**版本**: v2.0 (新增 Mailpit 支持)

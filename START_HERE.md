# 🎯 使用指南

## ✅ 配置已完成！

您的 GPT SheerID Auto 已成功配置 Mailpit 支持！

---

## 📋 下一步操作

### 1️⃣ 获取 ChatGPT Access Token

这是**唯一**还需要配置的项目：

1. 登录 [ChatGPT](https://chatgpt.com)
2. 访问 [Session API](https://chatgpt.com/api/auth/session)
3. 复制 `accessToken` 的值
4. 打开 `config.json`，替换：
   ```json
   "accessToken": "你的真实token"
   ```

### 2️⃣ 准备数据文件

创建或编辑 `data.txt`，格式：

```
firstName|lastName|branch|birthDate|dischargeDate
JOHN|SMITH|Army|1990-05-15|2023-06-01
JANE|DOE|Navy|1985-03-20|2022-08-15
```

**branch 可选值：**
- Army, Navy, Air Force, Marine Corps, Coast Guard, Space Force
- Army National Guard, Army Reserve, Navy Reserve
- Air National Guard, Air Force Reserve
- Marine Corps Forces Reserve, Coast Guard Reserve

### 3️⃣ 运行程序

```bash
python main.py
```

---

## 🔧 当前配置状态

### ✅ 已完成
- ✅ Mailpit 容器运行正常
- ✅ API 连接成功
- ✅ Web 界面可访问 (http://localhost:8025)
- ✅ Python 依赖已安装
- ✅ Docker 环境正常

### ⚠️ 待配置
- ⚠️ ChatGPT accessToken（见上方步骤 1）
- ⚠️ data.txt 数据文件（见上方步骤 2）

---

## 📊 Mailpit Web 界面

访问: **http://localhost:8025**

功能：
- 📧 查看所有接收的验证邮件
- 🔍 搜索和过滤邮件
- 📎 查看邮件内容和附件
- 🗑️ 清空测试邮件

---

## 🚀 快速测试

### 发送测试邮件到 Mailpit

您可以使用任何 SMTP 客户端发送邮件到：
- **SMTP 服务器**: localhost
- **端口**: 1025
- **收件人**: verify@test.com (或任意邮箱)

程序会自动从 Mailpit 读取邮件并提取验证链接。

---

## 📝 配置文件说明

### config.json

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

**参数说明：**
- `accessToken`: ChatGPT 会话令牌（必填）
- `programId`: SheerID 项目 ID（默认值通常不需要修改）
- `email.type`: 邮箱类型，当前为 `mailpit`
- `email.api_url`: Mailpit API 地址
- `email.email_address`: 接收邮件的地址（任意值）

---

## 🔄 切换邮箱类型

如果需要使用真实邮箱，修改 `config.json`：

### 使用 Gmail (IMAP)

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

### 使用 CloudMail

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

## 🐛 故障排除

### Mailpit 未运行

```bash
# 启动容器
docker-compose up -d

# 查看状态
docker ps

# 查看日志
docker logs mail-server
```

### AccessToken 过期

重新获取：
1. 访问 https://chatgpt.com/api/auth/session
2. 复制新的 `accessToken`
3. 更新 `config.json`

### 端口冲突

如果 8025 或 1025 端口被占用，修改 `docker-compose.yml`：

```yaml
ports:
  - "8026:8025"  # 修改为其他端口
  - "1026:1025"
```

然后更新 `config.json` 中的 `api_url`。

---

## 📂 输出文件

运行后会生成：

- `result.txt` - 验证结果日志
- `used.txt` - 已使用的数据记录

---

## 🎓 工作流程

1. **启动**: 程序读取 `config.json` 和 `data.txt`
2. **连接**: 连接到 Mailpit API
3. **提交**: 向 SheerID 提交验证信息
4. **等待**: 等待验证邮件发送到 Mailpit
5. **读取**: 从 Mailpit API 读取邮件
6. **提取**: 提取验证链接和 token
7. **验证**: 自动完成邮件验证
8. **完成**: 记录结果到文件

---

## 💡 提示

### 本地测试
- ✅ 使用 Mailpit，无需真实邮箱
- ✅ 可在 Web 界面查看所有邮件
- ✅ 快速测试和调试

### 生产环境
- ⚠️ 需要真实邮箱（IMAP 或 CloudMail）
- ⚠️ 确保邮箱能正常接收外部邮件

---

## 📞 需要帮助？

1. 查看 `result.txt` 日志文件
2. 访问 Mailpit Web 界面检查邮件
3. 运行 `python test_config.py` 检查配置
4. 查看 `MAILPIT_SETUP.md` 详细说明

---

**准备就绪！** 🚀

只需：
1. 填写 `accessToken`
2. 准备 `data.txt`
3. 运行 `python main.py`

**祝您使用愉快！**

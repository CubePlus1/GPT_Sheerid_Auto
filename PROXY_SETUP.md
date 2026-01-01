# 代理配置指南

## 📋 目录

- [为什么需要代理](#为什么需要代理)
- [代理格式说明](#代理格式说明)
- [配置步骤](#配置步骤)
- [测试代理](#测试代理)
- [常见问题](#常见问题)

---

## 为什么需要代理

使用代理可以：

- **提高成功率** - 避免被 SheerID 检测为频繁请求
- **模拟真实环境** - 使用不同 IP 地址提交验证
- **规避限制** - 绕过可能的 IP 速率限制
- **保护隐私** - 隐藏真实 IP 地址

> **注意**：代理是可选的。如果不配置代理，程序将使用直连模式。

---

## 代理格式说明

程序支持 **4 种代理格式**，可以混合使用：

### 格式 1: SOCKS5 认证代理（推荐）

```
IP地址:端口:用户名:密码
```

**示例：**
```
192.168.1.100:1080:user123:pass456
proxy.example.com:1080:myuser:mypass
```

**适用场景：** 购买的付费 SOCKS5 代理服务

---

### 格式 2: HTTP 无认证代理

```
IP地址:端口
```

**示例：**
```
192.168.1.101:8080
proxy.local.net:3128
```

**适用场景：** 本地代理服务器、公司内网代理

---

### 格式 3: SOCKS5 完整 URL

```
socks5://用户名:密码@IP地址:端口
```

**示例：**
```
socks5://user:pass@proxy.example.com:1080
socks5://admin:123456@10.0.0.1:1080
```

**适用场景：** 从代理服务商复制的完整连接字符串

---

### 格式 4: HTTP/HTTPS 完整 URL

```
http://IP地址:端口
https://IP地址:端口
```

**示例：**
```
http://proxy.example.com:8080
https://secure-proxy.com:443
http://user:pass@proxy.com:8080
```

**适用场景：** HTTP/HTTPS 代理服务

---

## 配置步骤

### 第 1 步：创建代理配置文件

在 `GPT_Sheerid_Auto` 目录下创建 `proxy.txt` 文件：

```powershell
# 在项目目录下
cd D:\0code\py\test\GPT_Sheerid_Auto

# 复制示例文件
Copy-Item proxy.example.txt proxy.txt

# 或直接创建新文件
New-Item -Path proxy.txt -ItemType File
```

### 第 2 步：编辑代理配置

用文本编辑器打开 `proxy.txt`，按照上面的格式添加代理：

```txt
# 代理配置文件 - 每行一个代理，程序会随机选择

# SOCKS5 认证代理（推荐）
192.168.1.100:1080:user123:pass456
proxy1.example.com:1080:myuser:mypass

# HTTP 代理
192.168.1.101:8080
proxy2.example.com:3128

# 完整 URL 格式
socks5://user:pass@proxy3.example.com:1080
http://proxy4.example.com:8080

# 以 # 开头的行是注释，会被忽略
# 空行也会被忽略
```

**重要提示：**
- ✅ 每行一个代理
- ✅ 可以混合使用不同格式
- ✅ 使用 `#` 添加注释
- ✅ 程序会随机选择一个代理使用
- ❌ 不要有多余的空格
- ❌ 确保文件编码为 UTF-8

### 第 3 步：保存并测试

保存 `proxy.txt` 后，运行程序：

```powershell
python main.py
```

你会看到类似的输出：

```
[代理] 使用代理: 192.168.1.100:1080 (认证)
[邮箱] 连接成功
[数据] 共 89 条
```

如果没有配置代理，会显示：

```
[代理] proxy.txt 不存在，将使用直连
[邮箱] 连接成功
[数据] 共 89 条
```

---

## 测试代理

### 方法 1: 使用程序自动测试

运行程序后，观察输出日志：

```
[代理] 使用代理: proxy.example.com:1080
    -> 创建验证请求...
```

如果能正常创建验证请求，说明代理工作正常。

### 方法 2: 手动测试代理

使用 curl 测试代理连通性：

```powershell
# 测试 HTTP 代理
curl -x http://192.168.1.101:8080 https://httpbin.org/ip

# 测试 SOCKS5 代理（需要 curl 支持 SOCKS5）
curl --socks5 192.168.1.100:1080 https://httpbin.org/ip

# 测试认证代理
curl -x socks5://user:pass@proxy.example.com:1080 https://httpbin.org/ip
```

成功时会返回代理服务器的 IP 地址。

### 方法 3: Python 脚本测试

创建 `test_proxy.py` 测试代理：

```python
import requests

# 测试 HTTP 代理
proxies = {
    'http': 'http://192.168.1.101:8080',
    'https': 'http://192.168.1.101:8080'
}

# 测试 SOCKS5 代理
# proxies = {
#     'http': 'socks5://user:pass@192.168.1.100:1080',
#     'https': 'socks5://user:pass@192.168.1.100:1080'
# }

try:
    response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
    print(f"✅ 代理工作正常")
    print(f"代理 IP: {response.json()['origin']}")
except Exception as e:
    print(f"❌ 代理连接失败: {e}")
```

运行：

```powershell
python test_proxy.py
```

---

## 常见问题

### ❓ 我没有代理，可以运行吗？

**可以。** 不配置代理时，程序会使用直连模式。只是在某些情况下可能会触发 SheerID 的速率限制。

---

### ❓ 代理连接失败怎么办？

**排查步骤：**

1. **检查代理格式** - 确保格式正确，没有多余空格
2. **测试代理连通性** - 使用上面的测试方法验证
3. **检查认证信息** - 确认用户名密码正确
4. **尝试其他代理** - 添加多个代理，程序会随机选择

**错误示例：**

```
❌ 192.168.1.100: 1080: user: pass   # 有多余空格
❌ 192.168.1.100:1080:user           # 格式不完整
❌ proxy.example.com                 # 缺少端口

✅ 192.168.1.100:1080:user:pass     # 正确
✅ 192.168.1.101:8080                # 正确
```

---

### ❓ 如何使用多个代理？

在 `proxy.txt` 中每行添加一个代理，程序会随机选择：

```txt
# 添加多个代理，随机使用
192.168.1.100:1080:user1:pass1
192.168.1.101:1080:user2:pass2
socks5://user3:pass3@proxy3.com:1080
http://proxy4.com:8080
```

每次运行程序时会随机选择其中一个使用。

---

### ❓ SOCKS5 和 HTTP 代理有什么区别？

| 特性 | SOCKS5 | HTTP |
|------|--------|------|
| **协议支持** | TCP/UDP | 仅 HTTP/HTTPS |
| **性能** | 更快 | 稍慢 |
| **兼容性** | 需要支持库 | 原生支持 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**推荐使用 SOCKS5 代理**，性能更好且更稳定。

---

### ❓ 代理显示"格式错误"怎么办？

检查 `proxy.txt` 文件：

```powershell
# 查看文件内容
Get-Content proxy.txt

# 检查是否有隐藏字符
Get-Content proxy.txt | Format-Hex
```

确保：
- 文件编码为 UTF-8
- 没有 BOM 头
- 行尾符为 LF 或 CRLF
- 没有隐藏字符

重新创建文件：

```powershell
# 删除旧文件
Remove-Item proxy.txt

# 创建新文件并添加内容
@"
192.168.1.100:1080:user:pass
192.168.1.101:8080
"@ | Out-File -FilePath proxy.txt -Encoding UTF8 -NoNewline
```

---

### ❓ 程序使用代理后变慢了

可能原因：

1. **代理服务器慢** - 尝试其他代理
2. **代理服务器远** - 选择地理位置近的代理
3. **认证失败重试** - 检查用户名密码是否正确

**解决方法：**

```txt
# 只保留快速的代理
192.168.1.100:1080:user:pass    # 快速代理
# 192.168.1.200:1080:user:pass  # 慢速代理（注释掉）
```

---

### ❓ 如何禁用代理？

**方法 1:** 删除或重命名 `proxy.txt`

```powershell
# 重命名为备份
Rename-Item proxy.txt proxy.txt.bak

# 或直接删除
Remove-Item proxy.txt
```

**方法 2:** 清空 `proxy.txt` 内容

```powershell
# 清空文件
Clear-Content proxy.txt
```

**方法 3:** 全部注释掉

```txt
# 192.168.1.100:1080:user:pass
# 192.168.1.101:8080
# 所有代理都注释掉
```

---

### ❓ 推荐的代理服务商

> **免责声明**：以下仅供参考，不构成推荐。请自行评估服务质量。

**付费代理服务：**
- **Bright Data** (luminati.io) - 专业级代理服务
- **Smartproxy** (smartproxy.com) - 性价比高
- **Oxylabs** (oxylabs.io) - 企业级服务
- **922S5** - 国内 SOCKS5 代理

**自建代理：**
- **V2Ray/Xray** - 开源代理工具
- **Shadowsocks** - 轻量级代理
- **Squid** - HTTP 代理服务器

---

## 配置示例

### 示例 1: 单个付费 SOCKS5 代理

```txt
# 使用购买的 SOCKS5 代理
proxy.service.com:1080:myusername:mypassword
```

### 示例 2: 多个代理池

```txt
# 代理池 - 随机选择使用
192.168.1.100:1080:user1:pass1
192.168.1.101:1080:user2:pass2
192.168.1.102:1080:user3:pass3
socks5://user4:pass4@proxy4.com:1080
socks5://user5:pass5@proxy5.com:1080
```

### 示例 3: 本地代理服务器

```txt
# 本地 Shadowsocks
127.0.0.1:1080

# 本地 V2Ray
127.0.0.1:10808
```

### 示例 4: 混合配置

```txt
# SOCKS5 代理（主要使用）
proxy1.com:1080:user1:pass1
proxy2.com:1080:user2:pass2

# HTTP 代理（备用）
192.168.1.101:8080

# 本地代理（测试用）
127.0.0.1:1080
```

---

## 安全建议

🔒 **保护代理凭证安全：**

1. **不要分享 proxy.txt** - 包含认证信息
2. **添加到 .gitignore** - 避免提交到版本控制
3. **定期更换密码** - 提高安全性
4. **使用专用代理** - 不要用于其他用途

**检查 .gitignore：**

```bash
# 确保 proxy.txt 在 .gitignore 中
cat .gitignore | grep proxy.txt
```

如果没有，添加：

```bash
echo "proxy.txt" >> .gitignore
```

---

## 故障排查流程

```
代理问题
    ↓
1. 检查 proxy.txt 是否存在
    ↓
2. 检查代理格式是否正确
    ↓
3. 测试代理连通性（curl/Python）
    ↓
4. 检查认证信息
    ↓
5. 查看程序日志输出
    ↓
6. 尝试禁用代理直连
    ↓
7. 联系代理服务商
```

---

## 总结

✅ **已完成：**
- 创建 `proxy.txt` 文件
- 添加代理配置
- 测试代理连通性
- 运行程序验证

❓ **遇到问题？**

1. 查看上面的常见问题部分
2. 检查程序输出日志
3. 尝试禁用代理测试
4. 查看 README.md 获取更多帮助

---

**相关文档：**
- [README.md](README.md) - 主要文档
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 部署指南
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考

**需要帮助？** 检查日志输出或查看完整文档。

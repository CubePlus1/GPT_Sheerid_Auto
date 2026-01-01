# 📚 文档索引指南

欢迎！这是 GPT SheerID Auto 项目的文档导航中心。

---

## 🎯 快速选择：我应该看哪个文档？

### 📖 "我是新手，想快速上手"

**推荐路径：**
1. 先看 [README.md](README.md) - **5 分钟快速开始**
2. 再看 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - **完整分步指南**
3. 遇到问题查 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - **快速参考表**

### 🔧 "我想深入了解具体配置"

**推荐文档：**
- Webhook 模式 → [WEBHOOK_GUIDE.md](WEBHOOK_GUIDE.md)
- Worker 配置 → [CLOUDFLARE_WORKER_FIX.md](CLOUDFLARE_WORKER_FIX.md)
- 快速查询 → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### 🚨 "我遇到问题需要排查"

**推荐文档：**
1. [README.md#故障排除](README.md#故障排除) - 常见问题解决
2. [QUICK_REFERENCE.md#故障排除速查](QUICK_REFERENCE.md#故障排除速查) - 快速诊断

### 💻 "我只是想快速查阅命令"

**推荐文档：**
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 所有命令、配置、API 端点

---

## 📑 完整文档清单

### 核心文档

| 文档 | 大小 | 阅读时间 | 用途 |
|------|------|---------|------|
| [README.md](README.md) | ⭐⭐⭐⭐ 大 | 20-30 分钟 | **主指南**：项目概述、快速开始、完整步骤、配置说明、故障排除、FAQ |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | ⭐⭐⭐⭐ 大 | 30-45 分钟 | **分步部署**：8 个阶段的详细操作步骤，包括检查清单和验证方法 |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | ⭐⭐⭐ 中 | 5-10 分钟 | **快速查询**：命令速查、API 端点、配置模板、故障排除速查 |

### 专题文档

| 文档 | 用途 |
|------|------|
| [WEBHOOK_GUIDE.md](WEBHOOK_GUIDE.md) | Webhook 邮件接收方式详细教程 |
| [CLOUDFLARE_WORKER_FIX.md](CLOUDFLARE_WORKER_FIX.md) | Cloudflare Worker 配置详解和常见错误 |
| [PROXY_SETUP.md](PROXY_SETUP.md) | **代理配置指南**：4 种代理格式、测试方法、故障排查 |
| [MAILPIT_SETUP.md](MAILPIT_SETUP.md) | Mailpit 本地测试环境配置（开发/测试用） |
| [START_HERE.md](START_HERE.md) | Mailpit 模式快速开始（已基本替代） |

---

## 🗂️ 文件结构说明

```
GPT_Sheerid_Auto/
│
├── 📖 文档文件
│   ├── README.md                    ← 从这里开始！
│   ├── DEPLOYMENT_GUIDE.md          ← 分步部署指南
│   ├── QUICK_REFERENCE.md           ← 快速查阅
│   ├── WEBHOOK_GUIDE.md             ← Webhook 详解
│   └── CLOUDFLARE_WORKER_FIX.md     ← Worker 配置
│
├── 🐍 Python 脚本
│   ├── main.py                      # 主验证程序
│   ├── email_receiver.py            # Flask 邮件服务
│   ├── webhook_email_client.py      # Webhook 客户端
│   ├── test_email_receiver.py       # 服务测试脚本
│   └── test_config.py               # 配置测试脚本
│
├── ⚙️ 配置文件
│   ├── config.json                  # 应用配置（需填写）
│   ├── config.example.json          # 配置示例
│   ├── data.txt                     # 验证数据（需填写）
│   ├── data.example.txt             # 数据示例
│   └── .gitignore                   # Git 忽略配置
│
├── 🌐 Cloudflare 文件
│   └── cloudflare-email-worker.js   # Worker 代码
│
├── 🐳 容器配置
│   └── docker-compose.yml           # Mailpit（可选）
│
├── 📦 项目管理
│   ├── requirements.txt             # Python 依赖
│   ├── pyproject.toml               # 项目配置（可选）
│   └── README.md (本目录)           # 项目说明
│
└── 📝 日志文件
    └── email_receiver.log           # Flask 服务日志（自动生成）
```

---

## 🚀 推荐阅读顺序

### 第一次使用（按顺序阅读）

1. **README.md 的"快速开始"部分** (5 分钟)
   - 了解项目是什么
   - 了解前置要求
   - 完成基础安装

2. **DEPLOYMENT_GUIDE.md 的"第一阶段"** (10 分钟)
   - 验证 Python 环境
   - 安装依赖
   - 下载 Cloudflare Tunnel

3. **DEPLOYMENT_GUIDE.md 的"第二阶段"** (15 分钟)
   - 启动 Flask 服务
   - 验证服务运行
   - 运行测试脚本

4. **README.md 的"详细部署步骤"** (40 分钟)
   - 完成 Cloudflare 配置
   - 创建 Worker
   - 配置 Email Routing

5. **DEPLOYMENT_GUIDE.md 的"第七阶段"** (10 分钟)
   - 获取 ChatGPT Token
   - 配置本地应用
   - 准备数据文件

6. **DEPLOYMENT_GUIDE.md 的"第八阶段"** (15 分钟)
   - 端到端测试
   - 验证所有服务

### 遇到问题时

- **查看故障排除** → [README.md#故障排除](README.md#故障排除)
- **快速命令速查** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Worker 问题** → [CLOUDFLARE_WORKER_FIX.md](CLOUDFLARE_WORKER_FIX.md)
- **Webhook 详情** → [WEBHOOK_GUIDE.md](WEBHOOK_GUIDE.md)

### 后续维护

- **启动服务** → [QUICK_REFERENCE.md#服务启动命令汇总](QUICK_REFERENCE.md#服务启动命令汇总)
- **API 查询** → [QUICK_REFERENCE.md#API-端点速查](QUICK_REFERENCE.md#API-端点速查)
- **配置修改** → [README.md#配置说明](README.md#配置说明)

---

## 📚 按主题查找

### 初始配置

| 需求 | 文档位置 |
|------|---------|
| 快速安装 | [README.md#快速开始](README.md#快速开始5分钟) |
| 分步部署 | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) |
| 环境检查 | [DEPLOYMENT_GUIDE.md#第一阶段](DEPLOYMENT_GUIDE.md#第一阶段基础环境准备10-分钟) |

### Cloudflare 配置

| 需求 | 文档位置 |
|------|---------|
| Email Routing | [README.md#步骤-4](README.md#步骤-4-cloudflare-email-routing-配置) |
| Worker 创建 | [README.md#步骤-5](README.md#步骤-5-cloudflare-worker-配置) 或 [CLOUDFLARE_WORKER_FIX.md](CLOUDFLARE_WORKER_FIX.md) |
| Tunnel 设置 | [README.md#步骤-3](README.md#步骤-3-cloudflare-tunnel-配置) 或 [DEPLOYMENT_GUIDE.md#第三阶段](DEPLOYMENT_GUIDE.md#第三阶段cloudflare-tunnel-配置10-分钟) |

### 本地应用

| 需求 | 文档位置 |
|------|---------|
| Flask 服务 | [README.md#步骤-2](README.md#步骤-2-本地-flask-服务配置) 或 [DEPLOYMENT_GUIDE.md#第二阶段](DEPLOYMENT_GUIDE.md#第二阶段本地服务配置15-分钟) |
| 配置文件 | [README.md#config.json-详解](README.md#configjson-详解) |
| 数据文件 | [README.md#data.txt-数据文件](README.md#datatxt-数据文件) |
| **代理配置** | [PROXY_SETUP.md](PROXY_SETUP.md) - 代理格式、测试、故障排查 |

### 测试 & 验证

| 需求 | 文档位置 |
|------|---------|
| 本地服务测试 | [README.md#测试-1](README.md#测试-1-本地服务验证) |
| Tunnel 测试 | [README.md#测试-2](README.md#测试-2-tunnel-连接验证) |
| 邮件转发 | [README.md#测试-3](README.md#测试-3-邮件转发验证) |
| Worker 日志 | [README.md#测试-4](README.md#测试-4-worker-日志检查) |
| 完整流程 | [README.md#测试-5](README.md#测试-5-完整流程测试) |

### 故障排除

| 问题 | 文档位置 |
|------|---------|
| Flask 连接失败 | [README.md#❌-cannot-connect-to-localhost5000](README.md#-cannot-connect-to-localhost5000) |
| Tunnel 404 错误 | [README.md#❌-tunnel-url-returns-404](README.md#-tunnel-url-returns-404) |
| Worker 错误 | [README.md#❌-worker-throws-error-unauthorized](README.md#-worker-throws-error-unauthorized) |
| 邮件未收到 | [README.md#❌-email-not-received-in-flask-service](README.md#-email-not-received-in-flask-service) |
| 链接提取失败 | [README.md#❌-no-verification-link-extracted](README.md#-no-verification-link-extracted) |

### 常见问题 (FAQ)

| 问题 | 文档位置 |
|------|---------|
| Cloudflare DNS | [README.md#q-我需要拥有-cloudflare-dns-吗](README.md#q-我需要拥有-cloudflare-dns-吗) |
| 其他邮件服务 | [README.md#q-可以使用其他邮件服务吗](README.md#q-可以使用其他邮件服务吗) |
| Token 过期 | [README.md#q-accesstoken-会过期吗](README.md#q-accesstoken-会过期吗) |
| 批量验证 | [README.md#q-是否支持批量验证](README.md#q-是否支持批量验证) |
| Tunnel URL | [README.md#q-tunnel-url-如何保持不变](README.md#q-tunnel-url-如何保持不变) |

---

## 🎓 学习路径建议

### 路径 A：快速启动者（时间有限）

**目标**：尽快让系统跑起来  
**总耗时**：1.5-2 小时

```
1. README.md (快速开始部分)        ← 5 分钟
2. DEPLOYMENT_GUIDE.md (扫一遍)     ← 15 分钟
3. 按 DEPLOYMENT_GUIDE 的 8 个阶段  ← 1.5 小时
4. 运行 python main.py             ← 完成！
```

### 路径 B：深度理解者（想完全掌握）

**目标**：充分理解每个组件的工作原理  
**总耗时**：3-4 小时

```
1. README.md (完整阅读)                 ← 30 分钟
2. DEPLOYMENT_GUIDE.md (详细阅读)       ← 45 分钟
3. WEBHOOK_GUIDE.md (理解 Webhook)      ← 30 分钟
4. CLOUDFLARE_WORKER_FIX.md (理解 Worker) ← 30 分钟
5. QUICK_REFERENCE.md (作为速查表)      ← 15 分钟
6. 逐步部署并验证每个阶段              ← 1.5 小时
```

### 路径 C：维护者（已部署，需要维护）

**目标**：了解如何监控、排查、更新系统  
**总耗时**：30-45 分钟

```
1. QUICK_REFERENCE.md (快速参考)        ← 10 分钟
2. README.md (故障排除部分)             ← 15 分钟
3. DEPLOYMENT_GUIDE.md (参考手册)       ← 10 分钟
4. 加入日常检查清单                     ← 完成！
```

---

## 🔍 高效查找指南

### 我知道关键词，但不知道在哪个文档

使用 Ctrl+F 在以下文档中搜索：

| 关键词类型 | 推荐搜索位置 |
|----------|-----------|
| 命令 | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| 配置 | [README.md](README.md) 的"配置说明"部分 |
| 步骤 | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) |
| API | [QUICK_REFERENCE.md#API-端点速查](QUICK_REFERENCE.md#API-端点速查) |
| 错误 | [README.md#故障排除](README.md#故障排除) |
| Worker | [CLOUDFLARE_WORKER_FIX.md](CLOUDFLARE_WORKER_FIX.md) |

### 文档关键词索引

**README.md 关键词：**
- 快速开始, 完整部署, 配置, 测试, 故障排除, FAQ, Email Routing, Worker, Tunnel

**DEPLOYMENT_GUIDE.md 关键词：**
- 第一阶段, 第二阶段, ..., 第八阶段, 终端, 验证, 环境变量, 清单

**QUICK_REFERENCE.md 关键词：**
- 启动命令, API 端点, 配置模板, 测试命令, 故障排除, 日志查看

**WEBHOOK_GUIDE.md 关键词：**
- Webhook 模式, Worker 代码, Flask, 邮件接收, 实时处理

**CLOUDFLARE_WORKER_FIX.md 关键词：**
- Worker 创建, 错误修复, 环境变量, Email Route, 调试

---

## 📞 需要帮助？

### 常见情况处理

| 情况 | 推荐操作 |
|------|---------|
| 不知道从哪开始 | 阅读本文件，按推荐路径走 |
| 卡在某个步骤 | 查看 DEPLOYMENT_GUIDE.md 的对应阶段 |
| 看不懂某个配置 | 查看 README.md 的"配置说明"部分 |
| 遇到错误信息 | 在 README.md 的"故障排除"中搜索错误内容 |
| 找不到某个命令 | 使用 Ctrl+F 在 QUICK_REFERENCE.md 中搜索 |
| 需要快速回顾 | 查看 QUICK_REFERENCE.md |

---

## 📊 文档统计

| 文档 | 字数 | 章节 | 代码块 | 更新时间 |
|------|------|------|--------|---------|
| README.md | ~8000 | 12 | 20+ | 2025-12-31 |
| DEPLOYMENT_GUIDE.md | ~7000 | 8 | 15+ | 2025-12-31 |
| QUICK_REFERENCE.md | ~5000 | 15 | 30+ | 2025-12-31 |
| WEBHOOK_GUIDE.md | ~8000 | 10 | 25+ | 原创 |
| CLOUDFLARE_WORKER_FIX.md | ~6000 | 8 | 20+ | 原创 |

**总文档字数**：~34000 字  
**总代码示例**：110+ 个

---

## ✨ 文档特色

- ✅ **可搜索** - 使用 Ctrl+F 快速定位内容
- ✅ **结构清晰** - 使用标题、表格、列表组织信息
- ✅ **示例丰富** - 每个步骤都有具体的命令和输出示例
- ✅ **分层递进** - 从快速开始到深度理解的完整路径
- ✅ **跨引用** - 在相关文档间建立链接便于导航
- ✅ **实用性强** - 专注解决实际问题

---

## 🎯 下一步

根据您的情况选择对应的文档：

1. **新用户** → 开始阅读 [README.md](README.md) 的"快速开始"部分
2. **逐步部署** → 按 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) 的 8 个阶段操作
3. **遇到问题** → 查看 [README.md#故障排除](README.md#故障排除)
4. **快速查询** → 使用 [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

**文档索引版本**：1.0  
**最后更新**：2025-12-31  
**维护者**：dy安心大油条

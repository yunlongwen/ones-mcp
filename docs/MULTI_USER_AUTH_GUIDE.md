# 📘 多用户认证模式使用指南

> ⭐ **这是项目的默认且推荐运行模式**

## 🎯 架构说明

本项目采用**多用户认证模式**，每个用户使用自己的 ONES 账号连接服务：

### ✨ 单用户模式 vs 多用户认证模式

| 项目 | 单用户模式（不推荐） | 多用户认证模式（推荐）⭐ |
|------|---------------------|----------------------|
| **认证信息位置** | Server端 `config.json` | Client端 `mcp.json` Headers |
| **用户数量** | 单用户（共享账号） | 多用户（各自账号） |
| **权限隔离** | ❌ 无隔离 | ✅ 完全隔离 |
| **安全性** | ⚠️ 所有人共用一个账号 | ✅ 各自使用自己的账号 |
| **审计追溯** | ❌ 无法区分操作者 | ✅ 可追溯到个人 |
| **服务端配置** | 需要配置用户凭据 | 只需配置 API 地址和团队 UUID |

---

## 📁 配置文件说明

### 1️⃣ Server端配置 (`config.json`)

**只需配置全局信息**，不包含任何用户凭据：

```json
{
  "ones_api_url": "http://172.16.81.11:30011/project/api",
  "team_uuid": "y7bXyZLk"
}
```

| 字段 | 说明 | 必填 |
|------|------|------|
| `ones_api_url` | ONES API地址 | ✅ |
| `team_uuid` | ONES团队UUID | ✅ |

### 2️⃣ Client端配置 (Cursor的 `mcp.json`)

**每个用户配置自己的认证信息**：

```json
{
  "mcpServers": {
    "ones-wiki": {
      "url": "http://127.0.0.1:8000/sse",
      "description": "ONES Wiki知识库",
      "headers": {
        "x-user-email": "zhangsan@adb.com",
        "x-user-password": "your-password",
        "x-default-space-uuid": "PLWdQVb5",
        "x-accessible-spaces": "C7ReCVYN,PLWdQVb5,Vj2fPcS7"
      }
    }
  }
}
```

#### HTTP Headers 参数说明

| Header 字段 | 说明 | 必填 | 示例 |
|------------|------|------|------|
| `x-user-email` | ONES账号邮箱 | ✅ | `zhangsan@adb.com` |
| `x-user-password` | ONES账号密码 | ✅ | `your-password` |
| `x-default-space-uuid` | 默认搜索空间UUID | ❌ | `PLWdQVb5` |
| `x-accessible-spaces` | 可访问空间列表（逗号分隔） | ❌ | `C7ReCVYN,PLWdQVb5,Vj2fPcS7` |

---

## 🚀 部署步骤

### Step 1: 更新Server端配置

在服务器上修改 `config.json`，移除用户凭据：

```bash
cd ~/mcp-server
# 备份原配置
cp config.json config.json.bak

# 编辑配置（只保留 ones_api_url 和 team_uuid）
nano config.json
```

### Step 2: 更新Server端代码

```bash
# 上传新版本的 server_http_simple.py
scp server_http_simple.py wenyl@127.0.0.1:~/mcp-server/

# 重启服务
ssh wenyl@127.0.0.1
sudo systemctl restart ones-wiki-mcp
sudo systemctl status ones-wiki-mcp
```

### Step 3: 配置Cursor客户端

**每个用户**在自己的Cursor中配置（Mac/Linux：`~/.cursor/mcp.json`，Windows：`%APPDATA%\Cursor\mcp.json`）：

```json
{
  "mcpServers": {
    "ones-wiki": {
      "url": "http://127.0.0.1:8000/sse",
      "headers": {
        "x-user-email": "你的邮箱@adb.com",
        "x-user-password": "你的密码",
        "x-default-space-uuid": "PLWdQVb5",
        "x-accessible-spaces": "C7ReCVYN,PLWdQVb5,Vj2fPcS7"
      }
    }
  }
}
```

⚠️ **注意**：每个人要使用**自己的账号和密码**！

### Step 4: 测试连接

1. 重启Cursor
2. 在Cursor中输入：`在wiki中搜索 女娲平台`
3. 查看服务器日志：`ssh wenyl@127.0.0.1 "sudo journalctl -u ones-wiki-mcp -f"`
4. 应该能看到类似日志：`用户 zhangsan@adb.com 认证成功`

---

## 🔐 架构说明

### 认证流程

```
┌─────────────────┐
│ Cursor (Client) │
│  用户A: a@x.com │
└────────┬────────┘
         │ HTTP Headers:
         │ x-user-email: a@x.com
         │ x-user-password: ***
         ↓
┌─────────────────────────────┐
│  MCP Server (127.0.0.1)  │
├─────────────────────────────┤
│ 1. 提取Headers中的用户凭据   │
│ 2. 创建用户专属WikiClient    │
│ 3. 调用ONES API登录         │
│ 4. 登录成功后建立SSE连接     │
│ 5. 创建独立的MCP Server实例  │
└────────┬────────────────────┘
         │ API请求带上用户Token
         ↓
┌─────────────────────────────┐
│  ONES Wiki API (172.16.81.11)│
└─────────────────────────────┘
```

### 多用户隔离

- **会话隔离**：每个SSE连接有独立的 `WikiClient` 实例
- **权限隔离**：使用各自的ONES账号，权限由ONES系统控制
- **数据隔离**：搜索结果、页面访问都基于各自的权限

---

## ✅ 验证多用户模式

### 场景1：不同用户同时连接

```bash
# 服务器日志应该显示：
用户 zhangsan@adb.com 认证成功
用户 lisi@adb.com 认证成功
用户 wangwu@adb.com 认证成功
```

### 场景2：权限隔离验证

- 用户A有空间1、2、3权限
- 用户B只有空间2权限
- 用户B搜索时只能看到空间2的结果

---

## 🛠️ 常见问题

### Q1: 认证失败怎么办？

**症状**：Cursor提示 `Loading tools...` 或 `认证失败`

**排查**：
1. 检查邮箱和密码是否正确
2. 检查ONES账号是否有效
3. 查看服务器日志：`sudo journalctl -u ones-wiki-mcp -f`

### Q2: Headers配置不生效？

**确认**：
- Headers中的key必须是小写：`x-user-email`（不是 `X-User-Email`）
- 密码中不要包含特殊字符（如引号），或使用转义

### Q3: 如何获取自己的space_uuid？

**方法1**：联系管理员
**方法2**：在Cursor中询问：`我有哪些Wiki空间权限？`

### Q4: 多个空间怎么配置？

使用逗号分隔，不要有空格：
```json
"x-accessible-spaces": "C7ReCVYN,PLWdQVb5,Vj2fPcS7"
```

---

## 📊 监控与日志

### 查看实时日志

```bash
# 查看服务器日志
sudo journalctl -u ones-wiki-mcp -f

# 查看特定用户的操作
sudo journalctl -u ones-wiki-mcp | grep "zhangsan@adb.com"

# 查看认证成功的用户
sudo journalctl -u ones-wiki-mcp | grep "认证成功"
```

### 日志示例

```
2025-11-06 10:15:23 - INFO - 收到SSE连接请求，提取用户认证信息...
2025-11-06 10:15:23 - INFO - 用户: zhangsan@adb.com
2025-11-06 10:15:24 - INFO - 用户 zhangsan@adb.com 认证成功
2025-11-06 10:15:24 - INFO - SSE连接已建立，开始服务用户: zhangsan@adb.com
2025-11-06 10:15:30 - INFO - [zhangsan@adb.com] 调用工具: search_pages, 参数: {'keyword': '女娲平台'}
```

---

## 🎉 优势总结

### ✅ 安全性
- 不再共享账号
- 密码由用户自己管理
- 操作可追溯到个人

### ✅ 灵活性
- 每个用户可配置不同的搜索范围
- 权限由ONES系统统一管理
- 无需重启服务器即可添加新用户

### ✅ 可维护性
- 服务器配置简化（只有2个字段）
- 不需要为每个新用户修改服务器
- 问题排查更容易（日志带用户标识）

---

## 📚 相关文档

- [完整教程](./MCP实战：将内部Wiki接入Cursor完整教程.md)
- [客户端配置示例](./client_config_example.json)
- [服务器配置示例](./config.json)

---

## 🔮 后续优化方向

1. **Token认证**：避免在配置文件中明文存储密码
2. **Web登录页面**：用户通过Web界面登录获取Token
3. **OAuth2/SSO集成**：支持企业统一认证
4. **细粒度权限控制**：在MCP层面添加额外的权限控制

---

如有问题，请联系管理员或查看服务器日志！🚀



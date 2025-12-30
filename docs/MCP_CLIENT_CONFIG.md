# MCP 客户端配置指南

## 🎯 推荐配置方式：HTTP/SSE 模式（多用户认证）

### 1. 在 Cursor 中配置

编辑 `~/.cursor/mcp.json`（Windows: `%APPDATA%\Cursor\mcp.json`）：

```json
{
  "mcpServers": {
    "ones-wiki": {
      "url": "http://127.0.0.1:8000/sse",
      "description": "ONES Wiki知识库（多用户认证）",
      "headers": {
        "x-user-email": "your_email@company.com",
        "x-user-password": "your_password",
        "x-default-space-uuid": "PLWdQVb5",
        "x-accessible-spaces": "C7ReCVYN,PLWdQVb5,Vj2fPcS7"
      }
    }
  }
}
```

> ⚠️ **重要**：请使用**你自己的** ONES 账号和密码，不要与他人共享！

### 2. 配置说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `url` | 服务器地址（SSE 端点） | `http://127.0.0.1:8000/sse` |
| `description` | 服务描述（可选） | `ONES Wiki知识库` |
| `x-user-email` | ONES 用户邮箱 | `your_email@company.com` |
| `x-user-password` | ONES 用户密码 | `your_password` |
| `x-default-space-uuid` | 默认空间 UUID | `PLWdQVb5` |
| `x-accessible-spaces` | 可访问的空间列表（逗号分隔） | `space1,space2,space3` |

### 3. 优势

✅ **多用户支持**：每个用户配置自己的凭据，互不干扰  
✅ **服务端配置简单**：服务端只需配置 API 地址和团队 UUID（仅 2 个字段）  
✅ **集中部署**：一台服务器，所有人使用  
✅ **权限隔离**：每个用户只能访问自己权限范围内的空间  

## 🔄 另一种配置方式：stdio 模式（本地运行）

如果你想在本地运行 MCP 服务器（不推荐，需要每个人都部署）：

### Cursor 配置

```json
{
  "mcpServers": {
    "ones-wiki": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

### Claude Desktop 配置

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "ones-wiki": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

**缺点**：
- ❌ 每个用户需要自己部署
- ❌ 需要本地安装 Python 环境
- ❌ 配置文件管理麻烦
- ❌ 无法集中管理和更新

## 📝 如何获取配置参数

### 获取服务器地址

```bash
# 在服务器上查看 IP
hostname -I

# 或者
ip addr show | grep inet
```

服务器地址格式：`http://<服务器IP>:8000/sse`

### 获取空间 UUID

1. 打开 ONES Wiki 页面
2. 查看浏览器地址栏
3. 格式：`https://your-ones.com/wiki/#/team/{team_uuid}/space/{space_uuid}/page/{page_uuid}`
4. 复制 `{space_uuid}` 部分

### 获取多个空间 UUID

如果你可以访问多个空间，将它们用逗号分隔：

```json
"x-accessible-spaces": "space1,space2,space3"
```

## 🔍 验证配置

### 1. 检查服务器状态

```bash
curl http://127.0.0.1:8000/health
```

应该返回：`{"status":"healthy"}`

### 2. 测试 SSE 连接

```bash
curl -N -H "x-user-email: your_email@company.com" \
     -H "x-user-password: your_password" \
     http://127.0.0.1:8000/sse
```

应该建立 SSE 连接并返回初始化消息。

### 3. 在 Cursor 中测试

配置完成后，在 Cursor 中：
1. 重启 Cursor
2. 打开 AI 对话
3. 输入：`请获取 ONES Wiki 页面树`
4. 应该能看到页面列表

## 🛠️ 故障排查

### 问题 1: 连接失败

**检查**：
```bash
# 1. 服务器是否运行
ps aux | grep server_http_simple

# 2. 端口是否开放
sudo netstat -tlnp | grep 8000

# 3. 防火墙规则
sudo ufw status
```

### 问题 2: 认证失败

**检查**：
- 邮箱和密码是否正确
- ONES 账号是否有 Wiki 访问权限
- 查看服务器日志：`tail -f mcp-server.log`

### 问题 3: 空间访问失败

**检查**：
- 空间 UUID 是否正确
- 账号是否有该空间的访问权限
- 在 ONES Wiki 网页端确认能否访问该空间

## 🎉 推荐配置总结

**服务端**（运维人员一次性部署）：
```bash
cd ~/mcp-server
bash deploy_simple.sh
```

**客户端**（每个用户自己配置）：
```json
{
  "ones-wiki": {
    "url": "http://127.0.0.1:8000/sse",
    "description": "ONES Wiki",
    "headers": {
      "x-user-email": "your_email@company.com",
      "x-user-password": "your_password",
      "x-default-space-uuid": "your_space_uuid",
      "x-accessible-spaces": "space1,space2"
    }
  }
}
```

就这么简单！🚀


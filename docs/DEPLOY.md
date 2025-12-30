# 部署指南

## 前置要求

- Python 3.10 或更高版本
- Linux 服务器（Ubuntu/Debian）
- 可访问的 ONES Wiki 系统

## 快速部署

### 1. 克隆或下载项目

```bash
cd ~
git clone <repository-url>
cd mcp-server
```

### 2. 配置 ONES 信息

```bash
cp config.example.json config.json
nano config.json  # 或使用 vim
```

编辑 `config.json`：

```json
{
  "ones_api_url": "http://your-ones-server:port/project/api",
  "team_uuid": "your_team_uuid"
}
```

**注意**：服务端只需要配置 API 地址和团队 UUID，不需要用户信息。

### 3. 一键部署

```bash
bash deploy.sh
```

就这么简单！

## 部署脚本说明

`deploy.sh` 会自动完成：

1. ✅ 检查 Python 版本
2. ✅ 创建虚拟环境（如果不存在）
3. ✅ 安装所有依赖
4. ✅ 启动服务

## 验证部署

```bash
# 检查服务是否运行
ps aux | grep server_http_simple

# 检查健康状态
curl http://localhost:8000/health
# 应该返回: {"status":"healthy"}

# 查看日志
tail -f mcp-server.log
```

## 常用命令

### 查看日志

```bash
# 实时日志
tail -f mcp-server.log

# 最近 100 行
tail -n 100 mcp-server.log

# 搜索错误
grep -i error mcp-server.log
```

### 停止服务

```bash
pkill -f server_http_simple
```

### 重启服务

```bash
bash deploy.sh
```

## 客户端配置

部署完成后，在 Cursor 的 `~/.cursor/mcp.json` 中配置：

```json
{
  "ones-wiki": {
    "url": "http://your-server-ip:8000/sse",
    "description": "ONES Wiki知识库",
    "headers": {
      "x-user-email": "your_email@company.com",
      "x-user-password": "your_password",
      "x-default-space-uuid": "your_space_uuid",
      "x-accessible-spaces": "space1,space2,space3"
    }
  }
}
```

## 故障排查

### 问题 1: Python 版本过低

**错误**: `Python 3.x is not supported`

**解决**: 升级到 Python 3.10+

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.10 python3.10-venv
```

### 问题 2: 虚拟环境创建失败

**错误**: `The virtual environment was not created successfully`

**解决**: 安装 venv 模块

```bash
sudo apt-get install python3-venv
```

### 问题 3: 依赖安装失败

**错误**: `ModuleNotFoundError` 或 `pip install failed`

**解决**: 

```bash
# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt
```

### 问题 4: 端口被占用

**错误**: `Address already in use`

**解决**:

```bash
# 查找占用端口的进程
sudo lsof -i :8000

# 停止进程
sudo kill -9 <PID>

# 或修改端口（在 server_http_simple.py 中）
```

### 问题 5: 服务启动后立即退出

**解决**: 查看日志找出原因

```bash
tail -n 50 mcp-server.log
```

常见原因：
- 配置文件错误
- 依赖缺失
- ONES API 连接失败

## 生产环境建议

### 使用 systemd（可选）

创建 `/etc/systemd/system/ones-wiki-mcp.service`:

```ini
[Unit]
Description=ONES Wiki MCP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/home/your-user/mcp-server
Environment="PATH=/home/your-user/mcp-server/venv/bin"
ExecStart=/home/your-user/mcp-server/venv/bin/python3 server_http_simple.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start ones-wiki-mcp
sudo systemctl enable ones-wiki-mcp
```

### 日志轮转

创建 `/etc/logrotate.d/ones-wiki-mcp`:

```
/home/your-user/mcp-server/mcp-server.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

## 安全建议

1. **配置文件权限**: `chmod 600 config.json`
2. **使用专用账号**: 不要使用个人 ONES 账号
3. **防火墙配置**: 只开放必要端口
4. **定期更新**: `git pull && bash deploy.sh`

---

**就这么简单！** 3 步完成部署：配置 → 运行脚本 → 完成！🚀

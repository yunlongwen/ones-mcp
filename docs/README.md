# ONES Wiki MCP Server - 完整文档

> 这是详细的技术文档。快速开始请看 [快速配置指南](快速配置指南.md)

## 📚 文档导航

### 快速开始
- **[快速配置指南](快速配置指南.md)** ⭐ - 2 分钟快速配置
- **[部署指南](DEPLOY.md)** - 服务端详细部署步骤
- **[客户端配置](MCP_CLIENT_CONFIG.md)** - 客户端配置详细说明

### 参考文档
- **[更新日志](CHANGELOG.md)** - 版本更新记录
- **[项目结构](PROJECT_STRUCTURE.md)** - 文件结构说明
- **[API 研究](ONES_WIKI_API_RESEARCH.md)** - ONES Wiki API 文档
- **[多用户认证](MULTI_USER_AUTH_GUIDE.md)** - 多用户认证技术细节
- **[完整教程](MCP实战：将内部Wiki接入Cursor完整教程.md)** - 从零开始的完整教程

### 整理记录
- **[文件整理总结](文件整理总结.md)** - 项目文件整理记录

## 🎯 推荐阅读路径

### 新用户
1. [快速配置指南](快速配置指南.md) - 了解如何配置
2. [部署指南](DEPLOY.md) - 部署服务器
3. [客户端配置](MCP_CLIENT_CONFIG.md) - 配置 Cursor

### 运维人员
1. [部署指南](DEPLOY.md) - 服务器部署
2. [多用户认证](MULTI_USER_AUTH_GUIDE.md) - 多用户架构
3. [项目结构](PROJECT_STRUCTURE.md) - 了解文件结构

### 开发人员
1. [API 研究](ONES_WIKI_API_RESEARCH.md) - API 文档
2. [多用户认证](MULTI_USER_AUTH_GUIDE.md) - 技术实现
3. [更新日志](CHANGELOG.md) - 了解最新变化

## 🚀 核心功能

### 完整的内容解析

- ✅ **代码块**：PlantUML、Mermaid、Python、Java 等所有语言
- ✅ **表格**：自动转换为 Markdown 格式
- ✅ **图片/附件**：提取图片 URL 和描述
- ✅ **文档结构**：完整保留标题、列表、段落层级

### 多用户支持

- ✅ HTTP/SSE 模式，支持多用户同时使用
- ✅ 每个用户使用自己的 ONES 凭据
- ✅ 权限隔离，安全可靠

### 易于部署

- ✅ 一键部署脚本（Linux/Windows）
- ✅ 自动依赖检查和安装
- ✅ 健康检查和日志管理

## 📖 详细功能说明

### 1. 获取知识库空间列表

```
"获取所有知识库空间"
```

返回所有可访问的空间列表。

### 2. 获取页面树结构

```
"获取空间 PLWdQVb5 的页面列表"
```

返回指定空间的页面树结构。

### 3. 获取页面内容

```
"显示页面 A9Lygq2T 的内容"
```

返回页面的完整内容，包括：
- 标题、正文、作者、创建时间
- **代码块**（PlantUML、Mermaid、代码）
- **表格**（Markdown 格式）
- **图片/附件**（含 URL）

### 4. 搜索页面

```
"搜索 wiki 中关于点检的文档"
```

在知识库中搜索关键词。

### 5. 查看页面历史

```
"显示页面 A9Lygq2T 的历史版本"
```

查看页面的修改历史。

## 🔧 配置说明

### 服务端配置（config.json）

```json
{
  "ones_api_url": "http://your-ones-server:port/project/api",
  "team_uuid": "your_team_uuid"
}
```

**注意**：服务端不需要配置用户信息！

### 客户端配置（mcp.json）

```json
{
  "ones-wiki": {
    "url": "http://server-ip:8000/sse",
    "headers": {
      "x-user-email": "your_email@company.com",
      "x-user-password": "your_password",
      "x-default-space-uuid": "your_space_uuid",
      "x-accessible-spaces": "space1,space2,space3"
    }
  }
}
```

## 🛠️ 故障排查

### 常见问题

1. **连接失败**
   - 检查服务器是否运行：`ps aux | grep server_http_simple`
   - 检查端口是否开放：`sudo netstat -tlnp | grep 8000`

2. **认证失败**
   - 检查邮箱和密码是否正确
   - 查看服务器日志：`tail -f mcp-server.log`

3. **空间访问失败**
   - 检查空间 UUID 是否正确
   - 确认账号有该空间的访问权限

详细的故障排查请看 [部署指南](DEPLOY.md)。

## 📞 获取帮助

- 查看 [快速配置指南](快速配置指南.md)
- 查看 [部署指南](DEPLOY.md)
- 查看 [客户端配置](MCP_CLIENT_CONFIG.md)
- 提交 GitHub Issue

## 🎉 开始使用

1. **服务端部署**：运行 `bash deploy_simple.sh`（Linux）或 `deploy.bat`（Windows）
2. **客户端配置**：编辑 `~/.cursor/mcp.json`
3. **开始使用**：在 Cursor 中使用 AI 访问 Wiki！

---

返回 [项目主页](../README.md)

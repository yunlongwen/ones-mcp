# ONES Wiki MCP Server

[English](./README_EN.md) | 简体中文

## 📖 项目背景

ONES 官方提供了 [ONES Copilot](https://docs.ones.cn/wiki/#/team/6mRWUuNv/space/JwHAUL1L/page/UEQ6z54V) 产品，包含了 MCP 服务器功能。但 ONES Copilot 需要**额外付费授权**，对于未购买该服务的团队来说无法使用。

本项目通过调用 **ONES 现有的开放 API**（Wiki API），为未购买 ONES Copilot 的团队提供了一个**开源、免费**的 MCP 服务器实现方案，让 AI 助手（如 Cursor、Claude Desktop）能够访问和查询公司内网的 ONES Wiki 知识库。

### 🎯 核心价值

- 💰 **零成本**：无需购买 ONES Copilot 授权，利用现有 ONES API
- 🔓 **开源免费**：代码完全开源，可自由部署和定制
- 🏢 **企业友好**：支持内网部署，数据不出公司网络
- 👥 **多用户支持**：支持团队多人同时使用，每人使用自己的账号
- 🔐 **权限隔离**：基于 ONES 原有权限体系，确保数据安全

## 📝 项目简介

这是一个用于连接 ONES Wiki 知识库的 MCP（Model Context Protocol）服务器，允许 AI 助手通过 MCP 协议访问和查询公司内网的 ONES Wiki 知识库。

## ✨ 主要特性

- 🔐 **多用户认证模式** - 每个用户使用自己的 ONES 账号，权限隔离
- 📚 获取知识库空间列表
- 🌲 查看知识库页面树结构
- 📄 **读取页面完整内容**，包括：
  - 📝 标题、段落、列表等富文本内容
  - 💻 代码块（支持各种编程语言语法高亮）
  - 📊 表格数据
  - 🖼️ 图片引用
  - 📈 **图表内容**（Mermaid 时序图/流程图、PlantUML 类图/时序图等）
- 🔍 搜索知识库页面
- 📜 查看页面历史版本
- 🌐 HTTP/SSE 服务端部署，支持多人同时使用

### 🎯 最新更新（v2.0）

**完整的内容解析支持**：
- ✅ **代码块**：PlantUML、Mermaid、Python、Java 等所有语言
- ✅ **表格**：自动转换为 Markdown 格式
- ✅ **图片/附件**：提取图片 URL 和描述
- ✅ **文档结构**：完整保留标题、列表、段落层级

> 现在 AI 可以直接分析 Wiki 中的 PlantUML 系统架构图、时序图等！

## 🚀 快速开始

### 第一步：服务端部署

#### Linux 服务器部署（推荐）

```bash
# 1. 克隆仓库
git clone <repository-url>
cd mcp-server

# 2. 配置服务端信息（仅需 2 个字段）
cp config.example.json config.json
nano config.json

# config.json 内容：
# {
#   "ones_api_url": "http://your-ones-server:port/project/api",
#   "team_uuid": "your_team_uuid"
# }

# 3. 一键部署
bash deploy.sh
```

#### Windows 本地运行

```batch
# 1. 配置服务端信息
copy config.example.json config.json
notepad config.json

# 2. 一键部署
deploy.bat
```

### 第二步：客户端配置（每个用户独立配置）

编辑 `~/.cursor/mcp.json`（Windows: `%APPDATA%\Cursor\mcp.json`）：

```json
{
  "mcpServers": {
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
}
```

> ⚠️ **重要**：每个用户使用自己的 ONES 账号和密码！

## 📚 文档

- **[快速配置指南](docs/快速配置指南.md)** / **[Quick Start Guide](docs/QUICK_START.md)** - 最简洁的配置说明 ⭐
- **[多用户认证指南](docs/MULTI_USER_AUTH_GUIDE.md)** - 多用户认证模式详解 ⭐
- **[部署指南](docs/DEPLOY.md)** - 详细的服务端部署步骤
- **[客户端配置](docs/MCP_CLIENT_CONFIG.md)** - 客户端配置详细说明
- **[更新日志](docs/CHANGELOG.md)** - 版本更新记录
- **[API 研究](docs/ONES_WIKI_API_RESEARCH.md)** - ONES Wiki API 文档

## 📁 项目结构

```
ones-wiki-mcp-server/
├── server_http_simple.py      # HTTP/SSE 服务器（生产环境，多用户认证）⭐
├── server.py                   # stdio 模式服务器（本地测试用）
├── ones_wiki_client.py         # ONES Wiki 客户端
├── config.json                 # 服务端配置（仅2个字段：API地址和团队UUID）
├── requirements.txt            # Python 依赖
├── deploy.sh                   # Linux 一键部署
├── deploy.bat                  # Windows 一键部署
└── docs/                       # 文档目录
    ├── MULTI_USER_AUTH_GUIDE.md # 多用户认证指南 ⭐
    ├── 快速配置指南.md          # 快速开始
    ├── DEPLOY.md                # 部署指南
    ├── MCP_CLIENT_CONFIG.md     # 客户端配置
    └── ...
```

## 🔧 常用命令

### Linux

```bash
# 部署/重启
bash deploy_simple.sh

# 查看日志
tail -f mcp-server.log

# 停止服务
pkill -f server_http_simple
```

### Windows

```batch
# 启动服务
deploy.bat

# 停止服务（Ctrl+C）
```

## 💡 使用示例

配置完成后，在 Cursor 中可以这样使用：

### 基础功能

- **搜索文档**："搜索 wiki 中关于点检的文档"
- **获取页面内容**："显示页面 A9Lygq2T 的内容"
- **查看页面列表**："获取知识库 PLWdQVb5 的所有页面"

### 高级功能：图表分析 📊

本 MCP 服务器支持**完整解析** Wiki 页面中的各类图表，包括：

#### 支持的图表类型

- 📈 **Mermaid 图表**
  - 流程图（Flowchart）
  - 时序图（Sequence Diagram）
  - 类图（Class Diagram）
  - 状态图（State Diagram）
  - 甘特图（Gantt Chart）
  
- 📐 **PlantUML 图表**
  - 类图（Class Diagram）
  - 时序图（Sequence Diagram）
  - 用例图（Use Case Diagram）
  - 组件图（Component Diagram）
  - 活动图（Activity Diagram）

#### 实际应用场景

- 🔍 **理解系统架构**："分析这个类图中各个模块的依赖关系"
- 📋 **解读业务流程**："这个时序图描述的是什么业务流程？"
- 🔄 **对比设计方案**："对比这两个流程图的区别"
- 📝 **生成文档**："基于这个架构图，生成系统设计文档"

> 💡 **技术说明**：图表内容通过解析 ONES Wiki 的富文本结构获得，支持嵌入式图表（embed）和代码块（code block）两种形式。

## 🔐 安全注意事项

### 服务端安全
- ⚠️ **不要提交** `config.json` 到版本控制
- ⚠️ **配置文件权限**：`chmod 600 config.json`（Linux）
- ⚠️ **服务端配置**只需配置 API 地址和团队 UUID，不包含任何用户凭据

### 客户端安全
- ✅ **多用户认证模式**：每个用户使用自己的 ONES 账号
- ✅ **权限隔离**：基于 ONES 系统的权限控制
- ✅ **审计追溯**：所有操作可追溯到具体用户
- ⚠️ **保护密码**：客户端配置文件包含密码，请妥善保管

## 📞 获取帮助

- 查看 [多用户认证指南](docs/MULTI_USER_AUTH_GUIDE.md) ⭐
- 查看 [快速配置指南](docs/快速配置指南.md)
- 查看 [部署指南](docs/DEPLOY.md)
- 查看 [完整文档](docs/README.md)
- 提交 GitHub Issue

## 📄 许可证

MIT License

---

**快速开始**：
1. **服务端**：配置 `config.json`（仅2个字段），运行 `bash deploy.sh`（Linux）或 `deploy.bat`（Windows）
2. **客户端**：每个用户在 `~/.cursor/mcp.json` 中配置自己的 ONES 账号
3. 在 Cursor 中使用 AI 访问 Wiki！🚀

> 💡 采用多用户认证模式，每个用户使用自己的账号，权限独立隔离

# ONES Wiki MCP Server

English | [简体中文](./README.md)

## 📖 Project Background

ONES officially provides the [ONES Copilot](https://docs.ones.cn/wiki/#/team/6mRWUuNv/space/JwHAUL1L/page/UEQ6z54V) product, which includes MCP server functionality. However, ONES Copilot requires **additional paid licensing**, making it unavailable for teams that haven't purchased this service.

This project provides an **open-source, free** MCP server implementation by utilizing **ONES' existing public APIs** (Wiki API), enabling teams without ONES Copilot licenses to connect AI assistants (such as Cursor, Claude Desktop) to their internal ONES Wiki knowledge base.

### 🎯 Core Value

- 💰 **Zero Cost**: No need to purchase ONES Copilot license, leverages existing ONES APIs
- 🔓 **Open Source**: Fully open-source code, freely deployable and customizable
- 🏢 **Enterprise-Friendly**: Supports on-premises deployment, data stays within company network
- 👥 **Multi-User Support**: Supports concurrent team usage, each user with their own account
- 🔐 **Permission Isolation**: Based on ONES' native permission system, ensuring data security

## 📝 Project Overview

This is an MCP (Model Context Protocol) server for connecting to ONES Wiki knowledge base, allowing AI assistants to access and query company's internal ONES Wiki through the MCP protocol.

## ✨ Key Features

- 🔐 **Multi-User Authentication** - Each user uses their own ONES account with permission isolation
- 📚 Retrieve knowledge base space lists
- 🌲 View knowledge base page tree structure
- 📄 **Read complete page content**, including:
  - 📝 Rich text content like titles, paragraphs, lists
  - 💻 Code blocks (supporting various programming languages)
  - 📊 Table data
  - 🖼️ Image references
  - 📈 **Diagram content** (Mermaid sequence/flow diagrams, PlantUML class/sequence diagrams, etc.)
- 🔍 Search knowledge base pages
- 📜 View page version history
- 🌐 HTTP/SSE server deployment, supporting concurrent multi-user access

### 🎯 Latest Updates (v2.0)

**Complete Content Parsing Support**:
- ✅ **Code Blocks**: PlantUML, Mermaid, Python, Java, and all other languages
- ✅ **Tables**: Automatically converted to Markdown format
- ✅ **Images/Attachments**: Extract image URLs and descriptions
- ✅ **Document Structure**: Fully preserve heading, list, and paragraph hierarchy

> Now AI can directly analyze PlantUML system architecture diagrams, sequence diagrams, and more from Wiki!

## 🚀 Quick Start

### Step 1: Server Deployment

#### Linux Server Deployment (Recommended)

```bash
# 1. Clone repository
git clone <repository-url>
cd mcp-server

# 2. Configure server (only 2 fields required)
cp config.example.json config.json
nano config.json

# config.json content:
# {
#   "ones_api_url": "http://your-ones-server:port/project/api",
#   "team_uuid": "your_team_uuid"
# }

# 3. One-click deployment
bash deploy.sh
```

#### Windows Local Deployment

```batch
# 1. Configure server
copy config.example.json config.json
notepad config.json

# 2. One-click deployment
deploy.bat
```

### Step 2: Client Configuration (Each User Configures Independently)

Edit `~/.cursor/mcp.json` (Windows: `%APPDATA%\Cursor\mcp.json`):

```json
{
  "mcpServers": {
    "ones-wiki": {
      "url": "http://your-server-ip:8000/sse",
      "description": "ONES Wiki Knowledge Base",
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

> ⚠️ **Important**: Each user should use their own ONES account and password!

## 📚 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** / **[快速配置指南](docs/快速配置指南.md)** - Simplest configuration instructions ⭐
- **[Multi-User Auth Guide](docs/MULTI_USER_AUTH_GUIDE.md)** - Multi-user authentication guide ⭐
- **[Deployment Guide](docs/DEPLOY.md)** - Detailed server deployment steps
- **[Client Configuration](docs/MCP_CLIENT_CONFIG.md)** - Detailed client configuration
- **[Changelog](docs/CHANGELOG.md)** - Version update history
- **[API Research](docs/ONES_WIKI_API_RESEARCH.md)** - ONES Wiki API documentation

## 📁 Project Structure

```
ones-wiki-mcp-server/
├── server_http_simple.py      # HTTP/SSE server (production, multi-user auth) ⭐
├── server.py                   # stdio mode server (local testing)
├── ones_wiki_client.py         # ONES Wiki client
├── config.json                 # Server config (only 2 fields: API URL and team UUID)
├── requirements.txt            # Python dependencies
├── deploy.sh                   # Linux one-click deployment
├── deploy.bat                  # Windows one-click deployment
└── docs/                       # Documentation directory
    ├── MULTI_USER_AUTH_GUIDE.md # Multi-user auth guide ⭐
    ├── 快速配置指南.md          # Quick start guide
    ├── DEPLOY.md                # Deployment guide
    ├── MCP_CLIENT_CONFIG.md     # Client configuration
    └── ...
```

## 🔧 Common Commands

### Linux

```bash
# Deploy/Restart
bash deploy.sh

# View logs
tail -f mcp-server.log

# Stop service
pkill -f server_http_simple
```

### Windows

```batch
# Start service
deploy.bat

# Stop service (Ctrl+C)
```

## 💡 Usage Examples

After configuration, you can use it in Cursor like this:

### Basic Features

- **Search documents**: "Search wiki for documents about inspection"
- **Get page content**: "Show content of page A9Lygq2T"
- **View page list**: "Get all pages in space PLWdQVb5"

### Advanced Feature: Diagram Analysis 📊

This MCP server supports **complete parsing** of various diagrams in Wiki pages, including:

#### Supported Diagram Types

- 📈 **Mermaid Diagrams**
  - Flowchart
  - Sequence Diagram
  - Class Diagram
  - State Diagram
  - Gantt Chart
  
- 📐 **PlantUML Diagrams**
  - Class Diagram
  - Sequence Diagram
  - Use Case Diagram
  - Component Diagram
  - Activity Diagram

#### Real-World Use Cases

- 🔍 **Understand System Architecture**: "Analyze the dependency relationships between modules in this class diagram"
- 📋 **Interpret Business Processes**: "What business process does this sequence diagram describe?"
- 🔄 **Compare Design Options**: "Compare the differences between these two flowcharts"
- 📝 **Generate Documentation**: "Generate system design documentation based on this architecture diagram"

> 💡 **Technical Note**: Diagram content is obtained by parsing ONES Wiki's rich text structure, supporting both embedded diagrams and code blocks.

## 🔐 Security Considerations

### Server Security
- ⚠️ **Do not commit** `config.json` to version control
- ⚠️ **File permissions**: `chmod 600 config.json` (Linux)
- ⚠️ **Server configuration** only requires API URL and team UUID, no user credentials

### Client Security
- ✅ **Multi-user authentication**: Each user uses their own ONES account
- ✅ **Permission isolation**: Based on ONES system's permission control
- ✅ **Audit trail**: All operations traceable to specific users
- ⚠️ **Protect passwords**: Client config files contain passwords, keep them secure

## 📞 Get Help

- Check [Multi-User Auth Guide](docs/MULTI_USER_AUTH_GUIDE.md) ⭐
- Check [Quick Configuration Guide](docs/快速配置指南.md)
- Check [Deployment Guide](docs/DEPLOY.md)
- Check [Complete Documentation](docs/README.md)
- Submit GitHub Issue

## 📄 License

MIT License

---

**Quick Start**:
1. **Server**: Configure `config.json` (only 2 fields), run `bash deploy.sh` (Linux) or `deploy.bat` (Windows)
2. **Client**: Each user configures their own ONES account in `~/.cursor/mcp.json`
3. Use AI to access Wiki in Cursor! 🚀

> 💡 Uses multi-user authentication mode, each user with their own account and independent permission isolation


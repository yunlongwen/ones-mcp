# 项目文件结构说明

## 📁 核心文件

### Python 代码
- **`server.py`** - MCP 标准模式服务器（stdio）
- **`server_http_simple.py`** - HTTP/SSE 模式服务器（推荐用于生产）
- **`ones_wiki_client.py`** - ONES Wiki API 客户端核心实现

### 配置文件
- **`config.json`** - 服务器配置（需自行创建，不提交到 Git）
- **`config.example.json`** - 配置文件示例
- **`requirements.txt`** - Python 依赖包列表

### 部署脚本
- **`deploy_simple.sh`** - ⭐ Linux 一键部署脚本（推荐）
- **`deploy.sh`** - 完整部署脚本（包含更多检查）
- **`install_on_server.sh`** - 服务器安装脚本
- **`run.sh`** / **`run.bat`** - 快速启动脚本
- **`run_http.sh`** / **`run_http.bat`** - HTTP 模式启动脚本

## 📚 文档文件

### 主要文档
- **`README.md`** - ⭐ 项目主文档（功能介绍、配置、使用）
- **`DEPLOY.md`** - ⭐ 部署指南（服务端部署步骤）
- **`MCP_CLIENT_CONFIG.md`** - ⭐ 客户端配置指南（重要！）
- **`CHANGELOG.md`** - 更新日志
- **`PROJECT_STRUCTURE.md`** - 本文档（文件结构说明）

### 参考文档
- **`ONES_WIKI_API_RESEARCH.md`** - ONES Wiki API 研究文档
- **`MULTI_USER_AUTH_GUIDE.md`** - 多用户认证指南（技术参考）
- **`MCP实战：将内部Wiki接入Cursor完整教程.md`** - 完整教程
- **`文件整理总结.md`** - 文件整理记录

## 🔧 其他文件

- **`LICENSE`** - MIT 许可证
- **`.gitignore`** - Git 忽略规则
- **`ones-wiki-mcp.service`** - systemd 服务配置（可选）

**注意**：客户端配置不需要 JSON 文件，直接在 Cursor 的 `mcp.json` 中配置！

## 📊 文件用途说明

### 日常使用

**本地开发（Cursor/Claude Desktop）**:
1. 配置: `config.json`
2. 运行: `python server.py`
3. 文档: `README.md`

**Linux 服务器部署**:
1. 配置: `config.json`
2. 部署: `bash deploy_simple.sh`
3. 日志: `tail -f mcp-server.log`
4. 文档: `DEPLOY.md`

### 不需要的文件

以下文件可以忽略（已在 .gitignore 中）:
- `config.json` - 包含敏感信息
- `*.log` - 日志文件
- `__pycache__/` - Python 缓存
- `venv/` - 虚拟环境

## 🗂️ 推荐的工作流

### 首次部署

```bash
# 1. 克隆仓库
git clone <repo-url>
cd ones-wiki-mcp-server

# 2. 配置
cp config.example.json config.json
nano config.json

# 3. 部署
bash deploy_simple.sh
```

### 更新代码

```bash
# 1. 拉取最新代码
git pull

# 2. 重启服务
bash deploy_simple.sh
```

### 查看日志

```bash
# 实时日志
tail -f mcp-server.log

# 最近 100 行
tail -n 100 mcp-server.log

# 搜索错误
grep -i error mcp-server.log
```

## 📝 文件清理建议

### 可以删除的文件（如果不需要）

- `MCP实战：将内部Wiki接入Cursor完整教程.md` - 如果已经部署完成
- `MULTI_USER_AUTH_GUIDE.md` - 如果不使用多用户模式
- `deploy.sh` - 如果使用 `deploy_simple.sh`
- `install_on_server.sh` - 如果已经安装完成
- `*.bat` 文件 - 如果只在 Linux 上运行

### 必须保留的文件

- `server_http_simple.py` - 核心服务器
- `ones_wiki_client.py` - 核心客户端
- `config.json` - 配置文件
- `requirements.txt` - 依赖列表
- `deploy_simple.sh` - 部署脚本
- `README.md` - 主文档

## 🎯 最小化部署

如果只需要最基本的功能，只需要这些文件：

```
ones-wiki-mcp-server/
├── server_http_simple.py    # 服务器
├── ones_wiki_client.py       # 客户端
├── config.json               # 配置
├── requirements.txt          # 依赖
├── deploy_simple.sh          # 部署脚本
└── README.md                 # 文档
```

其他文件都是可选的辅助文件。

---

**提示**: 如果不确定某个文件的用途，可以查看文件开头的注释说明。


# 更新日志

## 2024-12-16 - v2.0 重大更新

### 🎉 新功能：完整的代码块支持

### ✨ 新增功能

1. **完整的代码块支持**
   - ✅ 支持 PlantUML 文本画图源码提取
   - ✅ 支持 Mermaid 图表源码提取
   - ✅ 支持所有语言的代码块（Python, Java, JavaScript 等）
   - ✅ 正确解析带 `children` 结构的代码块

2. **表格内容解析**
   - ✅ 支持表格结构提取
   - ✅ 输出 Markdown 格式的表格

3. **嵌入内容处理**
   - ✅ 支持图片嵌入（显示图片URL）
   - ✅ 支持其他嵌入类型的识别

### 🔧 技术改进

1. **重构富文本解析逻辑**
   - 将 `_parse_wiki_content()` 重构为模块化设计
   - 新增独立的块处理方法：
     - `_process_code_block()` - 处理代码块
     - `_process_table_block()` - 处理表格
     - `_process_embed_block()` - 处理嵌入内容
     - `_process_heading_block()` - 处理标题
     - `_process_list_block()` - 处理列表
     - `_process_text_block()` - 处理普通文本
     - `_extract_text_from_text_array()` - 提取文本数组内容
   
2. **修复关键遗漏**
   - 之前只处理 `heading` 和 `type="list"` 块
   - 现在完整支持所有 ONES Wiki 块类型
   - 正确处理 `children` 引用结构（代码块、表格的子块）

### 📊 对比 GitHub 参考实现

参考了 [mikeysrecipes/ones-wiki-mcp-server](https://github.com/mikeysrecipes/ones-wiki-mcp-server) 的 Java 实现，确保功能对等：
- ✅ 代码块处理逻辑与 `processCodeBlock()` 对齐
- ✅ 表格处理逻辑与 `processTableBlock()` 对齐
- ✅ 嵌入内容处理逻辑与 `processEmbedBlock()` 对齐

### 🎯 解决的问题

**问题**：无法访问 Wiki 中的文本画图（PlantUML、Mermaid 等）

**根因**：原实现漏掉了 `type="code"` 块的处理，导致所有代码块内容被丢弃

**解决**：新增完整的代码块处理逻辑，递归解析 `children` 结构提取源码

### 📦 部署改进

1. **新增一键部署脚本** (`deploy_simple.sh`)
   - 自动检查依赖
   - 自动停止旧进程
   - 自动启动新服务
   - 健康检查验证

2. **简化文档结构**
   - 删除冗余的技术文档
   - 整合到 README 和 DEPLOY.md
   - 提供清晰的部署指南

3. **改进 .gitignore**
   - 排除日志文件
   - 排除配置文件
   - 排除临时文件

### ⚠️ 重启说明

修改后需要重启 MCP 服务器才能生效：
- **Cursor**: 重启 Cursor 或重启 MCP 服务器
- **Claude Desktop**: 重启应用
- **Linux 服务器**: 运行 `bash deploy_simple.sh`

## 2025-11-05 - 初始版本完成

### ✅ 已实现功能

1. **ONES系统登录认证** - 完全正常
2. **获取页面树** - ✅ 测试通过（13,102个页面）
3. **获取页面内容** - ✅ 测试通过
4. **智能搜索** - ✅ 实现了API+本地搜索混合模式
5. **获取页面历史** - ✅ 已实现

### 🔧 已修复问题

1. **UTF-8 BOM编码问题**
   - 问题：Windows系统JSON文件带BOM导致解析失败
   - 解决：使用 `utf-8-sig` 编码读取配置文件

2. **MCP客户端工作目录问题**
   - 问题：MCP客户端启动服务器时工作目录不在项目文件夹
   - 解决：使用 `Path(__file__).parent.absolute()` 获取脚本所在目录

3. **自建ONES API路径问题**
   - 问题：自建版ONES的API路径与标准版不同
   - 解决：实现多路径自动尝试机制，自动找到正确的API路径

4. **搜索API不可用问题**
   - 问题：搜索API返回404
   - 解决：实现本地搜索功能（基于页面树的标题搜索）
   - 结果：成功搜索"点检"找到71个相关页面

### ⚠️ 功能限制

1. **获取空间列表需要管理员权限**
   - 普通用户账号会返回403错误
   - 解决方案：在config.json中配置default_space_uuid

2. **本地搜索仅支持标题匹配**
   - 不搜索页面正文内容
   - 不区分大小写
   - 适合快速查找页面

### 🎯 测试结果

| 功能 | 状态 | 测试数据 |
|------|------|---------|
| 登录认证 | ✅ | Token获取成功 |
| 获取空间列表 | ⚠️ | 需要管理员权限 |
| 获取页面树 | ✅ | 13,102个页面 |
| 获取页面内容 | ✅ | 成功读取页面 |
| 搜索功能 | ✅ | 搜索"点检"找到71个结果 |

### 📝 配置说明

**必填项：**
- `ones_api_url`: 您的ONES系统API地址
- `team_uuid`: 团队UUID
- `user_email`: 用户邮箱
- `user_password`: 用户密码
- `default_space_uuid`: 默认空间UUID（推荐配置）

**实际配置示例（基于诺瓦星科技）：**
```json
{
  "ones_api_url": "http://127.0.0.1:30011/project/api",
  "team_uuid": "y7bXyZLk",
  "user_email": "your_email@adb.com",
  "user_password": "your_password",
  "default_space_uuid": "PLWdQVb5"
}
```

### 🚀 已验证的使用场景

1. ✅ 在空间中搜索特定关键词的页面
2. ✅ 获取空间的完整页面树结构
3. ✅ 读取特定页面的详细内容
4. ✅ 通过自然语言与Wiki交互

### 📖 下一步改进建议

1. **增强搜索功能**
   - 可选：支持页面内容全文搜索（需要逐页获取内容）
   - 可选：支持正则表达式搜索
   - 可选：搜索结果排序和分页

2. **缓存机制**
   - 可选：缓存页面树，减少API调用
   - 可选：缓存页面内容

3. **多空间支持**
   - 可选：如果有权限，支持跨空间搜索

4. **性能优化**
   - 可选：并发获取多个页面内容
   - 可选：增量更新页面树

---

## 项目状态：✅ 可用于生产环境

核心功能已完全实现并通过测试，可以在实际工作中使用。


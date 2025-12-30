# ONES Wiki API 研究总结

## 当前已实现的API（读取操作）

### ✅ 已验证可用的API端点

| 功能 | API端点 | 方法 | 状态 |
|------|---------|------|------|
| 登录 | `/project/api/project/auth/login` | POST | ✅ 可用 |
| 获取页面树 | `/wiki/api/wiki/team/{team_uuid}/space/{space_uuid}/page_tree` | GET | ✅ 可用 |
| 获取页面内容 | `/wiki/api/wiki/team/{team_uuid}/online_page/{page_uuid}/content` | GET | ✅ 可用 |
| 搜索页面 | `/wiki/api/wiki/team/{team_uuid}/pages/search` | POST | ⚠️ 可能不存在（404） |

## 尝试的创建/更新API端点（全部失败）

### ❌ 已测试的创建页面端点

所有以下端点都返回 **404 Not Found**：

1. `POST /wiki/api/wiki/team/{team_uuid}/pages`
2. `POST /wiki/api/wiki/team/{team_uuid}/page`
3. `POST /project/api/wiki/team/{team_uuid}/pages`
4. `POST /project/api/wiki/team/{team_uuid}/page`

### ❌ 已测试的更新页面端点

所有以下端点都返回 **404 Not Found**：

1. `PUT /wiki/api/wiki/team/{team_uuid}/page/{page_uuid}`
2. `PATCH /wiki/api/wiki/team/{team_uuid}/page/{page_uuid}`
3. `PUT /wiki/api/wiki/team/{team_uuid}/pages/{page_uuid}`
4. `PUT /project/api/wiki/team/{team_uuid}/page/{page_uuid}`
5. `PUT /wiki/api/wiki/team/{team_uuid}/online_page/{page_uuid}/content`
6. `PATCH /wiki/api/wiki/team/{team_uuid}/online_page/{page_uuid}/content`

## 可能的原因

1. **API未公开**：ONES Wiki可能没有提供公开的创建/更新API
2. **需要特殊权限**：可能需要管理员权限或特殊配置
3. **不同的API路径**：可能使用了非标准的RESTful路径
4. **WebSocket协议**：可能通过WebSocket进行实时编辑
5. **内部API**：创建/更新功能可能只通过Web界面实现

## 建议的下一步研究

### 1. 浏览器开发者工具分析

通过浏览器开发者工具（F12）捕获实际的API调用：

1. 打开ONES Wiki
2. 创建一个新页面或编辑现有页面
3. 在Network标签中查看实际的API请求
4. 记录请求的URL、方法、请求头和请求体

### 2. 查看ONES官方文档

- 查看ONES的官方API文档
- 联系ONES技术支持
- 查看ONES的开发者社区

### 3. 分析Web界面代码

- 查看ONES Wiki的JavaScript代码
- 查找创建/更新页面的前端实现
- 分析前端如何调用后端API

### 4. 尝试其他可能的端点

基于online_page API的模式，可能的端点：

- `/wiki/api/wiki/team/{team_uuid}/online_page/{page_uuid}` (PUT/PATCH)
- `/wiki/api/wiki/team/{team_uuid}/space/{space_uuid}/pages` (POST)
- `/wiki/api/wiki/team/{team_uuid}/space/{space_uuid}/page` (POST)

## 当前可用的功能

基于现有API，我们可以实现：

### ✅ 已实现的MCP Tools

1. **search_pages** - 搜索页面（标题+作者）
2. **get_page_content** - 获取页面完整内容

### 🔄 可以实现的内部方法（非MCP Tool）

1. **get_page_tree** - 获取页面树（已实现，供search_pages使用）
2. **get_spaces** - 获取空间列表（已实现，需要管理员权限）
3. **get_page_history** - 获取页面历史版本（已实现，但未测试）

## 结论

**目前ONES Wiki似乎没有提供公开的创建/更新API端点**。所有尝试的RESTful端点都返回404。

**建议**：
1. 通过浏览器开发者工具分析实际的API调用
2. 查看ONES官方文档或联系技术支持
3. 如果确实没有API，考虑使用浏览器自动化（如Playwright）来模拟用户操作

## 测试脚本

已创建以下测试脚本：
- `test_create_update_api.py` - 列出可能的API端点
- `test_write_apis.py` - 实际测试创建/更新API

运行方式：
```bash
python test_write_apis.py
```


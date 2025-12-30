# -*- coding: utf-8 -*-
"""
ONES Wiki MCP服务器 - HTTP/SSE模式（多用户认证版）
支持客户端通过HTTP Headers传递用户凭据
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Optional
import sys
import uuid

from mcp.server import Server
from mcp.types import Tool, TextContent
from ones_wiki_client import OnesWikiClient

try:
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Route, Mount
    from starlette.responses import Response, JSONResponse
    from starlette.requests import Request
    import uvicorn
except ImportError as e:
    print(f"错误：缺少依赖包: {e}")
    print("请运行：pip install mcp starlette uvicorn sse-starlette")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局服务器配置（API地址、团队UUID）
server_config: dict = {}

# 全局用户访问统计
# 格式: {user_email: {"search_pages": count, "get_page_content": count, "total": count}}
user_stats: dict = {}

# 用户统计数据持久化文件路径
STATS_FILE_PATH = Path(__file__).parent.absolute() / "user_stats.json"

def load_config() -> dict:
    """加载配置文件"""
    script_dir = Path(__file__).parent.absolute()
    config_path = script_dir / "config.json"
    
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def load_server_config():
    """加载服务器配置（只包含API地址和团队UUID）"""
    global server_config
    server_config = load_config()
    logger.info(f"服务器配置已加载: API={server_config.get('ones_api_url')}, Team={server_config.get('team_uuid')}")


def load_user_stats() -> dict:
    """从JSON文件加载用户统计数据"""
    try:
        if STATS_FILE_PATH.exists():
            with open(STATS_FILE_PATH, 'r', encoding='utf-8') as f:
                stats = json.load(f)
                logger.info(f"已加载用户统计数据: {len(stats)} 个用户")
                return stats
        else:
            logger.info("统计数据文件不存在，使用空数据初始化")
            return {}
    except json.JSONDecodeError as e:
        logger.error(f"统计数据文件解析失败: {e}")
        # 备份损坏的文件
        try:
            backup_path = STATS_FILE_PATH.with_suffix('.json.backup')
            STATS_FILE_PATH.rename(backup_path)
            logger.warning(f"已将损坏的文件备份到: {backup_path}")
        except Exception as backup_err:
            logger.error(f"备份损坏文件失败: {backup_err}")
        return {}
    except Exception as e:
        logger.error(f"加载统计数据失败: {e}")
        return {}


def save_user_stats():
    """将用户统计数据保存到JSON文件（原子写入）"""
    global user_stats
    try:
        # 先写入临时文件
        temp_file = STATS_FILE_PATH.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(user_stats, f, ensure_ascii=False, indent=2)
        
        # 原子重命名（避免写入过程中服务崩溃导致文件损坏）
        temp_file.replace(STATS_FILE_PATH)
        logger.debug(f"用户统计数据已保存: {len(user_stats)} 个用户")
    except Exception as e:
        logger.error(f"保存统计数据失败: {e}")


def extract_user_config_from_headers(headers: dict) -> dict:
    """从HTTP Headers中提取用户配置"""
    user_email = headers.get('x-user-email', '').strip()
    user_password = headers.get('x-user-password', '').strip()
    default_space = headers.get('x-default-space-uuid', '').strip()
    accessible_spaces_str = headers.get('x-accessible-spaces', '').strip()
    
    if not user_email or not user_password:
        raise ValueError("缺少用户认证信息: 需要HTTP Headers中的 x-user-email 和 x-user-password")
    
    # 解析accessible_spaces（逗号分隔）
    accessible_spaces = []
    if accessible_spaces_str:
        accessible_spaces = [s.strip() for s in accessible_spaces_str.split(',') if s.strip()]
    
    return {
        'user_email': user_email,
        'user_password': user_password,
        'default_space_uuid': default_space if default_space else None,
        'accessible_spaces': accessible_spaces
    }


def record_user_access(user_email: str, tool_name: str):
    """记录用户访问统计"""
    global user_stats
    
    if user_email not in user_stats:
        user_stats[user_email] = {
            "search_pages": 0,
            "get_page_content": 0,
            "total": 0
        }
    
    if tool_name in ["search_pages", "get_page_content"]:
        user_stats[user_email][tool_name] += 1
    user_stats[user_email]["total"] += 1
    
    # 实时保存统计数据
    save_user_stats()


def create_mcp_server_for_user(wiki_client: OnesWikiClient, user_config: dict) -> Server:
    """为特定用户创建MCP Server实例"""
    mcp_server = Server("ones-wiki-mcp-server")
    
    @mcp_server.list_tools()
    async def list_tools() -> list[Tool]:
        """列出所有可用工具"""
        return [
            Tool(
                name="search_pages",
                description="在Wiki知识库中搜索页面（关键词搜索）。支持搜索标题和作者信息。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "搜索关键词，支持中英文"
                        },
                        "space_uuid": {
                            "type": "string",
                            "description": "可选：限制在指定空间内搜索"
                        }
                    },
                    "required": ["keyword"]
                }
            ),
            Tool(
                name="get_page_content",
                description="获取Wiki页面的完整内容（纯文本格式）。需要提供page_uuid（可通过search_pages获得）。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_uuid": {
                            "type": "string",
                            "description": "页面UUID（从搜索结果中获取）"
                        }
                    },
                    "required": ["page_uuid"]
                }
            )
        ]
    
    @mcp_server.call_tool()
    async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """处理工具调用"""
        try:
            logger.info(f"[{user_config['user_email']}] 调用工具: {name}, 参数: {arguments}")
            
            # 记录用户访问统计
            record_user_access(user_config['user_email'], name)
            
            if name == "search_pages":
                # 搜索页面
                keyword = arguments.get("keyword")
                space_uuid = arguments.get("space_uuid")  # 可选
                
                if not keyword:
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "缺少必需参数: keyword"
                        }, ensure_ascii=False, indent=2)
                    )]
                
                results = await wiki_client.search_pages(keyword, space_uuid)
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "total": len(results),
                        "keyword": keyword,
                        "results": results
                    }, ensure_ascii=False, indent=2)
                )]
            
            elif name == "get_page_content":
                # 获取页面内容（使用 online_page API）
                page_uuid = arguments.get("page_uuid")
                
                if not page_uuid:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"error": "缺少必需参数: page_uuid"}, ensure_ascii=False, indent=2)
                    )]
                
                content = await wiki_client.get_page_content(page_uuid)
                
                if content:
                    # 返回格式化的内容
                    result = {
                        "page_uuid": page_uuid,
                        "plain_text": content.get('plain_text', ''),
                        "text_length": content.get('text_length', 0),
                        "version": content.get('version', 0)
                    }
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"error": "获取页面内容失败"}, ensure_ascii=False, indent=2)
                    )]
            
            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"未知工具: {name}",
                        "available_tools": ["search_pages", "get_page_content"]
                    }, ensure_ascii=False, indent=2)
                )]
        
        except Exception as e:
            logger.error(f"[{user_config['user_email']}] 执行工具 {name} 时出错: {str(e)}")
            return [TextContent(
                type="text",
                text=json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)
            )]
    
    return mcp_server


def create_app():
    """创建Starlette应用"""
    
    # 创建全局SSE传输实例
    sse_transport = SseServerTransport("/messages")
    
    async def handle_sse(request: Request):
        """处理SSE连接"""
        try:
            # 1. 从Headers提取用户配置
            logger.info("收到SSE连接请求，提取用户认证信息...")
            user_config = extract_user_config_from_headers(dict(request.headers))
            logger.info(f"用户: {user_config['user_email']}")
            
            # 2. 创建用户专属的Wiki客户端
            wiki_client = OnesWikiClient(
                api_url=server_config['ones_api_url'],
                team_uuid=server_config['team_uuid'],
                default_space_uuid=user_config.get('default_space_uuid'),
                accessible_spaces=user_config.get('accessible_spaces', [])
            )
            
            await wiki_client.__aenter__()
            
            try:
                # 3. 用户登录
                login_success = await wiki_client.login(
                    user_config['user_email'],
                    user_config['user_password']
                )
                
                if not login_success:
                    logger.error(f"用户 {user_config['user_email']} 登录失败")
                    return JSONResponse(
                        {"error": "认证失败"},
                        status_code=401
                    )
                
                logger.info(f"用户 {user_config['user_email']} 认证成功")
                
                # 4. 创建用户专属的MCP Server
                mcp_server = create_mcp_server_for_user(wiki_client, user_config)
                
                # 5. 建立SSE连接
                logger.info("建立SSE连接...")
                async with sse_transport.connect_sse(
                    request.scope, request.receive, request._send
                ) as streams:
                    logger.info(f"SSE连接已建立，开始服务用户: {user_config['user_email']}")
                    await mcp_server.run(
                        streams[0], streams[1], mcp_server.create_initialization_options()
                    )
                
                logger.info(f"用户 {user_config['user_email']} 的SSE连接已关闭")
                return Response()
            
            finally:
                # 6. 清理资源
                await wiki_client.__aexit__(None, None, None)
                logger.info(f"用户 {user_config['user_email']} 的Wiki客户端已清理")
        
        except ValueError as e:
            logger.error(f"认证信息错误: {e}")
            return JSONResponse(
                {"error": str(e)},
                status_code=400
            )
        except Exception as e:
            logger.error(f"处理SSE连接时出错: {e}", exc_info=True)
            return JSONResponse(
                {"error": "服务器内部错误"},
                status_code=500
            )
    
    async def handle_messages(scope, receive, send):
        """处理POST消息（ASGI应用）"""
        logger.info("收到POST消息，转发给SSE传输处理")
        await sse_transport.handle_post_message(scope, receive, send)
    
    async def health(request: Request):
        """健康检查"""
        return Response(
            json.dumps({"status": "ok", "service": "ones-wiki-mcp-server"}),
            media_type="application/json"
        )
    
    async def users_stats(request: Request):
        """用户访问统计页面"""
        global user_stats
        
        # 按总访问次数排序
        sorted_users = sorted(
            user_stats.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )
        
        # 生成表格行
        table_rows = ""
        for rank, (email, stats) in enumerate(sorted_users, 1):
            table_rows += f"""
                <tr>
                    <td>{rank}</td>
                    <td>{email}</td>
                    <td>{stats['total']}</td>
                </tr>
            """
        
        if not table_rows:
            table_rows = """
                <tr>
                    <td colspan="3" style="text-align: center; color: #999;">暂无访问记录</td>
                </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>用户访问统计 - ONES Wiki MCP Server</title>
            <meta charset="UTF-8">
            <meta http-equiv="refresh" content="10">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    border-bottom: 2px solid #4CAF50;
                    padding-bottom: 10px;
                }}
                .info {{
                    background: #e7f3ff;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #2196F3;
                    margin: 20px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th {{
                    background: #4CAF50;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: bold;
                }}
                td {{
                    padding: 12px;
                    border-bottom: 1px solid #ddd;
                }}
                tr:hover {{
                    background: #f5f5f5;
                }}
                .rank {{
                    font-weight: bold;
                    color: #4CAF50;
                }}
                .total {{
                    font-weight: bold;
                    color: #2196F3;
                }}
                .nav {{
                    margin-top: 20px;
                }}
                .nav a {{
                    color: #2196F3;
                    text-decoration: none;
                    padding: 8px 16px;
                    border: 1px solid #2196F3;
                    border-radius: 4px;
                }}
                .nav a:hover {{
                    background: #2196F3;
                    color: white;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 用户访问统计</h1>
                
                <div class="info">
                    <strong>💡 说明：</strong> 此页面每 10 秒自动刷新，实时显示所有用户的 MCP 工具调用统计。
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>排名</th>
                            <th>用户邮箱</th>
                            <th>调用次数</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
                
                <div class="nav">
                    <a href="/">← 返回首页</a>
                </div>
            </div>
        </body>
        </html>
        """
        return Response(html, media_type="text/html; charset=utf-8")
    
    async def homepage(request: Request):
        """主页"""
        # 读取部署配置获取端口
        deploy_config_path = Path(__file__).parent / "deploy_config.json"
        if deploy_config_path.exists():
            with open(deploy_config_path, 'r', encoding='utf-8') as f:
                deploy_config = json.load(f)
                port = deploy_config.get('port', 8000)
        else:
            port = 8000
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ONES Wiki MCP Server</title>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 900px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .status {{ color: #28a745; font-weight: bold; font-size: 18px; }}
                code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
                pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                h3 {{ margin-top: 30px; color: #333; }}
                .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌟 ONES Wiki MCP Server</h1>
                <p class="status">✓ 服务运行中（多用户认证模式）</p>
                
                <h3>📋 Cursor客户端配置 (mcp.json):</h3>
                <pre>{{
  "mcpServers": {{
    "ones-wiki": {{
      "url": "http://127.0.0.1:{port}/sse",
      "description": "ONES Wiki知识库",
      "headers": {{
        "x-user-email": "your-email@adb.com",
        "x-user-password": "your-password",
        "x-default-space-uuid": "PLWdQVb5",
        "x-accessible-spaces": "C7ReCVYN,PLWdQVb5,Vj2fPcS7"
      }}
    }}
  }}
}}</pre>

                <div class="warning">
                    <strong>⚠️ 注意：</strong> 请将上面配置中的认证信息替换为你自己的账号！
                    <ul>
                        <li><code>x-user-email</code>: 你的ONES账号邮箱</li>
                        <li><code>x-user-password</code>: 你的ONES账号密码</li>
                        <li><code>x-default-space-uuid</code>: 默认搜索的空间（可选）</li>
                        <li><code>x-accessible-spaces</code>: 可访问的空间列表，逗号分隔（可选）</li>
                    </ul>
                </div>

                <h3>🔍 如何获取 space_uuid（空间UUID）？</h3>
                <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; border-left: 4px solid #2196F3;">
                    <p><strong>通过Wiki URL获取：</strong></p>
                    <ol>
                        <li>打开ONES Wiki，进入你想访问的知识库空间</li>
                        <li>查看浏览器地址栏，URL格式类似：<br>
                            <code>http://your-ones-domain/wiki/#/team/xxx/space/<span style="color: #d32f2f; font-weight: bold;">PLWdQVb5</span>/home</code>
                        </li>
                        <li>其中 <code style="color: #d32f2f; font-weight: bold;">PLWdQVb5</code> 就是 space_uuid</li>
                        <li>将你有权限访问的所有空间UUID用逗号分隔，填入配置</li>
                    </ol>
                    
                    <p style="margin-top: 20px;"><strong>💡 配置说明：</strong></p>
                    <ul>
                        <li><code>x-default-space-uuid</code>: 单个空间UUID，用于指定默认搜索的空间</li>
                        <li><code>x-accessible-spaces</code>: 多个空间UUID，用逗号分隔，例如：<code>C7ReCVYN,PLWdQVb5,Vj2fPcS7</code></li>
                        <li><strong>⚠️ 建议至少配置 x-accessible-spaces</strong>，否则搜索功能可能无法正常工作</li>
                    </ul>
                </div>

                <h3>🔐 认证模式说明：</h3>
                <ul>
                    <li>✅ 每个用户使用自己的账号</li>
                    <li>✅ 支持多用户同时连接</li>
                    <li>✅ 数据隔离，权限独立</li>
                    <li>✅ 认证信息由客户端提供</li>
                </ul>
            </div>
        </body>
        </html>
        """
        return Response(html, media_type="text/html; charset=utf-8")
    
    routes = [
        Route("/", homepage),
        Route("/health", health),
        Route("/users", users_stats),
        Route("/sse", handle_sse),
        Mount("/messages", app=handle_messages),
    ]
    
    return Starlette(routes=routes)


async def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("启动ONES Wiki MCP服务器 (HTTP/SSE模式 - 多用户认证)")
    logger.info("=" * 60)
    
    try:
        # 加载服务器配置
        load_server_config()
        
        # 加载用户统计数据
        global user_stats
        user_stats = load_user_stats()
        
        # 加载部署配置
        deploy_config_path = Path(__file__).parent / "deploy_config.json"
        if deploy_config_path.exists():
            with open(deploy_config_path, 'r', encoding='utf-8') as f:
                deploy_config = json.load(f)
                host = deploy_config.get('host', '0.0.0.0')
                port = deploy_config.get('port', 8000)
        else:
            host = '0.0.0.0'
            port = 8000
        
        logger.info(f"服务器地址: http://{host}:{port}")
        logger.info(f"SSE端点: http://{host}:{port}/sse")
        logger.info("认证模式: 客户端Headers认证")
        logger.info("=" * 60)
        
        # 创建并运行应用
        app = create_app()
        
        config_uvicorn = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config_uvicorn)
        await server.serve()
    
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
    except Exception as e:
        logger.error(f"服务器运行错误: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("服务器已关闭")


if __name__ == "__main__":
    asyncio.run(main())

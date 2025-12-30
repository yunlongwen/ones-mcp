# -*- coding: utf-8 -*-
"""
ONES Wiki MCP服务器
提供与ONES Wiki知识库交互的MCP工具
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from ones_wiki_client import OnesWikiClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建MCP服务器实例
app = Server("ones-wiki-mcp-server")

# 全局ONES Wiki客户端
wiki_client: Optional[OnesWikiClient] = None
config: dict = {}


def load_config() -> dict:
    """加载配置文件"""
    # 获取脚本所在目录的绝对路径
    script_dir = Path(__file__).parent.absolute()
    config_path = script_dir / "config.json"
    
    if not config_path.exists():
        logger.error(f"config.json 文件不存在: {config_path}")
        logger.error("请参考 config.example.json 创建配置文件")
        raise FileNotFoundError(f"config.json 文件不存在: {config_path}")
    
    # 使用 utf-8-sig 编码来自动处理 Windows 系统的 BOM 标记
    with open(config_path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


async def initialize_client():
    """初始化ONES Wiki客户端"""
    global wiki_client, config
    
    try:
        config = load_config()
        wiki_client = OnesWikiClient(
            api_url=config['ones_api_url'],
            team_uuid=config['team_uuid']
        )
        
        # 进入异步上下文
        await wiki_client.__aenter__()
        
        # 登录
        success = await wiki_client.login(
            email=config['user_email'],
            password=config['user_password']
        )
        
        if not success:
            raise Exception("登录ONES系统失败")
        
        logger.info("ONES Wiki客户端初始化成功")
    except Exception as e:
        logger.error(f"初始化客户端失败: {str(e)}")
        raise


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="get_wiki_spaces",
            description="获取所有知识库空间列表",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_space_info",
            description="获取指定知识库空间的详细信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_uuid": {
                        "type": "string",
                        "description": "知识库空间的UUID"
                    }
                },
                "required": ["space_uuid"]
            }
        ),
        Tool(
            name="get_page_tree",
            description="获取指定知识库空间的页面树结构",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_uuid": {
                        "type": "string",
                        "description": "知识库空间的UUID"
                    }
                },
                "required": ["space_uuid"]
            }
        ),
        Tool(
            name="get_page_content",
            description="获取指定页面的详细内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_uuid": {
                        "type": "string",
                        "description": "页面的UUID"
                    }
                },
                "required": ["page_uuid"]
            }
        ),
        Tool(
            name="search_pages",
            description="在知识库中搜索页面",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "space_uuid": {
                        "type": "string",
                        "description": "可选：限制在特定空间内搜索"
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="get_page_history",
            description="获取页面的历史版本记录",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_uuid": {
                        "type": "string",
                        "description": "页面的UUID"
                    }
                },
                "required": ["page_uuid"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """处理工具调用"""
    if not wiki_client:
        return [TextContent(
            type="text",
            text="错误：Wiki客户端未初始化"
        )]
    
    try:
        if name == "get_wiki_spaces":
            spaces = await wiki_client.get_spaces()
            result = {
                "count": len(spaces),
                "spaces": [
                    {
                        "uuid": space.get('uuid'),
                        "name": space.get('name'),
                        "description": space.get('description', ''),
                        "owner": space.get('owner', {}).get('name', ''),
                        "create_time": space.get('create_time'),
                    }
                    for space in spaces
                ]
            }
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
        
        elif name == "get_space_info":
            space_uuid = arguments.get("space_uuid")
            space_info = await wiki_client.get_space_info(space_uuid)
            if space_info:
                return [TextContent(
                    type="text",
                    text=json.dumps(space_info, ensure_ascii=False, indent=2)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"未找到空间: {space_uuid}"
                )]
        
        elif name == "get_page_tree":
            space_uuid = arguments.get("space_uuid")
            pages = await wiki_client.get_page_tree(space_uuid)
            result = {
                "count": len(pages),
                "pages": [
                    {
                        "uuid": page.get('uuid'),
                        "title": page.get('title'),
                        "parent_uuid": page.get('parent_uuid'),
                        "position": page.get('position'),
                        "is_pinned": page.get('is_pinned', False),
                    }
                    for page in pages
                ]
            }
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
        
        elif name == "get_page_content":
            page_uuid = arguments.get("page_uuid")
            page = await wiki_client.get_page_content(page_uuid)
            if page:
                return [TextContent(
                    type="text",
                    text=json.dumps(page, ensure_ascii=False, indent=2)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"未找到页面: {page_uuid}"
                )]
        
        elif name == "search_pages":
            keyword = arguments.get("keyword")
            space_uuid = arguments.get("space_uuid")
            
            # 如果没有指定space_uuid，使用配置文件中的默认空间
            if not space_uuid:
                space_uuid = config.get('default_space_uuid')
                if not space_uuid:
                    return [TextContent(
                        type="text",
                        text="错误：需要指定space_uuid参数，或在config.json中配置default_space_uuid"
                    )]
            
            results = await wiki_client.search_pages(keyword, space_uuid)
            result = {
                "count": len(results),
                "keyword": keyword,
                "space_uuid": space_uuid,
                "results": [
                    {
                        "uuid": page.get('uuid'),
                        "title": page.get('title'),
                        "space_uuid": page.get('space_uuid', space_uuid),
                        "excerpt": page.get('excerpt', ''),
                        "updated_time": page.get('updated_time'),
                    }
                    for page in results
                ]
            }
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
        
        elif name == "get_page_history":
            page_uuid = arguments.get("page_uuid")
            versions = await wiki_client.get_page_history(page_uuid)
            result = {
                "count": len(versions),
                "versions": [
                    {
                        "version": ver.get('version'),
                        "title": ver.get('title'),
                        "author": ver.get('author', {}).get('name', ''),
                        "create_time": ver.get('create_time'),
                        "comment": ver.get('comment', ''),
                    }
                    for ver in versions
                ]
            }
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"未知工具: {name}"
            )]
    
    except Exception as e:
        logger.error(f"执行工具 {name} 时出错: {str(e)}")
        return [TextContent(
            type="text",
            text=f"错误: {str(e)}"
        )]


async def main():
    """主函数"""
    logger.info("启动ONES Wiki MCP服务器...")
    
    try:
        # 初始化客户端
        await initialize_client()
        
        # 启动服务器
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
    except Exception as e:
        logger.error(f"服务器运行错误: {str(e)}")
        raise
    finally:
        # 清理资源
        if wiki_client:
            await wiki_client.__aexit__(None, None, None)
        logger.info("服务器已关闭")


if __name__ == "__main__":
    asyncio.run(main())


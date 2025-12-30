# -*- coding: utf-8 -*-
"""
ONES Wiki API客户端
用于连接和操作ONES Wiki知识库
"""

import aiohttp
import json
from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class OnesWikiClient:
    """ONES Wiki API客户端类"""
    
    def __init__(self, api_url: str, team_uuid: str, default_space_uuid: Optional[str] = None, accessible_spaces: Optional[List[str]] = None):
        """
        初始化ONES Wiki客户端
        
        Args:
            api_url: ONES API地址
            team_uuid: 团队UUID
            default_space_uuid: 默认空间UUID（当无权限获取空间列表时使用）
            accessible_spaces: 可访问的空间UUID列表（用于无权限获取空间列表时的全局搜索）
        """
        self.api_url = api_url.rstrip('/')
        # 提取基础URL用于Wiki API（可能在不同路径）
        # 例如：http://127.0.0.1:30011/project/api -> http://127.0.0.1:30011
        if '/project/api' in self.api_url:
            self.base_url = self.api_url.replace('/project/api', '')
        else:
            self.base_url = self.api_url
        self.team_uuid = team_uuid
        self.default_space_uuid = default_space_uuid
        self.accessible_spaces = accessible_spaces or []
        self.token: Optional[str] = None
        self.user_uuid: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    async def login(self, email: str, password: str) -> bool:
        """
        登录ONES系统
        
        Args:
            email: 用户邮箱
            password: 用户密码
            
        Returns:
            登录是否成功
        """
        try:
            url = f"{self.api_url}/project/auth/login"
            payload = {
                "email": email,
                "password": password
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get('user', {}).get('token')
                    self.user_uuid = data.get('user', {}).get('uuid')
                    logger.info(f"成功登录ONES系统，用户UUID: {self.user_uuid}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"登录失败: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"登录异常: {str(e)}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.token:
            headers["Ones-User-Id"] = self.user_uuid
            headers["Ones-Auth-Token"] = self.token
        return headers
    
    async def get_spaces(self) -> List[Dict[str, Any]]:
        """
        获取知识库空间列表
        
        Returns:
            空间列表
        """
        # 尝试多个可能的API路径
        possible_urls = [
            f"{self.base_url}/wiki/api/wiki/team/{self.team_uuid}/spaces",  # 自建版可能的路径
            f"{self.base_url}/project/api/wiki/team/{self.team_uuid}/spaces",  # 标准路径
            f"{self.api_url}/wiki/team/{self.team_uuid}/spaces",  # 原路径
        ]
        
        headers = self._get_headers()
        
        for url in possible_urls:
            try:
                logger.info(f"尝试URL: {url}")
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        spaces = data.get('spaces', [])
                        logger.info(f"✓ 成功！获取到 {len(spaces)} 个知识库空间")
                        return spaces
                    else:
                        error_text = await response.text()
                        logger.warning(f"✗ 失败: {response.status} - {error_text[:100]}")
            except Exception as e:
                logger.warning(f"✗ 异常: {str(e)}")
                continue
        
        logger.error("所有API路径都失败了")
        return []
    
    async def get_space_info(self, space_uuid: str) -> Optional[Dict[str, Any]]:
        """
        获取知识库空间详情
        
        Args:
            space_uuid: 空间UUID
            
        Returns:
            空间详情
        """
        try:
            url = f"{self.api_url}/wiki/team/{self.team_uuid}/space/{space_uuid}"
            headers = self._get_headers()
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('space')
                else:
                    error_text = await response.text()
                    logger.error(f"获取空间详情失败: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"获取空间详情异常: {str(e)}")
            return None
    
    async def get_page_tree(self, space_uuid: str) -> List[Dict[str, Any]]:
        """
        获取知识库页面树结构
        
        Args:
            space_uuid: 空间UUID
            
        Returns:
            页面树列表
        """
        possible_urls = [
            f"{self.base_url}/wiki/api/wiki/team/{self.team_uuid}/space/{space_uuid}/page_tree",
            f"{self.base_url}/wiki/api/wiki/team/{self.team_uuid}/space/{space_uuid}/pages",
            f"{self.api_url}/wiki/team/{self.team_uuid}/space/{space_uuid}/page_tree",
            f"{self.api_url}/wiki/team/{self.team_uuid}/space/{space_uuid}/pages",
        ]
        
        headers = self._get_headers()
        
        for url in possible_urls:
            try:
                logger.info(f"尝试获取页面树 URL: {url}")
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        pages = data.get('pages', data.get('page_list', []))
                        logger.info(f"✓ 成功！获取到空间 {space_uuid} 的 {len(pages)} 个页面")
                        return pages
                    else:
                        error_text = await response.text()
                        logger.warning(f"✗ 失败: {response.status} - {error_text[:200]}")
            except Exception as e:
                logger.warning(f"✗ 异常: {str(e)}")
                continue
        
        logger.error("所有页面树API路径都失败了")
        return []
    
    async def get_page_content(self, page_uuid: str) -> Optional[Dict[str, Any]]:
        """
        获取页面内容（使用 online_page API）
        参考：https://github.com/brianxiadong/ones-wiki-mcp-server
        
        Args:
            page_uuid: 页面UUID
            
        Returns:
            页面内容（包含解析后的纯文本）
        """
        # 使用 online_page API 端点
        url = f"{self.base_url}/wiki/api/wiki/team/{self.team_uuid}/online_page/{page_uuid}/content"
        headers = self._get_headers()
        
        try:
            logger.info(f"获取页面内容: {url}")
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # 调试：保存原始content以供分析
                    content_json_str = data.get('content', '')
                    if content_json_str:
                        try:
                            # 尝试保存原始content到临时文件以供调试
                            import tempfile
                            import os
                            temp_dir = tempfile.gettempdir()
                            debug_file = os.path.join(temp_dir, f'ones_wiki_page_{page_uuid}_raw.json')
                            with open(debug_file, 'w', encoding='utf-8') as f:
                                f.write(content_json_str)
                            logger.info(f"原始content已保存到: {debug_file}")
                        except Exception as debug_err:
                            logger.warning(f"保存调试文件失败: {debug_err}")
                        
                        try:
                            # 解析富文本并转换为纯文本
                            plain_text = self._parse_wiki_content(content_json_str)
                            data['plain_text'] = plain_text
                            data['text_length'] = len(plain_text)
                            logger.info(f"成功解析页面内容，长度: {len(plain_text)} 字符")
                        except Exception as e:
                            logger.warning(f"解析富文本失败: {e}")
                            data['plain_text'] = ''
                    
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"获取页面内容失败: {response.status} - {error_text[:200]}")
                    return None
        except Exception as e:
            logger.error(f"获取页面内容异常: {str(e)}")
            return None
    
    def _extract_text_from_text_array(self, text_array: List[Any]) -> str:
        """
        从text数组中提取纯文本
        
        Args:
            text_array: text数组
            
        Returns:
            拼接后的文本
        """
        result = []
        for text_item in text_array:
            if isinstance(text_item, dict):
                insert_value = text_item.get('insert', '')
                if isinstance(insert_value, str):
                    result.append(insert_value)
        return ''.join(result)
    
    def _process_code_block(self, block: Dict[str, Any], content_data: Dict[str, Any]) -> str:
        """
        处理代码块（包括PlantUML、Mermaid等）
        
        Args:
            block: 代码块
            content_data: 完整的content数据（用于查找子块）
            
        Returns:
            格式化的代码块文本
        """
        result = ["\n```"]
        
        # 添加语言标识
        language = block.get('language', '')
        if language:
            result.append(language)
        result.append("\n")
        
        # 提取代码内容（从children中）
        children = block.get('children', [])
        code_lines = []
        
        for child_id in children:
            if not isinstance(child_id, str):
                continue
                
            # 从根节点查找子块
            child_node = content_data.get(child_id)
            if child_node is None:
                continue
            
            # 子块可能是数组或字典
            if isinstance(child_node, list):
                # 数组：包含多个段落
                for item in child_node:
                    if isinstance(item, dict) and 'text' in item:
                        text = self._extract_text_from_text_array(item['text'])
                        code_lines.append(text)
            elif isinstance(child_node, dict) and 'text' in child_node:
                # 字典：单个块
                text = self._extract_text_from_text_array(child_node['text'])
                code_lines.append(text)
        
        # 拼接代码内容
        code_content = ''.join(code_lines)
        result.append(code_content)
        
        # 确保代码块结尾有换行符
        if code_content and not code_content.endswith('\n'):
            result.append('\n')
        
        result.append("```\n")
        return ''.join(result)
    
    def _process_table_block(self, block: Dict[str, Any], content_data: Dict[str, Any]) -> str:
        """
        处理表格块
        
        Args:
            block: 表格块
            content_data: 完整的content数据
            
        Returns:
            格式化的表格文本
        """
        result = ["\n### 表格\n\n"]
        
        children = block.get('children', [])
        cols = block.get('cols', 2)
        
        for i, child_id in enumerate(children):
            if not isinstance(child_id, str):
                continue
            
            cell_node = content_data.get(child_id)
            if cell_node is None:
                continue
            
            # 处理单元格内容
            cell_text = ""
            if isinstance(cell_node, list):
                for cell_content in cell_node:
                    if isinstance(cell_content, dict) and 'text' in cell_content:
                        cell_text = self._extract_text_from_text_array(cell_content['text'])
                        break
            elif isinstance(cell_node, dict) and 'text' in cell_node:
                cell_text = self._extract_text_from_text_array(cell_node['text'])
            
            if cell_text.strip():
                result.append(f"| {cell_text.strip()} ")
            
            # 行结束
            if (i + 1) % cols == 0:
                result.append("|\n")
        
        result.append("\n")
        return ''.join(result)
    
    def _process_embed_block(self, block: Dict[str, Any], content_data: Dict[str, Any]) -> str:
        """
        处理嵌入块（图片、附件、mermaid、plantuml等）
        支持从embedData或children中提取内容
        
        Args:
            block: 嵌入块
            content_data: 完整的content数据（用于查找children）
            
        Returns:
            格式化的嵌入内容描述
        """
        embed_type = block.get('embedType', '')
        embed_data = block.get('embedData', {})
        children = block.get('children', [])
        
        # 调试：输出完整的block结构以分析数据格式
        logger.debug(f"嵌入块类型: {embed_type}, has_children: {len(children) > 0}")
        logger.debug(f"嵌入块数据: {json.dumps(embed_data, ensure_ascii=False, indent=2)}")
        
        if embed_type == 'image':
            src = embed_data.get('src', 'Unknown image')
            return f"\n[图片: {src}]\n"
        elif embed_type in ['mermaid', 'plantuml']:
            # 方案1：使用正确的字段名从embedData获取代码
            if embed_type == 'mermaid':
                code = embed_data.get('mermaidText', '')
            elif embed_type == 'plantuml':
                code = embed_data.get('plantumlText', '')
            else:
                code = ''
            
            # 如果成功提取到代码，返回格式化的代码块
            if code:
                return f"\n```{embed_type}\n{code}\n```\n"
            else:
                logger.warning(f"{embed_type}块未找到代码内容")
                return f"\n[嵌入内容: {embed_type}]\n"
        elif embed_type:
            # 其他嵌入类型，尝试提取通用代码或返回占位符
            code = (embed_data.get('code') or 
                   embed_data.get('content') or 
                   embed_data.get('source') or '')
            if code:
                return f"\n```{embed_type}\n{code}\n```\n"
            return f"\n[嵌入内容: {embed_type}]\n"
        
        return ""
    
    def _process_heading_block(self, block: Dict[str, Any]) -> str:
        """
        处理标题块
        
        Args:
            block: 标题块
            
        Returns:
            格式化的标题文本
        """
        heading_level = block.get('heading', 1)
        prefix = '#' * heading_level
        
        text_data = block.get('text', [])
        if isinstance(text_data, list):
            text = self._extract_text_from_text_array(text_data)
            if text.strip():
                return f"\n{prefix} {text}\n"
        
        return ""
    
    def _process_list_block(self, block: Dict[str, Any]) -> str:
        """
        处理列表块
        
        Args:
            block: 列表块
            
        Returns:
            格式化的列表项文本
        """
        ordered = block.get('ordered', False)
        level = block.get('level', 1)
        indent = "  " * (level - 1)
        prefix = f"{indent}1. " if ordered else f"{indent}- "
        
        text_data = block.get('text', [])
        if isinstance(text_data, list):
            text = self._extract_text_from_text_array(text_data)
            if text.strip():
                return f"{prefix}{text}\n"
        
        return ""
    
    def _process_text_block(self, block: Dict[str, Any]) -> str:
        """
        处理普通文本块
        
        Args:
            block: 文本块
            
        Returns:
            提取的文本
        """
        text_data = block.get('text', [])
        if isinstance(text_data, list):
            text = self._extract_text_from_text_array(text_data)
            if text.strip():
                return text
        
        return ""
    
    def _parse_wiki_content(self, content_json_str: str) -> str:
        """
        解析ONES Wiki富文本内容并转换为纯文本
        支持代码块（PlantUML/Mermaid）、表格、嵌入内容等
        
        Args:
            content_json_str: JSON字符串格式的内容
            
        Returns:
            解析后的纯文本
        """
        try:
            content_data = json.loads(content_json_str)
            result_lines = []
            
            # 处理 blocks 字段（主要内容）
            blocks = content_data.get('blocks', [])
            for block in blocks:
                if not isinstance(block, dict):
                    continue
                
                # 根据块类型分发处理
                block_type = block.get('type', '')
                block_content = ""
                
                if block_type == 'code':
                    # 代码块（PlantUML、Mermaid等）
                    block_content = self._process_code_block(block, content_data)
                elif block_type == 'table':
                    # 表格
                    block_content = self._process_table_block(block, content_data)
                elif block_type == 'embed':
                    # 嵌入内容（图片、附件等）
                    block_content = self._process_embed_block(block, content_data)
                elif block_type == 'list':
                    # 列表
                    block_content = self._process_list_block(block)
                elif 'heading' in block:
                    # 标题
                    block_content = self._process_heading_block(block)
                else:
                    # 普通文本或未知类型
                    block_content = self._process_text_block(block)
                
                if block_content:
                    result_lines.append(block_content)
            
            # 如果blocks为空，尝试遍历所有字段（兼容旧格式）
            if not result_lines:
                for block_id, blocks_list in content_data.items():
                    if block_id in ('blocks', 'meta', 'comments', 'authors', 'commentators'):
                        continue
                    if not isinstance(blocks_list, list):
                        continue
                    
                    for block in blocks_list:
                        if isinstance(block, dict):
                            text_data = block.get('text', [])
                            if isinstance(text_data, list):
                                text = self._extract_text_from_text_array(text_data)
                                if text.strip():
                                    result_lines.append(text)
            
            return '\n'.join(result_lines)
        
        except Exception as e:
            logger.error(f"解析富文本内容失败: {e}")
            return f"[解析错误: {e}]"
    
    async def search_pages(self, keyword: str, space_uuid: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        搜索页面（如果API不可用，则使用本地搜索）
        
        Args:
            keyword: 搜索关键词
            space_uuid: 可选的空间UUID，限制搜索范围（必填，因为需要获取页面树）
            
        Returns:
            搜索结果列表
        """
        # 如果没有指定space_uuid，使用本地搜索方法
        if not space_uuid:
            logger.info(f"未指定space_uuid，尝试使用本地搜索方法")
            return await self._local_search(keyword, space_uuid)
        
        # 尝试API搜索
        possible_urls = [
            f"{self.base_url}/wiki/api/wiki/team/{self.team_uuid}/pages/search",
            f"{self.api_url}/wiki/team/{self.team_uuid}/pages/search",
            f"{self.base_url}/wiki/api/wiki/search",
        ]
        
        headers = self._get_headers()
        payload = {
            "keyword": keyword,
            "team_uuid": self.team_uuid
        }
        if space_uuid:
            payload["space_uuid"] = space_uuid
        
        for url in possible_urls:
            try:
                logger.info(f"尝试搜索 URL: {url}")
                async with self.session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('pages', data.get('results', []))
                        logger.info(f"✓ API搜索成功！'{keyword}' 找到 {len(results)} 个结果")
                        return results
                    else:
                        error_text = await response.text()
                        logger.warning(f"✗ 失败: {response.status}")
            except Exception as e:
                logger.warning(f"✗ 异常: {str(e)}")
                continue
        
        # API搜索失败，使用本地搜索
        logger.info(f"API搜索失败，使用本地搜索方法")
        return await self._local_search(keyword, space_uuid)
    
    async def _local_search(self, keyword: str, space_uuid: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        本地搜索：通过获取页面树并在标题、作者中搜索关键词
        
        Args:
            keyword: 搜索关键词
            space_uuid: 空间UUID，如果为None则搜索所有空间
            
        Returns:
            搜索结果列表
        """
        logger.info(f"开始本地搜索：'{keyword}' 在空间 {space_uuid or '所有空间'}")
        
        # 如果没有指定space_uuid，则搜索所有空间
        if not space_uuid:
            logger.info("未指定space_uuid，尝试搜索所有空间")
            
            # 优先使用预定义的可访问空间列表（避免调用可能不存在的/spaces API）
            if self.accessible_spaces:
                logger.info(f"使用预定义的 {len(self.accessible_spaces)} 个可访问空间")
                all_results = []
                for space_id in self.accessible_spaces:
                    logger.info(f"正在搜索预定义空间: {space_id}")
                    space_results = await self._search_in_space(keyword, space_id, space_id)
                    all_results.extend(space_results)
                
                logger.info(f"全局搜索完成：'{keyword}' 在 {len(self.accessible_spaces)} 个预定义空间中找到 {len(all_results)} 个结果")
                return all_results
            
            # 如果没有配置accessible_spaces，尝试调用API获取空间列表
            spaces = await self.get_spaces()
            
            if not spaces:
                # API调用失败，使用默认空间
                if self.default_space_uuid:
                    logger.warning(f"无法获取空间列表，使用默认空间: {self.default_space_uuid}")
                    return await self._search_in_space(keyword, self.default_space_uuid)
                else:
                    logger.error("无法获取空间列表且未配置可访问空间或默认空间")
                    return []
            
            # 成功获取空间列表，搜索所有空间
            all_results = []
            for space in spaces:
                space_id = space.get('uuid')
                space_name = space.get('name', '未知空间')
                logger.info(f"正在搜索空间: {space_name} ({space_id})")
                
                space_results = await self._search_in_space(keyword, space_id, space_name)
                all_results.extend(space_results)
            
            logger.info(f"全局搜索完成：'{keyword}' 在 {len(spaces)} 个空间中找到 {len(all_results)} 个结果")
            return all_results
        
        # 指定了space_uuid，只搜索该空间
        return await self._search_in_space(keyword, space_uuid)
    
    async def _search_in_space(self, keyword: str, space_uuid: str, space_name: str = None) -> List[Dict[str, Any]]:
        """
        在指定空间中搜索
        
        Args:
            keyword: 搜索关键词
            space_uuid: 空间UUID
            space_name: 空间名称（可选，用于日志）
            
        Returns:
            搜索结果列表
        """
        # 获取页面树
        pages = await self.get_page_tree(space_uuid)
        
        if not pages:
            logger.warning(f"未获取到空间 {space_uuid} 的页面树")
            return []
        
        # 在标题、作者中搜索关键词（不区分大小写）
        keyword_lower = keyword.lower()
        results = []
        
        for page in pages:
            title = page.get('title', '')
            # 尝试获取作者信息（可能的字段名）
            owner_name = page.get('owner_name', '')
            creator_name = page.get('creator_name', '')
            author = page.get('author', '')
            
            # 检查是否在标题或作者中匹配
            title_match = keyword_lower in title.lower()
            author_match = (keyword_lower in owner_name.lower() or 
                          keyword_lower in creator_name.lower() or 
                          keyword_lower in author.lower())
            
            if title_match or author_match:
                match_info = []
                if title_match:
                    match_info.append(f'标题: {title}')
                if author_match:
                    author_info = owner_name or creator_name or author or '未知'
                    match_info.append(f'作者: {author_info}')
                
                # 如果有空间名称，添加到摘要中
                if space_name:
                    match_info.append(f'空间: {space_name}')
                
                results.append({
                    'uuid': page.get('uuid'),
                    'title': title,
                    'space_uuid': space_uuid,
                    'excerpt': ' | '.join(match_info),
                    'updated_time': page.get('updated_time'),
                    'owner_name': owner_name or creator_name or author,
                })
        
        logger.info(f"空间 {space_uuid} 搜索完成：找到 {len(results)} 个结果")
        return results
    
    async def get_page_history(self, page_uuid: str) -> List[Dict[str, Any]]:
        """
        获取页面历史版本
        
        Args:
            page_uuid: 页面UUID
            
        Returns:
            历史版本列表
        """
        try:
            url = f"{self.api_url}/wiki/team/{self.team_uuid}/page/{page_uuid}/versions"
            headers = self._get_headers()
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    versions = data.get('versions', [])
                    logger.info(f"获取到页面 {page_uuid} 的 {len(versions)} 个历史版本")
                    return versions
                else:
                    error_text = await response.text()
                    logger.error(f"获取页面历史失败: {response.status} - {error_text}")
                    return []
        except Exception as e:
            logger.error(f"获取页面历史异常: {str(e)}")
            return []


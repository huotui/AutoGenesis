import os
import pytest
import allure
import asyncio

# 确保能导入 common 模块
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.mcp_client import MCPClient
from common.attach import readAttach_mcp


@allure.epic("必应")
@allure.title("搜索微软")
@pytest.mark.asyncio
async def test_bing_search_microsoft():
    """测试Bing搜索微软并验证结果"""
    client = MCPClient()
    
    try:
        # 连接 MCP 服务器
        await client.connect()
        
        # 打开Bing首页
        await client.browser_navigate(
            url="https://cn.bing.com/",
            step="导航到Bing首页",
            scenario="Bing搜索微软验证"
        )
        
        # 等待页面加载
        await asyncio.sleep(2)
        
        # 在搜索框输入"微软"
        await client.send_keys(
            locator_value="#sb_form_q",
            text="微软",
            step="在搜索框输入微软",
            scenario="Bing搜索微软验证"
        )
        
        # 按Enter键执行搜索
        await client.press_key(
            key="Enter",
            step="按Enter键执行搜索",
            scenario="Bing搜索微软验证"
        )
        
        # 等待搜索结果加载
        await asyncio.sleep(3)
        
        # 等待搜索结果容器出现
        await client.wait_for_element(
            locator_value="#b_results",
            timeout=10000,
            step="等待搜索结果加载完成",
            scenario="Bing搜索微软验证"
        )
        
        # 验证搜索结果包含"微软"
        await client.verify_text_on_page(
            text="微软",
            step="验证搜索结果包含微软",
            scenario="Bing搜索微软验证"
        )
        
        # 截图并保存
        screenshot_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "log",
            "screenshot",
            "test_bing_search_microsoft.png"
        )
        await client.screenshot(
            file_path=screenshot_path,
            step="Take screenshot",
            scenario="Bing搜索微软验证"
        )
        
        # 附加截图到 allure 报告
        readAttach_mcp(screenshot_path, "test_bing_search_microsoft")
        
    finally:
        # 关闭连接
        await client.close()

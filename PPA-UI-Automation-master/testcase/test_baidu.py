import os
import pytest
import allure
import asyncio

# 确保能导入 common 模块
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.mcp_client import MCPClient
from common.attach import readAttach_mcp


@allure.epic("百度")
@allure.title("搜索playwright")
@pytest.mark.asyncio
async def test_playwright():
    """测试百度搜索 playwright"""
    client = MCPClient()
    
    try:
        # 连接 MCP 服务器
        await client.connect()
        
        # 打开百度
        await client.browser_navigate(
            url="https://www.baidu.com/",
            step="Open Baidu",
            scenario="搜索playwright"
        )
        
        # 等待页面加载
        await asyncio.sleep(2)
        
        # 点击搜索框
        await client.click_element(
            locator_value="#kw",
            step="Click search box",
            scenario="搜索playwright"
        )
        
        # 输入搜索内容
        await client.send_keys(
            locator_value="#kw",
            text="playwright",
            step="Input playwright",
            scenario="搜索playwright"
        )
        
        # 点击百度一下按钮
        await client.click_element(
            locator_value="button[id=su]",
            step="Click search button",
            scenario="搜索playwright"
        )
        
        # 截图并保存
        screenshot_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "log",
            "screenshot",
            "test_playwright.png"
        )
        await client.screenshot(
            file_path=screenshot_path,
            step="Take screenshot",
            scenario="搜索playwright"
        )
        
        # 附加截图到 allure 报告
        readAttach_mcp(screenshot_path, "test_playwright")
        
    finally:
        # 关闭连接
        await client.close()

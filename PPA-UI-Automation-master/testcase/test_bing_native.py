import os
import pytest
import allure
import asyncio
from playwright.async_api import async_playwright, expect
from common.attach import readAttach_mcp


@allure.epic("必应")
@allure.title("搜索微软 - 原生Playwright格式")
@pytest.mark.asyncio
async def test_bing_search_native():
    """测试Bing搜索微软 - 原生 Playwright 格式(高性能版本)"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 打开Bing首页
            await page.goto("https://cn.bing.com/")
            await page.wait_for_load_state("networkidle")
            
            # 等待页面加载
            await asyncio.sleep(2)
            
            # 在搜索框输入"微软"
            await page.locator("#sb_form_q").fill("微软")
            
            # 按Enter键执行搜索
            await page.keyboard.press("Enter")
            
            # 等待搜索结果加载
            await asyncio.sleep(3)
            
            # 等待搜索结果容器出现
            await page.wait_for_selector("#b_results", timeout=10000)
            
            # 验证搜索结果包含"微软"
            await expect(page).to_contain_text("微软")
            
            # 截图并保存
            screenshot_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "log",
                "screenshot",
                "test_bing_search_native.png"
            )
            await page.screenshot(path=screenshot_path)
            
            # 附加截图到 allure 报告
            readAttach_mcp(screenshot_path, "test_bing_search_native")
            
        finally:
            # 关闭浏览器
            await context.close()
            await browser.close()


@allure.epic("百度")
@allure.title("搜索playwright - 原生Playwright格式")
@pytest.mark.asyncio
async def test_baidu_playwright_native():
    """测试百度搜索 playwright - 原生 Playwright 格式"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 打开百度
            await page.goto("https://www.baidu.com/")
            await page.wait_for_load_state("networkidle")
            
            # 等待页面加载
            await asyncio.sleep(2)
            
            # 点击搜索框并输入
            await page.locator("#kw").fill("playwright")
            
            # 点击百度一下按钮
            await page.locator("button[id=su]").click()
            
            # 等待搜索结果加载
            await asyncio.sleep(2)
            
            # 截图并保存
            screenshot_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "log",
                "screenshot",
                "test_baidu_playwright_native.png"
            )
            await page.screenshot(path=screenshot_path)
            
            # 附加截图到 allure 报告
            readAttach_mcp(screenshot_path, "test_baidu_playwright_native")
            
        finally:
            # 关闭浏览器
            await context.close()
            await browser.close()


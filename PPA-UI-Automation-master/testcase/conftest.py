import os
import sys
import pytest
import allure
from pytest import Item

# 项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.mcp_client import MCPClient


# fixtures
def pytest_runtest_call(item: Item):
    if item.parent._obj.__doc__:
        allure.dynamic.feature(item.parent._obj.__doc__)
    if item.function.__doc__:
        allure.dynamic.title(item.function.__doc__)


@pytest.fixture(scope="function")
def mcp_client():
    """创建 MCP 客户端 fixture"""
    client = MCPClient()
    return client


@pytest.fixture(scope="function")
def page(mcp_client):
    """创建页面操作对象,基于 MCP 客户端"""
    class MCPPage:
        def __init__(self, client):
            self.client = client
            self.connected = False

        async def connect(self):
            if not self.connected:
                await self.client.connect()
                self.connected = True

        async def goto(self, url):
            await self.client.browser_navigate(url, step="Navigate to URL")

        async def click(self, selector):
            await self.client.click_element(selector, step=f"Click {selector}")

        async def fill(self, selector, text):
            await self.client.send_keys(selector, text, step=f"Fill {selector}")

        async def locator(self, selector):
            """返回 locator 对象,支持链式调用"""
            class Locator:
                def __init__(self, sel, cli):
                    self.selector = sel
                    self.client = cli

                async def click(self):
                    await self.client.click_element(self.selector, step=f"Click {self.selector}")

                async def fill(self, text):
                    await self.client.send_keys(self.selector, text, step=f"Fill {self.selector}")

                async def get_text(self):
                    return await self.client.get_text(self.selector, step=f"Get text from {self.selector}")

            return Locator(selector, self.client)

        async def get_by_role(self, role, name=None):
            class RoleLocator:
                def __init__(self, r, n, cli):
                    self.role = r
                    self.name = n
                    self.client = cli

                async def click(self):
                    locator = f"[role={self.role}]"
                    if self.name:
                        locator = f"text={self.name}"
                    await self.client.click_element(locator, step=f"Click {role} {name}")

            return RoleLocator(role, name, self.client)

    page = MCPPage(mcp_client)
    return page

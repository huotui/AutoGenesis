import asyncio
import json
import os
from typing import Any, Dict, Optional
import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.session = None
        self.stdio_context = None

    async def connect(self):
        mcp_server_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "playwright-mcp-server")
        )
        config_path = os.path.join(mcp_server_path, "conf", "playwright_conf.json")
        
        server_params = StdioServerParameters(
            command="python",
            args=["simple_server.py", "--transport", "stdio", "--config", config_path],
            cwd=mcp_server_path
        )
        
        try:
            self.stdio_context = stdio_client(server_params)
            read, write = await self.stdio_context.__aenter__()
            self.session = ClientSession(read, write)
            await self.session.__aenter__()
            await self.session.initialize()
            tools = await self.session.list_tools()
            print(f"Connected to MCP server, available tools: {[t.name for t in tools.tools]}")
        except Exception as e:
            print(f"Failed to connect to MCP server: {e}")
            if self.session:
                await self.session.__aexit__(None, None, None)
            if self.stdio_context:
                await self.stdio_context.__aexit__(None, None, None)
            raise
        
        return self

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if not self.session:
            raise RuntimeError("MCP client not connected")
        result = await self.session.call_tool(tool_name, arguments)
        return result

    async def browser_navigate(self, url: str, step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("browser_navigate", {
            "url": url,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def click_element(self, locator_value: str, locator_strategy: str = "css",
                           step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("click_element", {
            "locator_value": locator_value,
            "locator_strategy": locator_strategy,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def send_keys(self, locator_value: str, text: str, locator_strategy: str = "css",
                       step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("send_keys", {
            "locator_value": locator_value,
            "text": text,
            "locator_strategy": locator_strategy,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def get_text(self, locator_value: str, locator_strategy: str = "css",
                      step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("get_text", {
            "locator_value": locator_value,
            "locator_strategy": locator_strategy,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def screenshot(self, file_path: str, step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("screenshot", {
            "file_path": file_path,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def verify_element_exists(self, locator_value: str, locator_strategy: str = "css",
                                   step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("verify_element_exists", {
            "locator_value": locator_value,
            "locator_strategy": locator_strategy,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def verify_text_on_page(self, text: str, step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("verify_text_on_page", {
            "text": text,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def get_page_title(self, step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("get_page_title", {
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def get_page_url(self, step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("get_page_url", {
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def scroll_page(self, direction: str = "down", amount: int = 300,
                         step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("scroll_page", {
            "direction": direction,
            "amount": amount,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def wait_for_element(self, locator_value: str, timeout: int = 5000,
                              locator_strategy: str = "css",
                              step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("wait_for_element", {
            "locator_value": locator_value,
            "timeout": timeout,
            "locator_strategy": locator_strategy,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def press_key(self, key: str, step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("press_key", {
            "key": key,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def hover_element(self, locator_value: str, locator_strategy: str = "css",
                           step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("hover_element", {
            "locator_value": locator_value,
            "locator_strategy": locator_strategy,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def select_option(self, locator_value: str, option_value: str,
                           locator_strategy: str = "css",
                           step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("select_option", {
            "locator_value": locator_value,
            "option_value": option_value,
            "locator_strategy": locator_strategy,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def execute_javascript(self, script: str, step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("execute_javascript", {
            "script": script,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def find_element(self, locator_value: str, locator_strategy: str = "css",
                          step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("find_element", {
            "locator_value": locator_value,
            "locator_strategy": locator_strategy,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def scroll_to_element(self, locator_value: str, locator_strategy: str = "css",
                               step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("scroll_to_element", {
            "locator_value": locator_value,
            "locator_strategy": locator_strategy,
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def browser_close(self, step: str = "", scenario: str = "") -> Any:
        return await self.call_tool("browser_close", {
            "step": step,
            "scenario": scenario,
            "caller": "PPA-UI-Automation"
        })

    async def close(self):
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
            except:
                pass
        if self.stdio_context:
            try:
                await self.stdio_context.__aexit__(None, None, None)
            except:
                pass

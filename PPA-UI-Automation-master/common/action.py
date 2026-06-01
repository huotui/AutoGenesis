"""
常用操作封装 - 基于 MCP 客户端
"""


async def click_fill_mcp(client, locator_value, fills, locator_strategy="css", step="", scenario=""):
    """点击元素并输入文本"""
    await client.click_element(
        locator_value=locator_value,
        locator_strategy=locator_strategy,
        step=f"Click {locator_value}",
        scenario=scenario
    )
    await client.send_keys(
        locator_value=locator_value,
        text=fills,
        locator_strategy=locator_strategy,
        step=f"Fill {locator_value}",
        scenario=scenario
    )

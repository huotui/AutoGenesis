import allure

"""
结果处理动作封装
- readAttach: Playwright Page 对象截图 (旧版)
- readAttach_mcp: 直接读取已存在的截图文件 (MCP 版)
"""


# 结果截图与Allure提取 (旧版 - Playwright)
def readAttach(page, paths, fileName):
    page.screenshot(path=paths + fileName + ".png")
    with open(paths + fileName + ".png", "rb") as file:
        allure.attach(file.read(), name=fileName, attachment_type=allure.attachment_type.PNG)


# MCP 版本 - 直接读取已存在的截图文件
def readAttach_mcp(screenshot_path, fileName):
    """读取已存在的截图文件并附加到 Allure 报告"""
    with open(screenshot_path, "rb") as file:
        allure.attach(
            file.read(),
            name=fileName,
            attachment_type=allure.attachment_type.PNG
        )

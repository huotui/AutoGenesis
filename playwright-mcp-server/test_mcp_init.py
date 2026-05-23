import asyncio
import sys
import os

async def test_server_init():
    """Test MCP server initialization"""
    from mcp.client.stdio import stdio_client, StdioServerParameters
    from mcp.client.session import ClientSession
    
    server_params = StdioServerParameters(
        command="uv",
        args=[
            "run",
            "--project",
            r"d:\workspace\trae\AutoGenesis\playwright-mcp-server",
            "python",
            r"d:\workspace\trae\AutoGenesis\playwright-mcp-server\simple_server.py",
            "--transport",
            "stdio"
        ],
        env={**os.environ, "PYTHONIOENCODING": "utf-8"}
    )
    
    print("Starting MCP server...")
    try:
        async with stdio_client(server_params) as streams:
            print("Connected to server, initializing session...")
            async with ClientSession(*streams) as session:
                print("Initializing...")
                await session.initialize()
                print("✅ SUCCESS: MCP server initialized!")
                
                # Test a simple tool call
                result = await session.call_tool("get_page_title", {"caller": "test"})
                print(f"Tool call result: {result}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_server_init())

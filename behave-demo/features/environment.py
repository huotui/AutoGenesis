# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from asyncio.log import logger
import json
import os
import re
import time
import threading
import asyncio
import janus
import queue
import pathlib
from datetime import datetime
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client, StdioServerParameters
from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry
from applicationinsights import TelemetryClient

# MCP server name - set to a specific server name from .vscode/mcp.json to use it.
# Leave empty to auto-discover (prefers stdio over SSE, matching "auto-genesis" prefix).
AUTO_GENESIS_MCP_SERVER = ''

session_ready = threading.Event()

# Global package variable - loaded from environment
package = os.environ.get('PACKAGE', 'com.microsoft.emmx.canary')

# Retry configuration
# Supported modes: 'step' (retry failed steps), 'scenario' (retry entire scenario)
RETRY_CONFIG = {
    'mode': os.environ.get('RETRY_MODE', 'step'),  # 'step' or 'scenario'
    'max_attempts': int(os.environ.get('RETRY_MAX_ATTEMPTS', '0'))  # Default 0 retries
}

def get_retry_config():
    """Get current retry configuration.
    
    Returns:
        dict: Dictionary with 'mode' and 'max_attempts' keys
    """
    return RETRY_CONFIG.copy()

def should_retry_step():
    """Check if step retry is enabled."""
    return RETRY_CONFIG['mode'] == 'step' and RETRY_CONFIG['max_attempts'] > 0

def should_retry_scenario():
    """Check if scenario retry is enabled."""
    return RETRY_CONFIG['mode'] == 'scenario' and RETRY_CONFIG['max_attempts'] > 0

def load_mcp_config(server_name=None):
    """Load MCP server configuration from .vscode/mcp.json.

    Args:
        server_name: Exact server name to look up. If *None* or empty,
                     falls back to the first server whose name starts with
                     ``auto-genesis`` and uses the stdio transport (i.e. has
                     a ``command`` field).

    Returns:
        A dict with the resolved configuration::

            For stdio servers:
                {"transport": "stdio", "command": ..., "args": [...], "env": {...}}
            For SSE servers:
                {"transport": "sse", "url": ...}
    """
    # Walk up from this file's directory to find .vscode/mcp.json
    current_dir = pathlib.Path(__file__).parent
    mcp_config_path = None
    while True:
        candidate = current_dir / ".vscode" / "mcp.json"
        if candidate.exists():
            mcp_config_path = candidate
            break
        parent = current_dir.parent
        if parent == current_dir:
            # Reached filesystem root
            break
        current_dir = parent

    if mcp_config_path is None:
        raise FileNotFoundError(
            "MCP config file (.vscode/mcp.json) not found in any parent directory "
            f"starting from {pathlib.Path(__file__).parent}"
        )

    print(f"Found MCP config: {mcp_config_path}")

    with open(mcp_config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    servers = config.get("servers", {})

    # --- 1. Try the explicitly requested server name ---
    if server_name:
        if server_name not in servers:
            raise ValueError(
                f"MCP server '{server_name}' not found in mcp.json. "
                f"Available servers: {', '.join(servers.keys())}"
            )
        server_config = servers[server_name]
        result = _parse_server_config(server_name, server_config)
        print(f"Loaded MCP server '{server_name}' ({result['transport']}) from mcp.json")
        return result

    # --- 2. Auto-discover: prefer stdio, then SSE, matching "auto-genesis" prefix ---
    sse_fallback = None
    for name, server_config in servers.items():
        if not name.startswith("auto-genesis"):
            continue
        if "command" in server_config:
            result = _parse_server_config(name, server_config)
            print(f"Auto-discovered MCP server '{name}' (stdio) from mcp.json")
            return result
        if "url" in server_config and sse_fallback is None:
            sse_fallback = (name, server_config)

    if sse_fallback:
        name, server_config = sse_fallback
        result = _parse_server_config(name, server_config)
        print(f"Auto-discovered MCP server '{name}' (sse) from mcp.json")
        return result

    raise ValueError(
        "No matching MCP server found in mcp.json. "
        "Set AUTO_GENESIS_MCP_SERVER in environment.py, "
        f"or add a server whose name starts with 'auto-genesis'. "
        f"Available servers: {', '.join(servers.keys())}"
    )


def _parse_server_config(name, server_config):
    """Return a normalised config dict from a raw mcp.json server entry."""
    if "url" in server_config:
        return {
            "transport": "sse",
            "url": server_config["url"],
        }
    if "command" in server_config:
        return {
            "transport": "stdio",
            "command": server_config["command"],
            "args": server_config.get("args", []),
            "env": server_config.get("env", {}),
        }
    raise ValueError(
        f"MCP server '{name}' has neither 'url' (SSE) nor 'command' (stdio) configured."
    )

def take_screenshot(context, scenario_name):
    """
    Take a full screen screenshot and save it with the scenario name
    Screenshot naming convention: *{test_name}*.png
    Storage location: SCREENSHOT_DIR environment variable
    """
    try:
        # Get screenshot directory from environment variable
        screenshot_dir = os.environ.get('SCREENSHOT_DIR')
        if not screenshot_dir:
            # Fallback to default location if env var not set
            current_dir = pathlib.Path(__file__).parent.parent
            screenshot_dir = current_dir / 'screenshots'
        else:
            screenshot_dir = pathlib.Path(screenshot_dir)

        # Create screenshots directory if it doesn't exist
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        # Get testcase name (scenario_name is the testcase name)
        name = scenario_name

        # Clean test name for use as filename - replace spaces with underscores
        # Screenshot naming convention: *{test_name}*.png
        test_name_pattern = clean_test_name(name)

        # Add timestamp to avoid filename conflicts while following the pattern
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{test_name_pattern}_{timestamp}.png'

        # Full path for the screenshot
        screenshot_path = screenshot_dir / filename

        # Try Playwright screenshot tool first, fallback to legacy take_screenshot tool
        result = None
        try:
            print(f"Taking screenshot: {screenshot_path}")
            result = call_tool_sync(context, context.session.call_tool(
                name="screenshot", 
                arguments={
                    "caller": "behave-automation",
                    "file_path": str(screenshot_path),
                    "step": f"screenshot_{test_name_pattern}",
                    "scenario": scenario_name
                }
            ))
            print(f"Screenshot tool raw result type: {type(result)}")
            print(f"Screenshot tool raw result: {result}")
        except Exception as e1:
            print(f"Playwright screenshot failed: {e1}")
            import traceback
            traceback.print_exc()
            try:
                # Fallback to legacy take_screenshot tool
                result = call_tool_sync(context, context.session.call_tool(
                    name="take_screenshot", 
                    arguments={"save_path": str(screenshot_path)}
                ))
            except Exception as e2:
                print(f"Legacy screenshot also failed: {e2}")
                return None
        
        # Safely get the result JSON
        if result is None:
            print(f"Warning: Screenshot tool returned None")
            return None
            
        result_json = get_tool_json(result)
        if result_json is None:
            print(f"Warning: Could not parse screenshot result for {screenshot_path}")
            # Even if we can't parse the result, check if the file was created
            if os.path.exists(screenshot_path):
                print(f'Screenshot file exists: {screenshot_path}')
                return str(screenshot_path)
            return None
        
        status = result_json.get('status') if isinstance(result_json, dict) else None
        if status == "success":
            print(f'Screenshot saved: {screenshot_path}')
            return str(screenshot_path)
        else:
            print(f'Screenshot failed: {result_json}')
            return None

    except Exception as e:
        print(f'Error taking screenshot: {str(e)}')
        import traceback
        traceback.print_exc()
        return None

def clean_test_name(name):
    """
    Clean test case name by removing/replacing special characters

    Args:
        name: Original test case name

    Returns:
        str: Cleaned name suitable for file pattern matching
    """
    if not name:
        return ''

    # Replace common problematic characters with underscore
    # Keep only alphanumeric, underscore, hyphen, and space
    cleaned = re.sub(r'[^\w\s\-]', '_', name)

    # Replace multiple spaces with single space, then replace spaces with underscore
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = cleaned.replace(' ', '_')

    # Replace multiple underscores with single underscore
    cleaned = re.sub(r'_+', '_', cleaned)

    # Remove leading and trailing underscores
    cleaned = cleaned.strip('_')

    return cleaned

def before_all(context):
    import threading

    # Print package information for debugging
    global package
    if package:
        print(f"Package loaded from environment: {package}")
    else:
        print("Warning: 'package' environment variable not set")

    # Initialize Application Insights telemetry client
    telemetry_client = TelemetryClient('6cfcacca-7f4d-476e-85f4-c184d70ccff9')
    context.telemetry_client = telemetry_client 
    context._task_queue = janus.Queue()
    context._result_queue = janus.Queue()
    
    # Reset the global session_ready event
    session_ready.clear()

    def run_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def mcp_worker():
            global session_ready
            try:
                mcp_config = load_mcp_config(server_name=AUTO_GENESIS_MCP_SERVER or None)
                transport = mcp_config["transport"]

                if transport == "stdio":
                    print("Using stdio transport for MCP server")
                    command = mcp_config["command"]
                    args = mcp_config["args"]
                    env = mcp_config.get("env", {})
                    print(f"Loading MCP server with command: {command}")
                    print(f"Args: {args}")
                    
                    # Define MCP server parameters
                    server_params = StdioServerParameters(
                        command=command,
                        args=args,
                        env={**os.environ, **env} if env else None
                    )
                    
                    # Connect to server using stdio_client
                    async with stdio_client(server_params) as streams:
                        async with ClientSession(*streams) as session:
                            await session.initialize()
                            context.session = session
                            session_ready.set()

                            while True:
                                task = await context._task_queue.async_q.get()
                                if task is None:
                                    break

                                coro = task
                                result = await coro
                                await context._result_queue.async_q.put(result)
                else:
                    sse_url = mcp_config["url"]
                    print("Using SSE transport for MCP server")
                    print(f"Connecting to SSE server at {sse_url}")
                    async with sse_client(sse_url) as streams:
                        async with ClientSession(*streams) as session:
                            await session.initialize()
                            context.session = session
                            session_ready.set()

                            while True:
                                task = await context._task_queue.async_q.get()
                                if task is None:
                                    break

                                start = time.time()
                                coro = task
                                result = await coro
                                await context._result_queue.async_q.put(result)

            except Exception as e:
                print(f"MCP init failed: {repr(e)}")
                import traceback
                traceback.print_exc()
                session_ready.set()

        loop.run_until_complete(mcp_worker())

    thread = threading.Thread(target=run_loop, daemon=True)
    thread.start()

    if not session_ready.wait(timeout=90):
        raise TimeoutError("MCP server initialization timed out after 90 seconds")
    
    if not hasattr(context, 'session') or context.session is None:
        raise RuntimeError("MCP server session was not initialized. Check mcp.json configuration.")
    
    print("MCP server session initialized successfully")




def after_all(context):
   pass

def call_tool_sync(context, coro, timeout=400):
    start = time.time()
    context._task_queue.sync_q.put(coro)
    while True:
        try:
            result = context._result_queue.sync_q.get_nowait()
            return result
        except queue.Empty:
            if time.time() - start > timeout:
                raise TimeoutError("MCP tool invocation timed out.")
            time.sleep(0.1)


def get_tool_json(result):
    try:
        if isinstance(result, str):
            return result
        items = getattr(result, "content", None)
        if items:
            for item in items:
                if getattr(item, "text", None):
                    text = getattr(item, "text", None)
                    return json.loads(text)
    except Exception as e:
        print(f"Error getting tool JSON: {e}")
        
    return None


def before_scenario(context, scenario):
    context.scenario = scenario
    if 'wip' in scenario.tags:
        print(f"Skipping scenario '{scenario.name}' because it is marked as WIP.")
        scenario.skip("Scenario is marked as WIP")
        return
    
    # Clear browser state before each scenario to avoid session carryover
    try:
        result = call_tool_sync(context, context.session.call_tool(
            name="browser_close",
            arguments={'caller': 'behave-automation'}
        ))
        print(f"Browser closed before scenario: {scenario.name}")
    except Exception as e:
        print(f"Warning: Failed to close browser before scenario: {e}")
    
    pass

def after_scenario(context, scenario):
    take_screenshot(context, scenario.name)


def before_feature(context, feature):
    config = get_retry_config()
    print(f"Retry configuration: mode='{config['mode']}', max_attempts={config['max_attempts']}")
    
    # Only apply scenario-level retry if explicitly configured
    if should_retry_scenario():
        for scenario in feature.scenarios:
            patch_scenario_with_autoretry(scenario, max_attempts=config['max_attempts'])
        print(f"Scenario retry mode enabled: each scenario will retry up to {config['max_attempts']} times")
    else:
        print(f"Scenario retry mode disabled. Step retry mode: {should_retry_step()}")

def after_step(context, step):
    config = get_retry_config()
    
    if step.status == 'failed' and should_retry_step():
        # Store failed step info for retry tracking
        if not hasattr(context, '_step_retry_count'):
            context._step_retry_count = {}
        
        # Create unique key for this step
        step_key = f"{context.scenario.name}_{step.name}_{step.line}"
        
        if step_key not in context._step_retry_count:
            context._step_retry_count[step_key] = 0
        
        context._step_retry_count[step_key] += 1
        retry_count = context._step_retry_count[step_key]
        
        if retry_count <= config['max_attempts']:
            print(f"\n{'='*60}")
            print(f"STEP RETRY: '{step.name}' failed (attempt {retry_count}/{config['max_attempts']})")
            print(f"Retrying step...")
            print(f"{'='*60}\n")
            # Re-run the failed step
            try:
                step.run(context)
                print(f"Step '{step.name}' succeeded on retry {retry_count}")
                # Update telemetry for retry success
                context.telemetry_client.track_metric(
                    "TestStepRetried", 1,
                    properties={
                        "Platform": "", 
                        "Status": 'Passed',
                        "RetryCount": str(retry_count),
                        "RunSource": "OpenSource"
                    }
                )
            except Exception as e:
                print(f"Step '{step.name}' failed again on retry {retry_count}: {e}")
                context.telemetry_client.track_metric(
                    "TestStepRetried", 1,
                    properties={
                        "Platform": "", 
                        "Status": 'Failed',
                        "RetryCount": str(retry_count),
                        "RunSource": "OpenSource"
                    }
                )
    
    # Track telemetry for all executed steps
    if step.status != 'skipped':
        context.telemetry_client.track_metric(
            "TestStepExecuted", 1,
            properties={
                "Platform": "", 
                "Status": 'Passed' if step.status == 'passed' else 'Failed',
                "RunSource": "OpenSource"
            }
        )
        context.telemetry_client.flush()
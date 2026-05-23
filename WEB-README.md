# Playwright MCP Server - Web Testing

Playwright MCP Server is a web application automated testing service based on Model Context Protocol (MCP), specifically supporting automated test script generation for web browsers including Chromium, Firefox, and WebKit.

## Features

- 🤖 AI-assisted test script generation based on MCP protocol
- 🌐 Multi-browser support (Chromium, Firefox, WebKit)
- 🎯 Automatic generation of BDD format test code
- 🚀 Support for various AI programming clients (VS Code, Cursor, etc.)
- 📸 Screenshot capture capabilities
- 🔍 Advanced element location strategies

## Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- VS Code or Cursor

#### Install uv

```powershell
# Install uv for faster dependency management
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or download from https://github.com/astral-sh/uv/releases/latest
```

### 1. Clone the Repository

Open PowerShell and run:

    git clone https://github.com/microsoft/AutoGenesis.git
    cd AutoGenesis

### 2. Install Dependencies

Navigate to the `playwright-mcp-server` directory and install Python dependencies:

    cd playwright-mcp-server
    uv sync

**Dependencies include:**
- `playwright` - Playwright Python client
- `mcp` - Model Context Protocol SDK
- Other necessary utility libraries

### 3. Install Playwright Browsers

After installing dependencies, install the Playwright browsers:

    uv run playwright install

### 4. Configure Browser Environment

Create a local config file from the template, then edit it with your browser settings:

```bash
cp conf/playwright_conf.template.json conf/playwright_conf.json
```

Then update `conf/playwright_conf.json`:

    # Open conf/playwright_conf.json and update with your settings:
    # {
    #   "browser": {
    #     "browser_name": "chromium",
    #     "headless": false,
    #     "viewport": {
    #       "width": 1280,
    #       "height": 720
    #     },
    #     "timeout": 30000,
    #     "slow_mo": 500
    #   }
    # }

**Configuration Details:**
- `browser_name`: Browser type (chromium, firefox, webkit)
- `headless`: Whether to run browser in headless mode (true/false)
- `viewport`: Browser window size
  - `width`: Window width in pixels
  - `height`: Window height in pixels
- `timeout`: Default timeout in milliseconds
- `slow_mo`: Slow down operations by specified milliseconds (useful for debugging)

### 5. Start MCP Server

Start the MCP server (default startup mode is SSE):

    cd playwright-mcp-server
    uv run python simple_server.py --transport sse

### 6. Configure MCP Client

#### 6.1 VS Code Configuration

Create or edit `.vscode/mcp.json` in your project root:

**Method 1: Using SSE Mode (Server-Sent Events)**

    # Add MCP server configuration to .vscode/mcp.json:
    # {
    #   "servers": {
    #     "auto-genesis-mcp-web": {
    #       "url": "http://localhost:8000/sse"
    #     }
    #   }
    # }
    After configuration, you need to click start to launch

**Method 2: Using stdio Mode (Recommended for Local Development)**

    # Add MCP server configuration to .vscode/mcp.json:
    # {
    #   "servers": {
    #     "auto-genesis-mcp-web": {
    #       "command": "uv",
    #       "args": [
    #         "run",
    #         "--project",
    #         "c:\\Users\\username\\projects\\AutoGenesis\\playwright-mcp-server",
    #         "python",
    #         "c:\\Users\\username\\projects\\AutoGenesis\\playwright-mcp-server\\simple_server.py",
    #         "--transport",
    #         "stdio"
    #       ],
    #       "env": {
    #         "PYTHONIOENCODING": "utf-8",
    #         "PYTHONUTF8": "1",
    #         "LANG": "en_US.UTF-8",
    #         "LC_ALL": "en_US.UTF-8"
    #       }
    #     }
    #   }
    # }

**Note:** 
- stdio mode: VS Code automatically starts and manages the MCP server process, suitable for local development
- SSE mode: Requires manual start of MCP server (`uv run python simple_server.py --transport sse`), suitable for remote servers or multi-client scenarios
- Please replace the paths with your actual project paths

#### 6.2 Cursor Configuration

Configure MCP server in Cursor settings:

**Method 1: Using SSE Mode (Server-Sent Events)**

    # Add to Cursor MCP configuration:
    # {
    #   "mcpServers": {
    #     "auto-genesis-mcp-web": {
    #       "url": "http://localhost:8000/sse"
    #     }
    #   }
    # }

**Method 2: Using stdio Mode**

    # Add to Cursor MCP configuration:
    # {
    #   "mcpServers": {
    #     "auto-genesis-mcp-web": {
    #       "command": "uv",
    #       "args": [
    #         "run",
    #         "--project",
    #         "c:\\Users\\username\\projects\\AutoGenesis\\playwright-mcp-server",
    #         "python",
    #         "c:\\Users\\username\\projects\\AutoGenesis\\playwright-mcp-server\\simple_server.py",
    #         "--transport",
    #         "stdio"
    #       ],
    #       "env": {
    #         "PYTHONIOENCODING": "utf-8",
    #         "PYTHONUTF8": "1",
    #         "LANG": "en_US.UTF-8",
    #         "LC_ALL": "en_US.UTF-8"
    #       }
    #     }
    #   }
    # }

**Note:**
- SSE mode: Need to manually start the server first, then Cursor connects via HTTP
- stdio mode: Cursor automatically starts and manages the server process
- Please replace the paths with your actual project paths

#### 6.3 Specify MCP Server Name for Behave Tests

When running behave tests, the test framework auto-discovers MCP servers from `.vscode/mcp.json` whose names start with `auto-genesis`. If you have multiple MCP servers configured or use a custom server name, you can specify the exact server name by editing `behave-demo/features/environment.py`:

```python
# Set to a specific server name from .vscode/mcp.json to use it.
# Leave empty to auto-discover (prefers stdio over SSE, matching "auto-genesis" prefix).
AUTO_GENESIS_MCP_SERVER = 'auto-genesis-mcp-web'
```

This ensures behave connects to the correct MCP server, especially useful when you have multiple MCP servers configured.

### 7. Use MCP to Generate Test Code

#### 7.1 Write Test Cases

The project already includes a sample test case `behave-demo/features/demo.feature`, you can refer to it to write new test cases suitable for web testing.

View example:

```gherkin
# Reference behave-demo/features/demo.feature
Feature: Web Browser Testing

  Scenario: Open webpage and verify title
    Given Open browser and navigate to "https://www.bing.com"
    When Page title should contain "Bing"
    Then Verify search box exists
```

#### 7.2 Generate Test Code

Use the autoGenesis-run skill to automatically generate test code from your scenarios:

This project includes a pre-configured skill that simplifies the test execution process. Simply provide your scenario name and steps in natural language:

**Quick Example:**
```
Use skill autoGenesis-run to execute scenario: Test bing.com website
```

The skill will automatically:
- Locate the scenario from .feature files in behave-demo/features/
- Parse all scenario steps
- Execute each step through MCP tool calls
- Handle retry logic and error recovery
- Generate BDD test code
- Save the generated code to your project


**For more examples and usage details, see:** [.github/skills/autoGenesis-run/](.github/skills/autoGenesis-run/)

### 8. Run Generated Test Code

Before running tests, install dependencies in the `behave-demo` directory:

    cd behave-demo
    uv sync

#### 8.1 Run Specific Scenario

Run a specific test scenario by name:

    uv run python -m behave --name "Scenario Name"

#### 8.2 More Options

For more Behave run options and usage, please refer to [Behave Official Documentation](https://behave.readthedocs.io/).

Common command examples:

    # Generate JSON report
    uv run python -m behave --format json -o reports/results.json
    
    # Filter using tags
    uv run python -m behave --tags=@smoke
    
    # Verbose output
    uv run python -m behave -v


## Available MCP Tools

The Playwright MCP server provides the following automation tools:

### Browser Navigation
- `browser_navigate` - Navigate to a URL
- `browser_close` - Close browser

### Element Interaction
- `find_element` - Find element on page
- `click_element` - Click element
- `send_keys` - Enter text in element
- `get_text` - Get text content from element
- `select_option` - Select option from dropdown
- `press_key` - Press a keyboard key
- `hover_element` - Hover mouse over element
- `scroll_page` - Scroll page up or down
- `scroll_to_element` - Scroll to make element visible

### Page Information
- `get_page_title` - Get current page title
- `get_page_url` - Get current page URL
- `wait_for_element` - Wait for element to appear

### Verification
- `verify_element_exists` - Verify element exists on page
- `verify_element_not_exists` - Verify element does not exist
- `verify_element_attribute` - Verify element attribute value
- `verify_text_on_page` - Verify text exists on page

### Utilities
- `screenshot` - Take a screenshot
- `execute_javascript` - Execute JavaScript code

## Advanced Configuration

### Local LLM Integration (Optional)

#### Configure Local LLM (e.g., Ollama, LM Studio)

Set environment variables for local LLM integration:

    $env:LOCAL_LM_ENDPOINT = "http://localhost:11434"
    $env:LOCAL_LM_MODEL_NAME = "qwen2.5:7b"
    $env:LOCAL_LM_API_KEY = "your-api-key"  # Optional

Or create a `.env` file in the project root:

    LOCAL_LM_ENDPOINT=http://localhost:11434
    LOCAL_LM_MODEL_NAME=qwen2.5:7b
    LOCAL_LM_API_KEY=your-api-key

**Configuration Options:**
- `LOCAL_LM_ENDPOINT` - Local LLM service endpoint (default: http://localhost:11434)
- `LOCAL_LM_MODEL_NAME` - Model ID/name to use (e.g., qwen2.5:7b, qwen2.5-vl:7b, llava:7b)
- `LOCAL_LM_API_KEY` - API key for local LLM (optional, required by some services)

**Supported Local LLM Services:**
- **Ollama** (port 11434) - Most popular local LLM service
- **LM Studio** (port 1234) - GUI-based, easy to use
- **FastChat** (port 8000) - Supports multiple models
- **vLLM** (port 8000) - High-performance inference service
- **LocalAI** (port 8080) - Fully OpenAI API compatible

**Recommended Models for Vision Tasks:**
- `qwen2.5-vl:7b` - Supports Chinese and image analysis
- `llava:7b` - Vision-language model
- `qwen2.5:7b` - Good Chinese language support (text only)

#### Configure Azure OpenAI

Set environment variables for Azure OpenAI integration:

    $env:AZURE_OPENAI_ENDPOINT = "your-endpoint"
    $env:AZURE_OPENAI_API_KEY = "your-api-key"
    $env:AZURE_OPENAI_DEPLOYMENT = "your-deployment-name"

Then configure Azure OpenAI credentials in `llm/chat.py` to enable screenshot analysis functionality.

**Note:** The system automatically uses Azure OpenAI if configured, falling back to local LLM if Azure is unavailable.

### Headless Mode

For CI/CD pipelines or server environments, configure headless mode in `conf/playwright_conf.json`:

    # {
    #   "browser": {
    #     "browser_name": "chromium",
    #     "headless": true
    #   }
    # }

## Troubleshooting

### MCP Server Cannot Start

Check Python version and dependencies:

    python --version
    uv pip list

Or try re-syncing:

    uv sync

Ensure Python version is 3.10 or higher. Check the log file `logs/mcp_server.log` for detailed error information.

### Playwright Browsers Not Installed

Install Playwright browsers:

    uv run playwright install

### AI Client Cannot Recognize MCP Tools

- Restart VS Code or Cursor
- Check if MCP configuration file path is correct
- Confirm MCP Server has started successfully
- Verify Python path configuration

### Generated Code Cannot Run

Run tests in verbose mode to see detailed logs:

    behave -v

Check browser configuration file and browser launch status.

## Example Use Cases

View examples in the `behave-demo/features/` directory:

- `demo.feature` - Contains complete test scenario examples

## Contributing

Contributions are welcome! Please check [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## Contact

For questions or suggestions, please contact: autogenesis@microsoft.com

## License

Please check [LICENSE]

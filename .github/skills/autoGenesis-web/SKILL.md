---
name: autoGenesis-web
description: Execute Web test scenarios via playwright-mcp-server with auto code generation. Use when user provides a scenario name and asks to run, execute, or generate test code for web applications. Triggers on phrases like "execute web scenario X", "run playwright test for scenario", "generate test code for web scenario", "use autoGenesis-web skill", or when a scenario name is provided alongside a request to automate or test web apps. Reads scenario steps from .feature files in behave-demo/features/, drives each step through MCP tool calls with persistent retry, then saves generated pytest code to testcase directory.
---

# AutoGenesis Web

Execute Web test scenarios and automatically generate Python pytest test files using Playwright.

## Project Structure

**CRITICAL**: This skill works with the following project structure:

```
PPA-UI-Automation-master/
├── testcase/
│   ├── conftest.py           # Pytest fixtures (Allure)
│   ├── test_*.py             # Generated test files (OUTPUT HERE)
│   └── __init__.py
├── common/
│   ├── mcp_client.py         # MCP client wrapper (browser operations)
│   ├── action.py             # Common actions (click_fill_mcp, etc.)
│   ├── attach.py             # Screenshot and Allure attachment
│   └── read_file.py          # YAML file reader
├── data/
│   └── base.yaml             # Test data configuration
├── log/
│   └── screenshot/           # Screenshot storage
├── setting.py                # Project root path
├── pytest.ini                # Pytest configuration
├── run.py                    # Test runner
└── requirements.txt          # Python dependencies
```

**Generated test files MUST be saved to**: `PPA-UI-Automation-master/testcase/`

## Input

- **scenario_name** (required): Name of the test scenario to execute.
- **feature_file** (optional): Path to the `.feature` file. If omitted, search all files under `behave-demo/features/`.

## Workflow

### Step 0: Initialize Project Structure (if needed)

**CRITICAL**: Before proceeding, check if `PPA-UI-Automation-master/` directory exists in the current working directory.

**If `PPA-UI-Automation-master/` does NOT exist:**

1. The project structure should already exist with the following key files:
   ```
   PPA-UI-Automation-master/
   ├── testcase/
   │   ├── conftest.py
   │   └── test_*.py
   ├── common/
   ├── data/
   ├── setting.py
   ├── pytest.ini
   └── run.py
   ```

2. Install dependencies:
   ```bash
   cd PPA-UI-Automation-master
   pip install pytest pytest-asyncio allure-pytest mcp httpx
   ```

3. Confirm initialization:
   ```
   ✅ PPA-UI-Automation project ready
   ```

**If `PPA-UI-Automation-master/` already exists:**
- Skip this step and proceed to Step 1

### Step 1: Locate the Scenario

Search `behave-demo/features/**/*.feature` (or the specified `feature_file`) for a `Scenario:` line matching `scenario_name`. Extract the full step block (Given/When/Then/And lines).

If the scenario is not found, list available scenario names from the directory and ask the user to confirm.

### Step 2: Execute via MCP

Substitute `{{SCENARIO_NAME}}` and `{{SCENARIO_STEPS}}` in the prompt below, then execute it against playwright-mcp-server:

---

```
Scenario: {{SCENARIO_NAME}}
{{SCENARIO_STEPS}}

Please use playwright-mcp-server to execute the following instructions:

CRITICAL REQUIREMENTS - MUST FOLLOW EXACTLY:

0. **PARAMETER DISCIPLINE — READ TOOL SCHEMAS FIRST**:
   - BEFORE calling ANY MCP tool, you MUST inspect its input schema to learn the EXACT parameter names, types, required/optional status, and allowed values.
   - Pass ALL required parameters — do NOT omit any.
   - Do NOT invent, guess, or fabricate parameters that are not in the schema. If a parameter does not appear in the tool's schema, it does not exist — do NOT pass it.
   - Use parameter values EXACTLY as defined (e.g., if the schema shows enum values with a specific prefix, use that prefix).
   - If you are unsure about a parameter, re-check the tool schema. Never assume.

1. **BEFORE STARTING**: Call before_gen_code FIRST

2. **FOR EACH STEP EXECUTION**:
   - Call the appropriate MCP tool(s) for the step
   - A step may require MULTIPLE MCP calls to complete (e.g., navigate, wait for element, click, type text)
   - WAIT for each MCP tool response
   - **MANDATORY**: IMMEDIATELY analyze and report each MCP response:
     * State the tool called and its parameters
     * Explicitly report the status: "Status: success" or "Status: error"
     * If error: Quote the exact error message
     * If success: Confirm what was accomplished
   - **CRITICAL**: If ANY MCP call returns status ≠ "success", you MUST:
     * **IMMEDIATELY acknowledge the failure**
     * **Quote the exact error message** from the response
     * **Analyze why it failed** (wrong locator, element not visible, page not loaded, etc.)
     * **Implement retry strategy** - try alternative approaches immediately
     * **Continue retrying** until this specific operation succeeds
     * Do not proceed to next operation until current one succeeds
   - Only proceed to next step when current step is fully completed and verified

3. **VERIFICATION STEPS**:
   - ALL verification/validation steps (like "I should see...") MUST use MCP tools
   - NEVER perform verification by analyzing page source yourself
   - Use verify_element_exists, verify_text_on_page, or other MCP verification tools
   - If verification fails, try alternative locator strategies (CSS, XPath, ID, text)

4. **AFTER ALL STEPS COMPLETE**:
   - MANDATORY: Call preview_code_changes MCP tool to view generated code
   - MANDATORY: Call confirm_code_changes MCP tool to save the code
   - These two steps are REQUIRED and cannot be skipped
   - **PATH VERIFICATION**: After confirm_code_changes, verify the save location:
     * MCP server reports the path where it saved the file
     * Generated code should be a pytest test file, NOT a behave steps file

5. **ERROR HANDLING & RETRY STRATEGY**:
   - Retry alternative approaches in this order (keep trying until one succeeds):
     * **Level 1 - Standard Locators**: Try different locator strategies (CSS, XPath, ID, text, etc.)
     * **Level 2 - DOM Analysis**: Extract page DOM, analyze HTML structure, find elements by context (labels, parent containers, sibling elements)
     * **Level 3 - JavaScript Evaluation**: Use execute_javascript to find elements, trigger events, or interact with Vue/React components directly
     * **Level 4 - Alternative Attributes**: Try alternative element attributes or text values
     * **Level 5 - Similar Elements**: Try finding similar elements with different properties
     * **Level 6 - Wait & Retry**: Try waiting for element to be visible/attached before retrying the action
     * **Level 7 - Focus First**: Try clicking element before typing (some inputs need focus first)
     * **Level 8 - Break Down Steps**: Break complex steps into smaller MCP operations if needed
     * **Level 9 - Navigation Retry**: For navigation: try different URL formats or wait for page load
     * **Level 10 - AI Screenshot Analysis**: Capture screenshot and use verify_visual_task or evaluate_web_visual_task to locate elements visually, then use coordinates with document.elementFromPoint()
   - **MANDATORY**: After each retry attempt, explicitly report the result
   - **PERSISTENCE RULE**: Keep trying alternatives until the step operation succeeds
   - **DO NOT ASSUME SUCCESS** - every MCP call must be verified
   - **Only stop the entire step** if you've exhausted ALL reasonable alternatives

6. **EXECUTION RULES**:
   - Execute steps in exact order as written
   - Each step may require MULTIPLE MCP calls to complete fully
   - Use ONLY playwright-mcp-server MCP tools
   - Never modify, merge, skip, or add steps
   - When retrying, use the most successful approach in final generated code

7. **CODE GENERATION - AUTOMATED**:
   - **MCP SERVER AUTOMATICALLY RECORDS EXECUTION TRAJECTORY**:
     * Every MCP tool call is automatically recorded by the server
     * The `record_calls` decorator captures all tool invocations
     * Recording includes: tool name, parameters, step description, scenario name
   
   - **AUTOMATIC PYTEST FILE GENERATION**:
     * When you call `confirm_code_changes`, the MCP server will:
       1. Read the execution trajectory from the cache
       2. Convert each tool call to corresponding MCPClient async method
       3. Generate a complete pytest test file with proper format
       4. Save to `PPA-UI-Automation-master/testcase/test_<feature_name>.py`
   
   - **YOU DO NOT NEED TO MANUALLY WRITE CODE**:
     * The MCP server handles all code generation automatically
     * Just execute the test steps using MCP tools
     * Call `preview_code_changes` to review
     * Call `confirm_code_changes` to save the file
   
   - **GENERATED FILE FORMAT** (handled automatically by MCP server):
     * Proper imports (pytest, allure, asyncio, MCPClient, readAttach_mcp)
     * Allure decorators (@allure.epic, @allure.title, @pytest.mark.asyncio)
     * try/finally block with client.connect() and client.close()
     * All executed steps as async client method calls
     * Automatic screenshot and Allure attachment at the end

REMEMBER: Every step must be validated through MCP tools, not through your own analysis. When encountering errors, **RETRY with different approaches**. **Continue retrying until each operation succeeds**.

**CRITICAL SUCCESS VERIFICATION PROTOCOL**:
- After each MCP tool call, explicitly state: "✅ SUCCESS: [tool_name] completed" or "❌ FAILED: [tool_name] with error [message]"
- **RETRY UNTIL SUCCESS**: If you get "❌ FAILED", immediately try alternative approaches for the SAME operation
- Before moving to next step, confirm: "✅ STEP COMPLETED: [step_name] - all required actions successful"
- **DEFINITION OF SUCCESS**: Every operation in a step must return "status: success" before proceeding
```

---

### Step 3: Post-Execution & Path Verification

**CRITICAL - Automated File Generation via Execution Trajectory**:

After all test steps are executed via MCP tools, the MCP server has been **automatically recording** every tool call. Now:

1. **Preview the generated code** (optional but recommended):
   ```
   Call: preview_code_changes
   ```
   - This shows you the pytest code that will be generated
   - The code is automatically generated from the execution trajectory
   - Review to ensure all steps are captured correctly

2. **Confirm and save the test file**:
   ```
   Call: confirm_code_changes
   ```
   - The MCP server will:
     * Read all recorded tool calls from the execution trajectory cache
     * Convert each tool call to corresponding MCPClient async method calls
     * Generate a complete pytest test file with:
       - Proper imports and decorators
       - All executed steps in correct order
       - try/finally block with proper cleanup
       - Automatic screenshot and Allure attachment
     * Save to: `PPA-UI-Automation-master/testcase/test_<feature_name>.py`

3. **Confirm the save location** to the user:
   ```
   ✅ Test file saved to: PPA-UI-Automation-master/testcase/test_<name>.py
   ✅ Test function: test_<function_name>
   ```

3. **Conflict Prevention - CRITICAL**:
   - Each execution generates a new test file with unique function name
   - If a file with the same name already exists, it will be overwritten
   - To avoid conflicts, use descriptive and unique scenario names

4. **Provide run instructions**:

```bash
cd PPA-UI-Automation-master
pytest -vs --alluredir=./reports/tmp --clean-alluredir
```

Or run a specific test:

```bash
cd PPA-UI-Automation-master
pytest testcase/test_<name>.py -vs
```

## Configuration

Before running tests, ensure:

1. **playwright-mcp-server is installed and configured**:
   ```bash
   cd playwright-mcp-server
   pip install -e .
   ```

2. **playwright-mcp-server/conf/playwright_conf.json** is configured with the target browser:
   ```json
   {
     "browser": {
       "browser_name": "chromium",
       "headless": true,
       "viewport": {
         "width": 1680,
         "height": 1080
       },
       "timeout": 30000,
       "slow_mo": 500
     }
   }
   ```

3. **PPA-UI-Automation-master dependencies**:
   ```bash
   cd PPA-UI-Automation-master
   pip install -r requirements.txt
   ```

**Browser Options:**
- `chromium` - Google Chrome / Microsoft Edge
- `firefox` - Mozilla Firefox
- `webkit` - Safari

## MCP Tools Available

### Browser Navigation & Page Control
| Tool | Description | Parameters |
|------|-------------|------------|
| `browser_navigate` | Navigate to URL | `url`, `caller` |
| `browser_close` | Close browser | `caller` |
| `screenshot` | Take full-page screenshot | `file_path`, `caller` |
| `scroll_page` | Scroll page up or down | `direction`, `amount`, `caller` |
| `scroll_to_element` | Scroll page to make element visible | `locator_value`, `locator_strategy`, `caller` |

### Element Interaction
| Tool | Description | Parameters |
|------|-------------|------------|
| `click_element` | Click an element | `locator_value`, `locator_strategy`, `caller` |
| `hover_element` | Hover mouse over element (triggers dropdown menus) | `locator_value`, `locator_strategy`, `caller` |
| `send_keys` | Enter text in form field | `locator_value`, `text`, `locator_strategy`, `caller` |
| `press_key` | Press keyboard key | `key`, `caller` |
| `select_option` | Select dropdown option | `locator_value`, `option_value`, `locator_strategy`, `caller` |
| `execute_javascript` | Execute JS on page | `script`, `caller` |

### File Upload & Download
| Tool | Description | Parameters |
|------|-------------|------------|
| `upload_file` | Upload one or multiple files to file input element | `locator_value`, `file_paths` (list), `locator_strategy`, `caller` |
| `wait_for_download` | Wait for file download to complete and return downloaded file information | `download_dir`, `timeout`, `caller` |
| `verify_download_exists` | Verify file was downloaded successfully | `file_name`, `download_dir`, `caller` |

### Element Discovery
| Tool | Description | Parameters |
|------|-------------|------------|
| `find_element` | Find element on page | `locator_value`, `locator_strategy`, `caller` |
| `wait_for_element` | Wait for element to appear | `locator_value`, `locator_strategy`, `timeout`, `caller` |
| `get_text` | Get text content from element | `locator_value`, `locator_strategy`, `caller` |
| `get_page_title` | Get current page title | `caller` |
| `get_page_url` | Get current page URL | `caller` |

### Verification & Validation
| Tool | Description | Parameters |
|------|-------------|------------|
| `verify_element_exists` | Verify element exists | `locator_value`, `locator_strategy`, `caller` |
| `verify_element_not_exists` | Verify element does not exist | `locator_value`, `locator_strategy`, `caller` |
| `verify_element_attribute` | Verify element attribute value | `locator_value`, `attribute_name`, `expected_value`, `rule`, `caller` |
| `verify_text_on_page` | Verify text exists on page | `text`, `caller` |
| `verify_checkbox_state` | Verify checkbox/radio state (checked/unchecked) | `locator_value`, `expected_state`, `locator_strategy`, `caller` |
| `verify_element_value` | Verify form element value (input/textarea/select) | `locator_value`, `expected_value`, `locator_strategy`, `caller` |
| `verify_visual_task` | AI-powered visual verification from screenshot | `screenshot_path`, `task_description`, `caller` |
| `evaluate_web_visual_task` | AI-powered web page evaluation (screenshot + HTML) | `screenshot_path`, `task_description`, `caller` |

### Code Generation
| Tool | Description | Parameters |
|------|-------------|------------|
| `before_gen_code` | Initialize code generation session | `feature_file`, `step_file` |
| `preview_code_changes` | Preview generated code changes | (none) |
| `confirm_code_changes` | Confirm and save code changes | (none) |

### Configuration
| Tool | Description | Parameters |
|------|-------------|------------|
| `get_config` | Get current configuration | `caller` |
| `update_config` | Update configuration | `config_key`, `config_value`, `caller` |

## Common Locator Strategies

| Strategy | Example | Use Case |
|----------|---------|----------|
| CSS | `input[name="wd"]` | Most common, fast |
| XPath | `//input[@name="wd"]` | Complex queries |
| ID | `#search-box` | Unique elements |
| Text | `text=Click Here` | Button/link text |

## Advanced Element Location Strategies

### Strategy 1: DOM/Source Code Analysis

When standard locator strategies fail to find elements, use DOM/source code analysis:

**Step 1: Extract Page DOM Structure**
```javascript
// Get all interactive elements with their attributes
() => {
  const elements = Array.from(document.querySelectorAll('input, button, select, textarea, a, [role="button"], [role="link"]'));
  return elements.map(el => ({
    tag: el.tagName,
    type: el.type,
    id: el.id,
    name: el.name,
    placeholder: el.placeholder,
    text: el.textContent?.trim(),
    class: el.className,
    role: el.getAttribute('role'),
    ariaLabel: el.getAttribute('aria-label')
  }));
}
```

**Step 2: Analyze Page Source for Element Patterns**
```javascript
// Get the full HTML structure of the page or specific sections
() => document.body.innerHTML
// Or for a specific section:
() => document.querySelector('.main-content')?.innerHTML
```

**Step 3: Identify Elements by Context**
- Look for form elements by their surrounding `<form>` or `<div>` containers
- Identify buttons by their parent container classes (e.g., `.el-dialog`, `.modal-footer`)
- Find inputs by their associated `<label>` elements or placeholder text
- Use hierarchical relationships (e.g., `parent > child`, `sibling + sibling`)

**Step 4: Build Locators from Analysis**
- Extract unique attributes (id, name, data-testid, etc.)
- Use CSS selectors based on element hierarchy
- Create XPath expressions for complex relationships
- Identify Vue/React component patterns (e.g., `el-input`, `v-model` bindings)

### Strategy 2: AI Screenshot Analysis Fallback

When both standard locators and DOM analysis fail, use screenshot-based AI analysis:

**Step 1: Capture Screenshot**
```
Call: screenshot
Parameters: file_path="<path>/screenshot.png", caller="pytest-automation"
```

**Step 2: Analyze Screenshot with AI Vision**
```
Call: verify_visual_task or evaluate_web_visual_task
Parameters: 
  - screenshot_path: "<path>/screenshot.png"
  - task_description: "Find and describe the location of [element description]. Return the approximate coordinates and any visible text, labels, or identifiers associated with this element."
  - caller: "pytest-automation"
```

**Step 3: Use Coordinates for Element Location**
Based on the AI analysis results:
- If coordinates are provided, use JavaScript to click at those coordinates:
  ```javascript
  () => {
    // Click at approximate coordinates from AI analysis
    const element = document.elementFromPoint(x, y);
    if (element) {
      element.click();
      return 'Clicked element at coordinates';
    }
    return 'No element found at coordinates';
  }
  ```

**Step 4: Fallback Visual Verification**
- Use `verify_visual_task` to confirm element presence after actions
- Compare before/after screenshots to verify state changes
- Use visual cues (colors, icons, text) to confirm successful operations

**When to Use Each Strategy:**

| Situation | Recommended Strategy |
|-----------|---------------------|
| Standard elements (inputs, buttons, links) | CSS/XPath/ID/Text |
| Dynamic frameworks (Vue, React) | DOM Analysis + JavaScript evaluation |
| Canvas/SVG elements | DOM Analysis |
| Shadow DOM elements | DOM Analysis (traverse shadowRoot) |
| Complex visual layouts | AI Screenshot Analysis |
| Elements with dynamic IDs | DOM Analysis (find by context) |
| Custom components | AI Screenshot Analysis → DOM Analysis |
| When all else fails | AI Screenshot Analysis (last resort) |

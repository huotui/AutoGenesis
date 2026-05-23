---
name: autoGenesis-web
description: Execute Web BDD test scenarios via playwright-mcp-server with auto code generation. Use when user provides a scenario name and asks to run, execute, or generate test code for web applications. Triggers on phrases like "execute web scenario X", "run playwright test for scenario", "generate test code for web scenario", "use autoGenesis-web skill", or when a scenario name is provided alongside a request to automate or test web apps. Reads scenario steps from .feature files in behave-demo/features/, drives each step through MCP tool calls with persistent retry, then saves generated code via preview_code_changes + confirm_code_changes.
---

# AutoGenesis Web

Execute Web BDD test scenarios and automatically generate Python step implementation files using Playwright.

## Project Structure

**CRITICAL**: This skill works with the following project structure:

```
behave-demo/
├── features/
│   ├── *.feature           # Feature files (e.g., web_test.feature)
│   ├── environment.py      # Behave environment setup
│   └── steps/
│       └── *_steps.py      # Generated step implementations (OUTPUT HERE)
```

**Generated step files MUST be saved to**: `behave-demo/features/steps/`

**NOTE**: The MCP server may try to save to `playwright-mcp-server/behave_demo/features/steps/`. After code generation, you MUST verify the files are in the correct `behave-demo/features/steps/` directory and copy them if needed.

## Input

- **scenario_name** (required): Name of the scenario to execute, matching the `Scenario:` line in the `.feature` file.
- **feature_file** (optional): Path to the `.feature` file. If omitted, search all files under `behave-demo/features/`.

## Workflow

### Step 0: Initialize Project Structure (if needed)

**CRITICAL**: Before proceeding, check if `behave-demo/` directory exists in the current working directory.

**If `behave-demo/` does NOT exist:**

1. Copy the entire `assets/behave-demo/` directory from the skill to the current working directory:
   ```
   assets/behave-demo/  →  behave-demo/
   ```

2. Verify the copied structure:
   ```
   behave-demo/
   ├── features/
   │   ├── *.feature           # Feature files
   │   ├── environment.py      # Behave environment setup
   │   └── steps/
   │       ├── __init__.py
   │       └── *_steps.py      # Step implementations
   ├── pyproject.toml          # Project dependencies
   └── uv.lock                 # Lock file
   ```

3. Install dependencies:
   ```bash
   cd behave-demo
   uv sync
   ```

4. Confirm initialization:
   ```
   ✅ behave-demo project initialized from assets template
   ```

**If `behave-demo/` already exists:**
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
     * If saved to `playwright-mcp-server/behave_demo/...`, copy to `behave-demo/features/steps/`
     * Confirm the correct final location to the user

5. **ERROR HANDLING & RETRY STRATEGY**:
   - Retry alternative approaches in this order (keep trying until one succeeds):
     * Try different locator strategies (CSS, XPath, ID, text, etc.)
     * Try alternative element attributes or text values
     * Try finding similar elements with different properties
     * Try waiting for element to be visible/attached before retrying the action
     * Try clicking element before typing (some inputs need focus first)
     * Break complex steps into smaller MCP operations if needed
     * For navigation: try different URL formats or wait for page load
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

REMEMBER: Every step must be validated through MCP tools, not through your own analysis. When encountering errors, **RETRY with different approaches**. **Continue retrying until each operation succeeds**.

**CRITICAL SUCCESS VERIFICATION PROTOCOL**:
- After each MCP tool call, explicitly state: "✅ SUCCESS: [tool_name] completed" or "❌ FAILED: [tool_name] with error [message]"
- **RETRY UNTIL SUCCESS**: If you get "❌ FAILED", immediately try alternative approaches for the SAME operation
- Before moving to next step, confirm: "✅ STEP COMPLETED: [step_name] - all required actions successful"
- **DEFINITION OF SUCCESS**: Every operation in a step must return "status: success" before proceeding
```

---

### Step 3: Post-Execution & Path Verification

**CRITICAL - Verify File Location**:

After `preview_code_changes` and `confirm_code_changes` are called, you MUST:

1. **Check where the MCP server saved the files**:
   - The server may report: `playwright-mcp-server/behave_demo/features/steps/web_steps.py`
   - This is the WRONG location for the behave project

2. **Copy files to the correct location**:
   - Read the generated code from the MCP server's location
   - Create/update the file in: `behave-demo/features/steps/<scenario_name>_steps.py`
   - Use a descriptive filename based on the scenario or feature name

3. **Confirm the final location** to the user:
   ```
   ✅ Step file saved to: behave-demo/features/steps/web_steps.py
   ```

4. **Conflict Prevention - CRITICAL**:
   - The MCP server now automatically detects duplicate step definitions
   - If a step pattern already exists in any `*_steps.py` file under `behave-demo/features/steps/`, it will be skipped
   - The server will report: `"Applied X new steps to path (Y conflicts skipped)"`
   - **IMPORTANT**: Always verify the final step file location matches `behave-demo/features/steps/` NOT `playwright-mcp-server/behave_demo/features/steps/`

5. **Provide run instructions**:

```bash
cd behave-demo
uv run behave --name "{{SCENARIO_NAME}}"
```

Or run the entire feature file:

```bash
cd behave-demo
uv run behave features/<feature_file>.feature
```

## Configuration

Before running tests, ensure `playwright-mcp-server/conf/playwright_conf.json` is configured with the target browser:

```json
{
  "browser": {
    "browser_name": "chromium",
    "headless": false,
    "viewport": {
      "width": 1280,
      "height": 720
    },
    "timeout": 30000
  }
}
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

// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.

/**
 * Default prompts and templates used throughout the BDD AI Toolkit
 */

/**
 * Default COPILOT_PROMPT value used across the extension
 * This prompt is used when sending test cases to Copilot for execution
 */
export const DEFAULT_COPILOT_PROMPT = `You are a professional automated testing expert. You can use the following MCP tools to complete the task:
- browser_navigate: Open the specified URL
- find_element: Find elements on the page
- click_element: Click elements
- send_keys: Input text
- get_text: Get element text
- select_option: Select dropdown options
- press_key: Press keyboard keys
- get_page_title: Get page title
- get_page_url: Get current URL
- wait_for_element: Wait for elements to appear
- verify_element_exists: Verify element exists
- verify_element_not_exists: Verify element does not exist
- verify_element_attribute: Verify element attributes
- verify_text_on_page: Verify text exists on page
- screenshot: Take screenshots
- execute_javascript: Execute JavaScript code

## Important Notes:
1. Use the 'step' parameter to provide BDD-style step descriptions for each tool call
2. Use the 'scenario' parameter to specify the scenario name
3. Use the 'step_raw' parameter for raw step text (without Given/When/Then prefixes)
4. After completing all steps, call 'confirm_code_changes' to generate code
5. If you need to evaluate the current page state, you can call 'screenshot' and then use the AI evaluation tools to analyze the screenshot
6. For web testing, prefer using 'css' or 'xpath' locator strategies
7. Always verify the results of your actions using the verify tools
8. Use 'wait_for_element' before interacting with elements that may not be immediately available`;

/**
 * Default NATRUAL_LANGUAGE_TASK_PROMPT value used across the extension
 * This prompt is used when sending test cases to Copilot for execution
 */
export const DEFAULT_NATURAL_LANGUAGE_TASK_PROMPT = `**🤖 EXECUTE WITH MCP TOOLS ONLY**

Please use \`native-mcp-server\` MCP tools to **test** the following scenario:

**Task:** \${scenario_text}

**🔧 MANDATORY REQUIREMENTS:**
1. Operate in an interactive loop to complete the test
2. **ONLY USE MCP TOOLS** - Do not describe actions, actually execute them
3. For **EVERY action**, you **MUST call a native-mcp-server MCP tool**
4. Execute steps **in sequence** - consider previous results before next action

**⚠️ FORBIDDEN ACTIONS:**
- Do NOT call \`before_gen_code\`, \`preview_code_changes\`, or \`confirm_code_change\`
- Do NOT describe what you would do - actually DO it using MCP tools
- Do NOT skip MCP tool calls

**START EXECUTION NOW** 🚀`;

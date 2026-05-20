Feature: Web Testing with Playwright
  As a web tester
  I want to test web functionality using Playwright MCP Server
  So that I can verify web automation works correctly

  Scenario: Verify page title on Baidu
    Given I navigate to "https://www.baidu.com"
    When I get the page title
    Then the page title should contain "百度"

  Scenario: Verify element exists on example.com
    Given I navigate to "https://example.com"
    Then I should see the page heading

  Scenario: Verify text on example.com
    Given I navigate to "https://example.com"
    Then I should see text "Example Domain"

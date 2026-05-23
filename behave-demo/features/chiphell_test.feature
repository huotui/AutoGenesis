Feature: Chiphell Forum Testing
  As a web tester
  I want to test Chiphell forum functionality
  So that I can verify web automation works correctly

  Scenario: 测试 chiphell.com 论坛
    Given I navigate to "https://www.chiphell.com/forum.php"
    When I click the "相关讨论" topic link
    Then I should see the topic content page
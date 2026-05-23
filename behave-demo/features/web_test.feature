Feature: Bing Website Test

  Scenario: Open bing.com successfully
    Given I navigate to https://www.bing.com
    Then the page should load successfully
    And I should see the Bing search box

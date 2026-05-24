Feature: Library Website Testing
  As a library user
  I want to test the library website functionality
  So that I can verify borrowing and returning books works correctly

  Scenario: Login and borrow a book then return it
    Given I navigate to "http://localhost:9999/login"
    When I input "test" in the username field
    And I input "test" in the password field
    And I click the login button
    Then I should see the main page
    When I click the "图书查询" link
    Then I should see the book list
    When I click the borrow button for the first book in the list
    Then I should see the borrow success message
    When I click the "我的借阅" link
    Then I should see a "借阅中" record
    When I click the return button for the borrowed book
    Then I should see the return success message
    When I click the "我的借阅" link again
    Then I should not see any "借阅中" record

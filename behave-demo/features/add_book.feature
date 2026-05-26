Feature: Library Book Management
  As an administrator
  I want to add books with cover images
  So that the library catalog is complete and visually appealing

  Scenario: 添加图书并上传封面图片
    Given I navigate to "http://localhost:9999/"
    When I login with admin credentials "admin" and "admin"
    And I click the "图书查询" navigation menu
    And I click the "添加图书" button
    Then I should see the add book dialog
    When I click the cover image upload area with "+" icon
    And I select an image file "C:\Users\ihuotui\Downloads\dzq.png"
    Then I should see the image preview in the upload area
    When I input "测试图书1" in the book title field
    And I input "测试作者" in the author field
    And I input "9787111000001" in the ISBN field
    And I select "文学" from the category dropdown
    And I input "测试出版社" in the publisher field
    And I click the "保存" button
    Then I should see the book added successfully

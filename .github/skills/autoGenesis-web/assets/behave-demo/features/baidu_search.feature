Feature: 百度搜索功能测试
  作为网站用户
  我想要使用百度搜索功能
  以便于快速找到需要的信息

  @smoke
  Scenario: 搜索关键词并验证结果
    Given 我打开百度首页
    When 我在搜索框输入 "AutoGenesis"
    And 我点击搜索按钮
    Then 搜索结果页面应该包含 "AutoGenesis"

  @regression
  Scenario: 验证百度首页元素
    Given 我打开百度首页
    Then 页面标题应该包含 "百度"
    And 搜索按钮应该存在

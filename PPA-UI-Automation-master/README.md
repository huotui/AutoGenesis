<h1 align="center" style="margin: 30px 0 30px; font-weight: bold;">PPA-UI-Automation v1.0.0</h1>
<h4 align="center">基于python+yaml+allure开发的自动化框架</h4>

## 框架简介

PPA-UI-Automation是一套开源的UI四层自动化框架。

* 采用Python、Yaml、Allure技术与插件。
* 已搭建好一个框架和基本动作，直接写UI代码即可运行。
* Allure报告生成。

## 需安装的软件包

* pip install pyaml
* pip install playwright
* python -m playwright install chromium
* pip install allure-pytest
* pip install pytest
* pip install pytest-playwright

## 下载allure并配置环境

* 官网下载地址：https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/

## 内置主要目录

1. common（公共方法层）
2. testcase（用例层）
3. data（数据层）
4. log（日志层）
5. reports（报告层）

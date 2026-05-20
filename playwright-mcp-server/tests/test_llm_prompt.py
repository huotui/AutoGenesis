# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import pytest
import json
import os
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from llm.prompt import img_task_prompt, ImgTaskResponse, web_task_prompt, WebTaskResponse


class TestImgTaskPrompt:
    """Tests for img_task_prompt function"""

    def test_returns_string(self):
        result = img_task_prompt("test task")
        assert isinstance(result, str)

    def test_contains_task_info(self):
        result = img_task_prompt("Check if login button exists")
        assert "Check if login button exists" in result

    def test_empty_task_info(self):
        result = img_task_prompt("")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_instructions(self):
        result = img_task_prompt("test")
        assert "Instructions" in result
        assert "screenshot" in result.lower()


class TestImgTaskResponse:
    """Tests for ImgTaskResponse model"""

    def test_create_success_response(self):
        resp = ImgTaskResponse(result=True, reason="Task satisfied")
        assert resp.result is True
        assert resp.reason == "Task satisfied"

    def test_create_failure_response(self):
        resp = ImgTaskResponse(result=False, reason="Element not found")
        assert resp.result is False
        assert resp.reason == "Element not found"

    def test_get_json_schema(self):
        schema_str = ImgTaskResponse.get_json_schema()
        schema = json.loads(schema_str)
        assert "properties" in schema
        assert "result" in schema["properties"]
        assert "reason" in schema["properties"]

    def test_get_format_description(self):
        desc = ImgTaskResponse.get_format_description()
        assert "result" in desc
        assert "reason" in desc

    def test_get_example_json(self):
        example_str = ImgTaskResponse.get_example_json()
        example = json.loads(example_str)
        assert "result" in example
        assert "reason" in example

    def test_get_prompt_format(self):
        fmt = ImgTaskResponse.get_prompt_format()
        assert "JSON" in fmt
        assert "result" in fmt
        assert "reason" in fmt

    def test_model_validate_json(self):
        json_str = '{"result": true, "reason": "Test passed"}'
        resp = ImgTaskResponse.model_validate_json(json_str)
        assert resp.result is True
        assert resp.reason == "Test passed"


class TestWebTaskPrompt:
    """Tests for web_task_prompt function"""

    def test_returns_string(self):
        result = web_task_prompt("test task")
        assert isinstance(result, str)

    def test_contains_task_info(self):
        result = web_task_prompt("Check if login form is visible")
        assert "Check if login form is visible" in result

    def test_empty_task_info(self):
        result = web_task_prompt("")
        assert isinstance(result, str)

    def test_with_page_source(self):
        html = "<html><body><form id='login'></form></body></html>"
        result = web_task_prompt("Find login form", html)
        assert "Page Source" in result
        assert "<form id='login'>" in result

    def test_without_page_source(self):
        result = web_task_prompt("Find login form", "")
        assert "Page Source" not in result

    def test_contains_instructions(self):
        result = web_task_prompt("test")
        assert "Instructions" in result
        assert "HTML" in result or "web page" in result.lower()


class TestWebTaskResponse:
    """Tests for WebTaskResponse model"""

    def test_create_success_response(self):
        resp = WebTaskResponse(
            result=True,
            reason="Login form found",
            elements_found=["form#login", "input#username"]
        )
        assert resp.result is True
        assert resp.reason == "Login form found"
        assert len(resp.elements_found) == 2

    def test_create_failure_response(self):
        resp = WebTaskResponse(
            result=False,
            reason="Element not found",
            elements_found=[]
        )
        assert resp.result is False
        assert resp.elements_found == []

    def test_default_elements_found(self):
        resp = WebTaskResponse(result=True, reason="OK")
        assert resp.elements_found == []

    def test_get_json_schema(self):
        schema_str = WebTaskResponse.get_json_schema()
        schema = json.loads(schema_str)
        assert "properties" in schema
        assert "result" in schema["properties"]
        assert "reason" in schema["properties"]
        assert "elements_found" in schema["properties"]

    def test_get_format_description(self):
        desc = WebTaskResponse.get_format_description()
        assert "result" in desc
        assert "reason" in desc
        assert "elements_found" in desc

    def test_get_example_json(self):
        example_str = WebTaskResponse.get_example_json()
        example = json.loads(example_str)
        assert "result" in example
        assert "reason" in example
        assert "elements_found" in example

    def test_get_prompt_format(self):
        fmt = WebTaskResponse.get_prompt_format()
        assert "JSON" in fmt
        assert "result" in fmt
        assert "elements_found" in fmt

    def test_model_validate_json(self):
        json_str = '{"result": true, "reason": "Found", "elements_found": ["#btn"]}'
        resp = WebTaskResponse.model_validate_json(json_str)
        assert resp.result is True
        assert resp.elements_found == ["#btn"]

    def test_model_validate_json_without_elements(self):
        json_str = '{"result": false, "reason": "Not found"}'
        resp = WebTaskResponse.model_validate_json(json_str)
        assert resp.result is False
        assert resp.elements_found == []

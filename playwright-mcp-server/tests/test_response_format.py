# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import pytest
import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.response_format import (
    init_tool_response,
    format_tool_response,
    parse_tool_response,
    is_successful,
    handle_page_source,
)


class TestInitToolResponse:
    """Tests for init_tool_response"""

    def test_default_status_is_error(self):
        resp = init_tool_response()
        assert resp["status"] == "error"

    def test_default_data_is_empty(self):
        resp = init_tool_response()
        assert resp["data"] == {}

    def test_default_error_is_none(self):
        resp = init_tool_response()
        assert resp["error"] is None

    def test_has_timestamp(self):
        resp = init_tool_response()
        assert "timestamp" in resp
        assert resp["timestamp"] is not None


class TestFormatToolResponse:
    """Tests for format_tool_response"""

    def test_success_response(self):
        resp = {"status": "success", "data": {"key": "value"}}
        result = format_tool_response(resp)
        parsed = json.loads(result)
        assert parsed["status"] == "success"
        assert parsed["data"]["key"] == "value"

    def test_error_response(self):
        resp = {"status": "error", "data": {}, "error": "Something went wrong"}
        result = format_tool_response(resp)
        parsed = json.loads(result)
        assert parsed["status"] == "error"
        assert parsed["error"] == "Something went wrong"

    def test_error_not_included_when_none(self):
        resp = {"status": "success", "data": {}, "error": None}
        result = format_tool_response(resp)
        parsed = json.loads(result)
        assert "error" not in parsed

    def test_missing_status_raises_error(self):
        resp = {"data": {}}
        with pytest.raises(ValueError, match="must contain 'status' key"):
            format_tool_response(resp)

    def test_unicode_support(self):
        resp = {"status": "success", "data": {"text": "中文测试"}}
        result = format_tool_response(resp)
        parsed = json.loads(result)
        assert parsed["data"]["text"] == "中文测试"

    def test_empty_data(self):
        resp = {"status": "success"}
        result = format_tool_response(resp)
        parsed = json.loads(result)
        assert parsed["data"] == {}


class TestParseToolResponse:
    """Tests for parse_tool_response"""

    def test_parse_valid_json(self):
        json_str = '{"status": "success", "data": {"key": "value"}}'
        result = parse_tool_response(json_str)
        assert result["status"] == "success"
        assert result["data"]["key"] == "value"

    def test_parse_invalid_json(self):
        result = parse_tool_response("not valid json")
        assert result["status"] == "error"
        assert "Failed to parse" in result["error"]

    def test_parse_empty_string(self):
        result = parse_tool_response("")
        assert result["status"] == "error"


class TestIsSuccessful:
    """Tests for is_successful"""

    def test_success_response(self):
        json_str = '{"status": "success", "data": {}}'
        assert is_successful(json_str) is True

    def test_error_response(self):
        json_str = '{"status": "error", "data": {}, "error": "fail"}'
        assert is_successful(json_str) is False

    def test_invalid_json(self):
        assert is_successful("not json") is False

    def test_empty_string(self):
        assert is_successful("") is False


class TestHandlePageSource:
    """Tests for handle_page_source"""

    @pytest.fixture
    def mock_simplify(self):
        with patch('utils.element_util.simplify_page_source') as mock:
            mock.return_value = "<simplified>test</simplified>"
            yield mock

    @pytest.fixture
    def mock_summarize(self):
        with patch('utils.element_util.summarize_page_source') as mock:
            mock.return_value = "Page summary"
            yield mock

    def test_default_behavior_no_file_no_summary(self, mock_simplify):
        resp = {"data": {}}
        handle_page_source(resp, "<html>test</html>")
        assert "page_source" in resp["data"]
        assert resp["data"]["page_source"] == "<simplified>test</simplified>"

    def test_summary_only(self, mock_simplify, mock_summarize):
        resp = {"data": {}}
        handle_page_source(resp, "<html>test</html>", summary_only=True)
        assert "page_source_summary" in resp["data"]
        assert resp["data"]["page_source_summary"] == "Page summary"
        assert "page_source" not in resp["data"]

    def test_save_to_file(self, mock_simplify):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            temp_path = f.name
        
        try:
            resp = {"data": {}}
            handle_page_source(resp, "<html>test</html>", page_source_file=temp_path)
            assert resp["data"]["page_source_file"] == temp_path
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                content = f.read()
            assert content == "<simplified>test</simplified>"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_save_to_file_with_summary(self, mock_simplify, mock_summarize):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            temp_path = f.name
        
        try:
            resp = {"data": {}}
            handle_page_source(resp, "<html>test</html>", page_source_file=temp_path, summary_only=True)
            assert resp["data"]["page_source_file"] == temp_path
            assert resp["data"]["page_source_summary"] == "Page summary"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_no_data_key_creates_it(self, mock_simplify):
        resp = {}
        handle_page_source(resp, "<html>test</html>")
        assert "data" in resp
        assert "page_source" in resp["data"]

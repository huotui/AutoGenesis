# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import pytest
import json
import os
import tempfile
from unittest.mock import MagicMock, patch, PropertyMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from playwright_session import PlaywrightSessionManager


class TestPlaywrightSessionManager:
    """Tests for PlaywrightSessionManager"""

    @pytest.fixture
    def mock_playwright(self):
        with patch('playwright_session.sync_playwright') as mock_pw:
            mock_pw_instance = MagicMock()
            mock_pw.return_value.start.return_value = mock_pw_instance
            mock_browser = MagicMock()
            mock_pw_instance.chromium.launch.return_value = mock_browser
            mock_pw_instance.firefox.launch.return_value = mock_browser
            mock_pw_instance.webkit.launch.return_value = mock_browser
            mock_context = MagicMock()
            mock_browser.new_context.return_value = mock_context
            mock_page = MagicMock()
            mock_context.new_page.return_value = mock_page
            yield {
                'playwright': mock_pw,
                'pw_instance': mock_pw_instance,
                'browser': mock_browser,
                'context': mock_context,
                'page': mock_page,
            }

    @pytest.fixture
    def browser_config(self):
        return {
            "browser": {
                "browser_name": "chromium",
                "headless": True,
                "viewport": {"width": 1280, "height": 720},
                "timeout": 30000,
                "slow_mo": 500
            }
        }

    def test_init_chromium(self, mock_playwright, browser_config):
        manager = PlaywrightSessionManager(browser_config)
        mock_playwright['pw_instance'].chromium.launch.assert_called_once_with(headless=True)
        assert manager._browser is not None
        assert manager._page is not None

    def test_init_firefox(self, mock_playwright, browser_config):
        browser_config["browser"]["browser_name"] = "firefox"
        manager = PlaywrightSessionManager(browser_config)
        mock_playwright['pw_instance'].firefox.launch.assert_called_once_with(headless=True)

    def test_init_webkit(self, mock_playwright, browser_config):
        browser_config["browser"]["browser_name"] = "webkit"
        manager = PlaywrightSessionManager(browser_config)
        mock_playwright['pw_instance'].webkit.launch.assert_called_once_with(headless=True)

    def test_init_unsupported_browser(self, mock_playwright, browser_config):
        browser_config["browser"]["browser_name"] = "safari"
        with pytest.raises(ValueError, match="Unsupported browser: safari"):
            PlaywrightSessionManager(browser_config)

    def test_page_property(self, mock_playwright, browser_config):
        manager = PlaywrightSessionManager(browser_config)
        assert manager.page is not None

    def test_page_property_not_initialized(self, mock_playwright, browser_config):
        manager = PlaywrightSessionManager.__new__(PlaywrightSessionManager)
        manager._page = None
        with pytest.raises(RuntimeError, match="Browser page not initialized"):
            _ = manager.page

    def test_browser_property(self, mock_playwright, browser_config):
        manager = PlaywrightSessionManager(browser_config)
        assert manager.browser is not None

    def test_context_property(self, mock_playwright, browser_config):
        manager = PlaywrightSessionManager(browser_config)
        assert manager.context is not None

    def test_close(self, mock_playwright, browser_config):
        manager = PlaywrightSessionManager(browser_config)
        manager.close()
        mock_playwright['page'].close.assert_called_once()
        mock_playwright['context'].close.assert_called_once()
        mock_playwright['browser'].close.assert_called_once()
        mock_playwright['pw_instance'].stop.assert_called_once()

    def test_close_with_error(self, mock_playwright, browser_config):
        manager = PlaywrightSessionManager(browser_config)
        mock_playwright['page'].close.side_effect = Exception("close error")
        manager.close()
        mock_playwright['page'].close.assert_called_once()

    def test_update_config(self, mock_playwright, browser_config):
        manager = PlaywrightSessionManager(browser_config)
        new_config = {"browser": {"browser_name": "firefox"}}
        manager.update_config(new_config)
        assert manager._config == new_config

    def test_clear_gen_code_cache(self, mock_playwright, browser_config):
        manager = PlaywrightSessionManager(browser_config)
        manager.gen_code_cache = ["item1", "item2"]
        manager.gen_code_id = "test-id"
        manager.proposed_changes = ["change1"]
        manager.new_steps_count = 5
        manager.header_code = "header"
        
        manager.clear_gen_code_cache()
        
        assert manager.gen_code_cache == []
        assert manager.gen_code_id is None
        assert manager.proposed_changes == []
        assert manager.new_steps_count == 0
        assert manager.header_code is None

    def test_gen_code_cache_initial_state(self, mock_playwright, browser_config):
        manager = PlaywrightSessionManager(browser_config)
        assert manager.gen_code_cache == []
        assert manager.gen_code_id is None
        assert manager.steps_dir is None
        assert manager.step_file_target is None
        assert manager.proposed_changes == []
        assert manager.new_steps_count == 0
        assert manager.header_code is None

    def test_viewport_config(self, mock_playwright, browser_config):
        browser_config["browser"]["viewport"] = {"width": 1920, "height": 1080}
        manager = PlaywrightSessionManager(browser_config)
        mock_playwright['browser'].new_context.assert_called_once_with(
            viewport={"width": 1920, "height": 1080}
        )

    def test_default_viewport(self, mock_playwright):
        config = {"browser": {"browser_name": "chromium", "headless": True}}
        manager = PlaywrightSessionManager(config)
        mock_playwright['browser'].new_context.assert_called_once_with(
            viewport={"width": 1280, "height": 720}
        )

    def test_timeout_config(self, mock_playwright, browser_config):
        browser_config["browser"]["timeout"] = 60000
        manager = PlaywrightSessionManager(browser_config)
        mock_playwright['context'].set_default_timeout.assert_called_once_with(60000)

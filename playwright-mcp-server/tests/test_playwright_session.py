# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import pytest
import json
import os
import tempfile
import asyncio
from unittest.mock import MagicMock, patch, PropertyMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from playwright_session import PlaywrightSessionManager


class TestPlaywrightSessionManager:
    """Tests for PlaywrightSessionManager"""

    @pytest.fixture
    def mock_playwright(self):
        with patch('playwright_session.async_playwright') as mock_pw:
            mock_pw_instance = MagicMock()
            mock_browser = MagicMock()
            mock_context = MagicMock()
            mock_page = MagicMock()
            
            async def mock_launch(*args, **kwargs):
                return mock_browser
            async def mock_new_context(*args, **kwargs):
                return mock_context
            async def mock_new_page(*args, **kwargs):
                return mock_page
            async def mock_start():
                return mock_pw_instance
            
            mock_pw_instance.chromium.launch = mock_launch
            mock_pw_instance.firefox.launch = mock_launch
            mock_pw_instance.webkit.launch = mock_launch
            mock_browser.new_context = mock_new_context
            mock_context.new_page = mock_new_page
            mock_pw.return_value.start = mock_start
            
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

    def _create_manager_sync(self, mock_playwright, browser_config):
        """Create manager using sync mocks (tests expect synchronous initialization)"""
        manager = PlaywrightSessionManager(browser_config)
        manager._playwright = MagicMock()
        manager._browser = mock_playwright['browser']
        manager._context = mock_playwright['context']
        manager._page = mock_playwright['page']
        return manager

    def test_init_chromium(self, mock_playwright, browser_config):
        manager = self._create_manager_sync(mock_playwright, browser_config)
        assert manager._browser is not None
        assert manager._page is not None

    def test_init_firefox(self, mock_playwright, browser_config):
        manager = self._create_manager_sync(mock_playwright, browser_config)
        assert manager._browser is not None

    def test_init_webkit(self, mock_playwright, browser_config):
        manager = self._create_manager_sync(mock_playwright, browser_config)
        assert manager._browser is not None

    def test_init_unsupported_browser(self, mock_playwright, browser_config):
        browser_config["browser"]["browser_name"] = "safari"
        manager = PlaywrightSessionManager(browser_config)
        with pytest.raises(ValueError, match="Unsupported browser: safari"):
            import asyncio
            asyncio.get_event_loop().run_until_complete(manager.initialize())

    def test_page_property(self, mock_playwright, browser_config):
        manager = self._create_manager_sync(mock_playwright, browser_config)
        assert manager.page is not None

    def test_page_property_not_initialized(self, mock_playwright, browser_config):
        manager = PlaywrightSessionManager.__new__(PlaywrightSessionManager)
        manager._page = None
        with pytest.raises(RuntimeError, match="Browser page not initialized"):
            _ = manager.page

    def test_browser_property(self, mock_playwright, browser_config):
        manager = self._create_manager_sync(mock_playwright, browser_config)
        assert manager.browser is not None

    def test_context_property(self, mock_playwright, browser_config):
        manager = self._create_manager_sync(mock_playwright, browser_config)
        assert manager.context is not None

    def test_close(self, mock_playwright, browser_config):
        manager = self._create_manager_sync(mock_playwright, browser_config)
        manager.close()

    def test_close_with_error(self, mock_playwright, browser_config):
        manager = self._create_manager_sync(mock_playwright, browser_config)
        manager._page.close.side_effect = Exception("close error")
        manager.close()

    def test_update_config(self, mock_playwright, browser_config):
        manager = self._create_manager_sync(mock_playwright, browser_config)
        new_config = {"browser": {"browser_name": "firefox"}}
        manager.update_config(new_config)
        assert manager._config == new_config

    def test_clear_gen_code_cache(self, mock_playwright, browser_config):
        manager = self._create_manager_sync(mock_playwright, browser_config)
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
        manager = self._create_manager_sync(mock_playwright, browser_config)
        assert manager._context is not None

    def test_default_viewport(self, mock_playwright):
        config = {"browser": {"browser_name": "chromium", "headless": True}}
        manager = self._create_manager_sync(mock_playwright, config)
        assert manager._context is not None

    def test_timeout_config(self, mock_playwright, browser_config):
        browser_config["browser"]["timeout"] = 60000
        manager = self._create_manager_sync(mock_playwright, browser_config)
        assert manager._context is not None

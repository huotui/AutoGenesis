# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import pytest
import json
import os
import tempfile
import time
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.config_manager import ConfigManager, ConfigFileHandler


class TestConfigManager:
    """Tests for ConfigManager"""

    @pytest.fixture
    def config_data(self):
        return {
            "browser": {
                "browser_name": "chromium",
                "headless": True,
                "viewport": {"width": 1280, "height": 720},
                "timeout": 30000
            }
        }

    @pytest.fixture
    def config_file(self, config_data):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_init_with_config_path(self, config_file):
        manager = ConfigManager(config_path=config_file)
        config = manager.get_config()
        assert config is not None
        assert "browser" in config
        assert config["browser"]["browser_name"] == "chromium"

    def test_init_file_not_found(self):
        manager = ConfigManager(config_path="/nonexistent/path/config.json")
        config = manager.get_config()
        assert config == {}

    def test_get_config(self, config_file, config_data):
        manager = ConfigManager(config_path=config_file)
        config = manager.get_config()
        assert config["browser"]["browser_name"] == "chromium"
        assert config["browser"]["headless"] is True

    def test_get_config_returns_copy(self, config_file):
        manager = ConfigManager(config_path=config_file)
        config1 = manager.get_config()
        config2 = manager.get_config()
        assert config1 is not config2
        assert config1 == config2

    def test_reload_config(self, config_file, config_data):
        manager = ConfigManager(config_path=config_file)
        
        config_data["browser"]["browser_name"] = "firefox"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        result = manager.reload_config()
        assert result is True
        config = manager.get_config()
        assert config["browser"]["browser_name"] == "firefox"

    def test_reload_config_file_not_found(self):
        manager = ConfigManager.__new__(ConfigManager)
        manager.config_path = "/nonexistent/path.json"
        manager.on_config_change = None
        manager._lock = __import__('threading').Lock()
        manager._observer = None
        manager._config = {}
        
        result = manager.reload_config()
        assert result is False

    def test_config_change_callback(self, config_file, config_data):
        callback = MagicMock()
        manager = ConfigManager(config_path=config_file, on_config_change=callback)
        callback.assert_called_once()
        
        config_data["browser"]["browser_name"] = "firefox"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        manager.reload_config()
        assert callback.call_count == 2

    def test_config_change_callback_error(self, config_file):
        callback = MagicMock(side_effect=Exception("Callback error"))
        manager = ConfigManager(config_path=config_file, on_config_change=callback)
        callback.assert_called_once()

    def test_start_watching(self, config_file):
        with patch('utils.config_manager.Observer') as mock_observer_class:
            mock_observer = MagicMock()
            mock_observer_class.return_value = mock_observer
            
            manager = ConfigManager(config_path=config_file)
            manager.start_watching()
            
            mock_observer_class.assert_called_once()
            mock_observer.schedule.assert_called_once()
            mock_observer.start.assert_called_once()

    def test_start_watching_already_running(self, config_file):
        with patch('utils.config_manager.Observer') as mock_observer_class:
            mock_observer = MagicMock()
            mock_observer_class.return_value = mock_observer
            
            manager = ConfigManager(config_path=config_file)
            manager.start_watching()
            manager.start_watching()
            
            assert mock_observer_class.call_count == 1

    def test_stop_watching(self, config_file):
        with patch('utils.config_manager.Observer') as mock_observer_class:
            mock_observer = MagicMock()
            mock_observer_class.return_value = mock_observer
            
            manager = ConfigManager(config_path=config_file)
            manager.start_watching()
            manager.stop_watching()
            
            mock_observer.stop.assert_called_once()
            mock_observer.join.assert_called_once()
            assert manager._observer is None

    def test_stop_watching_not_started(self, config_file):
        manager = ConfigManager(config_path=config_file)
        manager.stop_watching()
        assert manager._observer is None

    def test_get_platform_config(self, config_file):
        manager = ConfigManager(config_path=config_file)
        browser_config = manager.get_platform_config("browser")
        assert browser_config is not None
        assert browser_config["browser_name"] == "chromium"

    def test_get_platform_config_not_found(self, config_file):
        manager = ConfigManager(config_path=config_file)
        result = manager.get_platform_config("nonexistent")
        assert result is None

    def test_get_platform_config_no_config(self):
        manager = ConfigManager.__new__(ConfigManager)
        manager._config = None
        manager._lock = __import__('threading').Lock()
        result = manager.get_platform_config("browser")
        assert result is None


class TestConfigFileHandler:
    """Tests for ConfigFileHandler"""

    def test_on_modified_config_file(self, config_file=None):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"browser": {"browser_name": "chromium"}}, f)
            temp_path = f.name
        
        try:
            mock_manager = MagicMock()
            mock_manager.config_path = temp_path
            handler = ConfigFileHandler(mock_manager)
            
            event = MagicMock()
            event.is_directory = False
            event.src_path = temp_path
            
            handler.on_modified(event)
            mock_manager.reload_config.assert_called_once()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_on_modified_directory_event(self):
        mock_manager = MagicMock()
        handler = ConfigFileHandler(mock_manager)
        
        event = MagicMock()
        event.is_directory = True
        
        handler.on_modified(event)
        mock_manager.reload_config.assert_not_called()

    def test_on_modified_different_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"browser": {"browser_name": "chromium"}}, f)
            config_path = f.name
        
        try:
            mock_manager = MagicMock()
            mock_manager.config_path = config_path
            handler = ConfigFileHandler(mock_manager)
            
            event = MagicMock()
            event.is_directory = False
            event.src_path = "/different/file.json"
            
            handler.on_modified(event)
            mock_manager.reload_config.assert_not_called()
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)

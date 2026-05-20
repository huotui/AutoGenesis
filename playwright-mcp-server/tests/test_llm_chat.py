# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import pytest
import json
import os
from unittest.mock import MagicMock, patch, PropertyMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from llm.chat import LLMClient, is_ai_enabled


class TestLLMClientInit:
    """Tests for LLMClient initialization"""

    @patch.dict(os.environ, {}, clear=True)
    def test_default_values(self):
        with patch('llm.chat.load_dotenv'):
            client = LLMClient()
            assert client.model_name == "azure gpt-4o 2025-01-01-preview"
            assert client.temperature == 0.2
            assert client.max_tokens == 4096
            assert client.max_retries == 2
            assert client.timeout == 60
            assert client.api_key is None
            assert client.azure_endpoint is None

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/"
    })
    def test_with_env_vars(self):
        with patch('llm.chat.load_dotenv'):
            client = LLMClient()
            assert client.api_key == "test-key"
            assert client.azure_endpoint == "https://test.openai.azure.com/"


class TestGetAzureModel:
    """Tests for get_azure_model method"""

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/"
    })
    def test_azure_model_success(self):
        with patch('llm.chat.load_dotenv'), \
             patch('llm.chat.AzureChatOpenAI') as mock_azure:
            mock_azure.return_value = MagicMock()
            client = LLMClient()
            model = client.get_azure_model()
            mock_azure.assert_called_once()
            assert model is not None

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/"
    })
    def test_azure_model_invalid_format(self):
        with patch('llm.chat.load_dotenv'):
            client = LLMClient()
            client.model_name = "azure"
            with pytest.raises(ValueError, match="Azure model name must be in the format"):
                client.get_azure_model()

    @patch.dict(os.environ, {}, clear=True)
    def test_azure_model_missing_api_key(self):
        with patch('llm.chat.load_dotenv'):
            client = LLMClient()
            client.model_name = "azure gpt-4o 2025-01-01-preview"
            with pytest.raises(ValueError, match="AZURE_OPENAI_API_KEY"):
                client.get_azure_model()

    @patch.dict(os.environ, {"AZURE_OPENAI_API_KEY": "test-key"}, clear=True)
    def test_azure_model_missing_endpoint(self):
        with patch('llm.chat.load_dotenv'):
            client = LLMClient()
            client.model_name = "azure gpt-4o 2025-01-01-preview"
            with pytest.raises(ValueError, match="AZURE_OPENAI_ENDPOINT"):
                client.get_azure_model()

    def test_unsupported_model(self):
        with patch('llm.chat.load_dotenv'):
            client = LLMClient()
            client.model_name = "unsupported-model"
            with pytest.raises(ValueError, match="Unsupported model name"):
                client.get_azure_model()


class TestCompressImage:
    """Tests for compress_image method"""

    def test_compress_small_image(self):
        from PIL import Image
        import io

        img = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        image_data = buffer.getvalue()

        with patch('llm.chat.load_dotenv'):
            client = LLMClient()
            result = client.compress_image(image_data)
            assert isinstance(result, bytes)
            assert len(result) > 0

    def test_compress_rgba_image(self):
        from PIL import Image
        import io

        img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        image_data = buffer.getvalue()

        with patch('llm.chat.load_dotenv'):
            client = LLMClient()
            result = client.compress_image(image_data)
            assert isinstance(result, bytes)
            assert len(result) > 0

    def test_compress_large_image(self):
        from PIL import Image
        import io

        img = Image.new('RGB', (2000, 2000), color='blue')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=100)
        image_data = buffer.getvalue()

        with patch('llm.chat.load_dotenv'):
            client = LLMClient()
            result = client.compress_image(image_data, target_length=60000)
            assert isinstance(result, bytes)
            assert len(result) <= 100000


class TestEvaluateTask:
    """Tests for evaluate_task method"""

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/"
    })
    def test_evaluate_task_azure(self):
        with patch('llm.chat.load_dotenv'), \
             patch.object(LLMClient, 'evaluate_task_with_azure') as mock_azure:
            mock_azure.return_value = MagicMock(result=True, reason="OK")
            client = LLMClient()
            result = client.evaluate_task("test task", b"image_data")
            mock_azure.assert_called_once_with("test task", b"image_data")

    @patch.dict(os.environ, {}, clear=True)
    def test_evaluate_task_local(self):
        with patch('llm.chat.load_dotenv'), \
             patch.object(LLMClient, 'evaluate_task_with_local_lm') as mock_local:
            mock_local.return_value = MagicMock(result=True, reason="OK")
            client = LLMClient()
            result = client.evaluate_task("test task", b"image_data")
            mock_local.assert_called_once_with("test task", b"image_data")

    @patch.dict(os.environ, {}, clear=True)
    def test_evaluate_task_no_provider(self):
        with patch('llm.chat.load_dotenv'):
            client = LLMClient()
            client.local_lm_endpoint = None
            with pytest.raises(Exception, match="No valid LLM provider"):
                client.evaluate_task("test task")


class TestEvaluateWebTask:
    """Tests for evaluate_web_task method"""

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/"
    })
    def test_evaluate_web_task_azure(self):
        with patch('llm.chat.load_dotenv'), \
             patch.object(LLMClient, 'evaluate_web_task_with_azure') as mock_azure:
            mock_azure.return_value = MagicMock(result=True, reason="OK", elements_found=[])
            client = LLMClient()
            result = client.evaluate_web_task("test task", "<html></html>", b"image_data")
            mock_azure.assert_called_once_with("test task", "<html></html>", b"image_data")

    @patch.dict(os.environ, {}, clear=True)
    def test_evaluate_web_task_local(self):
        with patch('llm.chat.load_dotenv'), \
             patch.object(LLMClient, 'evaluate_web_task_with_local_lm') as mock_local:
            mock_local.return_value = MagicMock(result=True, reason="OK", elements_found=[])
            client = LLMClient()
            result = client.evaluate_web_task("test task", "<html></html>")
            mock_local.assert_called_once_with("test task", "<html></html>", None)

    @patch.dict(os.environ, {}, clear=True)
    def test_evaluate_web_task_no_provider(self):
        with patch('llm.chat.load_dotenv'):
            client = LLMClient()
            client.local_lm_endpoint = None
            with pytest.raises(Exception, match="No valid LLM provider"):
                client.evaluate_web_task("test task")


class TestAvailabilityChecks:
    """Tests for availability check methods"""

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/"
    })
    def test_azure_gpt_available(self):
        with patch('llm.chat.load_dotenv'):
            client = LLMClient()
            assert client.azure_gpt_available() is True

    @patch.dict(os.environ, {}, clear=True)
    def test_azure_gpt_not_available(self):
        with patch('llm.chat.load_dotenv'):
            client = LLMClient()
            assert client.azure_gpt_available() is False

    def test_local_copilot_available_success(self):
        with patch('llm.chat.load_dotenv'), \
             patch('llm.chat.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [{"name": "gpt-4o"}, {"name": "llama3"}]
            }
            mock_get.return_value = mock_response
            client = LLMClient()
            assert client.local_copilot_available() is True

    def test_local_copilot_available_no_gpt4o(self):
        with patch('llm.chat.load_dotenv'), \
             patch('llm.chat.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [{"name": "llama3"}]
            }
            mock_get.return_value = mock_response
            client = LLMClient()
            assert client.local_copilot_available() is False

    def test_local_copilot_available_error(self):
        with patch('llm.chat.load_dotenv'), \
             patch('llm.chat.requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection refused")
            client = LLMClient()
            assert client.local_copilot_available() is False

    def test_local_copilot_available_http_error(self):
        with patch('llm.chat.load_dotenv'), \
             patch('llm.chat.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_get.return_value = mock_response
            client = LLMClient()
            assert client.local_copilot_available() is False


class TestIsAiEnabled:
    """Tests for is_ai_enabled function"""

    @patch.dict(os.environ, {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/"
    })
    def test_ai_enabled_with_azure(self):
        with patch('llm.chat.load_dotenv'):
            assert is_ai_enabled() is True

    @patch.dict(os.environ, {}, clear=True)
    def test_ai_not_enabled(self):
        with patch('llm.chat.load_dotenv'), \
             patch.object(LLMClient, 'local_copilot_available', return_value=False):
            assert is_ai_enabled() is False

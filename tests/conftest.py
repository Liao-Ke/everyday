import os
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mock_env():
    with patch.dict(
        os.environ,
        {
            "API_KEY": "test_zhipu_key",
            "API_KEY_DS": "test_ds_key",
            "API_KEY_KIMI": "test_kimi_key",
            "API_KEY_DOUBAO": "test_doubao_key",
            "API_KEY_QWEN": "test_qwen_key",
            "API_KEY_MODELSCOPE": "test_modelscope_key",
            "API_KEY_GEMINI": "test_gemini_key",
        },
    ):
        yield


@pytest.fixture
def sample_config():
    return {
        "name": "test_model",
        "API_KEY": "test_key",
        "CLIENT_PARAMS": {"base_url": "https://test.api.com"},
        "CHAT_PARAMS": {
            "model": "test-model",
            "messages": [{"role": "user", "content": "test"}],
        },
        "PREPROCESSORS": [],
        "POSTPROCESSORS": [],
        "POSTPROCESSOR_FILES": [],
    }


@pytest.fixture
def sample_response():
    return {"content": "# Test Story\n\nThis is a test story content."}


@pytest.fixture
def tmp_story_dir(tmp_path):
    story_dir = tmp_path / "story" / "故事"
    story_dir.mkdir(parents=True)
    return story_dir


@pytest.fixture
def sample_config_with_frontmatter():
    return {
        "name": "zhipu",
        "API_KEY": "test_key",
        "CLIENT_PARAMS": {"base_url": "https://test.api.com"},
        "CHAT_PARAMS": {
            "model": "test-model",
            "messages": [{"role": "user", "content": "test"}],
        },
        "PREPROCESSORS": [],
        "POSTPROCESSORS": [],
        "POSTPROCESSOR_FILES": [],
        "UPDATE_FRONTMATTER": True,
    }

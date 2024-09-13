import pytest
from unittest.mock import patch
import sys

sys.path.insert(0, '../ansible/roles/evaluation-tool/module_utils')

from create_model import create_chat_model_from_config, ChatOpenAiWithCustomClient, ChatGroqWithCustomClient, ChatOllamaWithCustomClient


@pytest.fixture
def gpt_config():
    return {
        "model": "gpt-3.5-turbo",
        "api_key": "test_api_key",
    }


@pytest.fixture
def groq_config():
    return {
        "api_key": "test_api_key",
        "models": {
            "llama31": "llama-model",
        }
    }


@pytest.fixture
def ollama_config():
    return {
        "model": "ollama",
    }


@patch('create_model.ChatOpenAiWithCustomClient')
def test_create_chat_model_gpt(MockChatOpenAiWithCustomClient, gpt_config):
    mock_instance = MockChatOpenAiWithCustomClient.return_value
    model = create_chat_model_from_config(gpt_config, "gpt")
    MockChatOpenAiWithCustomClient.assert_called_with(
        temperature=0.1,
        model=gpt_config["model"],
        api_key=gpt_config["api_key"]
    )
    assert model == mock_instance


@patch('create_model.ChatGroqWithCustomClient')
def test_create_chat_model_groq_llama(MockChatGroqWithCustomClient, groq_config):
    mock_instance = MockChatGroqWithCustomClient.return_value
    model = create_chat_model_from_config(groq_config, "groq")
    MockChatGroqWithCustomClient.assert_called_with(
        temperature=0.1,
        model=groq_config["models"]["llama31"],
        api_key=groq_config["api_key"]
    )
    assert model == mock_instance


@patch('create_model.ChatOllamaWithCustomClient')
def test_create_chat_model_ollama(MockChatOllamaWithCustomClient, ollama_config):
    mock_instance = MockChatOllamaWithCustomClient.return_value
    model = create_chat_model_from_config(ollama_config, "ollama")
    MockChatOllamaWithCustomClient.assert_called_with(
        temperature=0.1,
        model=ollama_config["model"]
    )
    assert model == mock_instance


def test_create_chat_model_invalid_identifier(gpt_config):
    with pytest.raises(ValueError) as excinfo:
        create_chat_model_from_config(gpt_config, "invalid")
    assert str(excinfo.value) == "Given identifier invalid is invalid"

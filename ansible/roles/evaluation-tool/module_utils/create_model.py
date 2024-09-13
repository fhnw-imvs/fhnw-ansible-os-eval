import httpx
import asyncio
from typing import List, Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_experimental.llms.ollama_functions import OllamaFunctions





class CustomHttpClient(httpx.Client):
    def __init__(self, *args, **kwargs):
        self.response_headers = []
        super().__init__(*args, **kwargs)

    def send(self, request: httpx.Request, **kwargs) -> httpx.Response:
        response = super().send(request, **kwargs)

        rate_limits = {
            "retry-after": response.headers.get("retry-after"),
            "x-ratelimit-limit-requests": response.headers.get("x-ratelimit-limit-requests"),
            "x-ratelimit-limit-tokens": response.headers.get("x-ratelimit-limit-tokens"),
            "x-ratelimit-remaining-requests": response.headers.get("x-ratelimit-remaining-requests"),
            "x-ratelimit-remaining-tokens": response.headers.get("x-ratelimit-remaining-tokens"),
            "x-ratelimit-reset-requests": response.headers.get("x-ratelimit-reset-requests"),
            "x-ratelimit-reset-tokens": response.headers.get("x-ratelimit-reset-tokens"),
        }

        self.response_headers.append(dict(rate_limits))

        return response


class ChatOpenAiWithCustomClient(ChatOpenAI):
    def __init__(self, **kwargs):
        custom_client = CustomHttpClient()
        super().__init__(http_client=custom_client, **kwargs)

    def get_response_headers(self) -> List[Dict[str, Any]]:
        return self.http_client.response_headers


class ChatGroqWithCustomClient(ChatGroq):
    def __init__(self, **kwargs):
        custom_client = CustomHttpClient()
        super().__init__(http_client=custom_client, **kwargs)

    def get_response_headers(self) -> List[Dict[str, Any]]:
        return self.http_client.response_headers


class ChatOllamaWithCustomClient(OllamaFunctions):
    def __init__(self, **kwargs):
        custom_client = CustomHttpClient()
        super().__init__(http_client=custom_client, **kwargs)

    def get_response_headers(self) -> List[Dict[str, Any]]:
        return self.http_client.response_headers


def create_chat_model_from_config(llm_config, identifier):
    api_key = llm_config.get("api_key")

    models = llm_config.get("models")
    if models:
        model_mapping = {
            "groq": models.get("llama31"),
            "groq-llama31": models.get("llama31"),
            "groq-llama70b": models.get("llama70b"),
            "groq-llama31_70b": models.get("llama31_70b")
        }
        model = model_mapping[identifier]
    else:
        model = llm_config.get("model")

    if identifier == "gpt":
        return ChatOpenAiWithCustomClient(
            temperature=0.1,
            model=model,
            api_key=api_key
        )
    elif identifier == "ollama":
        return ChatOllamaWithCustomClient(
            temperature=0.1,
            model=model,
        )
    elif identifier.startswith("groq"):
        return ChatGroqWithCustomClient(
            temperature=0.1,
            model=model,
            api_key=api_key
        )
    else:
        raise ValueError(f"Given identifier {identifier} is invalid")

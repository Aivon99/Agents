from __future__ import annotations

from gateway.providers.base import ProviderAdapter
from gateway.providers.cohere import CohereAdapter
from gateway.providers.gemini import GeminiAdapter
from gateway.providers.huggingface import HuggingFaceAdapter
from gateway.providers.openrouter import OpenRouterAdapter


PROVIDERS: dict[str, ProviderAdapter] = {
    'openrouter': OpenRouterAdapter(),
    'gemini': GeminiAdapter(),
    'cohere': CohereAdapter(),
    'huggingface': HuggingFaceAdapter(),
}

from pathlib import Path

from agno.models.ollama import Ollama
from agno.models.openai.chat import OpenAIChat

from canvy.types import canvyConfig, ModelProvider

CANVAS_TEST_KEY = (
    "1000~aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
)
CANVAS_TEST_URL = "https://university.canvas.com"
OPENAI_TEST_KEY = "sk-sam-altman"
OLLAMA_TEST_MODEL = "chatgippity:69T"

PROVIDER_TEST_KEYS = {
    "OpenAI": OPENAI_TEST_KEY,
    "Ollama": OLLAMA_TEST_MODEL,
}
PROVIDER_TEST_MAPPING = {
    "OpenAI": "openai_key",
    "Ollama": "ollama_model",
}
PROVIDER_TEST_MODELS = {
    "OpenAI": OpenAIChat,
    "Ollama": Ollama,
}


def vanilla_config(path: Path) -> canvyConfig:
    """
    canvyConfig(
        canvas_key=CANVAS_TEST_KEY,
        canvas_url=CANVAS_TEST_URL,
        storage_path=path,
        default_provider=ModelProvider.OPENAI,
    )
    """
    return canvyConfig(
        canvas_key=CANVAS_TEST_KEY,
        canvas_url=CANVAS_TEST_URL,
        storage_path=path,
        default_provider=ModelProvider.OPENAI,
    )

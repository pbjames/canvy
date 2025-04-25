from agno.models.ollama import Ollama
from openai import OpenAI

CANVAS_TEST_KEY = (
    "1000~aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
)
CANVAS_TEST_URL = "https://university.canvas.com"
OPENAI_TEST_KEY = "sk-sam-altman"
OLLAMA_TEST_MODEL = "chatgippity:69T"

PROVIDER_TEST_VALUES = {
    "Ollama": OLLAMA_TEST_MODEL,
    "OpenAI": OPENAI_TEST_KEY,
}
PROVIDER_TEST_MAPPING = {
    "Ollama": "ollama_model",
    "OpenAI": "openai_key",
}
PROVIDER_TEST_MODELS = {
    "Ollama": Ollama,
    "OpenAI": OpenAI,
}

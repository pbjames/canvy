from agno.models.ollama import Ollama
from agno.models.openai.chat import OpenAIChat

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

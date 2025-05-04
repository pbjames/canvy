import getpass
import logging
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, field_serializer, field_validator

from canvy.const import (
    API_KEY_DESC,
    API_KEY_REGEX,
    DEFAULT_PROVIDER_DESC,
    EDU_URL_DESC,
    OLLAMA_MODEL_DESC,
    OPENAI_KEY_DESC,
    STORAGE_PATH_DESC,
    URL_REGEX,
)

logger = logging.getLogger(__name__)


class ModelProvider(StrEnum):
    OLLAMA = "Ollama"
    OPENAI = "OpenAI"


class CanvyConfig(BaseModel):
    canvas_key: str = Field(description=API_KEY_DESC, pattern=API_KEY_REGEX)
    canvas_url: str = Field(description=EDU_URL_DESC, pattern=URL_REGEX)
    openai_key: str = Field(default="", description=OPENAI_KEY_DESC)
    ollama_model: str = Field(default="", description=OLLAMA_MODEL_DESC)
    storage_path: Path = Field(description=STORAGE_PATH_DESC)
    default_provider: ModelProvider = Field(
        ModelProvider.OPENAI, description=DEFAULT_PROVIDER_DESC
    )

    @field_validator("storage_path")
    @classmethod
    def verify_accessible_path(cls, value: Path) -> Path:
        """
        Test if the user can access a given path to prevent compounding files access errors
        """
        if value.exists() and value.owner() != getpass.getuser():
            e = f"Path {value} exists but we don't have permission to access it"
            raise ValueError(e)
        try:
            value.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(f"Unknown path resolution error: '{e}'")
            raise e
        return value

    @field_serializer("storage_path")
    def serialize_path(self, value: Path) -> str:
        """
        Do this or else it uses __repr__ for some reason
        """
        return str(value)

    @field_serializer("default_provider")
    def serialize_provider(self, value: ModelProvider) -> str:
        """
        Do this or else it turns into array for some reason
        """
        return str(value)


# INFO: Used for the children of modules (ModuleItem)
class ModuleItemType(StrEnum):
    HEADER = "SubHeader"
    PAGE = "Page"
    QUIZ = "Quiz"
    EXTERNAL_TOOL = "ExternalTool"
    EXTERNAL_URL = "ExternalUrl"
    ATTACHMENT = "File"
    DISCUSSION = "Discussion"
    ASSIGNMENT = "Assignment"


# INFO: Used for assignments
class SubmissionType(StrEnum):
    FILE_UPLOAD = "online_upload"
    TEXT_ENTRY = "online_text_entry"
    URL_ENTRY = "online_url"
    RECORDING = "media_recording"
    ANNOTATION = "student_annotation"

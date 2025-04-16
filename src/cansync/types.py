import logging
import os
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from cansync.const import (
    ANTHRO_KEY_DESC,
    API_KEY_DESC,
    API_KEY_REGEX,
    API_SK_REGEX,
    DEFAULT_DOWNLOAD_DIR,
    EDU_URL_DESC,
    OPENAI_KEY_DESC,
    STORAGE_PATH_DESC,
    URL_REGEX,
)

logger = logging.getLogger(__name__)


class CansyncConfig(BaseModel):
    canvas_key: str = Field(description=API_KEY_DESC, pattern=API_KEY_REGEX)
    canvas_url: str = Field(description=EDU_URL_DESC, pattern=URL_REGEX)
    openai_key: str = Field(description=OPENAI_KEY_DESC, pattern=API_SK_REGEX)
    anthro_key: str = Field(description=ANTHRO_KEY_DESC, pattern=API_SK_REGEX)
    storage_path: Path = Field(DEFAULT_DOWNLOAD_DIR, description=STORAGE_PATH_DESC)

    @field_validator("storage_path")
    @classmethod
    def verify_accessible_path(cls, value: Path) -> bool:
        """
        Test if the user can access a given path to prevent compounding
        files access errors
        """
        if value.exists():
            return value.owner() == os.getlogin()
        try:
            value.mkdir(parents=True)
            return True
        except PermissionError as e:
            logger.warning(e)
            return False
        except Exception as e:
            logger.warning(f"Unknown path resolution error: '{e}'")
            return False

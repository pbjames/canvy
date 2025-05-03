import logging.config
import os
import re
from functools import reduce
from pathlib import Path

import toml
from agno.models.base import Model
from agno.models.ollama import Ollama
from agno.models.openai.chat import OpenAIChat
from canvasapi.file import File

from canvy.const import CONFIG_PATH, LOG_FN, LOGGING_CONFIG, OPENAI_MODEL
from canvy.types import CanvyConfig

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """
    Setup logging using logging config defined in const.py because it's
    quite good
    """
    create_dir(LOG_FN.parent)
    return logging.config.dictConfig(LOGGING_CONFIG)


def better_course_name(name: str) -> str:
    """
    Removes ID numbers next to the given title of the course
    """
    return re.sub(r" ?\((\d,? ?)+\) ?", "", name)


def create_dir(directory: Path) -> None:
    logger.debug(f"Creating directory {directory} if not existing")
    os.makedirs(directory, exist_ok=True)


def get_config(path: Path | None = None) -> CanvyConfig:
    path = path or CONFIG_PATH
    with open(path) as fp:
        logger.debug(f"Retrieving config from {path}")
        config = CanvyConfig(**toml.load(fp))  # pyright: ignore[reportAny]
    return config


def set_config(config: CanvyConfig, dest: Path = CONFIG_PATH) -> None:
    dest = dest if dest else CONFIG_PATH
    with open(dest, "w") as fp:
        logger.debug("Writing config")
        toml.dump(config.model_dump(), fp)


def delete_config(path: Path = CONFIG_PATH):
    os.remove(path)


def download_structured(
    file: File, *dirs: str, storage_dir: Path | None = None, force: bool = False
) -> bool:
    """
    Download a canvasapi File and preserve course structure using directory names

    Args:
        file: File object given by Canvas, can raise various exceptions
        dirs: Series of directory names to make and download file into
        force: Overwrite any previously existing files

    Returns:
        If the file was downloaded
    """
    download_dir = Path(storage_dir or get_config().storage_path).expanduser()
    path: Path = reduce(lambda p, q: p / q, [download_dir, *map(Path, dirs)])
    filename: str = file.filename  # pyright: ignore[reportAny]
    file_path: Path = path / filename
    create_dir(path)
    if not file_path.is_file() or force:
        logger.info(f"Downloading {filename}{'(forced)' * force} into {file_path}")
        try:
            file.download(file_path)  # pyright: ignore[reportUnknownMemberType]
            return True
        except Exception as e:
            logger.warning(
                f"Tried to download {filename} but we likely don't have access ({e})"
            )
            return False
    else:
        logger.info(f"{filename} already present, skipping")
        return False


def provider(config: CanvyConfig) -> Model:
    """
    Get the preferred model provider from the config, default is OpenAI because
    lazy people. Implemented config check to prevent ambiguous errors

    Args:
        config: Config with provider

    Returns:
        Model: Agno model type to use, of which there are many
    """
    e = "Model set to {} but the key isn't in the config"
    if config.default_provider == "OpenAI":
        if key := config.openai_key:
            return OpenAIChat(id=OPENAI_MODEL, api_key=key)
        else:
            raise ValueError(e.format("OpenAI"))
    # elif config.default_provider == "Ollama":
    else:  # noqa: PLR5501
        if model := config.ollama_model:
            return Ollama(id=model)
        else:
            raise ValueError(e.format("Ollama"))

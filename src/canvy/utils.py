from __future__ import annotations

import logging.config
import os
import re
from collections.abc import Iterable
from functools import reduce
from pathlib import Path

from agno.models.ollama import Ollama
from agno.models.openai.chat import OpenAIChat
from agno.models.anthropic import Claude
import toml
from canvasapi.file import File

from canvy.const import (
    ANTHRO_MODEL,
    CONFIG_PATH,
    LOG_FN,
    LOGGING_CONFIG,
    OPENAI_MODEL,
    SUMMARIES_DIRNAME,
)
from canvy.types import CanvyConfig, Model

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


def has_config(path: Path | None = None) -> bool:
    try:
        get_config(path)
        return True
    except Exception as e:
        logger.info(f"Config test fail: {e}")
        return False


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
    file_name = file.filename  # pyright: ignore[reportAny]
    file_path: Path = concat_names(download_dir, (*dirs, file_name))
    create_dir(file_path.parent)
    if not file_path.is_file() or force:
        logger.info(f"Downloading {file_name}{'(forced)' * force} into {file_path}")
        try:
            file.download(file_path)  # pyright: ignore[reportUnknownMemberType]
            return True
        except Exception as e:
            logger.warning(
                f"Tried to download {file_name} but we likely don't have access ({e})"
            )
            return False
    else:
        logger.info(f"{file_name} already present, skipping")
        return False


def concat_names(base: Path, names: Iterable[str | Path]) -> Path:
    return reduce(lambda p, q: p / q, [base, *map(Path, names)])


def provider(config: CanvyConfig) -> Model:
    """
    Get the preferred model provider from the config, default is OpenAI because
    lazy people. Implemented config check to prevent ambiguous errors

    Args:
        config: Config with provider

    Returns:
        Model: Agno model type to use, of which there are many
    """
    if config.default_provider == "OpenAI":
        if key := config.openai_key:
            return OpenAIChat(id=OPENAI_MODEL, api_key=key)
    elif config.default_provider == "Anthropic":
        if key := config.anthropic_key:
            return Claude(id=ANTHRO_MODEL, api_key=key)
    elif config.default_provider == "Ollama":
        if model := config.ollama_model:
            return Ollama(id=model)
    return None


def setup_cache_mirror(config: CanvyConfig):
    base = config.storage_path / SUMMARIES_DIRNAME
    logger.info(f"Setting up cache mirror at {base}")
    for path in config.storage_path.rglob("*"):
        rebased = base / (path.relative_to(config.storage_path))
        logger.info(f"{path=} {rebased=}")
        if SUMMARIES_DIRNAME in str(path):
            continue
        elif path.is_file():
            rebased.parent.mkdir(parents=True, exist_ok=True)
            rebased.touch()
        elif path.is_dir():
            rebased.mkdir(parents=True, exist_ok=True)


def put_summary(config: CanvyConfig, path: Path, summary: str):
    path = (
        config.storage_path / SUMMARIES_DIRNAME / path.relative_to(config.storage_path)
    )
    path.write_text(summary)
    logger.info(f"Put summary {summary[:17]}.. into {path}")


def get_summary(config: CanvyConfig, path: Path):
    path = (
        config.storage_path / SUMMARIES_DIRNAME / path.relative_to(config.storage_path)
    )
    content = path.read_text()
    logger.info(f"Read summary {content}.. from {path}")
    return content

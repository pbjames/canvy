from __future__ import annotations

import logging.config
import os
import platform
import re
import subprocess
from collections.abc import Iterable
from functools import reduce
from pathlib import Path

import toml
from canvasapi.file import File

from canvy.const import (
    CONFIG_PATH,
    LOG_FN,
    LOGGING_CONFIG,
)
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


def start_process(*args: str):
    if (os_name := platform.system()) == "Linux":
        subprocess.run(("xdg-open", *args), check=False)
    elif os_name == "Windows":
        subprocess.run(("cmd", "/c", "start", *args), check=False)
    elif os_name == "Darwin":
        subprocess.run(("open", *args), check=False)
    else:
        logger.warning(f"Unhandled OS: {os_name}")

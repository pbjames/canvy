import json
import logging.config
import os
import re
from functools import reduce
from pathlib import Path

import toml
from canvasapi.file import File

from cansync.const import CONFIG_PATH, LOG_FN, LOGGING_CONFIG
from cansync.types import CansyncConfig

logger = logging.getLogger(__name__)


def verify_accessible_path(p: Path) -> bool:
    """
    Test if the user can access a given path to prevent compounding
    files access errors
    """
    if p.exists():
        return p.owner() == os.getlogin()

    try:
        p.mkdir(parents=True)
        return True
    except PermissionError as e:
        logger.warning(e)
        return False
    except Exception as e:
        logger.warning(f"Unknown path resolution error: '{e}'")
        return False


def setup_logging() -> None:
    """
    Setup logging using logging config defined in const.py because it's
    quite good
    """
    create_dir(LOG_FN.parent)
    logging.config.dictConfig(LOGGING_CONFIG)


def path_format(name: str) -> str:
    return name.replace(" ", "-")


def short_name(name: str, max_length: int) -> str:
    """
    Convert a long name to a short version for pretty UI
    """
    if len(name) <= max_length:
        return name.ljust(max_length)
    else:
        return name[: max_length - 2] + ".."


def same_length(*strings: str) -> list[str]:
    """
    Extends short_name to apply to all strings in a list with the max
    length set to that of the largest string
    """
    strings_max = max(map(len, strings))
    return [short_name(s, strings_max) for s in strings]


def better_course_name(name: str) -> str:
    """
    Removes ID numbers next to the given title of the course
    """
    return re.sub(r" \((\d,? ?)+\)", "", name)


def create_dir(directory: Path) -> None:
    logger.debug(f"Creating directory {directory} if not existing")
    os.makedirs(directory, exist_ok=True)


def create_config_at(config: CansyncConfig, path: Path = CONFIG_PATH) -> None:
    logger.debug(f"Creating new config file at {path}")
    create_dir(path)
    set_config(config, path)


def get_config(path: Path | None = None) -> CansyncConfig:
    path = path or CONFIG_PATH
    with open(path) as fp:
        logger.debug(f"Retrieving config from {path}")
        config = CansyncConfig(**toml.load(fp))  # pyright: ignore[reportAny]
    return config


def set_config(config: CansyncConfig, dest: Path = CONFIG_PATH) -> None:
    dest = dest if dest else CONFIG_PATH
    with open(dest, "w") as fp:
        logger.debug("Writing config")
        toml.dump(json.loads(config.model_dump_json()), fp)


def download_structured(file: File, *dirs: Path, force: bool = False) -> bool:
    """
    Download a canvasapi File and preserve course structure using directory names

    Args:
        file: File object given by Canvas, can raise various exceptions
        dirs: Series of directory names to make and download file into
        force: Overwrite any previously existing files

    Returns:
        If the file was downloaded
    """
    download_dir = Path(get_config().storage_path).expanduser()
    path: Path = reduce(lambda p, q: p / q, [download_dir, *dirs])
    filename: str = file.filename  # pyright: ignore[reportAny]
    file_path: Path = path / filename
    create_dir(path)
    if not file_path.is_file() or force:
        logger.info(f"Downloading {filename}{'(forced)' * force}")
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

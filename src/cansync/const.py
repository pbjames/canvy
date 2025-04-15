import logging
from pathlib import Path
from typing import Final

from platformdirs import (
    user_config_path,
    user_documents_path,
    user_log_path,
)

from cansync import APP_NAME

logger = logging.getLogger(__name__)

URL_REGEX: Final[str] = (
    r"[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]"
    + r"{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)"
)
API_KEY_REGEX: Final[str] = r"\d{4}~[A-Za-z0-9]{64}"
API_KEY_DESC: Final[str] = (
    "API key provided by Canvas which grants access to the API through your account"
)
EDU_URL_DESC: Final[str] = (
    "Institution URL that is used for Canvas, you should have this provided by them."
)
STORAGE_PATH_DESC: Final[str] = "Where to store files"

LOG_FN: Final[Path] = user_log_path(APP_NAME) / "cansync.log"
CONFIG_PATH: Final[Path] = user_config_path(APP_NAME) / "config.toml"
DEFAULT_DOWNLOAD_DIR: Final[Path] = user_documents_path() / APP_NAME

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(levelname)s: %(message)s"},
        "detailed": {
            "format": "[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": LOG_FN,
            "maxBytes": 10 * 1024**2,
            "backupCount": 3,
        },
    },
    "loggers": {"root": {"level": "DEBUG", "handlers": ["stderr", "file"]}},
}

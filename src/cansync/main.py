import logging
from getpass import getpass
from pathlib import Path

from canvasapi.canvas import Canvas, Course
from typer import Typer

from cansync.const import DEFAULT_DOWNLOAD_DIR
from cansync.scripts.downloader import download as _download
from cansync.types import CansyncConfig
from cansync.utils import (
    get_config,
    setup_logging,
)
from cansync.utils import set_config as utils_set_config

cli = Typer()
logger = logging.getLogger(__name__)


def default_config():
    config = get_config()
    canvas = Canvas(config.canvas_url, config.canvas_key)
    return canvas, config


@cli.command()
def download(path: Path | None = None, force: bool = False):
    canvas, config = default_config()
    _download(canvas, config.canvas_url, force=force)


@cli.command()
def courses():
    canvas, _ = default_config()
    courses: list[Course] = list(canvas.get_courses(enrollment_state="active"))
    for course in courses:
        print(f"{course}")  # noqa: T201


@cli.command()
def set_config(canvas_url: str, storage_path: Path | None = None):
    canvas_key = getpass("Canvas API Key: ")
    config = CansyncConfig(
        canvas_url=canvas_url,
        canvas_key=canvas_key,
        storage_path=storage_path or DEFAULT_DOWNLOAD_DIR,
    )
    utils_set_config(config)


def main():
    setup_logging()
    cli()


if __name__ == "__main__":
    main()

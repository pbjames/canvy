import inspect
import logging
from collections.abc import Callable
from functools import wraps
from getpass import getpass
from pathlib import Path
from typing import Any

from canvasapi.canvas import Canvas, Course
from typer import Typer

from cansync.const import (
    DEFAULT_DOWNLOAD_DIR,
)
from cansync.types import CansyncConfig
from cansync.utils import (
    get_config,
    setup_logging,
)
from cansync.utils import set_config as utils_set_config

cli = Typer()
logger = logging.getLogger(__name__)


def requires_config(func: Callable[..., None]):
    config = get_config()
    canvas = Canvas(config.canvas_url, config.canvas_key)
    names = ["config", "canvas"]

    @wraps(func)
    def with_config(*args: Any, **kwargs: Any):
        return func(canvas, config, *args, **kwargs)

    sig = inspect.signature(func)
    new_params = [
        param for name, param in sig.parameters.items() if name not in [*names, "_"]
    ]
    new_sig = sig.replace(parameters=new_params)
    with_config.__signature__ = new_sig  # pyright: ignore[reportAttributeAccessIssue]
    return with_config


@cli.command()
@requires_config
def download(canvas: Canvas, config: CansyncConfig):
    from cansync.scripts.downloader import download as download

    download(canvas, config.canvas_url)


@cli.command()
@requires_config
def teacher(_: Canvas, config: CansyncConfig):
    from cansync.scripts.teacher import teacher as teacher

    teacher(config)


@cli.command()
@requires_config
def courses(canvas: Canvas, _: CansyncConfig):
    courses: list[Course] = list(canvas.get_courses(enrollment_state="active"))
    for course in courses:
        print(f"{course}")  # noqa: T201


@cli.command()
def set_config(
    canvas_url: str, storage_path: Path | None = None, openai_key: str | None = None
):
    canvas_key = getpass("Canvas API Key: ")
    config = CansyncConfig(
        canvas_url=canvas_url,
        canvas_key=canvas_key,
        storage_path=storage_path or DEFAULT_DOWNLOAD_DIR,
        openai_key=openai_key,
    )
    utils_set_config(config)


def main():
    setup_logging()
    cli()


if __name__ == "__main__":
    main()

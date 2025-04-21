import inspect
import logging
import sys
from collections.abc import Callable
from functools import wraps
from getpass import getpass
from pathlib import Path
from typing import Any

from canvasapi.canvas import Canvas, Course
from canvasapi.requester import ResourceDoesNotExist
from pydantic import ValidationError
from rich import print as pprint
from typer import Typer

from cansync.const import (
    DEFAULT_DOWNLOAD_DIR,
)
from cansync.types import CansyncConfig
from cansync.utils import (
    delete_config,
    get_config,
    setup_logging,
)

cli = Typer()
logger = logging.getLogger(__name__)


def requires_config(func: Callable[..., None]):
    try:
        config = get_config()
        canvas = Canvas(config.canvas_url, config.canvas_key)
    except Exception as e:
        pprint(f"Either the config is messed up or the internet is: {e}")
        user_choice = input("Destroy config file? (Y/n): ").lower() == "y"
        if user_choice:
            delete_config()
        sys.exit(1)
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


@cli.command(short_help="Download files from Canvas")
@requires_config
def download(canvas: Canvas, config: CansyncConfig):
    from cansync.scripts.downloader import download as download

    try:
        count = download(canvas, config.canvas_url)
        pprint(f"[bold]{count}[/bold] new files! :speaking_head: :fire:")
    except (KeyboardInterrupt, EOFError):
        pprint("[bold red]Download stopping[/bold red]...")
        sys.exit(0)
    except ResourceDoesNotExist as e:
        pprint(f"We likely don't have access to courses no more :sad_cat:: {e}")
        sys.exit(1)


# TODO: Add more options and add disclaimers, improve tool usage and add a problem sheet
# making tool
@cli.command(short_help="Use an assistant to go through the files")
@requires_config
def teacher(_: Canvas, config: CansyncConfig):
    from cansync.scripts.teacher import teacher as teacher

    try:
        teacher(config)
    except (KeyboardInterrupt, EOFError):
        pprint("[bold red]Program exiting[/bold red]...")
        sys.exit(0)


# TODO: Make this pretty printed
@cli.command(short_help="List available courses")
@requires_config
def courses(canvas: Canvas, _: CansyncConfig):
    try:
        courses: list[Course] = list(canvas.get_courses(enrollment_state="active"))
        for course in courses:
            print(f"{course}")  # noqa: T201
    except ResourceDoesNotExist as e:
        pprint(f"We probably don't have access to this course: {e}")
    except Exception as e:
        pprint(f"Unknown error: {e}")


@cli.command(short_help="Set up config to use the rest of the tool")
def set_config(
    canvas_url: str, storage_path: Path | None = None, openai_key: str | None = None
):
    from cansync.utils import set_config

    try:
        canvas_key = getpass("Canvas API Key: ")
        config = CansyncConfig(
            canvas_url=canvas_url,
            canvas_key=canvas_key,
            storage_path=storage_path or DEFAULT_DOWNLOAD_DIR,
            openai_key=openai_key,
        )
        set_config(config)
    except ValidationError as e:
        pprint(f"Input values are incorrect: {e}")
    except (EOFError, KeyboardInterrupt):
        pprint("\n[bold red]Closing[/bold red]..")


def main():
    setup_logging()
    cli()
    # TODO: Use tests


if __name__ == "__main__":
    main()

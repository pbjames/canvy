import logging
import sys
from getpass import getpass
from pathlib import Path

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


def requires_config() -> tuple[Canvas, CansyncConfig]:
    try:
        config = get_config()
        canvas = Canvas(config.canvas_url, config.canvas_key)
        return canvas, config
    except FileNotFoundError:
        from cansync.utils import set_config

        choice = input("Config file doesn't exist, create one? (Y/n): ").lower() != "n"
        if not choice:
            sys.exit(1)
        config = CansyncConfig(
            canvas_url=input("Canvas URL: "),
            canvas_key=getpass("Canvas API Key: "),
            storage_path=Path(input("Store path (optional): ") or DEFAULT_DOWNLOAD_DIR),
            openai_key=getpass("Open AI Key (optional): ") or None,
        )
        set_config(config)
        return requires_config()  # XXX: Might be dangerous :smirking_cat:
    except ValidationError as e:
        pprint(f"Input values are incorrect: {e}")
    except (EOFError, KeyboardInterrupt):
        pprint("\n[bold red]Closing[/bold red]..")
    except Exception as e:
        pprint(f"Either the config is messed up or the internet is: {e}")
        user_choice = input("Destroy config file? (y/N): ").lower() == "y"
        if user_choice:
            delete_config()
    sys.exit(1)


@cli.command(short_help="Download files from Canvas")
def download():
    from cansync.scripts.downloader import download

    canvas, config = requires_config()
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
def teacher():
    from cansync.scripts.teacher import teacher

    _, config = requires_config()
    try:
        teacher(config)
    except (KeyboardInterrupt, EOFError):
        pprint("[bold red]Program exiting[/bold red]...")
        sys.exit(0)


# TODO: Make this pretty printed
@cli.command(short_help="List available courses")
def courses():
    canvas, _ = requires_config()
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

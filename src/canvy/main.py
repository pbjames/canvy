import logging
import sys
from getpass import getpass
from pathlib import Path

from canvasapi.canvas import Canvas, Course
from canvasapi.requester import ResourceDoesNotExist
from pydantic import ValidationError
from rich import print as pprint
from rich.prompt import Confirm, Prompt
from typer import Typer

from canvy.const import (
    CONFIG_PATH,
    DEFAULT_DOWNLOAD_DIR,
)
from canvy.types import CanvyConfig, ModelProvider
from canvy.utils import (
    better_course_name,
    create_dir,
    delete_config,
    get_config,
    setup_logging,
)

cli = Typer()
logger = logging.getLogger(__name__)


def add_https(url: str):
    return url if url.startswith(("https://", "https://")) else f"https://{url}"


def requires_config() -> CanvyConfig:
    try:
        config = get_config()
        return config
    except FileNotFoundError:
        from canvy.utils import set_config

        choice = Confirm.ask("Config file doesn't exist, create one?")
        if not choice:
            sys.exit(1)
        url = add_https(input("Canvas URL: "))
        api_key_url = f"{url}/profile/settings"
        config = CanvyConfig(
            canvas_url=url,
            canvas_key=getpass(f"Canvas API Key ({api_key_url}): "),
            storage_path=Path(input("Store path (optional): ") or DEFAULT_DOWNLOAD_DIR),
            openai_key=getpass("Open AI Key (optional): "),
            ollama_model=input("Ollama model (optional): "),
            default_provider=ModelProvider.OPENAI,
        )
        set_config(config)
        return requires_config()  # XXX: Might be dangerous :smirking_cat:
    except ValidationError as e:
        pprint(f"Input values are incorrect: {e}")
    except (EOFError, KeyboardInterrupt):
        pprint("\n[bold red]Closing[/bold red]..")
    except Exception as e:
        pprint(f"Either the config is messed up or the internet is: {e}")
        user_choice = Confirm.ask("Destroy config file?")
        if user_choice:
            delete_config()
    sys.exit(1)


def requires_canvas() -> tuple[Canvas, CanvyConfig]:
    config = requires_config()
    canvas = Canvas(config.canvas_url, config.canvas_key)
    return canvas, config


@cli.command(short_help="Download files from Canvas")
def download(*, force: bool = False):
    from canvy.scripts import download

    canvas, config = requires_canvas()
    try:
        count = download(canvas, config.canvas_url, force=force)
        pprint(f"[bold]{count}[/bold] new files! :speaking_head: :fire:")
    except (KeyboardInterrupt, EOFError):
        pprint("[bold red]Download stopping[/bold red]...")
        sys.exit(0)
    except ResourceDoesNotExist as e:
        pprint(f"We likely don't have access to courses no more :sad_cat:: {e}")
        sys.exit(1)


@cli.command(short_help="Use an assistant to go through the files")
def teacher():
    from canvy.scripts import teacher

    config = requires_config()
    try:
        teacher(config)
    except (KeyboardInterrupt, EOFError):
        pprint("[bold red]Program exiting[/bold red]...")
        sys.exit(0)


@cli.command(short_help="List available courses")
def courses(*, detailed: bool = False):
    canvas, _ = requires_canvas()
    try:
        courses: list[Course] = list(
            canvas.get_courses(  # pyright: ignore[reportUnknownMemberType]
                enrollment_state="active",
            ),
        )
        if detailed:
            from rich.console import Console
            from rich.table import Table

            table = Table(title="Courses")
            table.add_column("No. Students", style="bold green")
            table.add_column("Title", style="bold")
            table.add_column("Creation date")
            table.add_column("Start date")
            for course in courses:
                table.add_row(
                    getattr(course, "total_students", ""),
                    better_course_name(course.name),  # pyright: ignore[reportAny]
                    course.created_at,  # pyright: ignore[reportAny]
                    getattr(course, "start_at", ""),
                )
            console = Console()
            console.print(table)
        else:
            for course in courses:
                print(f"{course}")  # noqa: T201
    except ResourceDoesNotExist as e:
        pprint(f"We probably don't have access to this course: {e}")
    except Exception as e:
        pprint(f"Unknown error: {e}")


# TODO: Test ts
@cli.command(short_help="Edit config")
def edit_config():
    from canvy.utils import set_config

    current = requires_config()
    try:
        new = CanvyConfig(
            canvas_url=add_https(
                Prompt.ask("Canvas URL: ", default=current.canvas_url)
            ),
            canvas_key=Prompt.ask(
                "Canvas API Key: ",
                show_default=False,
                default=current.canvas_key,
                password=True,
            ),
            storage_path=Path(Prompt.ask("Store path: ", default=current.storage_path)),
            openai_key=Prompt.ask(
                "Open AI Key: ",
                show_default=False,
                default=current.openai_key,
                password=True,
            )
            or "",
            ollama_model=Prompt.ask("Ollama model: ", default=current.ollama_model),
            default_provider=ModelProvider(
                Prompt.ask("Default provider: ", choices=list(ModelProvider))
            ),
        )
        set_config(new)
    except Exception as e:
        pprint(f"[bold red]Bad config[\bold  red]: {e}")


# @cli.command(short_help="Get grades for each course and assignment")
# def grades(*, course_only: bool = False):
#     from canvy.scripts import grades
#
#     canvas, _ = requires_canvas()
#     try:
#         stuff = grades_by_course(canvas) if course_only else grades(canvas)
#         pprint(stuff)
#     except ResourceDoesNotExist as e:
#         pprint(f"We probably don't have access to this course: {e}")
#     except Exception as e:
#         pprint(f"Unknown error: {e}")


@cli.command(short_help="Set up config to use the rest of the tool")
def set_config(  # noqa: PLR0913
    canvas_url: str | None = None,
    canvas_key: str | None = None,
    storage_path: Path | None = None,
    openai_key: str | None = None,
    ollama_model: str | None = None,
    default_provider: ModelProvider | None = None,
):
    from canvy.utils import set_config

    try:
        url = add_https(canvas_url or input("Canvas URL -> https://"))
        api_key_url = f"{url}/profile/settings"
        config = CanvyConfig(
            canvas_url=url,
            canvas_key=canvas_key or getpass(f"Canvas API Key ({api_key_url}): "),
            storage_path=storage_path or DEFAULT_DOWNLOAD_DIR,
            openai_key=openai_key or "",
            ollama_model=ollama_model or "",
            default_provider=default_provider or ModelProvider.OPENAI,
        )
        set_config(config)
    except ValidationError as e:
        pprint(f"Input values are incorrect: {e}")
    except (EOFError, KeyboardInterrupt):
        pprint("\n[bold red]Closing[/bold red]..")


# @cli.callback(invoke_without_command=True)
# def tui():
#     from canvy.tui import run
#     run()


def main():
    create_dir(CONFIG_PATH.parent)
    setup_logging()
    cli()


if __name__ == "__main__":
    main()

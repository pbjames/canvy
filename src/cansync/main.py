import logging
import sys
from getpass import getpass
from pathlib import Path

from canvasapi.canvas import Canvas, Course
from canvasapi.requester import ResourceDoesNotExist
from pydantic import ValidationError
from rich import print as pprint
from rich.prompt import Prompt
from typer import Typer

from cansync.const import (
    CONFIG_PATH,
    DEFAULT_DOWNLOAD_DIR,
)
from cansync.scripts.grades import grades_by_course
from cansync.types import CansyncConfig, ModelProvider
from cansync.utils import (
    better_course_name,
    create_dir,
    delete_config,
    get_config,
    setup_logging,
)

cli = Typer()
logger = logging.getLogger(__name__)


def add_https(url: str):
    if url.startswith("https://") or url.startswith("http://"):
        return url
    return f"https://{url}"


def requires_config() -> tuple[Canvas, CansyncConfig]:
    try:
        config = get_config()
        canvas = Canvas(config.canvas_url, config.canvas_key)
        return canvas, config
    except FileNotFoundError:
        from cansync.utils import set_config

        choice = (
            Prompt.ask(
                "Config file doesn't exist, create one?", choices=["Y", "n"]
            ).lower()
            != "n"
        )
        if not choice:
            sys.exit(1)
        config = CansyncConfig(
            canvas_url=add_https(input("Canvas URL: ")),
            canvas_key=getpass("Canvas API Key: "),
            storage_path=Path(input("Store path (optional): ") or DEFAULT_DOWNLOAD_DIR),
            openai_key=getpass("Open AI Key (optional): ") or None,
            ollama_model=input("Ollama model (optional): ") or None,
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
        user_choice = (
            Prompt.ask("Destroy config file?", choices=["n", "Y"]).lower() == "y"
        )
        if user_choice:
            delete_config()
    sys.exit(1)


@cli.command(short_help="Download files from Canvas")
def download(*, force: bool = False):
    from cansync.scripts.downloader import download

    canvas, config = requires_config()
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
    from cansync.scripts.teacher import teacher

    _, config = requires_config()
    try:
        teacher(config)
    except (KeyboardInterrupt, EOFError):
        pprint("[bold red]Program exiting[/bold red]...")
        sys.exit(0)


@cli.command(short_help="List available courses")
def courses(*, detailed: bool = False):
    canvas, _ = requires_config()
    try:
        courses: list[Course] = list(canvas.get_courses(enrollment_state="active"))
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
                    better_course_name(course.name),
                    course.created_at,
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


@cli.command(short_help="Get grades for each course and assignment")
def grades(*, course_only: bool = False):
    from cansync.scripts.grades import grades

    canvas, _ = requires_config()
    try:
        stuff = grades_by_course(canvas) if course_only else grades(canvas)
        pprint(stuff)
    except ResourceDoesNotExist as e:
        pprint(f"We probably don't have access to this course: {e}")
    except Exception as e:
        pprint(f"Unknown error: {e}")


@cli.command(short_help="Set up config to use the rest of the tool")
def set_config(  # noqa: PLR0913
    canvas_url: str | None = None,
    canvas_key: str | None = None,
    storage_path: Path | None = None,
    openai_key: str | None = None,
    ollama_model: str | None = None,
    default_provider: ModelProvider | None = None,
):
    from cansync.utils import set_config

    try:
        config = CansyncConfig(
            canvas_url=add_https(canvas_url or input("Canvas URL -> https://")),
            canvas_key=canvas_key or getpass("Canvas API Key: "),
            storage_path=storage_path or DEFAULT_DOWNLOAD_DIR,
            openai_key=openai_key,
            ollama_model=ollama_model,
            default_provider=default_provider or ModelProvider.OPENAI,
        )
        set_config(config)
    except ValidationError as e:
        pprint(f"Input values are incorrect: {e}")
    except (EOFError, KeyboardInterrupt):
        pprint("\n[bold red]Closing[/bold red]..")


def main():
    create_dir(CONFIG_PATH.parent)
    setup_logging()
    cli()
    # TODO: Use tests


if __name__ == "__main__":
    main()

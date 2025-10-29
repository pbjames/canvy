import logging
import sys
from getpass import getpass
from pathlib import Path

from canvasapi.canvas import Canvas, Course
from canvasapi.requester import ResourceDoesNotExist
from pydantic import ValidationError
from rich import print as pprint
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm, Prompt
from typer import Typer

from canvy.const import (
    CONFIG_PATH,
    DEFAULT_DOWNLOAD_DIR,
    LOG_FN,
)
from canvy.types import CanvyConfig, CLIClearFile
from canvy.utils import (
    better_course_name,
    create_dir,
    delete_config,
    get_config,
    setup_logging,
)

cli = Typer()
logger = logging.getLogger(__name__)


def requires_config() -> CanvyConfig:
    try:
        config = get_config()
        return config
    except FileNotFoundError:
        from canvy.utils import set_config

        choice = Confirm.ask("Config file doesn't exist, create one?")
        if not choice:
            sys.exit(1)
        url = CanvyConfig.add_https(input("Canvas URL: "))
        api_key_url = f"{url}/profile/settings"
        api_key = getpass(f"Canvas API Key ({api_key_url}): (hidden)")
        storage_path = Path(input("Store path (optional): ") or DEFAULT_DOWNLOAD_DIR)
        config = CanvyConfig(
            canvas_url=url,
            canvas_key=api_key,
            storage_path=storage_path,
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


def fancy_print_courses(courses: list[Course]):
    table = Table(title="Courses")
    table.add_column("ID")
    table.add_column("Title", style="bold")
    table.add_column("Creation date")
    table.add_column("Start date")
    for i, course in enumerate(courses):
        table.add_row(
            str(i),
            better_course_name(course.name),  # pyright: ignore[reportAny]
            course.created_at,  # pyright: ignore[reportAny]
            getattr(course, "start_at", ""),
        )
    console = Console()
    console.print(table)


@cli.command(short_help="Download files from Canvas")
def download(*, force: bool = False):
    from canvy.scripts import download

    canvas, config = requires_canvas()
    try:
        count = download(
            canvas, config.storage_path, force=force, courses=config.selected_courses
        )
        pprint(f"[bold]{count}[/bold] new files! :speaking_head: :fire:")
    except (KeyboardInterrupt, EOFError):
        pprint("[bold red]Download stopping[/bold red]...")
        sys.exit(0)
    except ResourceDoesNotExist as e:
        pprint(f"We likely don't have access to courses no more :sad_cat:: {e}")
        sys.exit(1)


@cli.command(short_help="List available courses")
def courses(*, detailed: bool = True):
    canvas, _ = requires_canvas()
    try:
        courses: list[Course] = list(
            canvas.get_courses(  # pyright: ignore[reportUnknownMemberType]
                enrollment_state="active",
            ),
        )
        if detailed:
            fancy_print_courses(courses)
        else:
            # INFO: mainly for machine output
            for course in courses:
                print(f"{course}")  # noqa: T201
    except ResourceDoesNotExist as e:
        pprint(f"We probably don't have access to this course: {e}")
    except Exception as e:
        pprint(f"Unknown error: {e}")


@cli.command(short_help="Edit config")
def edit_config():
    from canvy.utils import set_config

    current = requires_config()
    try:
        new = CanvyConfig(
            canvas_url=Prompt.ask("Canvas URL: ", default=current.canvas_url),
            canvas_key=Prompt.ask(
                "Canvas API Key: ",
                show_default=False,
                default=current.canvas_key,
                password=True,
            ),
            storage_path=Path(Prompt.ask("Store path: ", default=current.storage_path)),
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


@cli.command(short_help="Configure selected courses to be downloaded exclusively")
def select_courses():
    from canvy.utils import set_config

    selected_courses: list[int] = []
    canvas, current_config = requires_canvas()
    try:
        courses: list[Course] = list(
            canvas.get_courses(  # pyright: ignore[reportUnknownMemberType]
                enrollment_state="active",
            ),
        )
        course_ids: list[int] = [course.id for course in courses]
        fancy_print_courses(courses)
        additions = Prompt.ask("[bold]IDs[/bold] to whitelist (e.g. 0,1,3-5): ")
        for id_to_add in additions.replace(" ", "").split(","):
            if len(ids := id_to_add.split("-")) > 1:
                low_id, high_id = ids
                selected_courses.extend(
                    course_ids[id] for id in range(int(low_id), int(high_id) + 1)
                )
            else:
                selected_courses.append(course_ids[int(id_to_add)])
        current_config.selected_courses = selected_courses
        set_config(current_config)
    except ValueError:
        pprint(f"[bold red]Invalid input.[/bold red]")
    except Exception as e:
        pprint(f"[bold red]Unknown error occured[/bold red]: {e}")


@cli.command(short_help="Set up config to use the rest of the tool")
def set_config(  # noqa: PLR0913
    canvas_url: str | None = None,
    canvas_key: str | None = None,
    storage_path: Path | None = None,
):
    from canvy.utils import set_config

    try:
        url = canvas_url or input("Canvas URL -> https://")
        api_key_url = f"{url}/profile/settings"
        config = CanvyConfig(
            canvas_url=url,
            canvas_key=canvas_key or getpass(f"Canvas API Key ({api_key_url}): "),
            storage_path=storage_path or DEFAULT_DOWNLOAD_DIR,
        )
        set_config(config)
    except ValidationError as e:
        pprint(f"Input values are incorrect: {e}")
    except (EOFError, KeyboardInterrupt):
        pprint("\n[bold red]Closing[/bold red]..")


@cli.command(short_help="Delete log files")
def clear(file_type: CLIClearFile):
    if (ft := CLIClearFile(file_type)) is CLIClearFile.LOGS:
        for path in LOG_FN.parent.glob(f"{LOG_FN.name}*"):
            path.unlink()
    elif ft is CLIClearFile.CONFIG:
        delete_config()


def main():
    create_dir(CONFIG_PATH.parent)
    setup_logging()
    cli()


if __name__ == "__main__":
    main()

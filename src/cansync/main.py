import logging
from getpass import getpass
from itertools import chain
from pathlib import Path

from canvasapi.canvas import Canvas, Course
from canvasapi.module import Module
from typer import Typer

from cansync.const import DEFAULT_DOWNLOAD_DIR
from cansync.types import CansyncConfig, ModuleItemType
from cansync.utils import get_config, setup_logging
from cansync.utils import set_config as utils_set_config

cli = Typer()
logger = logging.getLogger(__name__)


@cli.command()
def download():
    canvas, config, user_courses = courses()
    for course in user_courses:
        resources_regex = (
            rf"{config.canvas_url}/(api/v1/)?courses/{id}/{course.id}/([0-9]+)"
        )
        for module in list(course.get_modules()):
            for item in list(module.get_module_items()):
                if (type := ModuleItemType(item.type)) == ModuleItemType.PAGE:
                    page = course.get_page(item.url)  # TODO: url or html_url?
                    print("Found page: {item}")
                elif type is ModuleItemType.ATTACHMENT:
                    file = canvas.get_file(item.content_id)
                    print(f"Found file: {file}")


@cli.command()
def courses():
    config = get_config()
    canvas = Canvas(config.canvas_url, config.canvas_key)
    courses: list[Course] = list(canvas.get_courses(enrollment_state="active"))
    for course in courses:
        print(f"{course}")
    return canvas, config, courses


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

import logging
import re
from collections.abc import Generator
from getpass import getpass
from pathlib import Path

from canvasapi.canvas import Canvas, Course
from canvasapi.file import File
from canvasapi.page import Page
from typer import Typer

from cansync.const import DEFAULT_DOWNLOAD_DIR
from cansync.types import CansyncConfig, ModuleItemType
from cansync.utils import (
    better_course_name,
    download_structured,
    get_config,
    setup_logging,
)
from cansync.utils import set_config as utils_set_config

cli = Typer()
logger = logging.getLogger(__name__)


def extract_files_from_page(
    canvas: Canvas, regex: str, page: Page
) -> Generator[File, None, None]:
    for _, id in re.findall(regex, page.body):
        logger.info(f"Scanned files({id}) from Page({page.id})")
        if id is not None:
            yield canvas.get_file(id)


@cli.command()
def download(force: bool = False):
    canvas, config, user_courses = courses()
    file_queue: list[tuple[list[str], File]] = []
    for course in user_courses:
        resource_regex = rf"{config.canvas_url}/(api/v1/)?courses/{course.id}/files/([0-9]+)"  # TODO: Look into this
        course_name = better_course_name(course.name)
        while file_queue:
            paths, file = file_queue.pop(force)
            download_structured(file, *map(Path, paths), force=force)
        for module in list(course.get_modules()):
            for item in list(module.get_module_items()):
                if (type := ModuleItemType(item.type)) == ModuleItemType.PAGE:
                    page = course.get_page(item.page_url)
                    if getattr(page, "body", None) is None:
                        continue
                    logging.info("Found page: {item}")
                    files = extract_files_from_page(canvas, resource_regex, page)
                    file_queue.extend(
                        (
                            [course_name, module.name, getattr(page, "title", "None")],
                            file,
                        )
                        for file in files
                    )
                elif type is ModuleItemType.ATTACHMENT:
                    file = canvas.get_file(item.content_id)
                    logging.info(f"Found file: {file}")
                    file_queue.append(
                        (
                            [
                                course_name,
                                module.name,
                                getattr(file, "filename", "None"),
                            ],
                            file,
                        )
                    )


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

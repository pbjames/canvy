# pyright: reportAny=false
# pyright: reportUnknownMemberType=false
import logging
import re
from collections.abc import Generator
from pathlib import Path

from canvasapi.canvas import Canvas
from canvasapi.course import Course
from canvasapi.exceptions import ResourceDoesNotExist
from canvasapi.file import File
from canvasapi.module import Module, ModuleItem
from canvasapi.page import Page

from cansync.types import ModuleItemType
from cansync.utils import (
    better_course_name,
    download_structured,
)

logger = logging.getLogger(__name__)


def extract_files_from_page(
    canvas: Canvas,
    course: Course,
    module: Module,
    regex: str,
    page: Page,
):
    """
    Use a regex generated from the ID of the course to scrape canvas file links
    and add them to the download queue. We do this because there can be many unmarked
    or arbitrarily organised files on Canvas, depending on the module organiser.
    """
    page_title = getattr(page, "title", "No Title")
    names = [better_course_name(course.name), module.name, page_title]
    if getattr(page, "body", None) is None:
        return
    logging.info(f"Found page: {page}")
    for id in re.findall(regex, page.body):
        if id is None:
            continue
        logger.info(f"Scanned file({id}) from Page({page.page_id})")
        try:
            yield (names, canvas.get_file(id))
        except ResourceDoesNotExist as e:
            logger.warning(f"No access to scrape page: {e}")
        except Exception:
            logger.error(f"Unknown error downloading file {id}")


def module_item_files(
    canvas: Canvas, course: Course, module: Module, regex: str, item: ModuleItem
) -> Generator[tuple[list[str], File], None, None]:
    """
    Process module items into the file queue for downloads
    """
    course_name = better_course_name(course.name)
    if (type := ModuleItemType(item.type)) == ModuleItemType.PAGE:
        page = course.get_page(item.page_url)
        yield from extract_files_from_page(canvas, course, module, regex, page)
    elif type is ModuleItemType.ATTACHMENT:
        file = canvas.get_file(item.content_id)
        names = [course_name, module.name]
        logging.info(f"Found file: {file}")
        yield (names, file)


def download(canvas: Canvas, url: str) -> int:
    """
    Download every file accessible through a Canvas account through courses and modules
    """
    from rich.progress import Progress

    with Progress() as progress:
        user_courses = list(canvas.get_courses(enrollment_state="active"))
        file_queue: list[tuple[list[str], File]] = []
        download_count = 0
        progress_course = progress.add_task("Course", total=len(user_courses))
        for course in user_courses:
            progress.update(
                progress_course, description=f"Course: {course.course_code}", advance=0
            )
            resource_regex = rf"{url}/(?:api/v1/)?courses/{course.id}/files/([0-9]+)"
            while file_queue:
                paths, file = file_queue.pop()
                download_count += download_structured(file, *map(Path, paths))
            modules = list(course.get_modules())
            progress_module = progress.add_task(
                "Module", total=len(modules), start=False
            )
            for module in modules:
                progress.update(
                    progress_module, description=f"Module: {module.name}", advance=0
                )
                progress.start_task(progress_module)
                items = list(module.get_module_items())
                progress_items = progress.add_task(
                    "Items", total=len(items), start=False
                )
                for item in items:
                    progress.start_task(progress_items)
                    file_queue.extend(
                        module_item_files(canvas, course, module, resource_regex, item)
                    )
                    progress.update(progress_items, advance=1)
                progress.remove_task(progress_items)
                progress.update(progress_module, advance=1)
            progress.remove_task(progress_module)
            progress.update(progress_course, advance=1)
    return download_count

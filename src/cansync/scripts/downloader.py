# pyright: reportAny=false
# pyright: reportUnknownMemberType=false
import logging
import re
from pathlib import Path

from canvasapi.canvas import Canvas
from canvasapi.course import Course
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
    page_title = getattr(page, "title", "No Title")
    names = [better_course_name(course.name), module.name, page_title]
    if getattr(page, "body", None) is None:
        yield None  # INFO: Don't want to stop generator
    else:
        logging.info(f"Found page: {page}")
        for id in re.findall(regex, page.body):
            logger.info(f"Scanned files({id}) from Page({page.page_id})")
            if id is not None:
                yield (names, canvas.get_file(id))


def module_item_files(
    canvas: Canvas, course: Course, module: Module, regex: str, item: ModuleItem
):
    course_name = better_course_name(course.name)
    if (type := ModuleItemType(item.type)) == ModuleItemType.PAGE:
        page = course.get_page(item.page_url)
        yield from extract_files_from_page(canvas, course, module, regex, page)
    elif type is ModuleItemType.ATTACHMENT:
        file = canvas.get_file(item.content_id)
        names = [course_name, module.name]
        logging.info(f"Found file: {file}")
        yield (names, file)


def download(canvas: Canvas, url: str, force: bool):
    user_courses = canvas.get_courses(enrollment_state="active")
    file_queue: list[tuple[list[str], File]] = []
    for course in user_courses:
        resource_regex = rf"{url}/(?:api/v1/)?courses/{course.id}/files/([0-9]+)"
        while file_queue:
            paths, file = file_queue.pop(force)
            download_structured(file, *map(Path, paths), force=force)
        for module in list(course.get_modules()):
            for item in list(module.get_module_items()):
                item_source = module_item_files(
                    canvas, course, module, resource_regex, item
                )
                file_queue.extend(filter(None, item_source))

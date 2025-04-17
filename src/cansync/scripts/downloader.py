# pyright: reportAny=false
# pyright: reportUnknownMemberType=false
import logging
import re
from collections.abc import Generator
from pathlib import Path

from canvasapi.canvas import Canvas
from canvasapi.file import File
from canvasapi.page import Page

from cansync.types import ModuleItemType
from cansync.utils import (
    better_course_name,
    download_structured,
)

logger = logging.getLogger(__name__)


def extract_files_from_page(
    canvas: Canvas, regex: str, page: Page
) -> Generator[File, None, None]:
    for id in re.findall(regex, page.body):
        logger.info(f"Scanned files({id}) from Page({page.page_id})")
        if id is not None:
            yield canvas.get_file(id)


def download(canvas: Canvas, url: str, force: bool = False):
    user_courses = canvas.get_courses(enrollment_state="active")
    file_queue: list[tuple[list[str], File]] = []
    for course in user_courses:
        resource_regex = rf"{url}/(?:api/v1/)?courses/{course.id}/files/([0-9]+)"
        course_name = better_course_name(course.name)
        while file_queue:
            paths, file = file_queue.pop(force)
            download_structured(file, *map(Path, paths), force=force)
        for module in list(course.get_modules()):
            for item in list(module.get_module_items()):
                if (type := ModuleItemType(item.type)) == ModuleItemType.PAGE:
                    page = course.get_page(item.page_url)
                    page_title = getattr(page, "title", "No Title")
                    names = [course_name, module.name, page_title]
                    if getattr(page, "body", None) is None:
                        continue
                    logging.info("Found page: {item}")
                    files = extract_files_from_page(canvas, resource_regex, page)
                    file_queue.extend(
                        ([*names, getattr(file, "filename", "No Filename")], file)
                        for file in files
                    )
                elif type is ModuleItemType.ATTACHMENT:
                    file = canvas.get_file(item.content_id)
                    file_name = getattr(file, "filename", "No Filename")
                    names = [course_name, module.name, file_name]
                    logging.info(f"Found file: {file}")
                    file_queue.append((names, file))

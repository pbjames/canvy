# pyright: reportAny=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false
import logging
import re
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from canvasapi.canvas import Canvas
from canvasapi.course import Course
from canvasapi.exceptions import ResourceDoesNotExist
from canvasapi.file import File
from canvasapi.module import Module, ModuleItem
from canvasapi.page import Page

from canvy.types import ModuleItemType
from canvy.utils import better_course_name, download_structured, get_config

logger = logging.getLogger(__name__)


def extract_files_from_page(
    canvas: Canvas,
    course: Course,
    module: Module,
    page: Page,
):
    """
    Use a regex generated from the id of the course to scrape canvas file links
    and add them to the download queue. We do this because there can be many unmarked
    or arbitrarily organised files on Canvas, depending on the module organiser.

    Returns:
        download_structured arguments
    """
    # INFO: There has to be a better way bro
    regex = rf"{get_config().canvas_url}/(?:api/v1/)?courses/{course.id}/files/([0-9]+)"
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
    canvas: Canvas, course: Course, module: Module, item: ModuleItem
) -> Generator[tuple[list[str], File], None, None]:
    """
    Process module items into the file queue for downloads

    Returns:
        download_structured arguments - directly and through page scanning
    """
    course_name = better_course_name(course.name)
    if (type := ModuleItemType(item.type)) == ModuleItemType.PAGE:
        page = course.get_page(item.page_url)
        yield from extract_files_from_page(canvas, course, module, page)
    elif type is ModuleItemType.ATTACHMENT:
        file = canvas.get_file(item.content_id)
        names = [course_name, module.name]
        logging.info(f"Found file: {file}")
        yield (names, file)


def download(
    canvas: Canvas, storage_dir: Path | None = None, *, force: bool = False
) -> int:
    # TODO: Define behaviour for canvas files that are more recent than ours
    """
    Download every file accessible through a Canvas account on courses and modules

    Args:
        canvas: Canvas instance
        url: Institution URL where the Canvas server is hosted
        force: Override existing files?

    Returns:
        Downloaded file count - not including skipped downloads
    """
    from threading import Lock

    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import Progress

    count_lock = Lock()
    download_count = 0

    def safe_download(file: File, paths: list[str]):
        def inner():
            res = download_structured(
                file, *paths, storage_dir=storage_dir, force=force
            )
            with count_lock:
                nonlocal download_count
                download_count += res

        return inner

    console = Console()
    progress = Progress(expand=True)
    panel = Panel(progress, title="Downloading...", border_style="green", width=100)

    with (
        Live(panel, refresh_per_second=5, console=console),
        ThreadPoolExecutor(max_workers=5) as executor,
    ):
        user_courses = list(canvas.get_courses(enrollment_state="active"))
        progress_course = progress.add_task("Course", total=len(user_courses))
        progress_module = progress.add_task("Module")
        progress_items = progress.add_task("Downloading files...")
        for course in user_courses:
            progress.update(
                progress_course, description=f"Course: {course.course_code}"
            )
            for module in (modules := list(course.get_modules())):
                progress.update(
                    progress_module,
                    description=f"Module: {module.name}",
                    total=len(modules),
                )
                for item in (items := list(module.get_module_items())):
                    for paths, file in module_item_files(canvas, course, module, item):
                        progress.update(
                            progress_items,
                            description=f"  File: {file.filename}",
                            total=len(items),
                        )
                        executor.submit(safe_download(file, paths))
                    progress.update(progress_items, advance=1)
                progress.update(progress_module, advance=1)
                progress.reset(progress_items)
            progress.update(progress_course, advance=1)
            progress.reset(progress_module)
    return download_count

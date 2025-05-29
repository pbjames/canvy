# pyright: reportAny=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock
from typing import ClassVar, override

from agno.document.reader.pdf_reader import PDFReader
from canvasapi.canvas import Canvas
from canvasapi.file import File
from canvy.tui.const import CanvyMode
from textual import on, work
from textual.app import ComposeResult
from textual.color import Gradient
from textual.containers import HorizontalGroup, VerticalGroup, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.timer import Timer
from textual.widgets import (
    Button,
    DirectoryTree,
    Label,
    Markdown,
    ProgressBar,
)

from canvy.const import DOCSCRAPE_DEFAULT_MSG
from canvy.scripts import tutor
from canvy.scripts.downloader import module_item_files
from canvy.types import CanvyConfig, Model
from canvy.utils import (
    download_structured,
    get_config,
    get_summary,
    provider,
    put_summary,
    setup_cache_mirror,
)

logger = logging.getLogger(__name__)


COOL_GRADIENT: Gradient = Gradient.from_colors(
    "#881177",
    "#aa3355",
    "#cc6666",
    "#ee9944",
    "#eedd00",
    "#99dd55",
    "#44dd88",
    "#22ccbb",
    "#00bbcc",
    "#0099cc",
    "#3366bb",
    "#663399",
)


class FSTree(DirectoryTree):
    timer: Timer | None

    DEFAULT_CSS: ClassVar[
        str
    ] = """
    FSTree {
        width: 35%;
        border: vkey gray;
        background: $background;
    }
    """

    def __init__(
        self,
        path: str | Path,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        self.timer = None
        super().__init__(path, name=name, id=id, classes=classes, disabled=disabled)

    @override
    def on_mount(self):
        super().on_mount()
        self.timer = self.set_interval(3, callback=self.update_time)

    def update_time(self):
        self.reload()


class Content(VerticalGroup):
    """
    Show extracted PDF contents for fun
    """

    DEFAULT_CSS: ClassVar[
        str
    ] = """
    Content {
        content-align: center top;
        height: 100%
    }
    /*
    border: 'ascii', 'blank', 'dashed', 'double', 'heavy', 'hidden', 'hkey', 'inner',
            'none', 'outer', 'panel', 'round', 'solid', 'tab', 'tall', 'thick', 'vkey',
            'wide'
    */
    """

    @override
    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            Markdown(
                """\
# Canvy

Content for a selected file will appear here, it doesn't work very well with PDFs at the \
moment - unless you use an LLM.

## Supported File Types

Markdown syntax and extensions are supported.

- PDF documents
- Plaintext
- Markdown
"""
            )
        )


class DownloadControl(HorizontalGroup):
    """
    Report download progress
    """

    DEFAULT_CSS: ClassVar[
        str
    ] = """
    DownloadControl {
        dock: bottom;
        align: center middle;
        border: hkey gray;
    }

    #group_1 {
        align: center middle;
        width: 65%;
    }

    #group_2 {
        align: center middle;
        width: 35%;
    }

    #download_button {
        margin-right: 3;
    }

    #cancel_button {
        margin-right: 3;
    }

    VerticalGroup {
        width: auto;
        margin: 0 3;
    }
    """

    download_count: reactive[int] = reactive(0)
    _terminate: bool = False

    @property
    def terminate(self):
        return self._terminate

    @override
    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="group_1"):
            with VerticalGroup():
                yield Label("Files", id="lab_files")
                yield ProgressBar(id="pg_files", show_eta=False, gradient=COOL_GRADIENT)
            with VerticalGroup():
                yield Label("Modules", id="lab_modules")
                yield ProgressBar(
                    id="pg_modules", show_eta=False, gradient=COOL_GRADIENT
                )
            with VerticalGroup():
                yield Label("Courses", id="lab_courses")
                yield ProgressBar(
                    id="pg_courses", show_eta=False, gradient=COOL_GRADIENT
                )
        with HorizontalGroup(id="group_2"):
            yield Button("Download", id="download_button", variant="success")
            yield Button("Cancel", id="cancel_button", variant="primary")
            yield Button("Back", id="quit_button", variant="error")

    class Start(Message): ...

    class Stop(Message): ...

    @on(Button.Pressed, "#download_button")
    def start_download(self) -> None:
        self.post_message(self.Start())
        self.download()

    @on(Button.Pressed, "#cancel_button")
    def stop_download(self) -> None:
        self._terminate = True
        self.query_exactly_one("#pg_courses", expect_type=ProgressBar).update(total=0)
        self.query_exactly_one("#pg_modules", expect_type=ProgressBar).update(total=0)
        self.query_exactly_one("#pg_files", expect_type=ProgressBar).update(total=0)
        self.post_message(self.Stop())

    @on(Button.Pressed, "#quit_button")
    def quit(self) -> None:
        self.app.switch_mode(CanvyMode.MAIN)

    @work(thread=True)
    def download(self, *, force: bool = False):
        # TODO: Fix course length inaccuracy
        count_lock = Lock()
        config = get_config()
        canvas = Canvas(config.canvas_url, config.canvas_key)

        def safe_download(file: File, paths: list[str]):
            def inner():
                res = download_structured(
                    file, *paths, storage_dir=config.storage_path, force=force
                )
                with count_lock:
                    self.download_count += res

            return inner

        with ThreadPoolExecutor(max_workers=5) as executor:
            progress_courses = self.query_exactly_one(
                "#pg_courses", expect_type=ProgressBar
            )
            progress_modules = self.query_exactly_one(
                "#pg_modules", expect_type=ProgressBar
            )
            progress_files = self.query_exactly_one(
                "#pg_files", expect_type=ProgressBar
            )
            label_courses = self.query_exactly_one("#lab_courses", expect_type=Label)
            label_modules = self.query_exactly_one("#lab_modules", expect_type=Label)
            label_files = self.query_exactly_one("#lab_files", expect_type=Label)
            user_courses = list(canvas.get_courses(enrollment_state="active"))
            for course in user_courses:
                label_courses.update(f"Course: {course.course_code}")
                progress_courses.update(total=len(user_courses))
                for module in (modules := list(course.get_modules())):
                    label_modules.update(f"Module: {module.name}")
                    progress_modules.update(total=len(modules))
                    for item in module.get_module_items():
                        path_files = list(
                            module_item_files(canvas, course, module, item)
                        )
                        progress_files.update(total=len(path_files))
                        for paths, file in path_files:
                            if self.terminate:
                                executor.shutdown(wait=False, cancel_futures=True)
                                return
                            else:
                                label_files.update(f"Files: {file.filename}")
                                executor.submit(safe_download(file, paths))
                        progress_files.advance()
                    progress_modules.advance()
                    progress_files.update(total=0)
                progress_courses.advance()
                progress_modules.update(total=0)
            progress_courses.update(total=0)


class DownloadPage(Screen[None]):
    llm_provider: Model
    config: CanvyConfig

    def __init__(
        self, name: str | None = None, id: str | None = None, classes: str | None = None
    ) -> None:
        super().__init__(name, id, classes)
        self.config = get_config()
        self.llm_provider = provider(self.config)
        if self.llm_provider is not None:
            setup_cache_mirror(self.config)  # maybe expensive?

    @override
    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            fst = FSTree(self.config.storage_path)
            yield fst
            yield Content()
        yield DownloadControl()

    @on(FSTree.FileSelected)
    def update_on_select(self, msg: FSTree.FileSelected):
        logger.info(f"File {msg.path} selected on FSTree")
        file_path = msg.path
        md_widget = self.query_exactly_one(Markdown)
        if (ext := file_path.suffix) == ".pdf":
            self.populate_document(file_path)
        elif ext in {".txt", ".md", ""}:
            md_widget.update(file_path.read_text())
        else:
            logger.warning(f"Unhandled file type: {file_path}")

    def populate_document(self, file_path: Path):
        md_widget = self.query_exactly_one(Markdown)
        documents = PDFReader().read(file_path)
        content = "".join(d.content for d in documents)
        if self.llm_provider is None:
            md_widget.update(DOCSCRAPE_DEFAULT_MSG + content)
        else:
            agent = tutor(self.config, interactive=False)
            if response := get_summary(self.config, file_path):
                md_widget.update(response)
                return
            response = agent.run(
                f"Summarise the content from: {file_path}", stream=True
            )
            total = []
            for r in response:
                # TODO: Re-rendering causes the FSTree to not populate while the response is being built
                total.append(r.content)
                md_widget.update("".join(total))
            put_summary(self.config, file_path, "".join(total))

    def on_mount(self):
        self.border_title: str = "Login"

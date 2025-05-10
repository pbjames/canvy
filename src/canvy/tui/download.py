import logging
from typing import ClassVar, override

from textual import on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, ProgressBar, TextArea, Tree

logger = logging.getLogger(__name__)


class FilesTree(VerticalGroup):
    """
    Watch the storage directory - that's all
    """

    DEFAULT_CSS: ClassVar[
        str
    ] = """
    FilesTree {
    }
    """

    @override
    def compose(self) -> ComposeResult:
        yield Tree("Storage")


class Content(VerticalGroup):
    """
    Show extracted PDF contents for fun
    """

    @override
    def compose(self) -> ComposeResult:
        yield TextArea("hello everynyan")


class Progress(HorizontalGroup):
    """
    Report download progress
    """

    @override
    def compose(self) -> ComposeResult:
        yield ProgressBar()
        yield ProgressBar()
        yield ProgressBar()


class DownloadControl(HorizontalGroup):
    """
    Hold like 2 buttons
    """

    class Start(Message): ...

    class Stop(Message): ...

    @on(Button.Pressed, "#download_button")
    def start_download(self) -> None: ...

    @on(Button.Pressed, "#cancel_button")
    def stop_download(self) -> None: ...

    @override
    def compose(self) -> ComposeResult:
        yield Button("Download", id="download_button", variant="success")
        yield Button("Cancel", id="cancel_button", variant="primary")


class DownloadPage(Screen[None]):
    DEFAULT_CSS: ClassVar[
        str
    ] = """
    DownloadPage {
    }
    """

    @override
    def compose(self) -> ComposeResult:
        yield FilesTree()
        with VerticalGroup():
            yield Content()
            yield DownloadControl()
        yield Progress()

    def on_mount(self):
        self.border_title: str = "Login"

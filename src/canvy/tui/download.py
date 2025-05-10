import logging
import sys
from typing import ClassVar, override

from textual import on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, DirectoryTree, Footer, Header, ProgressBar, Static

from canvy.utils import get_config

logger = logging.getLogger(__name__)


class FSTree(DirectoryTree):
    DEFAULT_CSS: ClassVar[
        str
    ] = """
    FSTree {
        width: 35%;
        border: vkey gray;
        background: $background;
    }
    """


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
    """

    @override
    def compose(self) -> ComposeResult:
        yield Static(
            """\
        hello everynyan
        f
        fdjklafj

        fjdklafjalk
        """
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
        margin: 1;
        width: 65%
    }

    #group_2 {
        align: center middle;
        margin: 0;
        width: 35%
    }

    #download_button {
        margin-right: 3;
    }

    #cancel_button {
        margin-right: 3;
    }
    """
    # INFO: 'ascii', 'blank', 'dashed', 'double', 'heavy', 'hidden', 'hkey', 'inner',
    # 'none', 'outer', 'panel', 'round', 'solid', 'tab', 'tall', 'thick', 'vkey', or 'wide'

    class Start(Message): ...

    class Stop(Message): ...

    class Quit(Message): ...

    @on(Button.Pressed, "#download_button")
    def start_download(self) -> None: ...

    @on(Button.Pressed, "#cancel_button")
    def stop_download(self) -> None: ...

    @on(Button.Pressed, "#quit_button")
    def quit(self) -> None:
        self.post_message(self.Quit())

    @override
    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="group_1"):
            yield ProgressBar()
            yield ProgressBar()
            yield ProgressBar()
        with HorizontalGroup(id="group_2"):
            yield Button("Download", id="download_button", variant="success")
            yield Button("Cancel", id="cancel_button", variant="primary")
            yield Button("Quit", id="quit_button", variant="error")


class DownloadPage(Screen[None]):
    DEFAULT_CSS: ClassVar[
        str
    ] = """
    DownloadPage {
    }
    """

    @override
    def compose(self) -> ComposeResult:
        config = get_config()
        with HorizontalGroup():
            yield FSTree(config.storage_path)
            yield Content()
        yield DownloadControl()

    @on(DownloadControl.Quit)
    def quit(self):
        self.app.exit()

    def on_mount(self):
        self.border_title: str = "Login"

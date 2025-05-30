from typing import ClassVar, override

from canvy.tui.const import CanvyMode
from canvy.types import CanvyConfig
from canvy.utils import get_config, provider
from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button


class MainPage(Screen[None]):
    DEFAULT_CSS: ClassVar[
        str
    ] = """
    MainPage {
        align: center middle;
    }

    VerticalGroup {
        align: center top;
        border: heavy gray;
        max-width: 15%;
    }

    Button {
        margin: 1 0;
    }

    .disabled {
        hatch: cross gray;
    }
    """

    config: CanvyConfig

    class Switch(Message):
        def __init__(self, target: CanvyMode) -> None:
            self.target: str = target
            super().__init__()

    def __init__(
        self, name: str | None = None, id: str | None = None, classes: str | None = None
    ) -> None:
        self.config = get_config()
        super().__init__(name, id, classes)

    @override
    def compose(self) -> ComposeResult:
        # TODO: Check if this raises an error on shorthand syntax
        with VerticalGroup():
            yield Button("Download", id="download_button")
            yield Button(
                "Tutor", id="tutor_button", disabled=provider(self.config) is None
            )
            yield Button("Settings", id="settings_button")
            yield Button("Quit", id="quit_button", variant="error")

    @on(Button.Pressed)
    def emit_switch(self, event: Button.Pressed):
        selected = {
            "download_button": CanvyMode.DOWNLOAD,
            "tutor_button": CanvyMode.TUTOR,
            "settings_button": CanvyMode.SETTINGS
        }.get(event.button.id or "")
        self.app.switch_mode(selected or CanvyMode.MAIN)

    @on(Button.Pressed, "#quit_button")
    def quit(self):
        self.app.exit()

from typing import ClassVar, override

from canvy.types import CanvyConfig
from canvy.utils import get_config
from textual import on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.screen import Screen
from textual.widgets import Button, Input


class HelpPage(Screen[None]):
    DEFAULT_CSS: ClassVar[str] = """
    Help {
        layout: vertical;
        align: center middle;
        border-title-align: center;
        max-width: 30%;
        border: heavy gray;
        padding: 2
    }

    Input {
        margin: 1;
    }

    Button  {
        margin: 1;
    }
    """

    config: CanvyConfig

    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        self.config = get_config()

    @override
    def compose(self) -> ComposeResult:
        yield Input("", id="")
        with HorizontalGroup():
            yield Button("Save", id="save_button", variant="primary")
            yield Button("Back", id="quit_button", variant="error")

    @on(Button.Pressed, "#quit_button")
    def quit(self):
        self.app.exit()

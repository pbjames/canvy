import logging
from typing import ClassVar, override

from pydantic import ValidationError
from textual.app import App, ComposeResult
from textual.binding import BindingType
from textual.containers import VerticalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, Static

from canvy.types import CanvyConfig

logger = logging.getLogger(__name__)


class LoginPage(VerticalGroup):

    def on_button_pressed(self, event: Button.Pressed):
        url_input = self.query_one("#url_input").value
        sk_input = self.query_one("#sk_input").value
        logger.info(f"Login page info: {url_input}: {sk_input[:5] + "."*20}")
        try:
            config = CanvyConfig(canvas_url=url_input, canvas_key=sk_input)
            set_config(config)
        except ValidationError as e:
            logger.error(e)
    @override
    def compose(self) -> ComposeResult:
        yield Static("Login")
        yield Input(id="url_input")
        yield Input(id="sk_input")
        yield Button("Submit", variant="success")


class Canvy(App[None]):
    BINDINGS: ClassVar[list[BindingType]] = []

    @override
    def compose(self) -> ComposeResult:
        yield Header()
        yield LoginPage()
        yield Footer()
        # yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch(), id="timers")


def run():
    app = Canvy()
    app.run()

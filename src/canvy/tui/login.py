import logging
from typing import ClassVar, override

from canvy.tui.const import CanvyMode
from pydantic import ValidationError
from textual import on
from textual.app import ComposeResult
from textual.containers import Center
from textual.screen import Screen
from textual.widgets import Button, Input

from canvy.const import LOGIN_CULPRITS
from canvy.types import CanvyConfig
from canvy.utils import set_config

logger = logging.getLogger(__name__)


class LoginPage(Screen[None]):
    DEFAULT_CSS: ClassVar[
        str
    ] = """
    Screen {
        align: center middle;
    }

    LoginPage {
        layout: vertical;
        align: center middle;
        border-title-align: center;
        transition: offset 200ms;
        width: 30%;
        border: heavy gray;
        padding: 2;
    }

    Input {
        margin: 1;
    }

    Button {
        margin: 1;
    }
    """

    @override
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Your Canvas URL", id="url_input")
        yield Input(placeholder="API Key", id="sk_input")
        with Center():
            yield Button("Submit", variant="success")

    def on_mount(self):
        self.border_title: str = "Login"

    @on(Button.Pressed)
    def validate_inputs(self, _: Button.Pressed):
        url_input: str = self.query_one("#url_input", expect_type=Input).value
        sk_input: str = self.query_one("#sk_input", expect_type=Input).value
        logger.info(f"Login page info: {url_input}: {sk_input[:5] + "."*20}")
        try:
            config = CanvyConfig(canvas_url=url_input, canvas_key=sk_input)
            set_config(config)
            self.app.switch_mode(CanvyMode.MAIN)
        except ValidationError as e:
            logger.info(f"Invalid login page submission: {e}")
            culprits: list[str] = [str(next(iter(d["loc"]))) for d in e.errors()]
            for culprit in reversed(culprits):
                self.notify(f"Invalid [b]{LOGIN_CULPRITS[culprit]}[/b]", severity="error")

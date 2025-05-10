import logging
from typing import ClassVar, override

from pydantic import ValidationError
from textual import on
from textual.app import App, ComposeResult
from textual.binding import BindingType
from textual.containers import VerticalGroup
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, Static

from canvy.types import CanvyConfig
from canvy.utils import has_config, set_config

logger = logging.getLogger(__name__)


class LoginPage(VerticalGroup):
    DEFAULT_CSS: ClassVar[
        str
    ] = """
    LoginPage {
        offset-x: 0;
        transition: offset 200ms;
        &.-invisible {
            offset-x: -100%;
        }
    }
    """

    class Success(Message):
        """
        Tell CanvyApp that we've logged in
        """

        def __init__(self) -> None:
            super().__init__()

    def on_button_pressed(self, _: Button.Pressed):
        url_input: str = self.query_one("#url_input", expect_type=Input).value
        sk_input: str = self.query_one("#sk_input", expect_type=Input).value
        logger.info(f"Login page info: {url_input}: {sk_input[:5] + "."*20}")
        try:
            config = CanvyConfig(canvas_url=url_input, canvas_key=sk_input)
            set_config(config)
            self.post_message(self.Success())
        except ValidationError as e:
            logger.info(f"Invalid login page submission: {e}")

    @override
    def compose(self) -> ComposeResult:
        yield Static("Login")
        yield Input(id="url_input")
        yield Input(id="sk_input")
        yield Button("Submit", variant="success")


class Canvy(App[None]):
    BINDINGS: ClassVar[list[BindingType]] = []
    logged_in: reactive[bool] = reactive(False)  # noqa: FBT003

    @on(LoginPage.Success)
    def hide_login_page(self):
        self.query_one(LoginPage).set_class(True, "-invisible")  # noqa: FBT003

    @override
    def compose(self) -> ComposeResult:
        yield Header()
        if not has_config():
            yield LoginPage()
        yield Footer()


def run():
    app = Canvy()
    app.run()

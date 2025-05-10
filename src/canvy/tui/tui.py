import logging
from collections.abc import Callable
from typing import ClassVar

from textual import on
from textual.app import App
from textual.binding import BindingType
from textual.screen import Screen

from canvy.tui.download import DownloadPage
from canvy.tui.login import LoginPage
from canvy.utils import has_config

logger = logging.getLogger(__name__)


class Canvy(App[None]):
    MODES: ClassVar[dict[str, str | Callable[..., Screen[None]]]] = {
        "login": LoginPage,
        "main": DownloadPage,
    }
    BINDINGS: ClassVar[list[BindingType]] = []

    @on(LoginPage.Success)
    def switch_from_login_page(self):
        self.switch_mode("main")

    @on(LoginPage.Error)
    def notify_login_error(self, message: LoginPage.Error):
        self.notify(message.err_msg, severity="error")

    def on_mount(self):
        self.switch_mode("login" if not has_config() else "main")


def run():
    app = Canvy()
    app.run()

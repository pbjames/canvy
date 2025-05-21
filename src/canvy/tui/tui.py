import logging
from collections.abc import Callable
from typing import ClassVar

from canvy.tui.const import CanvyMode
from canvy.tui.mainpage import MainPage
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
        CanvyMode.LOGIN: LoginPage,
        CanvyMode.DOWNLOAD: DownloadPage,
        CanvyMode.TUTOR: DownloadPage,
        CanvyMode.SETTINGS: DownloadPage,
        CanvyMode.MAIN: MainPage,
    }
    BINDINGS: ClassVar[list[BindingType]] = []

    @on(LoginPage.Success)
    def switch_from_login_page(self):
        self.switch_mode(CanvyMode.MAIN)

    @on(MainPage.Switch)
    def switch_from_main_page(self, event: MainPage.Switch):
        self.switch_mode(event.target)

    @on(LoginPage.Error)
    def notify_login_error(self, message: LoginPage.Error):
        self.notify(message.err_msg, severity="error")

    def on_mount(self):
        self.switch_mode("login" if not has_config() else "main")


def run():
    app = Canvy()
    app.run()

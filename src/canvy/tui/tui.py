import logging
from collections.abc import Callable
from typing import ClassVar

from canvy.tui.const import CanvyMode
from canvy.tui.help import HelpPage
from canvy.tui.main import MainPage
from canvy.tui.settings import SettingsPage
from canvy.tui.tutor import TutorPage
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
        CanvyMode.TUTOR: TutorPage,
        CanvyMode.SETTINGS: SettingsPage,
        CanvyMode.MAIN: MainPage,
        CanvyMode.HELP: HelpPage,
    }
    BINDINGS: ClassVar[list[BindingType]] = []

    def on_mount(self):
        self.switch_mode("login" if not has_config() else "main")


def run():
    app = Canvy()
    app.run()
